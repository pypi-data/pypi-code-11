import hashlib
import hmac
import base64
from datetime import datetime, tzinfo, timedelta
import requests
import json
import platform

try:
    import urllib.parse as urllib
except ImportError:
    import urllib


class TelestreamCloudException(Exception):

    def __init__(self, msg, response=None):
        super(TelestreamCloudException, self).__init__(msg)
        self.response = response


class TelestreamCloudRequest(object):
    def __init__(self, verb, path, cred, data={}, timestamp=None):
        self.verb = verb.upper()
        self.path = self.canonical_path(path)
        self.cred = cred
        self.data = data
        self.timestamp = timestamp

        for name, val in self.data.items():
            if name == 'pipeline' and isinstance(val, dict):
                self.data[name] = json.dumps(val)

        signed_params = self.signed_params()

        self.files = None
        if self.verb == 'POST' and ('file' in data):
            self.files = {'file': open(data['file'], 'rb')}

        path_and_querystring = path + "?" + self.canonical_querystring(signed_params)
        self.requests_url = '{}{}'.format(self.api_url(), path_and_querystring)

    def send(self):
        response = getattr(requests, self.verb.lower())(self.requests_url, files=self.files)
        if not response.ok:
            msg = 'Error {}, {} '.format(response.status_code, response.reason)
            if response.text:
                msg += response.text
            raise TelestreamCloudException(msg, response)
        return response

    def signed_params(self):
        auth_params = self.data.copy()
        if 'factory_id' in self.cred.keys():
            auth_params['factory_id'] = self.cred['factory_id']
        auth_params['access_key'] = self.cred['access_key']
        auth_params['timestamp'] = self.timestamp or self.generate_timestamp()
        additional_args = auth_params.copy()
        additional_args.update(auth_params)

        # NOTE: when creating the authorisation signature for this
        # request do not include the file parameter.
        if 'file' in additional_args:
            del(additional_args['file'])

        auth_params['signature'] = self.generate_signature(
                                              self.verb,
                                              self.path,
                                              self.cred["api_host"],
                                              self.cred["secret_key"],
                                              additional_args)
        return auth_params

    def api_protocol(self):
        if str(self.cred["api_port"]) == '443':
            return 'https'
        return 'http'

    def api_url(self):
        return self.api_protocol() + '://' + self.api_host_and_port() + \
               self.api_path()

    def api_host_and_port(self):
        ret = self.cred["api_host"]
        if str(self.cred["api_port"]) != '80':
            ret += ':' + str(self.cred["api_port"])
        return ret

    def api_path(self):
        return '/v' + str(self.cred["api_version"])

    def generate_signature(self, verb, request_uri, host, secret_key, params={}):
        query_string = self.canonical_querystring(params)

        string_to_sign = (
            verb.upper() + "\n" +
            host.lower() + "\n" +
            request_uri + "\n" +
            query_string
        )

        signature = hmac.new(secret_key.encode('utf-8'),
                             string_to_sign.encode('utf-8'),
                             hashlib.sha256).digest()
        return base64.b64encode(signature).strip()

    def urlescape(self, s):
        if platform.python_version() >= '3' and isinstance(s, int):
            s = str(s)
        elif platform.python_version() < '3':
            s = unicode(s).encode('utf-8')
        return urllib.quote(s).replace("%7E", "~").replace(' ', '%20').replace('/', '%2F')

    def canonical_path(self, path):
        return '/' + path.strip(' \t\n\r\0\x0B/')

    def canonical_querystring(self, d):
        def recursion(d, base=None):
            pairs = []

            ordered_params = sorted([(k, v) for k, v in d.items()])
            for key, value in ordered_params:
                if key == 'file':
                    continue
                if hasattr(value, 'values'):
                    pairs += recursion(value, key)
                else:
                    new_pair = None
                    if base:
                        new_pair = "%s[%s]=%s" % (base, self.urlescape(key), self.urlescape(value))
                    else:
                        new_pair = "%s=%s" % (self.urlescape(key), self.urlescape(value))
                    pairs.append(new_pair)
            return pairs
        return '&'.join(recursion(d))

    def generate_timestamp(self):
        return datetime.now(UTC()).isoformat()


class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)
