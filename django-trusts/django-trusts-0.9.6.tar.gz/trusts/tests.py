import os
import json
import settings
import unittest

from decimal import Decimal
from urllib import urlencode
from urlparse import urlparse
from datetime import date, datetime, timedelta
from mock import Mock

from django.apps import apps
from django.db import models, connection, IntegrityError
from django.db.models import F
from django.db.models.base import ModelBase
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.color import no_style
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.management import update_contenttypes
from django.test import TestCase, TransactionTestCase
from django.test.client import MULTIPART_CONTENT, Client
from django.http.request import HttpRequest

from trusts.models import Trust, TrustUserPermission, TrustManager, Content, Junction
from trusts.backends import TrustModelBackend
from trusts.decorators import permission_required


def create_test_users(test):
    # Create a user.
    test.username = 'daniel'
    test.password = 'pass'
    test.user = User.objects.create_user(test.username, 'daniel@example.com', test.password)
    test.user.is_active = True
    test.user.save()

    # Create another
    test.name1 = 'anotheruser'
    test.pass1 = 'pass'
    test.user1 = User.objects.create_user(test.name1, 'another@example.com', test.pass1)
    test.user1.is_active = True
    test.user1.save()

def get_or_create_root_user(test):
    # Create a user.

    pk = getattr(settings, 'TRUSTS_ROOT_SETTLOR', 1)
    test.user_root, created = User.objects.get_or_create(pk=pk)


class TrustTest(TestCase):
    ROOT_PK = getattr(settings, 'TRUSTS_ROOT_PK', 1)
    SETTLOR_PK = getattr(settings, 'TRUSTS_ROOT_SETTLOR', None)

    def setUp(self):
        super(TrustTest, self).setUp()

        call_command('create_trust_root')

        get_or_create_root_user(self)

        create_test_users(self)

    def get_perm_code(self, perm):
        return '%s.%s' % (
            perm.content_type.app_label, perm.codename
         )

    def test_root(self):
        root = Trust.objects.get_root()
        self.assertEqual(root.pk, self.ROOT_PK)
        self.assertEqual(root.pk, root.trust.pk)
        self.assertEqual(Trust.objects.filter(trust=F('id')).count(), 1)

    def test_trust_unique_together_title_settlor(self):
        # Create `Title A` for user
        self.trust = Trust(settlor=self.user, title='Title A', trust=Trust.objects.get_root())
        self.trust.save()

        # Create `Title A` for user1
        self.trust1 = Trust(settlor=self.user1, title='Title A', trust=Trust.objects.get_root())
        self.trust1.save()

        # Empty string title should be allowed (reserved for settlor_default)
        self.trust = Trust(settlor=self.user, title='', trust=Trust.objects.get_root())
        self.trust.save()

        # Create `Title A` for user, again (should fail)
        try:
            self.trust2 = Trust(settlor=self.user, title='Title A', trust=Trust.objects.get_root())
            self.trust2.save()
            self.fail('Expected IntegrityError not raised.')
        except IntegrityError as ie:
            pass

    def test_read_permissions_added(self):
        ct = ContentType.objects.get_for_model(Trust)
        self.assertIsNotNone(Permission.objects.get(
            content_type=ct,
            codename='%s_%s' % ('read', ct.model)
        ))

    def test_filter_by_user_perm(self):
        self.trust1, created = Trust.objects.get_or_create_settlor_default(self.user)

        self.trust2 = Trust(settlor=self.user, title='Title 0A', trust=Trust.objects.get_root())
        self.trust2.save()
        tup = TrustUserPermission(trust=self.trust2, entity=self.user, permission=Permission.objects.first())
        tup.save()

        self.trust3 = Trust(settlor=self.user, title='Title 0B', trust=Trust.objects.get_root())
        self.trust3.save()

        self.trust4 = Trust(settlor=self.user1, title='Title 1A', trust=Trust.objects.get_root())
        self.trust4.save()
        tup = TrustUserPermission(trust=self.trust4, entity=self.user, permission=Permission.objects.first())
        tup.save()

        self.trust5 = Trust(settlor=self.user1, title='Title 1B', trust=Trust.objects.get_root())
        self.trust5.save()
        self.group = Group(name='Group A')
        self.group.save()
        self.user.groups.add(self.group)
        self.trust5.groups.add(self.group)

        self.trust6 = Trust(settlor=self.user1, title='Title 1C', trust=Trust.objects.get_root())
        self.trust6.save()

        trusts = Trust.objects.filter_by_user_perm(self.user)
        trust_pks = [t.pk for t in trusts]
        self.assertEqual(trusts.count(), 3)
        self.assertTrue(self.trust2.id in trust_pks)
        self.assertTrue(self.trust4.id in trust_pks)
        self.assertTrue(self.trust5.id in trust_pks)

    def test_change_trust(self):
        self.trust1 = Trust(settlor=self.user, title='Title 0A', trust=Trust.objects.get_root())
        self.trust1.save()

        self.trust2 = Trust(settlor=self.user1, title='Title 1A', trust=Trust.objects.get_root())
        self.trust2.save()

        try:
            self.trust2.trust = self.trust1
            self.trust2.full_clean()
            self.fail('Expected ValidationError not raised.')
        except ValidationError as ve:
            pass


