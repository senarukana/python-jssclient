# -*- coding: utf-8 -*-
# nepo.nepoclient.jds.httpclient
# Copyright (C) 2012-2013 the nepo authors and contributors <see AUTHORS file>
#
# This module is part of nepo and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

""" HTTPClient """
import urllib
import hashlib
import hmac
import base64
import logging
import httplib
import json
import datetime

from jssclient import exceptions


GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
def timestamp():
    return datetime.datetime.utcnow().strftime(GMT_FORMAT)


class HTTPClient:

    USER_AGENT = 'python-jssclient'
    API_VERSION_1_DOT_0 = 'jds'

    def __init__(
            self, hostname, access_key, secret_key,
            timeout=30, http_log_debug=False
        ):

        self.hostname = hostname
        self.access_key = access_key
        self.secret_key = secret_key
        self.timeout = timeout
        self.http_log_debug = http_log_debug

        self._logger = logging.getLogger(__name__)
        if self.http_log_debug:
            ch = logging.StreamHandler()
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(ch)

    def http_log_request(self, url, method, body, headers):
        if not self.http_log_debug:
            return

        string_parts = ['curl -i']
        string_parts.append(' %s' % url)
        string_parts.append(' -X %s' % method)

        for element in headers:
            header = ' -H "%s: %s"' % (element, headers[element])
            string_parts.append(header)

        if body:
            string_parts.append(" -d '%s'" % (body))

        self._logger.debug("\nreq: %s\n" % "".join(string_parts))

    def http_log_response(self, status, headers, body=None):
        if not self.http_log_debug:
            return
        self._logger.debug('reply: %s' % status)
        for h in headers:
            self._logger.debug('header: %s: %s' % (h[0], h[1]))
        if body:
            self._logger.debug('body: %s' % body)

    def get_token(self, method, content_md5, content_type, datenow, resource):
        buf = [method, content_md5, content_type, datenow, resource]
        # for i in buf: print type(i)
        buf_str = '\n'.join(buf)
        hashv = hmac.new(self.secret_key, buf_str, hashlib.sha1).digest()
        signature = base64.encodestring(hashv).strip()
        return "jingdong %s:%s" % (self.access_key, signature)


    def _request(self, method, resource, body, headers, readed, kwargs={}):

        conn = httplib.HTTPConnection(self.hostname)
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        if 'Content-Length' not in headers:
            headers['Content-Length'] = 0

        headers['Date'] = timestamp()
        headers['User-Agent'] = 'JSS-SDK-PYTHON/1.0.1'

        headers['Authorization'] = self.get_token(method,
                                                  '',
                                                  headers['Content-Type'],
                                                  headers['Date'],
                                                  resource)

        if kwargs and isinstance(kwargs, dict):
            resource = '%s?%s' % (resource, urllib.urlencode(kwargs))

        body = json.dumps(body) if body else None
        if headers['Content-Length'] == 0 and body:
            headers['Content-Length'] = len(body)
        debug_url = 'http://%s%s' % (self.hostname, resource)
        self.http_log_request(debug_url, method, headers=headers, body=body)

        conn.request(method, resource, body, headers)

        resp = conn.getresponse()
        status = resp.status
        headers = resp.getheaders()

        if readed or status >= 400:
            raw_body_resp = resp.read()
            body = json.loads(raw_body_resp) if raw_body_resp else ''
            if status >= 400:
                raise exceptions.from_response(status, body)
            self.http_log_response(status, headers, body)
            return body

        self.http_log_response(status, headers)
        return resp

    def get_request_conn(self, method, resource, headers):
        conn = httplib.HTTPConnection(self.hostname)
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        if 'Content-Length' not in headers:
            headers['Content-Length'] = 0
        headers['User-Agent'] = 'JSS-SDK-PYTHON/1.0.1'
        headers['Date'] = timestamp()
        print headers
        headers['Authorization'] = self.get_token(method,
                                                  '',
                                                  headers['Content-Type'],
                                                  str(headers['Date']),
                                                  resource)
        conn.putrequest(method, resource)
        for key, value in headers.iteritems():
            conn.putheader(key, value)
        conn.endheaders()
        debug_url = 'http://%s%s' % (self.hostname, resource)
        self.http_log_request(debug_url, method, headers=headers, body=None)
        return conn


    def get(self, resource, body={}, headers={}, readed=True, kwargs={}):
        return self._request('GET', resource, body, headers,
                             readed=readed, kwargs=kwargs)

    def post(self, resource, body={}, headers={}, readed=True):
        return self._request('POST', resource, body, headers, readed=readed)

    def delete(self, resource, body={}, headers={}, readed=True):
        return self._request('DELETE', resource, body, headers, readed=readed)

    def put(self, resource, body={}, headers={}, readed=True):
        return self._request('PUT', resource, body, headers, readed=readed)
