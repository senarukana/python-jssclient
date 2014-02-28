import os
import eventlet

from jssclient import mime_type
from jssclient import exceptions
from jssclient import httpclient



class Client:
    """Jiongdong Cloud Storage Service SDK"""

    def __init__(self, hostname, access_key, secret_key,
                 http_log_debug=True,
                 io_buffer_size=64 * 1024,
                 chunck_size=16 * 1024 * 1024):
        self.hostname = hostname
        self.access_key = access_key
        self.secret_key = secret_key
        self.http_log_debug = http_log_debug
        self.conn = httpclient.HTTPClient(hostname,
                                          access_key,
                                          secret_key,
                                          http_log_debug=http_log_debug)
        self.io_buffer_size = io_buffer_size
        self.chunck_size = chunck_size

    def new_httpclient(self):
        return httpclient.HTTPClient(self.hostname,
                                     self.access_key,
                                     self.secret_key,
                                     self.http_log_debug)

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

    def big_object_put(self, bucket_name, object_name,
                       file_path=None, thread_size=8,
                       io_buffer_size=128 * 1024 * 1024):
        if not file_path:
            file_path = object_name
        total_size = os.path.getsize(file_path)
        # initialize multi-part upload
        upload_id = self.init_multipart_upload(bucket_name, object_name)

        parts = []

        # Inner Method
        def put_piece(start_pos, end_pos, part_id, data):
            if end_pos >= total_size:
                end_pos = total_size
            print 'bytes=%s-%s(%s)' % (start_pos, end_pos, part_id)
            part = self.upload_part(bucket_name, object_name,
                                    upload_id, part_id, data)
            parts.append(part)

        # divide file and upload in a green pool
        try:
            start_pos = 0
            end_pos = io_buffer_size
            # Create a new green pool
            green_pool = eventlet.GreenPool(thread_size)
            part_index = 0
            with open(file_path, 'rb') as fd:
                while start_pos < total_size:
                    data = fd.read(end_pos - start_pos)
                    green_pool.spawn(put_piece, start_pos,
                                     end_pos, part_index, data)
                    part_index += 1
                    start_pos = end_pos
                    end_pos += io_buffer_size
            parts_dict = {'Part': parts}
        except:
            # abort multi-part upload
            self.abort_multipart_upload(bucket_name, object_name, upload_id)
            raise
        else:
            # wait all green thread finished
            green_pool.waitall()
            # complete multi-part upload.
            self.complete_multipart_upload(bucket_name, object_name,
                                           upload_id, parts_dict)

    def big_object_get(self, bucket_name, object_name,
                       file_path=None, thread_size=4,
                       io_buffer_size=32 * 1024 * 124):
        if not file_path:
            file_path = object_name

        if os.path.exists(file_path): os.remove(file_path)

        # Get the total length of the big object
        resource = '/%s/%s' % (bucket_name, object_name)
        conn = self.conn.get_request_conn('GET', resource)
        response = conn.getresponse()
        if response.status >= 400:
            raise exceptions.from_response(response.status,
                                           body=response.read())
        content_length = int(dict(response.getheaders())['content-length'])

        # Inner Method, Download a io_buffer_size piece of data and write file.
        def get_piece(start_pos, end_pos):
            if end_pos >= content_length:
                bytes_str = 'bytes=%s-' % start_pos
            else:
                bytes_str = 'bytes=%s-%s' % (start_pos, end_pos - 1)
            headers = {'Range': bytes_str}
            print bytes_str
            cli = self.new_httpclient()
            cli_conn = cli.get_request_conn('GET', resource, headers)
            resp = cli_conn.getresponse()
            if resp.status >= 400:
                raise exceptions.from_response(resp.status, resp.read())
            data = resp.read()
            data_size = len(data)
            if data_size <= 0:
                return
            with open(file_path, 'awb') as fd:
                fd.seek(start_pos)
                fd.write(data)
            resp.close()

        # start position, end position
        green_pool = eventlet.GreenPool(thread_size)
        start_pos = 0
        end_pos = io_buffer_size
        while start_pos < content_length:
            green_pool.spawn(get_piece, start_pos, end_pos)
            start_pos = end_pos
            end_pos += io_buffer_size

        # Wait all green finished
        green_pool.waitall()
        local_size = os.path.getsize(file_path)
        error_msg = 'Size of local object(%s bytes) is not different from'\
        ' the size of remote jss object(%s bytes)' % (local_size,
                                                      content_length)
        assert local_size == content_length, error_msg


    def init_multipart_upload(self, bucket_name, object_name):
        resource = '/%s/%s?uploads' % (bucket_name, object_name)
        return self.conn.post(resource)['UploadId']

    def upload_part(self, bucket_name, object_name, upload_id, part_id, data):
        resrc_format = '/%s/%s?partNumber=%s&uploadId=%s'
        resource = resrc_format % (bucket_name, object_name,
                                   part_id, upload_id)
        headers = {'Content-Length': len(data)}
        conn = self.conn.get_request_conn('PUT', resource , headers)
        conn.send(data)
        resp = conn.getresponse()
        if resp.status >= 400:
            raise exceptions.from_response(resp.status, resp.read())
        etag = dict(resp.getheaders())['etag'].strip('"')
        resp.close()
        return {'PartNumber': part_id,
                'ETag': etag}

    def complete_multipart_upload(self, bucket_name,
                                  object_name,
                                  upload_id,
                                  parts_dict):
        """
        {
            "ETag": "d25ebb012cdbb28a3f309ea565c56cea", 
            "Bucket": "liningbo", 
            "Key": "testObject"
        }
        """
        resource = '/%s/%s?uploadId=%s' % (bucket_name,
                                           object_name,
                                           upload_id)
        parts = parts_dict['Part']
        parts_dict['Part'] = sorted(parts, key=lambda x: x['PartNumber'])
        return self.conn.post(resource, body=parts_dict)


    def abort_multipart_upload(self, bucket_name, object_name, upload_id):
        resource = '/%s/%s?uploadId=%s' % (bucket_name, object_name, upload_id)
        self.conn.delete(resource)

    def list_parts(self, bucket_name, object_name, upload_id):
        """
        {
            "UploadId": "A3C3D598BDB0E114", 
            "Part": [], 
            "Bucket": "jss", 
            "Key": "quick-object-put"
        }
        """
        resource = '/%s/%s?uploadId=%s' % (bucket_name, object_name, upload_id)
        return self.conn.get(resource)

    def list_multipart_uploads(self, bucket_name):
        """
        {
            "Prefix": null, 
            "Bucket": "jss", 
            "Upload": [
                {
                    "UploadId": "AA2C3A6634CA4746", 
                    "Initiated": "Thu, 27 Feb 2014 02:55:36 GMT", 
                    "Key": "oracle-jdk.tar.gz"
                }, 
                {
                    "UploadId": "A3C3D598BDB0E114", 
                    "Initiated": "Thu, 27 Feb 2014 02:42:51 GMT", 
                    "Key": "quick-object-put"
                }
            ]
        }
        """
        resource = '/%s?uploads' % bucket_name
        return self.conn.get(resource)