class DecoratorsTest(TestCase):
    def setUp(self):
        super(DecoratorsTest, self).setUp()

        call_command('create_trust_root')

        get_or_create_root_user(self)

        create_test_users(self)

    def test_permission_required(self):
        self.group = Group(name='Group A')
        self.group.save()

        request = HttpRequest()
        setattr(request, 'user', self.user)
        request.META['SERVER_NAME'] = 'beedesk.com'
        request.META['SERVER_PORT'] = 80

        # test a) has_perms() == False
        mock = Mock(return_value='Response')
        has_perms = Mock(return_value=False)
        self.user.has_perms = has_perms

        decorated_func = permission_required(
            'auth.read_group',
            fieldlookups_kwargs={'pk': 'pk'},
            raise_exception=False
        )(mock)
        response = decorated_func(request, pk=self.group.pk)

        self.assertFalse(mock.called)
        self.assertTrue(response.status_code, 403)
        self.assertTrue(has_perms.called)
        self.assertEqual(has_perms.call_args[0][0], ('auth.read_group',))
        filter = has_perms.call_args[0][1]
        self.assertIsNotNone(filter)
        self.assertEqual(filter.count(), 1)
        self.assertEqual(filter.first().pk, self.group.pk)

        # test b) has_perms() == False
        mock = Mock(return_value='Response')
        has_perms = Mock(return_value=True)
        self.user.has_perms = has_perms

        decorated_func = permission_required(
            'auth.read_group',
            fieldlookups_kwargs={'pk': 'pk'}
        )(mock)
        response = decorated_func(request, pk=self.group.pk)

        self.assertTrue(mock.called)
        mock.assert_called_with(request, pk=self.group.pk)
        self.assertEqual(response, 'Response')
        self.assertEqual(has_perms.call_args[0][0], ('auth.read_group',))
        filter = has_perms.call_args[0][1]
        self.assertIsNotNone(filter)
        self.assertEqual(filter.count(), 1)
        self.assertEqual(filter.first().pk, self.group.pk)


class RuntimeModel(object):
    """
    Base class for tests of runtime model mixins.
    """

    def setUp(self):
        # Create the schema for our test model
        self._style = no_style()
        sql, _ = connection.creation.sql_create_model(self.model, self._style)

        with connection.cursor() as c:
            for statement in sql:
                c.execute(statement)

        content_model = self.content_model if hasattr(self, 'content_model') else self.model
        app_config = apps.get_app_config(content_model._meta.app_label)
        update_contenttypes(app_config, verbosity=1, interactive=False)
        create_permissions(app_config, verbosity=1, interactive=False)

        super(RuntimeModel, self).setUp()

    def workaround_contenttype_cache_bug(self):
        # workaround bug: https://code.djangoproject.com/ticket/10827
        from django.contrib.contenttypes.models import ContentType
        ContentType.objects.clear_cache()

    def tearDown(self):
        # Delete the schema for the test model
        content_model = self.content_model if hasattr(self, 'content_model') else self.model
        sql = connection.creation.sql_destroy_model(self.model, (), self._style)

        with connection.cursor() as c:
            for statement in sql:
                c.execute(statement)

        self.workaround_contenttype_cache_bug()

        super(RuntimeModel, self).tearDown()


