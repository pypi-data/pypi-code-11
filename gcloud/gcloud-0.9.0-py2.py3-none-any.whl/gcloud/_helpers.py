# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Thread-local resource stack.

This module is not part of the public API surface of `gcloud`.
"""

import calendar
import datetime
import os
from threading import local as Local
import socket
import sys

from google.protobuf import timestamp_pb2
import six
from six.moves.http_client import HTTPConnection  # pylint: disable=F0401

from gcloud.environment_vars import PROJECT

try:
    from google.appengine.api import app_identity
except ImportError:
    app_identity = None


_NOW = datetime.datetime.utcnow  # To be replaced by tests.
_RFC3339_MICROS = '%Y-%m-%dT%H:%M:%S.%fZ'


class _LocalStack(Local):
    """Manage a thread-local LIFO stack of resources.

    Intended for use in :class:`gcloud.datastore.batch.Batch.__enter__`,
    :class:`gcloud.storage.batch.Batch.__enter__`, etc.
    """
    def __init__(self):
        super(_LocalStack, self).__init__()
        self._stack = []

    def __iter__(self):
        """Iterate the stack in LIFO order.
        """
        return iter(reversed(self._stack))

    def push(self, resource):
        """Push a resource onto our stack.
        """
        self._stack.append(resource)

    def pop(self):
        """Pop a resource from our stack.

        :raises: IndexError if the stack is empty.
        :returns: the top-most resource, after removing it.
        """
        return self._stack.pop()

    @property
    def top(self):
        """Get the top-most resource

        :returns: the top-most item, or None if the stack is empty.
        """
        if len(self._stack) > 0:
            return self._stack[-1]


class _UTC(datetime.tzinfo):
    """Basic UTC implementation.

    Implementing a small surface area to avoid depending on ``pytz``.
    """

    _dst = datetime.timedelta(0)
    _tzname = 'UTC'
    _utcoffset = _dst

    def dst(self, dt):  # pylint: disable=unused-argument
        """Daylight savings time offset."""
        return self._dst

    def fromutc(self, dt):
        """Convert a timestamp from (naive) UTC to this timezone."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self)
        return super(_UTC, self).fromutc(dt)

    def tzname(self, dt):  # pylint: disable=unused-argument
        """Get the name of this timezone."""
        return self._tzname

    def utcoffset(self, dt):  # pylint: disable=unused-argument
        """UTC offset of this timezone."""
        return self._utcoffset

    def __repr__(self):
        return '<%s>' % (self._tzname,)

    def __str__(self):
        return self._tzname


def _ensure_tuple_or_list(arg_name, tuple_or_list):
    """Ensures an input is a tuple or list.

    This effectively reduces the iterable types allowed to a very short
    whitelist: list and tuple.

    :type arg_name: string
    :param arg_name: Name of argument to use in error message.

    :type tuple_or_list: sequence of string
    :param tuple_or_list: Sequence to be verified.

    :rtype: list of string
    :returns: The ``tuple_or_list`` passed in cast to a ``list``.
    :raises: class:`TypeError` if the ``tuple_or_list`` is not a tuple or
             list.
    """
    if not isinstance(tuple_or_list, (tuple, list)):
        raise TypeError('Expected %s to be a tuple or list. '
                        'Received %r' % (arg_name, tuple_or_list))
    return list(tuple_or_list)


def _app_engine_id():
    """Gets the App Engine application ID if it can be inferred.

    :rtype: string or ``NoneType``
    :returns: App Engine application ID if running in App Engine,
              else ``None``.
    """
    if app_identity is None:
        return None

    return app_identity.get_application_id()


