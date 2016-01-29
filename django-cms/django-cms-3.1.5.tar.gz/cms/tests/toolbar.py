# -*- coding: utf-8 -*-
from __future__ import with_statement
import datetime
from operator import attrgetter
import re

from django.contrib import admin
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template.defaultfilters import truncatewords
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, override

from cms.api import create_page, create_title, add_plugin
from cms.cms_toolbar import (ADMIN_MENU_IDENTIFIER, ADMINISTRATION_BREAK, get_user_model,
                             LANGUAGE_MENU_IDENTIFIER)
from cms.middleware.toolbar import ToolbarMiddleware
from cms.models import Page, UserSettings, PagePermission
from cms.toolbar.items import (ToolbarAPIMixin, LinkItem, ItemSearchResult,
                               Break, SubMenu, AjaxItem)
from cms.toolbar.toolbar import CMSToolbar
from cms.test_utils.project.placeholderapp.models import (Example1, CharPksExample,
                                                          MultilingualExample1)
from cms.test_utils.project.placeholderapp.views import (detail_view, detail_view_char,
                                                         detail_view_multi,
                                                         detail_view_multi_unfiltered, ClassDetail)
from cms.test_utils.testcases import (CMSTestCase,
                                      URL_CMS_PAGE_ADD, URL_CMS_PAGE_CHANGE)
from cms.test_utils.util.context_managers import UserLoginContext
from cms.utils.conf import get_cms_setting
from cms.utils.i18n import get_language_tuple
from cms.utils.urlutils import admin_reverse
from cms.views import details


class ToolbarTestBase(CMSTestCase):
    def get_page_request(self, page, user, path=None, edit=False, lang_code='en', disable=False):
        path = path or page and page.get_absolute_url()
        if edit:
            path += '?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')
        request = RequestFactory().get(path)
        request.session = {}
        request.user = user
        request.LANGUAGE_CODE = lang_code
        if edit:
            request.GET = {'edit': None}
        else:
            request.GET = {'edit_off': None}
        if disable:
            request.GET[get_cms_setting('CMS_TOOLBAR_URL__DISABLE')] = None
        request.current_page = page
        mid = ToolbarMiddleware()
        mid.process_request(request)
        if hasattr(request,'toolbar'):
            request.toolbar.populate()
        return request

    def get_anon(self):
        return AnonymousUser()

    def get_staff(self):
        staff = self._create_user('staff', True, False)
        staff.user_permissions.add(Permission.objects.get(codename='change_page'))
        return staff

    def get_nonstaff(self):
        nonstaff = self._create_user('nonstaff')
        nonstaff.user_permissions.add(Permission.objects.get(codename='change_page'))
        return nonstaff

    def get_superuser(self):
        superuser = self._create_user('superuser', True, True)
        return superuser

    def _fake_logentry(self, instance_id, user, text, model=Page):
        LogEntry.objects.log_action(
            user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(model).pk,
            object_id=instance_id,
            object_repr=text,
            action_flag=CHANGE,
        )
        entry = LogEntry.objects.filter(user=user, object_id=instance_id, action_flag__in=(CHANGE,))[0]
        session = self.client.session
        session['cms_log_latest'] = entry.pk
        session.save()


@override_settings(ROOT_URLCONF='cms.test_utils.project.nonroot_urls')
class ToolbarMiddlewareTest(ToolbarTestBase):

    def test_no_app_setted_show_toolbar_in_non_cms_urls(self):
        request = self.get_page_request(None, self.get_anon(), '/')
        self.assertTrue(hasattr(request,'toolbar'))

    def test_no_app_setted_show_toolbar_in_cms_urls(self):
        page = create_page('foo','col_two.html','en',published=True)
        request = self.get_page_request(page, self.get_anon())
        self.assertTrue(hasattr(request,'toolbar'))

    @override_settings(CMS_APP_NAME='cms')
    def test_app_setted_hide_toolbar_in_non_cms_urls_toolbar_hide_unsetted(self):
        request = self.get_page_request(None, self.get_anon(), '/')
        self.assertTrue(hasattr(request,'toolbar'))

    @override_settings(CMS_APP_NAME='cms')
    @override_settings(CMS_TOOLBAR_HIDE=True)
    def test_app_setted_hide_toolbar_in_non_cms_urls(self):
        request = self.get_page_request(None, self.get_anon(), '/')
        self.assertFalse(hasattr(request,'toolbar'))

    @override_settings(CMS_APP_NAME='cms')
    def test_app_setted_show_toolbar_in_cms_urls(self):
        page = create_page('foo','col_two.html','en',published=True)
        request = self.get_page_request(page, self.get_anon())
        self.assertTrue(hasattr(request,'toolbar'))


