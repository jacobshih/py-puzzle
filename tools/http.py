################################################################################

import httplib
import urllib
import urllib2
import base64
import json
import locale
import ssl
import sys
from urllib2 import HTTPError, URLError

################################################################################

__all__ = []


def export(obj):
    __all__.append(obj.__name__)
    return obj


################################################################################
@export
class HTTP(object):
    REALM = None
    TIMEOUT = 20


################################################################################
class PreemptiveBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
    """
    Preemptive basic auth.
    Instead of waiting for a 401 to then retry with the credentials,
    send the credentials if the url is handled by the password manager.
    Note: please use realm=None when calling add_password.
    """

    def http_request(self, req):
        url = req.get_full_url()
        realm = None
        # this is very similar to the code from retry_http_basic_auth()
        # but returns a request object.
        user, pw = self.passwd.find_user_password(realm, url)
        if user:
            raw = '%s:%s' % (user, pw)
            auth = 'Basic %s' % base64.b64encode(raw).strip()
            req.add_unredirected_header(self.auth_header, auth)
        return req

    https_request = http_request


################################################################################
# deco_httpreq() is a decorator function that helps send the http request.
# url: request url.
# data: post data, if the data is not empty, it sends request with post method.
# userinfo: a string combination of web username and password, separated by a colon.
# timeout: http timeout. default 20 seconds.
def deco_httpreq(f):
    def d_f(that, url, data=None, userinfo=None):
        encoding = locale.getdefaultlocale()[1] or 'utf8'
        httpcode = 0
        try:
            opener, url, data, timeout = f(that, url, data, userinfo)
            resp = opener.open(url, data, timeout)
            return resp
        except URLError, e:
            r = {
                'reason': '%s' % str(e.reason).decode(encoding).encode('utf8'),
                'exception': '%s' % str(e).decode(encoding).encode('utf8')
            }
            if isinstance(e, HTTPError):
                r['code'] = httpcode = e.code
            response = json.dumps(r)
            return httpcode, response
        except httplib.BadStatusLine as e:
            r = {
                'reason': '%s %s' % ('BadStatusLine', e.line),
                'exception': '%s' % str(e).decode(encoding).encode('utf8')
            }
            response = json.dumps(r)
            return httpcode, response
        except IOError as e:
            r = {
                'reason': '%s' % 'IOError',
                'exception': '%s' % str(e).decode(encoding).encode('utf8')
            }
            response = json.dumps(r)
            return httpcode, response
        pass

    return d_f


################################################################################
# noinspection PyProtectedMember,PyProtectedMember
@export
class HttpClient(object):
    validMethods = ('get', 'post')

    def __init__(self, opener=None):
        self._opener = opener if opener is not None else urllib2.build_opener()
        pass

    @classmethod
    def build_opener(cls, realm, url, username, password):
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(realm, url, username, password)
        basic_auth = PreemptiveBasicAuthHandler(passman)
        if sys.version_info >= (2, 7, 9):
            # noinspection PyProtectedMember
            https_handler = urllib2.HTTPSHandler(context=ssl._create_unverified_context())
        else:
            https_handler = urllib2.HTTPSHandler()
        opener = urllib2.build_opener(basic_auth, https_handler)
        return opener

    @classmethod
    def is_valid_method(cls, method):
        return True if method in cls.validMethods else False

    def install_opener(self, opener):
        self._opener = opener
        urllib2.install_opener(self._opener)
        pass

    @deco_httpreq
    def get(self, url, data=None, userinfo=None, timeout=HTTP.TIMEOUT):
        opener = self.get_opener(url, userinfo)
        if data is not None:
            # append data to url as query string, and reset data to None for get request.
            if isinstance(data, dict):
                url += '?' + urllib.urlencode(data).encode()
            else:
                url += '?' + data.encode()
            data = None
            pass
        return opener, url, data, timeout

    @deco_httpreq
    def post(self, url, data, userinfo=None, timeout=HTTP.TIMEOUT):
        opener = self.get_opener(url, userinfo)
        if isinstance(data, dict):
            postdata = urllib.urlencode(data).encode()
        else:
            postdata = data.encode()
        return opener, url, postdata, timeout

    def get_opener(self, url, userinfo=None):
        if userinfo is None:
            opener = self._opener
        else:
            user = userinfo.split(':')[0] if -1 != userinfo.find(':') else userinfo
            pwd = userinfo.split(':')[1] if -1 != userinfo.find(':') else ''
            opener = HttpClient.build_opener(HTTP.REALM, url, user, pwd)
        return opener


if __name__ == '__main__':
    pass
