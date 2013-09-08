# -*- coding: utf-8 -*-
'''
Created on Jul 8, 2013

@auther: openinx@gmail.com
'''

from urllib import urlencode
import logging
import httplib
import hashlib
import json


class HTTPClient:

    USER_AGENT = 'python-jssclient'

    def __init__(
            self, access_key, secret_key, service_url, 
            timeout=30, http_log_debug=False
        ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.service_url = service_url
        self.timeout = timeout
        self.http_log_debug = http_log_debug

        self._logger = logging.getLogger(__name__)
        if self.http_log_debug:
            ch = logging.StreamHandler()
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(ch)

    def http_log_request(self, url, method, body={}, headers={}):
        if not self.http_log_debug:
            return

        string_parts = ['curl -i']
        string_parts.append(' %s' % url)
        string_parts.append(' -X %s' % method)

        for element in headers:
            header = ' -H "%s: %s"' % (element, headers[element])
            string_parts.append(header)

        if 'body' in body:
            string_parts.append(" -d '%s'" % (body))

        self._logger.debug("\nREQUEST: %s\n" % "".join(string_parts))

    def http_log_response(self, status, headers, body):
        if not self.http_log_debug:
            return
        self._logger.debug('RESPONSE: status  : %s' % status)
        for h in headers:
            self._logger.debug('RESPONSE: header  : %s: %s' % (h[0], h[1]))
        self._logger.debug('RESPONSE: body    : %s' % body)

    def auth_info(self):
        raw_s = self.access_key + self.secret_key
        raw_signature = hashlib.sha256(raw_s).hexdigest()
        signature = utils.base64_encode(raw_signature)
        auth = {'AccessKey': self.access_key, 'Signature': signature}
        return auth

    @property
    def request_url(self):
        return '/%s' % (self.version,)

    def _request(self, method, body={}, headers={}):
        conn = httplib.HTTPConnection(host=self.host, port=self.port)
        if method not in ['GET', 'POST', 'DELETE', 'PUT']:
            raise exceptions.MethodNotSupported(method)

        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'
        headers['User-Agent'] = self.USER_AGENT

        body.update(self.auth_info())

        if method == 'GET':
            resource = '%s/?%s' % (self.request_url, urlencode(body))
        if method == 'POST':
            resource = self.request_url
        if method == 'DELETE':
            resource = self.request_url
        if method == 'PUT':
            resource = self.request_url

        body = json.dumps(body)

        debug_url = 'http://%s:%s%s' % (self.host, self.port, resource)
        self.http_log_request(debug_url, method, headers=headers, body=body)

        conn.request(method, resource, body, headers)

        resp = conn.getresponse()
        status = resp.status
        headers = resp.getheaders()
        raw_body_resp = resp.read()
        body = json.loads(raw_body_resp)

        self.http_log_response(status, headers, body)

        if status >= 400:
            exc_instance = getattr(exceptions, body['error']['title'])
            raise exc_instance

        return body

    def get(self, body={}, headers={}):
        return self._request('GET', body, headers)

    def post(self, body={}, headers={}):
        return self._request('POST', body, headers)

    def delete(self, body={}, headers={}):
        return self._request('DELETE', body, headers)

    def put(self, body={}, headers={}):
        return self._request('PUT', body, headers)