@override_settings(CMS_PERMISSION=False)
class ToolbarTests(ToolbarTestBase):

    def test_no_page_anon(self):
        request = self.get_page_request(None, self.get_anon(), '/')
        toolbar = CMSToolbar(request)
        toolbar.populate()
        toolbar.post_template_populate()
        items = toolbar.get_left_items() + toolbar.get_right_items()
        self.assertEqual(len(items), 0)

    def test_no_page_staff(self):
        request = self.get_page_request(None, self.get_staff(), '/')
        toolbar = CMSToolbar(request)
        toolbar.populate()
        toolbar.post_template_populate()
        items = toolbar.get_left_items() + toolbar.get_right_items()
        # Logo + admin-menu + logout
        self.assertEqual(len(items), 2, items)
        admin_items = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, 'Test').get_items()
        self.assertEqual(len(admin_items), 10, admin_items)

    def test_no_page_superuser(self):
        request = self.get_page_request(None, self.get_superuser(), '/')
        toolbar = CMSToolbar(request)
        toolbar.populate()
        toolbar.post_template_populate()
        items = toolbar.get_left_items() + toolbar.get_right_items()
        # Logo + edit-mode + admin-menu + logout
        self.assertEqual(len(items), 2)
        admin_items = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, 'Test').get_items()
        self.assertEqual(len(admin_items), 11, admin_items)

    def test_anon(self):
        page = create_page('test', 'nav_playground.html', 'en')
        request = self.get_page_request(page, self.get_anon())
        toolbar = CMSToolbar(request)

        items = toolbar.get_left_items() + toolbar.get_right_items()
        self.assertEqual(len(items), 0)

    def test_nonstaff(self):
        page = create_page('test', 'nav_playground.html', 'en', published=True)
        request = self.get_page_request(page, self.get_nonstaff())
        toolbar = CMSToolbar(request)
        items = toolbar.get_left_items() + toolbar.get_right_items()
        # Logo + edit-mode + logout
        self.assertEqual(len(items), 0)

    @override_settings(CMS_PERMISSION=True)
    def test_template_change_permission(self):
        page = create_page('test', 'nav_playground.html', 'en', published=True)
        request = self.get_page_request(page, self.get_nonstaff())
        toolbar = CMSToolbar(request)
        items = toolbar.get_left_items() + toolbar.get_right_items()
        self.assertEqual([item for item in items if item.css_class_suffix == 'templates'], [])

    def test_markup(self):
        create_page("toolbar-page", "nav_playground.html", "en", published=True)
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nav_playground.html')
        self.assertContains(response, '<div id="cms_toolbar"')
        self.assertContains(response, 'cms.base.css')

    def test_markup_generic_module(self):
        create_page("toolbar-page", "col_two.html", "en", published=True)
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="cms_submenu-item cms_submenu-item-title"><span>Generic</span>')

    def test_markup_flash_custom_module(self):
        superuser = self.get_superuser()
        create_page("toolbar-page", "col_two.html", "en", published=True)
        with self.login_user_context(superuser):
            response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="LinkPlugin">')
        self.assertContains(response,
                            '<div class="cms_submenu-item cms_submenu-item-title"><span>Different Grouper</span>')

    def test_markup_menu_items(self):
        superuser = self.get_superuser()
        create_page("toolbar-page", "col_two.html", "en", published=True)
        with self.login_user_context(superuser):
            response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            '<div class="cms_submenu-item"><a href="/some/url/" data-rel="ajax"')
        self.assertContains(response,
                            '<div class="cms_submenu-item"><a href="/some/other/url/" data-rel="ajax_add"')

    def test_markup_toolbar_url_page(self):
        superuser = self.get_superuser()
        page_1 = create_page("top-page", "col_two.html", "en", published=True)
        page_2 = create_page("sec-page", "col_two.html", "en", published=True, parent=page_1)
        page_3 = create_page("trd-page", "col_two.html", "en", published=False, parent=page_1)

        # page with publish = draft
        # check when in draft mode
        with self.login_user_context(superuser):
            response = self.client.get('%s?%s' % (
                page_2.get_absolute_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="%s?%s"' % (
            page_2.get_public_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_OFF')
        ))
        # check when in live mode
        with self.login_user_context(superuser):
            response = self.client.get('%s?%s' % (
                page_2.get_absolute_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_OFF')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="%s?%s"' % (
            page_2.get_draft_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')
        ))
        self.assertEqual(page_2.get_draft_url(), page_2.get_public_url())

        # page with publish != draft
        page_2.get_title_obj().slug = 'mod-page'
        page_2.get_title_obj().save()
        # check when in draft mode
        with self.login_user_context(superuser):
            response = self.client.get('%s?%s' % (
                page_2.get_absolute_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="%s?%s"' % (
            page_2.get_public_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_OFF')
        ))
        # check when in live mode
        with self.login_user_context(superuser):
            response = self.client.get('%s?%s' % (
                page_2.get_public_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_OFF')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="%s?%s"' % (
            page_2.get_draft_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')
        ))
        self.assertNotEqual(page_2.get_draft_url(), page_2.get_public_url())

        # not published page
        # check when in draft mode
        with self.login_user_context(superuser):
            response = self.client.get('%s?%s' % (
                page_3.get_absolute_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'cms_toolbar-item_switch')
        self.assertEqual(page_3.get_public_url(), '')
        self.assertNotEqual(page_3.get_draft_url(), page_3.get_public_url())

    def test_markup_plugin_template(self):
        page = create_page("toolbar-page-1", "col_two.html", "en", published=True)
        plugin_1 = add_plugin(page.placeholders.get(slot='col_left'), language='en',
                              plugin_type='TestPluginAlpha', alpha='alpha')
        plugin_2 = add_plugin(page.placeholders.get(slot='col_left'), language='en',
                              plugin_type='TextPlugin', body='text')
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        response_text = response.render().rendered_content
        self.assertTrue(re.search('edit_plugin.+/admin/custom/view/%s' % plugin_1.pk, response_text))
        self.assertTrue(re.search('move_plugin.+/admin/custom/move/', response_text))
        self.assertTrue(re.search('delete_plugin.+/admin/custom/delete/%s/' % plugin_1.pk, response_text))
        self.assertTrue(re.search('add_plugin.+/admin/custom/view/', response_text))
        self.assertTrue(re.search('copy_plugin.+/admin/custom/copy/', response_text))

        self.assertTrue(re.search('edit_plugin.+/en/admin/cms/page/edit-plugin/%s' % plugin_2.pk, response_text))
        self.assertTrue(re.search('delete_plugin.+/en/admin/cms/page/delete-plugin/%s/' % plugin_2.pk, response_text))

    def test_show_toolbar_to_staff(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        request = self.get_page_request(page, self.get_staff(), '/')
        toolbar = CMSToolbar(request)
        self.assertTrue(toolbar.show_toolbar)

    def test_show_toolbar_with_edit(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        request = self.get_page_request(page, AnonymousUser(), edit=True)
        toolbar = CMSToolbar(request)
        self.assertTrue(toolbar.show_toolbar)

    def test_show_toolbar_staff(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        request = self.get_page_request(page, self.get_staff(), edit=True)
        self.assertTrue(request.session.get('cms_build', True))
        self.assertTrue(request.session.get('cms_edit', False))

    def test_hide_toolbar_non_staff(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        request = self.get_page_request(page, self.get_nonstaff(), edit=True)
        self.assertFalse(request.session.get('cms_build', True))
        self.assertFalse(request.session.get('cms_edit', True))

    def test_hide_toolbar_disabled(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        # Edit mode should re-enable the toolbar in any case
        request = self.get_page_request(page, self.get_staff(), edit=False, disable=True)
        self.assertTrue(request.session.get('cms_toolbar_disabled'))
        toolbar = CMSToolbar(request)
        self.assertFalse(toolbar.show_toolbar)

    def test_show_disabled_toolbar_with_edit(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        request = self.get_page_request(page, self.get_staff(), edit=True, disable=True)
        self.assertFalse(request.session.get('cms_toolbar_disabled'))
        toolbar = CMSToolbar(request)
        self.assertTrue(toolbar.show_toolbar)

    def test_show_toolbar_login_anonymous(self):
        create_page("toolbar-page", "nav_playground.html", "en", published=True)
        response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cms_form-login')

    @override_settings(CMS_TOOLBAR_ANONYMOUS_ON=False)
    def test_hide_toolbar_login_anonymous_setting(self):
        create_page("toolbar-page", "nav_playground.html", "en", published=True)
        response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'cms_form-login')

    def test_hide_toolbar_login_nonstaff(self):
        create_page("toolbar-page", "nav_playground.html", "en", published=True)
        with self.login_user_context(self.get_nonstaff()):
            response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'cms_form-login')
        self.assertNotContains(response, 'cms_toolbar')

    def test_admin_logout_staff(self):
        with override_settings(CMS_PERMISSION=True):
            with self.login_user_context(self.get_staff()):
                response = self.client.get('/en/admin/logout/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
                self.assertTrue(response.status_code, 200)

    def test_show_toolbar_without_edit(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        request = self.get_page_request(page, AnonymousUser(), edit=False)
        toolbar = CMSToolbar(request)
        self.assertFalse(toolbar.show_toolbar)

    def test_publish_button(self):
        page = create_page('test', 'nav_playground.html', 'en', published=True)
        request = self.get_page_request(page, self.get_superuser(), edit=True)
        toolbar = CMSToolbar(request)
        toolbar.populate()
        toolbar.post_template_populate()
        self.assertTrue(toolbar.edit_mode)
        items = toolbar.get_left_items() + toolbar.get_right_items()
        self.assertEqual(len(items), 7)

    def test_no_publish_button(self):
        page = create_page('test', 'nav_playground.html', 'en', published=True)
        user = self.get_staff()
        request = self.get_page_request(page, user, edit=True)
        toolbar = CMSToolbar(request)
        toolbar.populate()
        toolbar.post_template_populate()
        self.assertTrue(page.has_change_permission(request))
        self.assertFalse(page.has_publish_permission(request))
        self.assertTrue(toolbar.edit_mode)
        items = toolbar.get_left_items() + toolbar.get_right_items()
        # Logo + templates + page-menu + admin-menu + logout
        self.assertEqual(len(items), 5)

        # adding back structure mode permission
        permission = Permission.objects.get(codename='use_structure')
        user.user_permissions.add(permission)

        request.user = get_user_model().objects.get(pk=user.pk)
        toolbar = CMSToolbar(request)
        toolbar.populate()
        toolbar.post_template_populate()
        items = toolbar.get_left_items() + toolbar.get_right_items()
        # Logo + edit mode + templates + page-menu + admin-menu + logout
        self.assertEqual(len(items), 6)

    def test_no_change_button(self):
        page = create_page('test', 'nav_playground.html', 'en', published=True)
        user = self.get_staff()
        user.user_permissions.all().delete()
        request = self.get_page_request(page, user, edit=True)
        toolbar = CMSToolbar(request)
        toolbar.populate()
        toolbar.post_template_populate()
        self.assertFalse(page.has_change_permission(request))
        self.assertFalse(page.has_publish_permission(request))

        items = toolbar.get_left_items() + toolbar.get_right_items()
        # Logo + page-menu + admin-menu + logout
        self.assertEqual(len(items), 3, items)
        admin_items = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, 'Test').get_items()
        self.assertEqual(len(admin_items), 9, admin_items)

    def test_button_consistency_staff(self):
        """
        Tests that the buttons remain even when the language changes.
        """
        user = self.get_staff()
        cms_page = create_page('test-en', 'nav_playground.html', 'en', published=True)
        create_title('de', 'test-de', cms_page)
        cms_page.publish('de')
        en_request = self.get_page_request(cms_page, user, edit=True)
        en_toolbar = CMSToolbar(en_request)
        en_toolbar.populate()
        en_toolbar.post_template_populate()
        # Logo + templates + page-menu + admin-menu + logout
        self.assertEqual(len(en_toolbar.get_left_items() + en_toolbar.get_right_items()), 5)
        de_request = self.get_page_request(cms_page, user, path='/de/', edit=True, lang_code='de')
        de_toolbar = CMSToolbar(de_request)
        de_toolbar.populate()
        de_toolbar.post_template_populate()
        # Logo + templates + page-menu + admin-menu + logout
        self.assertEqual(len(de_toolbar.get_left_items() + de_toolbar.get_right_items()), 5)

    def test_double_menus(self):
        """
        Tests that even called multiple times, admin and language buttons are not duplicated
        """
        user = self.get_staff()
        en_request = self.get_page_request(None, user, edit=True, path='/')
        toolbar = CMSToolbar(en_request)
        toolbar.populated = False
        toolbar.populate()
        toolbar.populated = False
        toolbar.populate()
        toolbar.populated = False
        toolbar.post_template_populate()
        admin = toolbar.get_left_items()[0]
        lang = toolbar.get_left_items()[1]
        self.assertEqual(len(admin.get_items()), 10)
        self.assertEqual(len(lang.get_items()), len(get_language_tuple(1)))

    @override_settings(CMS_PLACEHOLDER_CONF={'col_left': {'name': 'PPPP'}})
    def test_placeholder_name(self):
        superuser = self.get_superuser()
        create_page("toolbar-page", "col_two.html", "en", published=True)
        with self.login_user_context(superuser):
            response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PPPP')

    def test_user_settings(self):
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.get('/en/admin/cms/usersettings/')
            self.assertEqual(response.status_code, 200)

    def test_remove_lang(self):
        create_page('test', 'nav_playground.html', 'en', published=True)
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            self.assertEqual(response.status_code, 200)
            setting = UserSettings.objects.get(user=superuser)
            setting.language = 'it'
            setting.save()
            with self.settings(LANGUAGES=(('en', 'english'),)):
                response = self.client.get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, '/it/')

    def test_get_alphabetical_insert_position(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        request = self.get_page_request(page, self.get_staff(), '/')
        toolbar = CMSToolbar(request)
        toolbar.get_left_items()
        toolbar.get_right_items()

        admin_menu = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, 'TestAppMenu')

        # Insert alpha
        alpha_position = admin_menu.get_alphabetical_insert_position('menu-alpha', SubMenu, None)

        # As this will be the first item added to this, this use should return the default, or namely None
        if not alpha_position:
            alpha_position = admin_menu.find_first(Break, identifier=ADMINISTRATION_BREAK) + 1
        admin_menu.get_or_create_menu('menu-alpha', 'menu-alpha', position=alpha_position)

        # Insert gamma (should return alpha_position + 1)
        gamma_position = admin_menu.get_alphabetical_insert_position('menu-gamma', SubMenu)
        self.assertEqual(int(gamma_position), int(alpha_position) + 1)
        admin_menu.get_or_create_menu('menu-gamma', 'menu-gamma', position=gamma_position)

        # Where should beta go? It should go right where gamma is now...
        beta_position = admin_menu.get_alphabetical_insert_position('menu-beta', SubMenu)
        self.assertEqual(beta_position, gamma_position)

    def test_out_of_order(self):
        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        request = self.get_page_request(page, self.get_staff(), '/')
        toolbar = CMSToolbar(request)
        menu1 = toolbar.get_or_create_menu("test")
        menu2 = toolbar.get_or_create_menu("test", "Test", side=toolbar.RIGHT, position=2)

        self.assertEqual(menu1, menu2)
        self.assertEqual(menu1.name, 'Test')
        self.assertEqual(len(toolbar.get_right_items()), 1)

    def test_page_create_redirect(self):
        superuser = self.get_superuser()
        page = create_page("home", "nav_playground.html", "en",
                           published=True)
        resolve_url_on = '%s?%s' % (admin_reverse('cms_page_resolve'),
                                    get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        resolve_url_off = '%s?%s' % (admin_reverse('cms_page_resolve'),
                                     get_cms_setting('CMS_TOOLBAR_URL__EDIT_OFF'))
        with self.login_user_context(superuser):
            response = self.client.post(resolve_url_on, {'pk': '', 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '')
            page_data = self.get_new_page_data(parent_id=page.pk)
            self.client.post(URL_CMS_PAGE_ADD, page_data)

            # test redirection when toolbar is in edit mode
            response = self.client.post(resolve_url_on, {'pk': Page.objects.all()[2].pk,
                                                         'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '/en/test-page-1/')

            self.client.post(URL_CMS_PAGE_ADD, page_data)

            # test redirection when toolbar is not in edit mode
            response = self.client.post(resolve_url_off, {'pk': Page.objects.all()[2].pk,
                                                          'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '/en/')

    def test_page_edit_redirect_editmode(self):
        page1 = create_page("home", "nav_playground.html", "en",
                            published=True)
        page2 = create_page("test", "nav_playground.html", "en",
                            published=True)
        page3 = create_page("non-pub", "nav_playground.html", "en",
                            published=False)
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            page_data = self.get_new_page_data()
            self.client.post(URL_CMS_PAGE_CHANGE % page2.pk, page_data)
            url = '%s?%s' % (admin_reverse('cms_page_resolve'),
                             get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            # first call returns the latest modified page with updated slug even if a different
            # page has been requested
            response = self.client.post(url, {'pk': page1.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '/en/test-page-1/')
            # following call returns the actual page requested
            response = self.client.post(url, {'pk': page1.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '/en/')
            # non published page - staff user can access it
            response = self.client.post(url, {'pk': page3.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '/en/non-pub/')
        # anonymous users should be redirected to the root page
        response = self.client.post(url, {'pk': page3.pk, 'model': 'cms.page'})
        self.assertEqual(response.content.decode('utf-8'), '/')

    def test_page_edit_redirect_no_editmode(self):
        page1 = create_page("home", "nav_playground.html", "en",
                            published=True)
        page2 = create_page("test", "nav_playground.html", "en",
                            published=True, parent=page1)
        page3 = create_page("non-pub-1", "nav_playground.html", "en",
                            published=False, parent=page2)
        page4 = create_page("non-pub-2", "nav_playground.html", "en",
                            published=False, parent=page3)
        superuser = self.get_superuser()
        url = admin_reverse('cms_page_resolve')
        with self.login_user_context(superuser):
            # checking the redirect by passing URL parameters
            # redirect to the same page
            response = self.client.post(url, {'pk': page1.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), page1.get_absolute_url())
            # redirect to the same page
            response = self.client.post(url, {'pk': page2.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), page2.get_absolute_url())
            # redirect to the first published ancestor
            response = self.client.post(url, {'pk': page3.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '%s?%s' % (
                page3.get_absolute_url(),
                get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            )
            # redirect to the first published ancestor
            response = self.client.post(url, {'pk': page4.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '%s?%s' % (
                page4.get_absolute_url(),
                get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            )

            # checking the redirect by setting the session data
            self._fake_logentry(page1.get_draft_object().pk, superuser, 'test page')
            response = self.client.post(url, {'pk': page2.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), page1.get_public_object().get_absolute_url())

            self._fake_logentry(page2.get_draft_object().pk, superuser, 'test page')
            response = self.client.post(url, {'pk': page1.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), page2.get_public_object().get_absolute_url())

            self._fake_logentry(page3.get_draft_object().pk, superuser, 'test page')
            response = self.client.post(url, {'pk': page1.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '%s?%s' % (
                page3.get_absolute_url(),
                get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            )

            self._fake_logentry(page4.get_draft_object().pk, superuser, 'test page')
            response = self.client.post(url, {'pk': page1.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '%s?%s' % (
                page4.get_absolute_url(),
                get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            )

    def test_page_edit_redirect_errors(self):
        page1 = create_page("home", "nav_playground.html", "en",
                            published=True)
        page2 = create_page("test", "nav_playground.html", "en",
                            published=True, parent=page1)
        create_page("non-pub", "nav_playground.html", "en",
                    published=False, parent=page2)
        superuser = self.get_superuser()
        url = admin_reverse('cms_page_resolve')

        with self.login_user_context(superuser):
            # logentry - non existing id - parameter is used
            self._fake_logentry(9999, superuser, 'test page')
            response = self.client.post(url, {'pk': page2.pk, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), page2.get_public_object().get_absolute_url())
            # parameters - non existing id - no redirection
            response = self.client.post(url, {'pk': 9999, 'model': 'cms.page'})
            self.assertEqual(response.content.decode('utf-8'), '')

    def test_remove_language(self):
        item_name = attrgetter('name')

        page = create_page("toolbar-page", "nav_playground.html", "en",
                           published=True)
        create_title(title="de page", language="de", page=page)
        create_title(title="fr page", language="fr", page=page)

        request = self.get_page_request(page, self.get_staff(), '/', edit=True)
        toolbar = CMSToolbar(request)
        toolbar.populate()
        meu = toolbar.get_menu(LANGUAGE_MENU_IDENTIFIER)
        self.assertTrue(any([item for item in meu.get_items() if hasattr(item, 'name') and item_name(item).startswith('Delete German')]))
        self.assertTrue(any([item for item in meu.get_items() if hasattr(item, 'name') and item_name(item).startswith('Delete English')]))
        self.assertTrue(any([item for item in meu.get_items() if hasattr(item, 'name') and item_name(item).startswith('Delete French')]))

        reduced_langs = {
            1: [
                {
                    'code': 'en',
                    'name': 'English',
                    'fallbacks': ['fr', 'de'],
                    'public': True,
                },
                {
                    'code': 'fr',
                    'name': 'French',
                    'public': True,
                },
            ]
        }

        with self.settings(CMS_LANGUAGES=reduced_langs):
            toolbar = CMSToolbar(request)
            toolbar.populate()
            meu = toolbar.get_menu(LANGUAGE_MENU_IDENTIFIER)
            self.assertFalse(any([item for item in meu.get_items() if hasattr(item, 'name') and item_name(item).startswith('Delete German')]))
            self.assertTrue(any([item for item in meu.get_items() if hasattr(item, 'name') and item_name(item).startswith('Delete English')]))
            self.assertTrue(any([item for item in meu.get_items() if hasattr(item, 'name') and item_name(item).startswith('Delete French')]))

    def get_username(self, user=None, default=''):
        user = user or self.request.user
        try:
            name = user.get_full_name()
            if name:
                return name
            else:
                return user.get_username()
        except (AttributeError, NotImplementedError):
            return default

    def test_toolbar_logout(self):
        '''
        Tests that the Logout menu item includes the user's full name, if the
        relevant fields were populated in auth.User, else the user's username.
        '''
        superuser = self.get_superuser()

        # Ensure that some other test hasn't set the name fields
        if superuser.get_full_name():
            # Looks like it has been set, clear them
            superuser.first_name = ''
            superuser.last_name = ''
            superuser.save()

        page = create_page("home", "nav_playground.html", "en",
                           published=True)
        page.publish('en')
        self.get_page_request(page, superuser, '/')
        #
        # Test that the logout shows the username of the logged-in user if
        # first_name and last_name haven't been provided.
        #
        with self.login_user_context(superuser):
            response = self.client.get(page.get_absolute_url('en') + '?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            toolbar = response.context['request'].toolbar
            admin_menu = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)
            self.assertTrue(admin_menu.find_first(AjaxItem, name=_(u'Logout %s') % self.get_username(superuser)))

        #
        # Test that the logout shows the logged-in user's name, if it was
        # populated in auth.User.
        #
        superuser.first_name = 'Super'
        superuser.last_name = 'User'
        superuser.save()
        # Sanity check...
        self.get_page_request(page, superuser, '/')
        with self.login_user_context(superuser):
            response = self.client.get(page.get_absolute_url('en') + '?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            toolbar = response.context['request'].toolbar
            admin_menu = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)
            self.assertTrue(admin_menu.find_first(AjaxItem, name=_(u'Logout %s') % self.get_username(superuser)))

    @override_settings(CMS_PERMISSION=True)
    def test_toolbar_logout_redirect(self):
        """
        Tests the logount AjaxItem on_success parameter in four different conditions:

         * published page: no redirect
         * unpublished page: redirect to the home page
         * published page with login_required: redirect to the home page
         * published page with view permissions: redirect to the home page
        """
        superuser = self.get_superuser()
        page0 = create_page("home", "nav_playground.html", "en",
                            published=True)
        page1 = create_page("internal", "nav_playground.html", "en",
                            published=True, parent=page0)
        page2 = create_page("unpublished", "nav_playground.html", "en",
                            published=False, parent=page0)
        page3 = create_page("login_restricted", "nav_playground.html", "en",
                            published=True, parent=page0, login_required=True)
        page4 = create_page("view_restricted", "nav_playground.html", "en",
                            published=True, parent=page0)
        PagePermission.objects.create(page=page4, can_view=True,
                                      user=superuser)
        page4.publish('en')
        page4 = page4.get_public_object()
        self.get_page_request(page4, superuser, '/')

        with self.login_user_context(superuser):
            # Published page, no redirect
            response = self.client.get(page1.get_absolute_url('en') + '?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            toolbar = response.context['request'].toolbar
            menu_name = _(u'Logout %s') % self.get_username(superuser)
            admin_menu = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)
            self.assertTrue(admin_menu.find_first(AjaxItem, name=menu_name).item.on_success)

            # Unpublished page, redirect
            response = self.client.get(page2.get_absolute_url('en') + '?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            toolbar = response.context['request'].toolbar
            admin_menu = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)

            self.assertEquals(admin_menu.find_first(AjaxItem, name=menu_name).item.on_success, '/')

            # Published page with login restrictions, redirect
            response = self.client.get(page3.get_absolute_url('en') + '?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            toolbar = response.context['request'].toolbar
            admin_menu = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)
            self.assertEquals(admin_menu.find_first(AjaxItem, name=menu_name).item.on_success, '/')

            # Published page with view permissions, redirect
            response = self.client.get(page4.get_absolute_url('en') + '?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
            toolbar = response.context['request'].toolbar
            admin_menu = toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)
            self.assertEquals(admin_menu.find_first(AjaxItem, name=menu_name).item.on_success, '/')


class EditModelTemplateTagTest(ToolbarTestBase):
    urls = 'cms.test_utils.project.placeholderapp_urls'
    edit_fields_rx = "(\?|&amp;)edit_fields=%s"

    def tearDown(self):
        Example1.objects.all().delete()
        MultilingualExample1.objects.all().delete()
        super(EditModelTemplateTagTest, self).tearDown()

    def test_markup_toolbar_url_model(self):
        superuser = self.get_superuser()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        # object
        # check when in draft mode
        request = self.get_page_request(page, superuser, edit=True)
        response = detail_view(request, ex1.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="%s?%s"' % (
            ex1.get_public_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_OFF')
        ))
        # check when in live mode
        request = self.get_page_request(page, superuser, edit=False)
        response = detail_view(request, ex1.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="%s?%s"' % (
            ex1.get_draft_url(), get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')
        ))
        self.assertNotEqual(ex1.get_draft_url(), ex1.get_public_url())

    def test_anon(self):
        user = self.get_anon()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        request = self.get_page_request(page, user, edit=False)
        response = detail_view(request, ex1.pk)
        self.assertContains(response, "<h1>char_1</h1>")
        self.assertNotContains(response, "CMS.API")

    def test_noedit(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        request = self.get_page_request(page, user, edit=False)
        response = detail_view(request, ex1.pk)
        self.assertContains(response, "<h1>char_1</h1>")
        self.assertContains(response, "CMS.API")

    def test_edit(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">char_1</div></h1>' % (
                'placeholderapp', 'example1', 'char_1', ex1.pk))

    def test_invalid_item(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model fake "char_1" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s cms_render_model"></div>' % ex1.pk)

    def test_as_varname(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "char_1" as tempvar %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertNotContains(
            response,
            '<div class="cms_plugin cms_plugin-%s cms_render_model"></div>' % ex1.pk)

    def test_edit_render_placeholder(self):
        """
        Tests the {% render_placeholder %} templatetag.
        """
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()

        render_placeholder_body = "I'm the render placeholder body"

        plugin = add_plugin(ex1.placeholder, u"TextPlugin", u"en", body=render_placeholder_body)

        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_placeholder instance.placeholder %}</h1>
<h2>{% render_placeholder instance.placeholder as tempvar %}</h2>
<h3>{{ tempvar }}</h3>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<h1><div class="cms_placeholder cms_placeholder-{0}"></div>\n'
            '<div class="cms_plugin cms_plugin-{1}">{2}</div></h1>'.format(ex1.placeholder.pk,
                                                                           plugin.pk, render_placeholder_body)
            )

        self.assertContains(
            response,
            '<h2></h2>',
        )

        #
        # NOTE: Using the render_placeholder "as" form should /not/ render
        # frontend placeholder editing support.
        #
        self.assertContains(
            response,
            '<h3>{0}</h3>'.format(render_placeholder_body)
            )

        self.assertContains(
            response,
            'CMS.Plugin(\'cms_plugin-{0}\''.format(plugin.pk)
        )

        self.assertContains(
            response,
            'CMS.Plugin(\'cms_placeholder-{0}\''.format(ex1.placeholder.pk)
        )

    def test_filters(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1, <p>hello</p>, <p>hello</p>, <p>hello</p>, <p>hello</p>", char_2="char_2",
                       char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "char_1" "" "" 'truncatewords:2' %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">%s</div></h1>' % (
                'placeholderapp', 'example1', 'char_1', ex1.pk, truncatewords(ex1.char_1, 2)))

    def test_filters_date(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1, <p>hello</p>, <p>hello</p>, <p>hello</p>, <p>hello</p>", char_2="char_2",
                       char_3="char_3",
                       char_4="char_4", date_field=datetime.date(2012, 1, 1))
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "date_field" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)

        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">%s</div></h1>' % (
                'placeholderapp', 'example1', 'date_field', ex1.pk,
                ex1.date_field.strftime("%Y-%m-%d")))

        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "date_field" "" "" 'date:"Y m d"' %}</h1>
{% endblock content %}
'''
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">%s</div></h1>' % (
                'placeholderapp', 'example1', 'date_field', ex1.pk,
                ex1.date_field.strftime("%Y %m %d")))

    def test_filters_notoolbar(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1, <p>hello</p>, <p>hello</p>, <p>hello</p>, <p>hello</p>", char_2="char_2",
                       char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "char_1" "" "" 'truncatewords:2'  %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=False)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(response,
                            '<h1>%s</h1>' % truncatewords(ex1.char_1, 2))

    def test_no_cms(self):
        user = self.get_staff()
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_icon instance %}
{% endblock content %}
'''
        request = self.get_page_request('', user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-%s cms_render_model_icon"><img src="/static/cms/img/toolbar/render_model_placeholder.png"></div>' % (
                'placeholderapp', 'example1', ex1.pk))
        self.assertContains(response, "'onClose': 'REFRESH_PAGE',")

    def test_icon_tag(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_icon instance %}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-%s cms_render_model_icon"><img src="/static/cms/img/toolbar/render_model_placeholder.png"></div>' % (
                'placeholderapp', 'example1', ex1.pk))

    def test_icon_followed_by_render_model_block_tag(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4", date_field=datetime.date(2012, 1, 1))
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_icon instance "char_1" %}

{% render_model_block instance "char_2" %}
    {{ instance }}
    <h1>{{ instance.char_1 }} - {{  instance.char_2 }}</h1>
    <span class="date">{{ instance.date_field|date:"Y" }}</span>
    {% if instance.char_1 %}
    <a href="{% url 'detail' instance.pk %}">successful if</a>
    {% endif %}
{% endrender_model_block %}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            "new CMS.Plugin('cms_plugin-{0}-{1}-{2}-{3}'".format('placeholderapp', 'example1', 'char_1', ex1.pk))

        self.assertContains(
            response,
            "new CMS.Plugin('cms_plugin-{0}-{1}-{2}-{3}'".format('placeholderapp', 'example1', 'char_2', ex1.pk))

    def test_add_tag(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_add instance %}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-add-%s cms_render_model_add"><img src="/static/cms/img/toolbar/render_model_placeholder.png"></div>' % (
                'placeholderapp', 'example1', ex1.pk))

    def test_add_tag_class(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_add instance_class %}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-add-%s cms_render_model_add"><img src="/static/cms/img/toolbar/render_model_placeholder.png"></div>' % (
                'placeholderapp', 'example1', '0'))

    def test_add_tag_classview(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_add instance_class %}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        view_func = ClassDetail.as_view(template_string=template_text)
        response = view_func(request, pk=ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-add-%s cms_render_model_add"><img src="/static/cms/img/toolbar/render_model_placeholder.png"></div>' % (
                'placeholderapp', 'example1', '0'))

    def test_block_tag(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4", date_field=datetime.date(2012, 1, 1))
        ex1.save()

        # This template does not render anything as content is saved in a
        # variable and never inserted in the page
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_block instance as rendered_model %}
    {{ instance }}
    <h1>{{ instance.char_1 }} - {{  instance.char_2 }}</h1>
    {{ instance.date_field|date:"Y" }}
    {% if instance.char_1 %}
    <a href="{% url 'detail' instance.pk %}">successful if</a>
    {% endif %}
{% endrender_model_block %}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertNotContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-%s cms_render_model_icon"><img src="/static/cms/img/toolbar/render_model_icon.png"></div>' % (
                'placeholderapp', 'example1', ex1.pk))

        # This template does not render anything as content is saved in a
        # variable and inserted in the page afterwards
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_block instance as rendered_model %}
    {{ instance }}
    <h1>{{ instance.char_1 }} - {{  instance.char_2 }}</h1>
    <span class="date">{{ instance.date_field|date:"Y" }}</span>
    {% if instance.char_1 %}
    <a href="{% url 'detail' instance.pk %}">successful if</a>
    {% endif %}
{% endrender_model_block %}
{{ rendered_model }}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        # Assertions on the content of the block tag
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-%s cms_render_model cms_render_model_block">' % (
                'placeholderapp', 'example1', ex1.pk))
        self.assertContains(response, '<h1>%s - %s</h1>' % (ex1.char_1, ex1.char_2))
        self.assertContains(response, '<span class="date">%s</span>' % (ex1.date_field.strftime("%Y")))
        self.assertContains(response, '<a href="%s">successful if</a>\n    \n</div>' % (reverse('detail', args=(ex1.pk,))))

        # This template is rendered directly
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_block instance %}
    {{ instance }}
    <h1>{{ instance.char_1 }} - {{  instance.char_2 }}</h1>
    <span class="date">{{ instance.date_field|date:"Y" }}</span>
    {% if instance.char_1 %}
    <a href="{% url 'detail' instance.pk %}">successful if</a>
    {% endif %}
{% endrender_model_block %}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        # Assertions on the content of the block tag
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-%s cms_render_model cms_render_model_block">' % (
                'placeholderapp', 'example1', ex1.pk))
        self.assertContains(response, '<h1>%s - %s</h1>' % (ex1.char_1, ex1.char_2))
        self.assertContains(response, '<span class="date">%s</span>' % (ex1.date_field.strftime("%Y")))
        self.assertContains(response, '<a href="%s">successful if</a>\n    \n</div>' % (reverse('detail', args=(ex1.pk,))))

        # Changelist check
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
{% render_model_block instance 'changelist' %}
    {{ instance }}
{% endrender_model_block %}
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        # Assertions on the content of the block tag
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-changelist-%s cms_render_model cms_render_model_block">' % (
                'placeholderapp', 'example1', ex1.pk))
        self.assertContains(
            response,
            "'edit_plugin': '%s?language=%s&amp;edit_fields=changelist'" % (admin_reverse('placeholderapp_example1_changelist'), 'en'))

    def test_invalid_attribute(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "fake_field" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model"></div>' % (
                'placeholderapp', 'example1', 'fake_field', ex1.pk))

        # no attribute
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-%s cms_render_model"></div>' % ex1.pk)

    def test_callable_item(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "callable_item" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">char_1</div></h1>' % (
                'placeholderapp', 'example1', 'callable_item', ex1.pk))

    def test_view_method(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "callable_item" "char_1,char_2" "en" "" "" "dynamic_url" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response, "'edit_plugin': '/admin/placeholderapp/example1/edit-field/%s/en/" % ex1.pk)

    def test_view_url(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "callable_item" "char_1,char_2" "en" "" "admin:placeholderapp_example1_edit_field" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response, "'edit_plugin': '/admin/placeholderapp/example1/edit-field/%s/en/" % ex1.pk)

    def test_method_attribute(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "callable_item" "char_1,char_2" "en" "" "" "static_admin_url" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        ex1.set_static_url(request)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">char_1</div></h1>' % (
                'placeholderapp', 'example1', 'callable_item', ex1.pk))

    def test_admin_url(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "callable_item" "char_1" "en" "" "admin:placeholderapp_example1_edit_field" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(response,
                            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">char_1</div></h1>' % (
                                'placeholderapp', 'example1', 'callable_item', ex1.pk))

    def test_admin_url_extra_field(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "callable_item" "char_2" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(response,
                            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">char_1</div></h1>' % (
                                'placeholderapp', 'example1', 'callable_item', ex1.pk))
        self.assertContains(response, "/admin/placeholderapp/example1/edit-field/%s/en/" % ex1.pk)
        self.assertTrue(re.search(self.edit_fields_rx % "char_2", response.content.decode('utf8')))

    def test_admin_url_multiple_fields(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "callable_item" "char_1,char_2" "en" "" "admin:placeholderapp_example1_edit_field" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">char_1</div></h1>' % (
                'placeholderapp', 'example1', 'callable_item', ex1.pk))
        self.assertContains(response, "/admin/placeholderapp/example1/edit-field/%s/en/" % ex1.pk)
        self.assertTrue(re.search(self.edit_fields_rx % "char_1", response.content.decode('utf8')))
        self.assertTrue(re.search(self.edit_fields_rx % "char_1%2Cchar_2", response.content.decode('utf8')))

    def test_instance_method(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance "callable_item" %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">char_1</div></h1>' % (
                'placeholderapp', 'example1', 'callable_item', ex1.pk))

    def test_item_from_context(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()
        template_text = '''{% extends "base.html" %}
{% load cms_tags %}

{% block content %}
<h1>{% render_model instance item_name %}</h1>
{% endblock content %}
'''
        request = self.get_page_request(page, user, edit=True)
        response = detail_view(request, ex1.pk, template_string=template_text,
                               item_name="callable_item")
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">char_1</div></h1>' % (
                'placeholderapp', 'example1', 'callable_item', ex1.pk))

    def test_edit_field(self):
        from django.contrib.admin import site

        exadmin = site._registry[Example1]

        user = self.get_superuser()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()

        request = self.get_page_request(page, user, edit=True)
        request.GET['edit_fields'] = 'char_1'
        response = exadmin.edit_field(request, ex1.pk, "en")
        self.assertContains(response, 'id="id_char_1"')
        self.assertContains(response, 'value="char_1"')

    def test_edit_field_not_allowed(self):
        from django.contrib.admin import site

        exadmin = site._registry[Example1]

        user = self.get_superuser()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex1 = Example1(char_1="char_1", char_2="char_2", char_3="char_3",
                       char_4="char_4")
        ex1.save()

        request = self.get_page_request(page, user, edit=True)
        request.GET['edit_fields'] = 'char_3'
        response = exadmin.edit_field(request, ex1.pk, "en")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Field char_3 not found')

    def test_multi_edit(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        title = create_title("fr", "test", page)

        exm = MultilingualExample1()
        exm.translate("en")
        exm.char_1 = 'one'
        exm.char_2 = 'two'
        exm.save()
        exm.translate("fr")
        exm.char_1 = "un"
        exm.char_2 = "deux"
        exm.save()

        request = self.get_page_request(page, user, edit=True, lang_code="en")
        response = detail_view_multi(request, exm.pk)
        self.assertContains(
            response,
            '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">one</div></h1>' % (
                'placeholderapp', 'multilingualexample1', 'char_1', exm.pk))
        self.assertContains(response, "/admin/placeholderapp/multilingualexample1/edit-field/%s/en/" % exm.pk)
        self.assertTrue(re.search(self.edit_fields_rx % "char_1", response.content.decode('utf8')))
        self.assertTrue(re.search(self.edit_fields_rx % "char_1%2Cchar_2", response.content.decode('utf8')))

        with self.settings(LANGUAGE_CODE="fr"):
            request = self.get_page_request(title.page, user, edit=True, lang_code="fr")
            response = detail_view_multi(request, exm.pk)
            self.assertContains(
                response,
                '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">un</div></h1>' % (
                    'placeholderapp', 'multilingualexample1', 'char_1', exm.pk))
            self.assertContains(response, "/admin/placeholderapp/multilingualexample1/edit-field/%s/fr/" % exm.pk)
            self.assertTrue(re.search(self.edit_fields_rx % "char_1%2Cchar_2", response.content.decode('utf8')))

    def test_multi_edit_no500(self):
        user = self.get_staff()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        title = create_title("fr", "test", page)

        exm = MultilingualExample1()
        exm.translate("fr")
        exm.char_1 = "un"
        exm.char_2 = "deux"
        exm.save()

        with self.settings(LANGUAGE_CODE="fr"):
            request = self.get_page_request(title.page, user, edit=True, lang_code="fr")
            response = detail_view_multi_unfiltered(request, exm.pk)
            self.assertContains(
                response,
                '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">un</div></h1>' % (
                    'placeholderapp', 'multilingualexample1', 'char_1', exm.pk))
            self.assertContains(response, "/admin/placeholderapp/multilingualexample1/edit-field/%s/fr/" % exm.pk)
            self.assertTrue(re.search(self.edit_fields_rx % "char_1%2Cchar_2", response.content.decode('utf8')))

        with self.settings(LANGUAGE_CODE="de"):
            request = self.get_page_request(title.page, user, edit=True, lang_code="de")
            response = detail_view_multi_unfiltered(request, exm.pk)
            self.assertContains(
                response,
                '<h1><div class="cms_plugin cms_plugin-%s-%s-%s-%s cms_render_model">un</div></h1>' % (
                    'placeholderapp', 'multilingualexample1', 'char_1', exm.pk))
            self.assertContains(response, "/admin/placeholderapp/multilingualexample1/edit-field/%s/de/" % exm.pk)
            self.assertTrue(re.search(self.edit_fields_rx % "char_1%2Cchar_2", response.content.decode('utf8')))

    def test_edit_field_multilingual(self):
        from django.contrib.admin import site

        exadmin = site._registry[MultilingualExample1]

        user = self.get_superuser()
        page = create_page('Test', 'col_two.html', 'en', published=True)
        title = create_title("fr", "test", page)

        exm = MultilingualExample1()
        exm.translate("en")
        exm.char_1 = 'one'
        exm.char_2 = 'two'
        exm.save()
        exm.translate("fr")
        exm.char_1 = "un"
        exm.char_2 = "deux"
        exm.save()

        request = self.get_page_request(page, user, edit=True)
        request.GET['edit_fields'] = 'char_2'

        with override('en'):
            response = exadmin.edit_field(request, exm.pk, "en")
            self.assertContains(response, 'id="id_char_2"')
            self.assertContains(response, 'value="two"')

        with override('fr'):
            response = exadmin.edit_field(request, exm.pk, "fr")
            self.assertContains(response, 'id="id_char_2"')
            self.assertContains(response, 'value="deux"')

        with override('fr'):
            with self.settings(LANGUAGE_CODE="fr"):
                request = self.get_page_request(title.page, user, edit=True, lang_code="fr")
                request.GET['edit_fields'] = 'char_2'
                response = exadmin.edit_field(request, exm.pk, "fr")
                self.assertContains(response, 'id="id_char_2"')
                self.assertContains(response, 'value="deux"')

    def test_edit_page(self):
        language = "en"
        user = self.get_superuser()
        page = create_page('Test', 'col_two.html', language, published=True)
        title = page.get_title_obj(language)
        title.menu_title = 'Menu Test'
        title.page_title = 'Page Test'
        title.title = 'Main Test'
        title.save()
        page.publish('en')
        page.reload()
        request = self.get_page_request(page, user, edit=True)
        response = details(request, '')
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-cms-page-get_page_title-%s cms_render_model">%s</div>' % (
                page.pk, page.get_page_title(language)))
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-cms-page-get_menu_title-%s cms_render_model">%s</div>' % (
                page.pk, page.get_menu_title(language)))
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-cms-page-get_title-%s cms_render_model">%s</div>' % (
                page.pk, page.get_title(language)))
        self.assertContains(
            response,
            '<div class="cms_plugin cms_plugin-cms-page-changelist-%s cms_render_model cms_render_model_block">\n        <h3>Menu</h3>' % page.pk)
        self.assertContains(
            response,
            "'edit_plugin': '%s?language=%s&amp;edit_fields=changelist'" % (admin_reverse('cms_page_changelist'), language))