class TrustContentTestMixin(object):
    def reload_test_users(self):
        # reloading user to purge the _trust_perm_cache
        self.user_root = User._default_manager.get(pk=self.user_root.pk)
        self.user = User._default_manager.get(pk=self.user.pk)
        self.user1 = User._default_manager.get(pk=self.user1.pk)

    def create_test_fixtures(self):
        self.group = Group(name="Test Group")
        self.group.save()

    def set_perms(self):
        for codename in ['change', 'add', 'delete']:
            setattr(self, 'perm_%s' % codename,
                '%s.%s_%s' % (self.app_label, codename, self.model_name)
            )

    def get_perm_code(self, perm):
        return '%s.%s' % (
            perm.content_type.app_label, perm.codename
         )

    def set_perms(self):
        for codename in ['change', 'add', 'delete']:
            setattr(self, 'perm_%s' % codename,
                Permission.objects.get_by_natural_key('%s_%s' % (codename, self.model_name), self.app_label, self.model_name)
            )

    def setUp(self):
        super(TrustContentTestMixin, self).setUp()

        get_or_create_root_user(self)

        call_command('create_trust_root')

        create_test_users(self)

        self.create_test_fixtures()

        content_model = self.content_model if hasattr(self, 'content_model') else self.model
        self.app_label = content_model._meta.app_label
        self.model_name = content_model._meta.model_name

        self.set_perms()

    def assertIsIterable(self, obj, msg='Not an iterable'):
        return self.assertTrue(hasattr(obj, '__iter__'))

    def test_unknown_content(self):
        self.trust = Trust(settlor=self.user, trust=Trust.objects.get_root())
        self.trust.save()

        perm = TrustModelBackend().get_group_permissions(self.user, {})
        self.assertIsNotNone(perm)
        self.assertIsIterable(perm)
        self.assertEqual(len(perm), 0)

        trusts = Trust.objects.filter_by_content(self.user)
        self.assertEqual(trusts.count(), 0)

    def test_user_not_in_group_has_no_perm(self):
        self.trust = Trust(settlor=self.user, trust=Trust.objects.get_root(), title='trust 1')
        self.trust.save()

        self.content = self.create_content(self.trust)
        had = self.user.has_perm(self.get_perm_code(self.perm_change), self.content)

        self.reload_test_users()

        self.perm_change.group_set.add(self.group)
        self.perm_change.save()

        had = self.user.has_perm(self.get_perm_code(self.perm_change), self.content)
        self.assertFalse(had)

    def test_user_in_group_has_no_perm(self):
        self.trust = Trust(settlor=self.user, trust=Trust.objects.get_root())
        self.trust.save()

        self.content = self.create_content(self.trust)

        self.test_user_not_in_group_has_no_perm()

        self.reload_test_users()

        self.user.groups.add(self.group)

        had = self.user.has_perm(self.get_perm_code(self.perm_change), self.content)
        self.assertFalse(had)

    def test_user_in_group_has_perm(self):
        self.trust = Trust(settlor=self.user, trust=Trust.objects.get_root(), title='a title')
        self.trust.save()
        self.content = self.create_content(self.trust)

        self.trust1 = Trust(settlor=self.user1, trust=Trust.objects.get_root())
        self.trust1.save()

        self.test_user_in_group_has_no_perm()

        self.reload_test_users()

        self.trust.groups.add(self.group)

        had = self.user.has_perm(self.get_perm_code(self.perm_change), self.content)
        self.assertTrue(had)

        had = self.user.has_perm(self.get_perm_code(self.perm_add), self.content)
        self.assertFalse(had)

    def test_has_perm(self):
        self.trust = Trust(settlor=self.user, trust=Trust.objects.get_root())
        self.trust.save()
        self.content = self.create_content(self.trust)

        self.trust1 = Trust(settlor=self.user1, trust=Trust.objects.get_root())
        self.trust1.save()

        had = self.user.has_perm(self.get_perm_code(self.perm_change), self.content)
        self.assertFalse(had)
        had = self.user.has_perm(self.get_perm_code(self.perm_add), self.content)
        self.assertFalse(had)

        trust = Trust(settlor=self.user, title='Test trusts')
        trust.save()

        self.reload_test_users()
        had = self.user.has_perm(self.get_perm_code(self.perm_change), self.content)
        self.assertFalse(had)

        tup = TrustUserPermission(trust=self.trust, entity=self.user, permission=self.perm_change)
        tup.save()

        self.reload_test_users()
        had = self.user.has_perm(self.get_perm_code(self.perm_change), self.content)
        self.assertTrue(had)

    def test_has_perm_disallow_no_perm_content(self):
        self.test_has_perm()

        self.content1 = self.create_content(self.trust1)
        had = self.user.has_perm(self.get_perm_code(self.perm_change), self.content1)
        self.assertFalse(had)

    def test_has_perm_disallow_no_perm_perm(self):
        self.test_has_perm()

        had = self.user.has_perm(self.get_perm_code(self.perm_add), self.content)
        self.assertFalse(had)

    def test_get_or_create_default_trust(self):
        trust, created = Trust.objects.get_or_create_settlor_default(self.user)
        content = self.create_content(trust)
        had = self.user.has_perm(self.get_perm_code(self.perm_change), content)
        self.assertFalse(had)

        tup = TrustUserPermission(trust=trust, entity=self.user, permission=self.perm_change)
        tup.save()

        self.reload_test_users()
        had = self.user.has_perm(self.get_perm_code(self.perm_change), content)
        self.assertTrue(had)

    def test_has_perm_queryset(self):
        self.test_has_perm()

        self.content1 = self.create_content(self.trust)

        self.reload_test_users()
        content_model = self.content_model if hasattr(self, 'content_model') else self.model
        qs = content_model.objects.filter(pk__in=[self.content.pk, self.content1.pk])
        had = self.user.has_perm(self.get_perm_code(self.perm_change), qs)
        self.assertTrue(had)

    def test_mixed_trust_queryset(self):
        self.test_has_perm()

        self.content1 = self.create_content(self.trust1)
        self.content2 = self.create_content(self.trust)

        self.reload_test_users()
        qs = self.model.objects.all()
        had = self.user.has_perm(self.get_perm_code(self.perm_change), qs)

        self.assertFalse(had)

    def test_read_permissions_added(self):
        ct = ContentType.objects.get_for_model(self.model)
        self.assertIsNotNone(Permission.objects.get(
            content_type=ct,
            codename='%s_%s' % ('read', ct.model)
        ))


