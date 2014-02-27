import uuid
import json
import unittest
from jssclient import httpclient

"""
192.168.12.24 
test/test
root/1qaz2wsx

ListAllBuckets:
{
    "Buckets": [
        {
            "CreationDate": "Wed, 26 Feb 2014 06:19:51 GMT", 
            "Name": "test", 
            "Location": ""
        }, 
        {
            "CreationDate": "Fri, 24 Jan 2014 07:44:19 GMT", 
            "Name": "jss", 
            "Location": "jd-storage-huabei-1"
        }, 
        {
            "CreationDate": "Wed, 26 Feb 2014 06:31:46 GMT", 
            "Name": "test-79c7a45d-e073-4f5b-b822-671bc8e03b18", 
            "Location": "jd-storage-huabei-1"
        }, 
        {
            "CreationDate": "Wed, 26 Feb 2014 06:32:12 GMT", 
            "Name": "test-180b23a7-368c-45b6-a1e2-dd979871eb56", 
            "Location": "jd-storage-huabei-1"
        }, 
        {
            "CreationDate": "Wed, 26 Feb 2014 06:32:20 GMT", 
            "Name": "test-c1c82b82-eaba-4c9a-8bf4-5fbf79048589", 
            "Location": "jd-storage-huabei-1"
        }, 
        {
            "CreationDate": "Wed, 26 Feb 2014 06:32:25 GMT", 
            "Name": "test-92c75eab-e12b-4ae8-b83f-d8c465a34616", 
            "Location": "jd-storage-huabei-1"
        }, 
        {
            "CreationDate": "Wed, 26 Feb 2014 06:32:29 GMT", 
            "Name": "test-2ae09f65-8af8-4def-a6fe-f103a570ad71", 
            "Location": "jd-storage-huabei-1"
        }
    ]
}

"""
config = {
        'hostname' : 'storage.jd.com',
        'jss_access_key': 'test',
        'jss_secret_key': 'test',
}


def gen_uuid():
    return str(uuid.uuid4())

def get_httpclient():
    return httpclient.HTTPClient(config['hostname'],
                                 config['jss_access_key'],
                                 config['jss_secret_key'],
                                 http_log_debug=False)


class HttpClientTestCase(unittest.TestCase):

    def setUp(self):
        self.cli = get_httpclient()

    def tearDown(self):
        print 'helloworld'

def list_buckets():
    cli = get_httpclient()
    ans = cli.get('/')
    print type(ans)
    for bucket in ans['Buckets']:
        print bucket['Name']

def create_buckets():
    cli = get_httpclient()
    ans = cli.put('/test-%s' % gen_uuid())
    print ans

def delete_buckets():
    cli = get_httpclient()
    ans = cli.delete('/test-2ae09f65-8af8-4def-a6fe-f103a570ad71')
    print ans

def list_objects():
    """
    {
    "MaxKeys": 1000, 
    "Prefix": null, 
    "HasNext": false, 
    "Name": "test", 
    "Marker": null, 
    "Delimiter": null, 
    "Contents": [
        {
            "LastModified": "Wed, 26 Feb 2014 05:52:29 GMT", 
            "ETag": "382be650c3aa2dbc806bc21cc61f1bf8", 
            "Key": "books/jack/chinese/test2.txt", 
            "Size": 68
        }, 
        {
            "LastModified": "Wed, 26 Feb 2014 05:52:35 GMT", 
            "ETag": "382be650c3aa2dbc806bc21cc61f1bf8", 
            "Key": "books/jack/chinese/test3.txt", 
            "Size": 68
        }, 
        {
            "LastModified": "Wed, 26 Feb 2014 05:52:38 GMT", 
            "ETag": "382be650c3aa2dbc806bc21cc61f1bf8", 
            "Key": "books/jack/chinese/test4.txt", 
            "Size": 68
        }, 
        {
            "LastModified": "Wed, 26 Feb 2014 05:52:10 GMT", 
            "ETag": "382be650c3aa2dbc806bc21cc61f1bf8", 
            "Key": "books/jack/english/test.txt", 
            "Size": 68
        }, 
        {
            "LastModified": "Wed, 26 Feb 2014 07:12:43 GMT", 
            "ETag": "e59955d9b5c2644a8e1498d30cd004f3", 
            "Key": "make_data.py", 
            "Size": 2460
        }, 
        {
            "LastModified": "Wed, 26 Feb 2014 05:51:53 GMT", 
            "ETag": "382be650c3aa2dbc806bc21cc61f1bf8", 
            "Key": "readme.txt", 
            "Size": 68
        }
    ], 
    "CommonPrefixes": []
}
    """
    cli = get_httpclient()
    ans = cli.get('/test')
    keys = ['HasNext', 'Name', 'Prefix',
            'MaxKeys', 'Delimiter', 'Marker',
            'Contents', 'CommonPrefixes']
    for ky in keys:
        print '%s\t%s' % (ky, ans[ky])
    for content in ans['Contents']:
        print content.keys()
        print content['Key']


