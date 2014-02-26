import uuid
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
                                 http_log_debug=True)


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


def put_object():
    cli = get_httpclient()
    # cli.put(resource, body, headers, readed)


def main():
    list_buckets()
    # list_objects()
    # create_buckets()
    # print '*' * 80
    # list_buckets()

    # print '*' * 80
    # delete_buckets()


    # print '*' * 80
    # list_buckets()

    # cli = get_httpclient()
    # ans = cli.get('/', readed=True)
    # for bucket in ans['Buckets']:
    #    print bucket['Name']
    # cli.put('/huzheng-%s' % gen_uuid())
    pass

if __name__ == '__main__':
    main()