def _compute_engine_id():
    """Gets the Compute Engine project ID if it can be inferred.

    Uses 169.254.169.254 for the metadata server to avoid request
    latency from DNS lookup.

    See https://cloud.google.com/compute/docs/metadata#metadataserver
    for information about this IP address. (This IP is also used for
    Amazon EC2 instances, so the metadata flavor is crucial.)

    See https://github.com/google/oauth2client/issues/93 for context about
    DNS latency.

    :rtype: string or ``NoneType``
    :returns: Compute Engine project ID if the metadata service is available,
              else ``None``.
    """
    host = '169.254.169.254'
    uri_path = '/computeMetadata/v1/project/project-id'
    headers = {'Metadata-Flavor': 'Google'}
    connection = HTTPConnection(host, timeout=0.1)

    try:
        connection.request('GET', uri_path, headers=headers)
        response = connection.getresponse()
        if response.status == 200:
            return response.read()
    except socket.error:  # socket.timeout or socket.error(64, 'Host is down')
        pass
    finally:
        connection.close()


def _get_production_project():
    """Gets the production project if it can be inferred."""
    return os.getenv(PROJECT)


def _determine_default_project(project=None):
    """Determine default project ID explicitly or implicitly as fall-back.

    In implicit case, supports three environments. In order of precedence, the
    implicit environments are:

    * GCLOUD_PROJECT environment variable
    * Google App Engine application ID
    * Google Compute Engine project ID (from metadata server)

    :type project: string
    :param project: Optional. The project name to use as default.

    :rtype: string or ``NoneType``
    :returns: Default project if it can be determined.
    """
    if project is None:
        project = _get_production_project()

    if project is None:
        project = _app_engine_id()

    if project is None:
        project = _compute_engine_id()

    return project


def _millis(when):
    """Convert a zone-aware datetime to integer milliseconds.

    :type when: :class:`datetime.datetime`
    :param when: the datetime to convert

    :rtype: integer
    :returns: milliseconds since epoch for ``when``
    """
    micros = _microseconds_from_datetime(when)
    return micros // 1000


def _datetime_from_microseconds(value):
    """Convert timestamp to datetime, assuming UTC.

    :type value: float
    :param value: The timestamp to convert

    :rtype: :class:`datetime.datetime`
    :returns: The datetime object created from the value.
    """
    return _EPOCH + datetime.timedelta(microseconds=value)


def _microseconds_from_datetime(value):
    """Convert non-none datetime to microseconds.

    :type value: :class:`datetime.datetime`
    :param value: The timestamp to convert.

    :rtype: integer
    :returns: The timestamp, in microseconds.
    """
    if not value.tzinfo:
        value = value.replace(tzinfo=UTC)
    # Regardless of what timezone is on the value, convert it to UTC.
    value = value.astimezone(UTC)
    # Convert the datetime to a microsecond timestamp.
    return int(calendar.timegm(value.timetuple()) * 1e6) + value.microsecond


def _millis_from_datetime(value):
    """Convert non-none datetime to timestamp, assuming UTC.

    :type value: :class:`datetime.datetime`, or None
    :param value: the timestamp

    :rtype: integer, or ``NoneType``
    :returns: the timestamp, in milliseconds, or None
    """
    if value is not None:
        return _millis(value)


def _total_seconds_backport(offset):
    """Backport of timedelta.total_seconds() from python 2.7+.

    :type offset: :class:`datetime.timedelta`
    :param offset: A timedelta object.

    :rtype: int
    :returns: The total seconds (including microseconds) in the
              duration.
    """
    seconds = offset.days * 24 * 60 * 60 + offset.seconds
    return seconds + offset.microseconds * 1e-6


def _total_seconds(offset):
    """Version independent total seconds for a time delta.

    :type offset: :class:`datetime.timedelta`
    :param offset: A timedelta object.

    :rtype: int
    :returns: The total seconds (including microseconds) in the
              duration.
    """
    if sys.version_info[:2] < (2, 7):  # pragma: NO COVER
        return _total_seconds_backport(offset)
    else:
        return offset.total_seconds()


def _rfc3339_to_datetime(dt_str):
    """Convert a string to a native timestamp.

    :type dt_str: str
    :param dt_str: The string to convert.

    :rtype: :class:`datetime.datetime`
    :returns: The datetime object created from the string.
    """
    return datetime.datetime.strptime(
        dt_str, _RFC3339_MICROS).replace(tzinfo=UTC)


