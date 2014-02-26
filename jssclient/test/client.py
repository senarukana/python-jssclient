'''
Created on Dec 31, 2013

@author: hz
'''

import uuid
from jssclient import client
from jssclient.test.config import config

def get_client():
    return client.Client(config['hostname'],
                         config['jss_access_key'],
                         config['jss_secret_key'],
                         http_log_debug=False)

def gen_uuid():
    return str(uuid.uuid4())

def test_object_put():
    cli = get_client()
    cli.object_put('test',
                   'make_data.py-%s' % gen_uuid(),
                   file_path='/home/hz/make_data.py')


def test_object_get():
    cli = get_client()
    cli.object_get('test', 'make_data.py', '/home/hz/test/good.py')


def test_object_list():
    cli = get_client()
    ans = cli.object_list('test', marker=1, max_keys=10)
    for i in ans['Contents']:
        print i
    print len(ans['Contents'])


def main():
    test_object_list()
    # for _ in range(1501):
    #    test_object_put()
    # test_object_get()

if __name__ == '__main__':
    main()
