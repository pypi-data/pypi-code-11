# Copyright (c) 2013-2015 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

"""Miscellaneous utility classes and functions"""

import ipaddress
import socket

from random import SystemRandom

from .constants import DEFAULT_LANG


# Define a version of randrange which is based on SystemRandom(), so that
# we get back numbers suitable for cryptographic use.
_random = SystemRandom()
randrange = _random.randrange


def all_ints(seq):
    """Return if a sequence contains all integers"""

    return all(isinstance(i, int) for i in seq)


# Punctuation to map when creating handler names
_HANDLER_PUNCTUATION = (('@', '_at_'), ('.', '_dot_'), ('-', '_'))

def map_handler_name(name):
    """Map punctuation so a string can be used as a handler name"""

    for old, new in _HANDLER_PUNCTUATION:
        name = name.replace(old, new)

    return name


def _normalize_scoped_ip(addr):
    """Normalize scoped IP address

       The ipaddress module doesn't handle scoped addresses properly,
       so we strip off the CIDR suffix here and normalize scoped IP
       addresses using socket.inet_pton before we pass them into
       ipaddress.

    """

    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            return socket.inet_ntop(family, socket.inet_pton(family, addr))
        except (ValueError, socket.error):
            pass

    return addr


def ip_address(addr):
    """Wrapper for ipaddress.ip_address which supports scoped addresses"""

    return ipaddress.ip_address(_normalize_scoped_ip(addr))


def ip_network(addr):
    """Wrapper for ipaddress.ip_network which supports scoped addresses"""

    idx = addr.find('/')
    if idx >= 0:
        addr, mask = addr[:idx], addr[idx:]
    else:
        mask = ''

    return ipaddress.ip_network(_normalize_scoped_ip(addr) + mask)


class Error(Exception):
    """General SSH error"""

    def __init__(self, errtype, code, reason, lang):
        super().__init__('%s Error: %s' % (errtype, reason))
        self.code = code
        self.reason = reason
        self.lang = lang


class DisconnectError(Error):
    """SSH disconnect error

       This exception is raised when a serious error occurs which causes
       the SSH connection to be disconnected. Exception codes should be
       taken from :ref:`disconnect reason codes <DisconnectReasons>`.

       :param int code:
           Disconnect reason, taken from :ref:`disconnect reason
           codes <DisconnectReasons>`
       :param str reason:
           A human-readable reason for the disconnect
       :param str lang:
           The language the reason is in

    """

    def __init__(self, code, reason, lang=DEFAULT_LANG):
        super().__init__('Disconnect', code, reason, lang)


class ChannelOpenError(Error):
    """SSH channel open error

       This exception is raised by connection handlers to report
       channel open failures.

       :param int code:
           Channel open failure  reason, taken from :ref:`channel open
           failure reason codes <ChannelOpenFailureReasons>`
       :param str reason:
           A human-readable reason for the channel open failure
       :param str lang:
           The language the reason is in

    """

    def __init__(self, code, reason, lang=DEFAULT_LANG):
        super().__init__('Channel Open', code, reason, lang)


class PasswordChangeRequired(Exception):
    """SSH password change required

       This exception is raised during password validation on the
       server to indicate that a password change is required. It
       shouuld be raised when the password provided is valid but
       expired, to trigger the client to provide a new password.

       :param str prompt:
           The prompt requesting that the user enter a new password
       :param str lang:
           The language that the prompt is in

    """

    def __init__(self, prompt, lang=DEFAULT_LANG):
        super().__init__('Password change required: %s' % prompt)
        self.prompt = prompt
        self.lang = lang


class BreakReceived(Exception):
    """SSH break request received

       This exception is raised on an SSH server stdin stream when the
       client sends a break on the channel.

       :param int msec:
           The duration of the break in milliseconds

    """

    def __init__(self, msec):
        super().__init__('Break for %s msec' % msec)
        self.msec = msec


class SignalReceived(Exception):
    """SSH signal request received

       This exception is raised on an SSH server stdin stream when the
       client sends a signal on the channel.

       :param str signal:
           The name of the signal sent by the client

    """

    def __init__(self, signal):
        super().__init__('Signal: %s' % signal)
        self.signal = signal


class TerminalSizeChanged(Exception):
    """SSH terminal size change notification received

       This exception is raised on an SSH server stdin stream when the
       client sends a terminal size change on the channel.

       :param int width:
           The new terminal width
       :param int height:
           The new terminal height
       :param int pixwidth:
           The new terminal width in pixels
       :param int pixheight:
           The new terminal height in pixels

    """

    def __init__(self, width, height, pixwidth, pixheight):
        super().__init__('Terminal size change: (%s, %s, %s, %s)' %
                         (width, height, pixwidth, pixheight))
        self.width = width
        self.height = height
        self.pixwidth = pixwidth
        self.pixheight = pixheight
