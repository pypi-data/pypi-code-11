# -*- coding: utf-8 -*-

import  cos2
import uuid
if __name__ == '__main__':

    accessKeyId = 'AccessKeyId'
    accessKeySecret = 'AccessKeySecret'
    bucket_name = 'BucketName'
    endpoint = 'http://cos-beta.chinac.com'

    bucketName = 'my-first-cos-bucket-' + str(uuid.uuid1())
    objectName = 'my-first-cos-object.txt'

# print bucketName
    print '==========================================='
    print 'Getting Started with COS SDK for Python'
    print '===========================================\n'

# Init COS Python SDK
    auth = cos2.Auth(accessKeyId, accessKeySecret)
    bucket = cos2.Bucket(auth, endpoint, bucketName)

# Create a new COS PublicRead bucket
    print 'Creating bucket ' + bucketName
# bucket.create_bucket(cos2.BUCKET_ACL_PUBLIC_READ)
    bucket.create_bucket()

# List the buckets in your account
    print 'Listing buckets'
    service = cos2.Service(auth, endpoint, connect_timeout=30)
    for bucketInfo in service.list_buckets().buckets:
        print ' - ' + bucketInfo.name

# Upload an object to your bucket
    print 'Uploading a new object to COS from memory'
    content = 'Thank you for using COS SDK for Python'
    bucket.put_object(objectName, content)


# Determine whether an object residents in your bucket
    exist = bucket.object_exists(objectName)
    print exist
    print(bucket.get_object(objectName).read())



