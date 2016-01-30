# -*- coding: utf-8 -*-

"""
cos2.iterators
~~~~~~~~~~~~~~

该模块包含了一些易于使用的迭代器，可以用来遍历Bucket、文件、分片上传等。
"""

from .models import MultipartUploadInfo, SimplifiedObjectInfo
from .exceptions import ServerError

from . import defaults


class _BaseIterator(object):
    def __init__(self, marker, max_retries):
        self.is_truncated = True
        self.next_marker = marker

        max_retries = defaults.get(max_retries, defaults.request_retries)
        self.max_retries = max_retries if max_retries > 0 else 1

        self.entries = []

    def _fetch(self):
        raise NotImplemented    # pragma: no cover

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.entries:
                return self.entries.pop(0)

            if not self.is_truncated:
                raise StopIteration

            self.fetch_with_retry()

    def next(self):
        return self.__next__()

    def fetch_with_retry(self):
        for i in range(self.max_retries):
            try:
                self.is_truncated, self.next_marker = self._fetch()
            except ServerError as e:
                if e.status // 100 != 5:
                    raise

                if i == self.max_retries - 1:
                    raise
            else:
                return


class BucketIterator(_BaseIterator):
    """遍历用户Bucket的迭代器。

    每次迭代返回的是 :class:`SimplifiedBucketInfo <cos2.models.SimplifiedBucketInfo>` 对象。

    :param service: :class:`Service <cos2.Service>` 对象
    :param prefix: 只列举匹配该前缀的Bucket
    :param marker: 分页符。只列举Bucket名字典序在此之后的Bucket
    :param max_keys: 每次调用 `list_buckets` 时的max_keys参数。注意迭代器返回的数目可能会大于该值。
    """
    def __init__(self, service, prefix='', marker='', max_keys=100, max_retries=None):
        super(BucketIterator, self).__init__(marker, max_retries)
        self.service = service
        self.prefix = prefix
        self.max_keys = max_keys

    def _fetch(self):
        result = self.service.list_buckets()
        self.entries = result.buckets

        return result.is_truncated, result.next_marker


class ObjectIterator(_BaseIterator):
    """遍历Bucket里文件的迭代器。

    每次迭代返回的是 :class:`SimplifiedObjectInfo <cos2.models.SimplifiedObjectInfo>` 对象。
    当 `SimplifiedObjectInfo.is_prefix()` 返回True时，表明是公共前缀（目录）。

    :param bucket: :class:`Bucket <cos2.Bucket>` 对象
    :param prefix: 只列举匹配该前缀的文件
    :param delimiter: 目录分隔符
    :param marker: 分页符
    :param max_keys: 每次调用 `list_objects` 时的max_keys参数。注意迭代器返回的数目可能会大于该值。
    """
    def __init__(self, bucket, prefix='', delimiter='', marker='', max_keys=100, max_retries=None):
        super(ObjectIterator, self).__init__(marker, max_retries)

        self.bucket = bucket
        self.prefix = prefix
        self.delimiter = delimiter
        self.max_keys = max_keys

    def _fetch(self):
        result = self.bucket.list_objects(prefix=self.prefix,
                                          delimiter=self.delimiter,
                                          marker=self.next_marker,
                                          max_keys=self.max_keys)
        self.entries = result.object_list + [SimplifiedObjectInfo(prefix, None, None, None, None)
                                             for prefix in result.prefix_list]
        self.entries.sort(key=lambda obj: obj.key)


        return result.is_truncated, result.next_marker


class MultipartUploadIterator(_BaseIterator):
    """遍历Bucket里未完成的分片上传。

    每次返回 :class:`MultipartUploadInfo <cos2.models.MultipartUploadInfo>` 对象。
    当 `MultipartUploadInfo.is_prefix()` 返回True时，表明是公共前缀（目录）。

    :param bucket: :class:`Bucket <cos2.Bucket>` 对象
    :param prefix: 仅列举匹配该前缀的文件的分片上传
    :param delimiter: 目录分隔符
    :param key_marker: 文件名分页符
    :param upload_id_marker: 分片上传ID分页符
    :param max_uploads: 每次调用 `list_multipart_uploads` 时的max_uploads参数。注意迭代器返回的数目可能会大于该值。
    """
    def __init__(self, bucket,upload_id_marker='',
                 max_uploads=1000, max_retries=None):
        super(MultipartUploadIterator, self).__init__(upload_id_marker, max_retries)

        self.bucket = bucket
        self.next_upload_id_marker = upload_id_marker
        self.max_uploads = max_uploads

    def _fetch(self):
        result = self.bucket.list_multipart_uploads(upload_id_marker=self.next_upload_id_marker,
                                                    max_uploads=self.max_uploads)
        self.entries = result.upload_list
        self.entries.sort(key=lambda u: u.key)

        self.next_upload_id_marker = result.next_upload_id_marker
        return result.is_truncated, result.next_upload_id_marker


class PartIterator(_BaseIterator):
    """遍历一个分片上传会话中已经上传的分片。

    :param bucket: :class:`Bucket <cos2.Bucket>` 对象
    :param key: 文件名
    :param upload_id: 分片上传ID
    :param marker: 分页符
    :param max_parts: 每次调用 `list_parts` 时的max_parts参数。注意迭代器返回的数目可能会大于该值。
    """
    def __init__(self, bucket, key, upload_id,
                 marker='0', max_parts=1000, max_retries=None):
        super(PartIterator, self).__init__(marker, max_retries)

        self.bucket = bucket
        self.key = key
        self.upload_id = upload_id
        self.max_parts = max_parts

    def _fetch(self):
        result = self.bucket.list_parts(self.key, self.upload_id,
                                        marker=self.next_marker,
                                        max_parts=self.max_parts)
        self.entries = result.parts

        return result.is_truncated, result.next_marker

