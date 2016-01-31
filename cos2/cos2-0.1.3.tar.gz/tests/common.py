import os
import random
import string
import unittest
import time
import tempfile

import cos2


COS_ID = 'AccessKeyId'
COS_SECRET =  'AccessKeySecret'
COS_ENDPOINT ='http://cos-beta.chinac.com'
COS_BUCKET =  'BucketName'
COS_CNAME = ''


def random_string(n):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n))


def random_bytes(n):
    return cos2.to_bytes(random_string(n))


def delete_keys(bucket, key_list):
    if not key_list:
        return

    n = 100
    grouped = [key_list[i:i+n] for i in range(0, len(key_list), n)]
    for g in grouped:
        bucket.batch_delete_objects(g)

def delete_bucket(bucket):
    bucket.delete_bucket()

class CosTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(CosTestCase, self).__init__(*args, **kwargs)
        self.bucket = None
        self.prefix = random_string(12)
        self.default_connect_timeout = cos2.defaults.connect_timeout

    def setUp(self):
        cos2.defaults.connect_timeout = self.default_connect_timeout

        self.bucket = cos2.Bucket(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT, COS_BUCKET)
        self.bucket.create_bucket()
        self.key_list = []
        self.temp_files = []

    def tearDown(self):
        for temp_file in self.temp_files:
            os.remove(temp_file)
        delete_keys(self.bucket, self.key_list)
        delete_bucket(self.bucket)


    def random_key(self, suffix=''):
        key = self.prefix + random_string(12) + suffix
        self.key_list.append(key)

        return key

    def _prepare_temp_file(self, content):
        fd, pathname = tempfile.mkstemp(suffix='test-upload')

        os.write(fd, content)
        os.close(fd)

        self.temp_files.append(pathname)
        return pathname

    def retry_assert(self, func):
        for i in range(5):
            if func():
                return
            else:
                time.sleep(i+2)

        self.assertTrue(False)
