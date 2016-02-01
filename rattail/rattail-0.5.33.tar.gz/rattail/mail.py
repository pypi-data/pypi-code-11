# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Email Framework
"""

from __future__ import unicode_literals, absolute_import

import smtplib
import logging
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException

from rattail import exceptions
from rattail.core import UNSPECIFIED
from rattail.files import resource_path
from rattail.util import import_module_path


log = logging.getLogger(__name__)


def send_email(config, key, data={}, attachments=[], fallback_key=None):
    """
    Send an email message of the given type, per config, with the given data
    and/or attachments.
    """
    email = get_email(config, key, fallback_key)
    if email.get_enabled():
        msg = email.make_message(data, attachments)
        deliver_message(config, msg)
    else:
        log.debug("skipping email of type '{0}' per config".format(key))


def get_email(config, key, fallback_key=None):
    """
    Return an email instance of the given type.
    """
    for email in iter_emails(config):
        if email.key == key or email.__name__ == key:
            return email(config, key, fallback_key)
    return Email(config, key, fallback_key)


def iter_emails(config):
    """
    Iterate over all available email types.
    """
    for module in config.getlist('rattail.mail', 'emails', default=[]):
        module = import_module_path(module)
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and issubclass(obj, Email)
                and not obj.abstract and obj is not Email):
                yield obj


def deliver_message(config, msg, recipients=UNSPECIFIED):
    """
    Deliver an email message using the given SMTP configuration.
    """
    if recipients is UNSPECIFIED:
        recips = set()
        to = msg.get_all('To')
        if to:
            recips = recips.union(set(to))
        cc = msg.get_all('Cc')
        if cc:
            recips = recips.union(set(cc))
        bcc = msg.get_all('Bcc')
        if bcc:
            recips = recips.union(set(bcc))
    else:
        recips = set(recipients)
    if not recips:
        raise RuntimeError("No recipients for email: {0}".format(repr(msg)))

    server = config.get('rattail.mail', 'smtp.server', default='localhost')
    username = config.get('rattail.mail', 'smtp.username')
    password = config.get('rattail.mail', 'smtp.password')

    if config.getbool('rattail.mail', 'send_emails', default=True):

        log.debug("connecting to server: {0}".format(server))
        session = smtplib.SMTP(server)
        if username and password:
            result = session.login(username, password)
            log.debug("login result is: {0}".format(repr(result)))

        result = session.sendmail(msg['From'], recips, msg.as_string())
        log.debug("sendmail result is: {0}".format(repr(result)))
        session.quit()

    else:
        log.debug("config says no emails, but would have sent one to: {0}".format(recips))


class Email(object):
    # Note: The docstring of an email is leveraged by code, hence this odd one.
    """
    (This email has no description.)
    """
    key = None
    fallback_key = None
    abstract = False
    default_prefix = "[rattail]"
    default_subject = "Automated message"

    def __init__(self, config, key=None, fallback_key=None):
        self.config = config

        if key:
            self.key = key
        elif not self.key:
            self.key = self.__class__.__name__
            if self.key == 'Email':
                raise exceptions.ConfigurationError("Email instance has no key: {0}".format(repr(self)))

        if fallback_key:
            self.fallback_key = fallback_key

        templates = config.getlist('rattail.mail', 'templates')
        templates = [resource_path(p) for p in templates]
        self.templates = TemplateLookup(directories=templates)

    def sample_data(self, request):
        return {}

    def get_enabled(self):
        """
        Get the enabled flag for the email's message type.
        """
        enabled = self.config.getbool('rattail.mail', '{0}.enabled'.format(self.key))
        if enabled is not None:
            return enabled
        enabled = self.config.getbool('rattail.mail', 'default.enabled')
        if enabled is not None:
            return enabled
        return self.config.getbool('rattail.mail', 'send_emails', default=True)

    def get_sender(self):
        """
        Returns the value for the message's ``From:`` header.

        :rtype: unicode
        """
        sender = self.config.get('rattail.mail', '{0}.from'.format(self.key))
        if not sender:
            sender = self.config.get('rattail.mail', 'default.from')
            if not sender:
                raise exceptions.SenderNotFound(self.key)
        return sender

    def get_replyto(self):
        """
        Get the Reply-To address for the message.
        """
        replyto = self.config.get('rattail.mail', '{0}.replyto'.format(self.key))
        if not replyto:
            replyto = self.config.get('rattail.mail', 'default.replyto')
        return replyto

    def get_recips(self, type_='to'):
        """
        Returns a list of recipients of the given type for the message.

        :param type_: Must be one of: ``('to', 'cc', 'bcc')``.

        :rtype: list
        """
        try:
            if type_.lower() not in ('to', 'cc', 'bcc'):
                raise Exception
        except:
            raise ValueError("Recipient type must be one of ('to', 'cc', 'bcc'); "
                             "not: {0}".format(repr(type_)))
        type_ = type_.lower()
        recips = self.config.getlist('rattail.mail', '{0}.{1}'.format(self.key, type_))
        if not recips:
            recips = self.config.getlist('rattail.mail', 'default.{0}'.format(type_))
        return recips

    def get_prefix(self, data={}):
        """
        Returns a string to be used as the subject prefix for the message.

        :rtype: unicode
        """
        prefix = self.config.get('rattail.mail', '{0}.prefix'.format(self.key))
        if not prefix:
            prefix = self.config.get('rattail.mail', 'default.prefix')
        return prefix or self.default_prefix

    def get_subject(self, data={}):
        """
        Returns the base value for the message's subject header, i.e. minus
        prefix.

        :rtype: unicode
        """
        subject = self.config.get('rattail.mail', '{0}.subject'.format(self.key),
                                  default=self.default_subject)
        if not subject:
            subject = self.config.get('rattail.mail', 'default.subject')
        if subject:
            subject = Template(subject).render(**data)
        return subject

    def get_complete_subject(self, data={}):
        """
        Returns the value for the message's ``Subject:`` header, i.e. the base
        subject with the prefix applied.  Note that config may provide the
        complete subject also, in which case the prefix and base subject are
        not considered.

        :rtype: unicode
        """
        return "{0} {1}".format(self.get_prefix(data), self.get_subject(data))

    def get_template(self, type_):
        """
        Locate and return the Mako email template of the given type
        (e.g. 'html'), or ``None`` if no such template can be found.
        """
        try:
            return self.templates.get_template('{0}.{1}.mako'.format(self.key, type_))
        except TopLevelLookupException:
            if self.fallback_key:
                try:
                    return self.templates.get_template('{0}.{1}.mako'.format(self.fallback_key, type_))
                except TopLevelLookupException:
                    pass

    def make_message(self, data={}, attachments=[]):
        """
        Returns a proper email ``Message`` instance which may be sent via SMTP.
        """
        txt_template = self.get_template('txt')
        html_template = self.get_template('html')

        if txt_template and html_template:
            msg = MIMEMultipart(_subtype='alternative', _subparts=[
                MIMEText(_text=txt_template.render(**data), _charset='utf_8'),
                MIMEText(_text=html_template.render(**data), _subtype='html', _charset='utf_8'),
            ])
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[msg] + attachments)

        elif txt_template:
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[
                    MIMEText(_text=txt_template.render(**data), _charset='utf_8'),
                ] + attachments)
            else:
                msg = MIMEText(_text=txt_template.render(**data), _charset='utf_8')

        elif html_template:
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[
                    MIMEText(_text=html_template.render(**data), _subtype='html', _charset='utf_8'),
                ] + attachments)
            else:
                msg = MIMEText(_text=html_template.render(**data), _subtype='html', _charset='utf_8')

        else:
            raise exceptions.MailTemplateNotFound(self.key)

        # subject/from
        msg['Subject'] = self.get_complete_subject(data)
        msg['From'] = self.get_sender()

        # reply-to
        replyto = self.get_replyto()
        if replyto:
            msg.add_header('Reply-To', replyto)

        # recipients
        to = self.get_recips('to')
        cc = self.get_recips('cc')
        bcc = self.get_recips('bcc')
        if not (to or cc or bcc):
            raise exceptions.RecipientsNotFound(self.key)
        if to:
            for recip in to:
                msg['To'] = recip
        if cc:
            for recip in cc:
                msg['Cc'] = recip
        if bcc:
            for recip in bcc:
                msg['Bcc'] = recip

        return msg