def _datetime_to_rfc3339(value):
    """Convert a native timestamp to a string.

    :type value: :class:`datetime.datetime`
    :param value: The datetime object to be converted to a string.

    :rtype: str
    :returns: The string representing the datetime stamp.
    """
    return value.strftime(_RFC3339_MICROS)


def _to_bytes(value, encoding='ascii'):
    """Converts a string value to bytes, if necessary.

    Unfortunately, ``six.b`` is insufficient for this task since in
    Python2 it does not modify ``unicode`` objects.

    :type value: str / bytes or unicode
    :param value: The string/bytes value to be converted.

    :type encoding: str
    :param encoding: The encoding to use to convert unicode to bytes. Defaults
                     to "ascii", which will not allow any characters from
                     ordinals larger than 127. Other useful values are
                     "latin-1", which which will only allows byte ordinals
                     (up to 255) and "utf-8", which will encode any unicode
                     that needs to be.

    :rtype: str / bytes
    :returns: The original value converted to bytes (if unicode) or as passed
              in if it started out as bytes.
    :raises: :class:`TypeError <exceptions.TypeError>` if the value
             could not be converted to bytes.
    """
    result = (value.encode(encoding)
              if isinstance(value, six.text_type) else value)
    if isinstance(result, six.binary_type):
        return result
    else:
        raise TypeError('%r could not be converted to bytes' % (value,))


def _pb_timestamp_to_datetime(timestamp):
    """Convert a Timestamp protobuf to a datetime object.

    :type timestamp: :class:`google.protobuf.timestamp_pb2.Timestamp`
    :param timestamp: A Google returned timestamp protobuf.

    :rtype: :class:`datetime.datetime`
    :returns: A UTC datetime object converted from a protobuf timestamp.
    """
    return (
        _EPOCH +
        datetime.timedelta(
            seconds=timestamp.seconds,
            microseconds=(timestamp.nanos / 1000.0),
        )
    )


def _datetime_to_pb_timestamp(when):
    """Convert a datetime object to a Timestamp protobuf.

    :type when: :class:`datetime.datetime`
    :param when: the datetime to convert

    :rtype: :class:`google.protobuf.timestamp_pb2.Timestamp`
    :returns: A timestamp protobuf corresponding to the object.
    """
    ms_value = _microseconds_from_datetime(when)
    seconds, micros = divmod(ms_value, 10**6)
    nanos = micros * 10**3
    return timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)


def _has_field(message_pb, property_name):
    """Determine if a field is set on a protobuf.

    :type message_pb: :class:`google.protobuf.message.Message`
    :param message_pb: The message to check for ``property_name``.

    :type property_name: str
    :param property_name: The property value to check against.

    :rtype: bool
    :returns: Flag indicating if ``property_name`` is set on ``message_pb``.
    """
    # NOTE: As of proto3, HasField() only works for message fields, not for
    #       singular (non-message) fields. First try to use HasField and
    #       if it fails (with a ValueError) we manually consult the fields.
    try:
        return message_pb.HasField(property_name)
    except ValueError:
        all_fields = set([field.name for field in message_pb._fields])
        return property_name in all_fields


def _get_pb_property_value(message_pb, property_name):
    """Return a message field value.

    :type message_pb: :class:`google.protobuf.message.Message`
    :param message_pb: The message to check for ``property_name``.

    :type property_name: str
    :param property_name: The property value to check against.

    :rtype: object
    :returns: The value of ``property_name`` set on ``message_pb``.
    :raises: :class:`ValueError <exceptions.ValueError>` if the result returned
             from the ``message_pb`` does not contain the ``property_name``
             value.
    """
    if _has_field(message_pb, property_name):
        return getattr(message_pb, property_name)
    else:
        raise ValueError('Message does not contain %s.' % (property_name,))


try:
    from pytz import UTC  # pylint: disable=unused-import,wrong-import-position
except ImportError:
    UTC = _UTC()  # Singleton instance to be used throughout.

# Need to define _EPOCH at the end of module since it relies on UTC.
_EPOCH = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=UTC)
