import urllib2
import httplib
import datetime
import hashlib
import json
import hmac
import base64
import os
from jssclient import mime_type
from jssclient import exceptions


GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
BUFFER_SIZE = 65536


def parser_response(func):
    def _inner(*args, **kwargs):
        response = func(*args, **kwargs)
        data = response.read()
        if not data:
            return True
        objs = json.loads(data)
        return objs
    return _inner


class Client:
    """Jiongdong Cloud Storage Service SDK"""

    def __init__(self, access_key, secret_key, jss_url):
        self.access_key = access_key 
        self.secret_key = secret_key
        self.jss_url = jss_url
        self.check_result = True

    @parser_response
    def bucket_create(self, bucket_name):
        """
        create a new bucket
        @param bucket_name:string

        """
        response = self._make_request('PUT', bucket_name)
        self.check_response(response)
        return response

    @parser_response
    def bucket_delete(self, bucket_name):
        """
        delete a  bucket
        @param bucket_name:string
        """
        response = self._make_request('DELETE', bucket_name)
        self.check_response(response)
        return response

    @parser_response
    def bucket_list(self):
        """
        list user's all  buckets
        """
        response = self._make_request('GET')
        self.check_response(response)
        return response

    @parser_response
    def object_put(self, bucket_name, object_name, file_path):
        """
        upload a object(file) to one of user's  bucket
        @param bucket_name: string
        @param object_name: string
        @param file_path: string
        """

        response = self._make_request_upload_object('PUT', bucket_name, object_name, path = file_path)
        self.check_response(response)
        return response

    @parser_response
    def object_delete(self, bucket_name, object_name):
        """
        delete one object of bucket
        @param bucket_name: string
        @param object_name: string

        """
        response = self._make_request('DELETE', bucket_name, object_name)
        self.check_response(response)
        return response

    @parser_response
    def object_list(self, bucket_name):
        """
        get all objects info of one user's bucket
        @param bucket_name: string
        """
        response = self._make_request('GET', bucket_name)
        self.check_response(response)
        return response

    @parser_response
    def object_get(self, bucket_name, object_name, local_file_path):
        """
        download an object of buket to local path
        @param bucket_name: string
        @param object_name: string
        @param local_file_path: string
        """
        response = self._make_request('GET', bucket_name, object_name)
        self._generate_file_from_response(response, local_file_path)
        self.check_response(response)
        return response

    def _generate_file_from_response(self, response, local_file_path):
        """
        generate file from response for method get_object
        @param response: HTTPResponse
        @param local_file_path: string

        """
        fp = open(local_file_path, 'wb')
        while True:
            data = response.read(BUFFER_SIZE)
            if len(data) > 0:
                fp.write(data)
            else:
                break
        if fp:
            fp.flush()
            fp.close()

    def _make_request(self, method, bucket_name='', key='', query_args={}, data=''):
        """
        make request and get response
        @param bucket_name:
        @param key: object name or other
        @param query_args: query params   eg. ?reName=newname&b=c
        @param headers: http header
        @param data: http body
        """
        headers, url_resource = self._generater_header({}, method, bucket_name, key)
        connection = httplib.HTTPConnection(self.jss_url)
        connection.request(method, url_resource, data, headers)
        response = connection.getresponse()

        return response

    def _make_request_upload_object(self, method, bucket_name='', key='', path=''):
        """
        make request and get response for method put_object 

        """
        headers, url_resource = self._generater_header({}, method, bucket_name, key, path)
        connection = httplib.HTTPConnection(self.jss_url)

        connection.putrequest(method, url_resource)

        for key in headers:
            connection.putheader(key, str(headers[key]))
        connection.endheaders()

        openfile = open(path, 'rb')
        while True:
            read_bytes = openfile.read(BUFFER_SIZE)
            if not read_bytes:
                break
            connection.send(read_bytes)

        response = connection.getresponse()
        return response

    def _query_args_to_string(self, query_args):
        """
        Combine url query strings
        @param query_args: url query arguments
        @return: url query string
        """

        pairs = []
        for key, value in query_args.items():
            piece = key
            if value != None:
                piece += "=%s" % urllib2.quote(str(value))
            pairs.append(piece)
        return '&'.join(pairs)

    def _generater_header(self, headers, method, bucket_name, key, path=''):
        """
        generater http header for method _make_request_put_object

        """
        http_verb = method
        url_resource = '/' + bucket_name
        if key != '':
            url_resource += '/' + key

        if method != 'GET':
            if path != '':
                extend_name = path.split('.')
                content_type = mime_type.get_type(extend_name[-1].lower())
                size = self._get_file_size(path)
                if size != 0:
                    headers['Content-Length'] = size
            else:
                content_type = 'application/json'
            if 'Content-Length' not in headers.keys():
                headers['Content-Length'] = 0
        else:
            content_type = 'application/json'

        current_date = datetime.datetime.utcnow().strftime(GMT_FORMAT)
        string_to_sign = self._get_string_to_sign(http_verb, '', content_type, current_date, url_resource)
        headers['AUTHORIZATION'] = self._get_token(string_to_sign)
        headers['Date'] = str(current_date)
#        if 'Content-Type' not in headers.keys():
        headers['Content-Type'] = content_type
        return headers, url_resource

    def _get_file_size(self, path):
        openfile = open(path, 'r')
        size = 0
        if openfile != None:
            openfile.seek(0, os.SEEK_END)
            size = openfile.tell()
            openfile.close()

        return size

    def _signatrue(self, string_to_sign):
        return base64.encodestring(hmac.new(str(self.secret_key),\
            string_to_sign, hashlib.sha1).digest()).strip()

    def _get_token(self, string_to_sign):
        signature = self._signatrue(string_to_sign)
        token = "jingdong" + " " + self.access_key + ":" + signature
        return token

    def _get_string_to_sign(self, http_verb,
                             content_md5,
                             content_type,
                             current_date,
                             url_resource):
        string_to_sign = http_verb + \
                         "\n" + content_md5 + \
                         "\n" + content_type + \
                         "\n" + str(current_date) + \
                         "\n" + url_resource
        return string_to_sign

    def setCheck_Result(self, check=True):
        self.check_result = check

    def check_response(self, response):
        if int(response.status) >= 400:
            body = response.read()
            if body:
                body = json.loads(body)
            raise exceptions.from_response(response, body)