class ContentTestCase(TrustContentTestMixin, RuntimeModel, TransactionTestCase):
    contents = []

    def setUp(self):
        mixin = Content

        # Create a dummy model which extends the mixin
        self.model = ModelBase('TestModel' + mixin.__name__, (mixin,),
            {'__module__': mixin.__module__})
        self.model.id = models.AutoField(primary_key=True)
        self.content_model = self.model

        super(ContentTestCase, self).setUp()

    def create_content(self, trust):
        content = self.model(trust=trust)
        content.save()

        self.contents.insert(0, content)

        return content


class JunctionTrustTestCase(TrustContentTestMixin, RuntimeModel, TransactionTestCase):
    class TestMixin(models.Model):
        content = models.ForeignKey(Group, unique=True, null=False, blank=False)
        name = models.CharField(max_length=40, null=False, blank=False)

        class Meta:
            abstract = True


    def setUp(self):
        mixin = Junction
        self.model = ModelBase('GroupJunction', (self.TestMixin, mixin),
            {'__module__': mixin.__module__})

        self.content_model = Group

        super(JunctionTrustTestCase, self).setUp()

    def create_content(self, trust):
        import uuid

        content = self.content_model(name=str(uuid.uuid4()))
        content.save()

        junction = self.model(content=content, trust=trust)
        junction.save()

        return content

    @unittest.expectedFailure
    def test_read_permissions_added(self):
        super(JunctionTrustTestCase, self).test_read_permissions_added()


class TrustAsContentTestCase(TrustContentTestMixin, TestCase):
    serialized_rollback = True
    count = 0

    def setUp(self):
        self.model = Trust
        self.content_model = Trust

        super(TrustAsContentTestCase, self).setUp()

    def create_content(self, trust):
        self.count += 1
        content = Trust(title='Test Trust as Content %s' % self.count, trust=trust)
        content.save()
        return content
