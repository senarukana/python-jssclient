import os

from jssclient import mime_type
from jssclient import exceptions
from jssclient import httpclient


class Client:
    """Jiongdong Cloud Storage Service SDK"""

    def __init__(self, hostname, access_key, secret_key,
                 http_log_debug=False,
                 io_buffer_size=64 * 1024,
                 chunck_size=16 * 1024 * 1024):
        self.conn = httpclient.HTTPClient(hostname,
                                          access_key,
                                          secret_key,
                                          http_log_debug=http_log_debug)
        self.io_buffer_size = io_buffer_size
        self.chunck_size = chunck_size

    def bucket_create(self, bucket_name):
        resource = '/%s' % bucket_name
        return self.conn.put(resource=resource)

    def bucket_delete(self, bucket_name):
        resource = '/%s' % bucket_name
        return self.conn.delete(resource=resource)

    def bucket_list(self):
        return self.conn.get(resource='/')

    def object_put(self, bucket_name, object_name, file_path=None):
        resource = '/%s/%s' % (bucket_name, object_name)
        if not file_path:
            file_path = object_name
        headers = {}
        headers['Content-Length'] = os.path.getsize(file_path)
        suffix = file_path.rpartition('.')[2].lower()
        headers['Content-Type'] = mime_type.get_type(suffix)

        conn = self.conn.get_request_conn('PUT', resource, headers)
        with open(file_path, 'rb') as fd:
            while True:
                data = fd.read(self.io_buffer_size)
                if not data:
                    break
                print len(data)
                conn.send(data)
        response = conn.getresponse()
        print response.status
        if response.status >= 400:
            raise exceptions.from_response(response.status, body=response.read())
        print response.read()

    def object_delete(self, bucket_name, object_name):
        resource = '/%s/%s' % (bucket_name, object_name)
        return self.conn.delete(resource)

    def object_list(self, bucket_name, marker=None, max_keys=None, prefix=None, delimiter=None):
        kwargs = {}
        if marker:
            kwargs['marker'] = marker
        if  max_keys:
            kwargs['max_keys'] = max_keys
        if prefix:
            kwargs['prefix'] = prefix
        if delimiter:
            kwargs['delimiter'] = delimiter
        resource = '/%s' % bucket_name
        return self.conn.get(resource, kwargs=kwargs)

    def object_get_conn(self, bucket_name, object_name):
        resource = '/%s/%s' % (bucket_name, object_name)
        return self.conn.get(resource, readed=False)

    def object_get(self, bucket_name, object_name, file_path=None):
        conn = self.object_get_conn(bucket_name, object_name)
        if not file_path:
            file_path = object_name
        with open(file_path, 'w') as fd:
            while True:
                data = conn.read(self.io_buffer_size)
                if not data or len(data) == 0:
                    break
                fd.write(data)
            conn.close()