class CharPkFrontendPlaceholderAdminTest(ToolbarTestBase):

    def get_admin(self):
        admin.autodiscover()
        return admin.site._registry[CharPksExample]

    def test_url_char_pk(self):
        """
        Tests whether the frontend admin matches the edit_fields url with alphanumeric pks
        """
        ex = CharPksExample(
            char_1='one',
            slug='some-Special_slug_123',
        )
        ex.save()
        superuser = self.get_superuser()
        with UserLoginContext(self, superuser):
            response = self.client.get(admin_reverse('placeholderapp_charpksexample_edit_field', args=(ex.pk, 'en')),
                                       data={'edit_fields': 'char_1'})
            # if we get a response pattern matches
            self.assertEqual(response.status_code, 200)

    def test_url_numeric_pk(self):
        """
        Tests whether the frontend admin matches the edit_fields url with numeric pks
        """
        ex = Example1(
            char_1='one',
            char_2='two',
            char_3='tree',
            char_4='four'
        )
        ex.save()
        superuser = self.get_superuser()
        with UserLoginContext(self, superuser):
            response = self.client.get(admin_reverse('placeholderapp_example1_edit_field', args=(ex.pk, 'en')),
                                       data={'edit_fields': 'char_1'})
            # if we get a response pattern matches
            self.assertEqual(response.status_code, 200)

    def test_view_char_pk(self):
        """
        Tests whether the admin urls triggered when the toolbar is active works
        (i.e.: no NoReverseMatch is raised) with alphanumeric pks
        """
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex = CharPksExample(
            char_1='one',
            slug='some-Special_slug_123',
        )
        ex.save()
        superuser = self.get_superuser()
        request = self.get_page_request(page, superuser, edit=True)
        response = detail_view_char(request, ex.pk)
        # if we get a response pattern matches
        self.assertEqual(response.status_code, 200)

    def test_view_numeric_pk(self):
        """
        Tests whether the admin urls triggered when the toolbar is active works
        (i.e.: no NoReverseMatch is raised) with numeric pks
        """
        page = create_page('Test', 'col_two.html', 'en', published=True)
        ex = Example1(
            char_1='one',
            char_2='two',
            char_3='tree',
            char_4='four'
        )
        ex.save()
        superuser = self.get_superuser()
        request = self.get_page_request(page, superuser, edit=True)
        response = detail_view(request, ex.pk)
        # if we get a response pattern matches
        self.assertEqual(response.status_code, 200)