def quick_object_put(bucket_name, object_name):
    """
    {
        "Bucket": "jss", 
        "UploadId": "A3C3D598BDB0E114", 
        "Key": "quick-object-put"
    }
    """
    cli = get_httpclient()
    resource = '/%s/%s?uploads' % (bucket_name, object_name)
    ans = cli.post(resource)
    upload_id = ans['UploadId']
    return upload_id


def part_upload(bucket_name, object_name, upload_id):
    cli = get_httpclient()
    part_dict = {'Part': []}
    parts = []
    with open('/home/hz/qpress-dic/aio.hpp', 'rb') as  fd:
        part_number = 1
        while True:
            data = fd.read(128)
            if not data:
                break
            # print len(data)
            resource = '/%s/%s?partNumber=%s&uploadId=%s' % (bucket_name, object_name, part_number, upload_id)
            headers = {'Content-Length': len(data)}
            conn = cli.get_request_conn('PUT', resource, headers)
            conn.send(data)
            resp = conn.getresponse()
            headers = dict(resp.getheaders())
            if resp.status >= 400:
                raise Exception('Error: %s' % resp.read())

            parts.append({'PartNumber': part_number,
                          'ETag': headers['etag'].strip('"')})

            body = resp.read()
            print '###', body, '##'
            # body = json.loads(resp.read())
            print type(headers), type(body)
            part_number += 1

    part_dict['Part'] = parts
    return part_dict

def complete_upload(bucket_name, object_name, upload_id, part_dict):
    resource = '/%s/%s?uploadId=%s' % (bucket_name, object_name, upload_id)
    cli = get_httpclient()
    ans = cli.post(resource, body=sorted(part_dict))
    print json.dumps(ans, indent=4)

def abort_multipart_upload(bucket_name, object_name, upload_id):
    resource = '/%s/%s?uploadId=%s' % (bucket_name, object_name, upload_id)
    cli = get_httpclient()
    ans = cli.delete(resource)
    print 'Abort Multipart upload:' , ans


def list_parts(bucket_name, object_name, upload_id):
    """
    {
        "UploadId": "A3C3D598BDB0E114", 
        "Part": [], 
        "Bucket": "jss", 
        "Key": "quick-object-put"
    }
    """
    resource = '/%s/%s?uploadId=%s' % (bucket_name, object_name, upload_id)
    cli = get_httpclient()
    ans = cli.get(resource)
    print json.dumps(ans, indent=4)


def list_multipart_uploads(bucket_name):
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
    resource = '/%s?uploads' % (bucket_name)
    cli = get_httpclient()
    ans = cli.get(resource)
    print json.dumps(ans, indent=4)


def object_get_range(bucket_name, object_name, io_buffer_size=64 * 1024):
    # headers['Range'] = 'Bytes=' + str(start_pos) + '-' + str(end_pos)
    resource = '/%s/%s' % (bucket_name, object_name)
    cli = get_httpclient()
    conn = cli.get_request_conn('GET', resource)
    response = conn.getresponse()
    print response.status, dict(response.getheaders())
    headers = dict(response.getheaders())
    content_length = int(headers['content-length'])
    print 'Content-Length from Server Headers:%s' % content_length
    response.close()
    with open('/home/hz/test/index.html', 'w') as fd:
        start_pos = 0
        end_pos = io_buffer_size
        while start_pos < content_length:
            cli = get_httpclient()
            bytes_str = None
            print 'DEBUG:#', end_pos, content_length, end_pos <= content_length
            if end_pos >= content_length:
                print '*' * 32
                bytes_str = 'bytes=%s-' % start_pos
            else:
                bytes_str = 'bytes=%s-%s' % (start_pos, end_pos - 1)
            headers = {'Range': bytes_str}
            print bytes_str, content_length
            conn = cli.get_request_conn('GET', resource, headers)
            resp = conn.getresponse()
            if resp.status >= 400:
                raise Exception('Error:%s' % resp.read())
            data = resp.read()
            read_size = len(data)
            if read_size <= 0:
                break
            print '###Get data from server:%s' % read_size
            fd.write(data)
            start_pos = end_pos
            end_pos += read_size
            resp.close()


def main():
    bucket_name = 'jss'
    object_name = 'quick-object-put'
    upload_id = 'A3C3D598BDB0E114'
    object_get_range('jss', 'index')
    list_multipart_uploads(bucket_name)
    list_parts(bucket_name, object_name, upload_id)

if __name__ == '__main__':
    main()