class ToolbarAPITests(TestCase):
    def test_find_item(self):
        api = ToolbarAPIMixin()
        first = api.add_link_item('First', 'http://www.example.org')
        second = api.add_link_item('Second', 'http://www.example.org')
        all_links = api.find_items(LinkItem)
        self.assertEqual(len(all_links), 2)
        result = api.find_first(LinkItem, name='First')
        self.assertNotEqual(result, None)
        self.assertEqual(result.index, 0)
        self.assertEqual(result.item, first)
        result = api.find_first(LinkItem, name='Second')
        self.assertNotEqual(result, None)
        self.assertEqual(result.index, 1)
        self.assertEqual(result.item, second)
        no_result = api.find_first(LinkItem, name='Third')
        self.assertEqual(no_result, None)

    def test_find_item_lazy(self):
        lazy_attribute = lazy(lambda x: x, str)('Test')
        api = ToolbarAPIMixin()
        api.add_link_item(lazy_attribute, None)
        result = api.find_first(LinkItem, name='Test')
        self.assertNotEqual(result, None)
        self.assertEqual(result.index, 0)

    def test_not_is_staff(self):
        request = RequestFactory().get('/en/?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
        request.session = {}
        request.LANGUAGE_CODE = 'en'
        request.user = AnonymousUser()
        toolbar = CMSToolbar(request)
        self.assertEqual(len(toolbar.get_left_items()), 0)
        self.assertEqual(len(toolbar.get_right_items()), 0)

    def test_item_search_result(self):
        item = object()
        result = ItemSearchResult(item, 2)
        self.assertEqual(result.item, item)
        self.assertEqual(int(result), 2)
        result += 2
        self.assertEqual(result.item, item)
        self.assertEqual(result.index, 4)
