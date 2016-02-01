#
# Copyright 2015, Couchbase, Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json

from couchbase._pyport import basestring
from couchbase.views.iterator import AlreadyQueriedError
from couchbase.exceptions import CouchbaseError, NotSupportedError


class N1QLError(CouchbaseError):
    @property
    def n1ql_errcode(self):
        return self.objextra['code']


CONSISTENCY_REQUEST = 'request_plus'
"""
For use with :attr:`~.N1QLQuery.consistency`, will ensure that query
results always reflect the latest data in the server
"""

CONSISTENCY_NONE = 'none'
"""
For use with :attr:`~.N1QLQuery.consistency`, will allow cached
values to be returned. This will improve performance but may not
reflect the latest data in the server.
"""


class N1QLQuery(object):
    def __init__(self, query, *args, **kwargs):
        """
        Create an N1QL Query object. This may be passed as the
        `params` argument to :class:`N1QLRequest`.

        :param query: The query string to execute
        :param args: Positional placeholder arguments. These satisfy
            the placeholder values for positional placeholders in the
            query string, such as ``$1``, ``$2`` and so on.
        :param kwargs: Named placeholder arguments. These satisfy
            named placeholders in the query string, such as
            ``$name``, ``$email`` and so on. For the placeholder
            values, omit the leading sigil (``$``).

        Use positional parameters::

            q = N1QLQuery('SELECT * FROM `travel-sample` '
                          'WHERE type=$1 AND id=$2',
                          'airline', 0)

            for row in cb.n1ql_query(q):
                print 'Got', row

        Use named parameters::

            q = N1QLQuery('SELECT * FROM `travel-sample` '
                          'WHERE type=$type AND id=$id',
                           type='airline', id=0)
            for row in cb.n1ql_query(q):
                print 'Got', row


        When using placeholders, ensure that the placeholder value is
        the *unserialized* (i.e. native) Python value, not the JSON
        serialized value. For example the query
        ``SELECT * FROM products WHERE tags IN ["sale", "clearance"]``
        can be rewritten using placeholders:

        Correct::

            N1QLQuery('SELECT * FROM products WHERE tags IN $1',
                      ['sale', 'clearance'])

        Incorrect::

            N1QLQuery('SELECT * FROM products WHERE tags IN $1',
                      "[\\"sale\\",\\"clearance\\"]")

        Since the placeholders are serialized to JSON internally anyway.
        """

        self._adhoc = True
        self._body = {'statement': query}
        if args:
            self._add_pos_args(*args)
        if kwargs:
            self._set_named_args(**kwargs)

    def _set_named_args(self, **kv):
        """
        Set a named parameter in the query. The named field must
        exist in the query itself.

        :param kv: Key-Value pairs representing values within the
            query. These values should be stripped of their leading
            `$` identifier.

        """
        for k in kv:
            self._body['${0}'.format(k)] = kv[k]
        return self

    def _add_pos_args(self, *args):
        """
        Set values for *positional* placeholders (``$1,$2,...``)

        :param args: Values to be used
        """
        arg_array = self._body.setdefault('args', [])
        arg_array.extend(args)

    def set_option(self, name, value):
        """
        Set a raw option in the query. This option is encoded
        as part of the query parameters without any client-side
        verification. Use this for settings not directly exposed
        by the Python client.

        :param name: The name of the option
        :param value: The value of the option
        """
        self._body[name] = value

    @property
    def statement(self):
        return self._body['statement']

    @property
    def consistency(self):
        """
        Sets the consistency level.

        :see: :data:`CONSISTENCY_NONE`, :data:`CONSISTENCY_REQUEST`
        """
        return self._body.get('scan_consistency', CONSISTENCY_NONE)

    @consistency.setter
    def consistency(self, value):
        self._body['scan_consistency'] = value

    def _add_scanvec(self, mutinfo):
        """
        Internal method used to specify a scan vector.
        :param mutinfo: A tuple in the form of
            `(vbucket id, vbucket uuid, mutation sequence)`
        """
        vb, uuid, seq = mutinfo
        self._body.setdefault('scan_vector', {})[vb] = {
            'value': seq,
            'guard': str(uuid)
        }
        self.consistency = 'at_plus'

    def consistent_with_ops(self, *ops, **kwargs):
        """
        Ensure results reflect consistency of one or more mutations.
        This is similar to setting :attr:`consistency` to
        :data:`CONSISTENCY_REQUEST`, but is more optimal as the query
        will use cached data, *except* when the given mutation(s) are
        concerned. This option is useful for use patterns when an
        application has just performed a mutation, and wishes to
        perform a query in which the newly-performed mutation
        should reflect on the query results.

        :param ops: One or more :class:`~.OperationResult` objects
        :param bool quiet: Whether to suppress throwing an exception
            if one or more operations are missing mutation information.
        :raise: :exc:`~.NotSupportedError` if one of the mutations

        .. note::

            This feature requires Couchbase Server 4.0 or greater,
            and also requires that `fetch_mutation_tokens=true`
            be specified in the connection string when creating
            a :class:`~couchbase.bucket.Bucket`


        .. code-block:: python

            cb = Bucket('couchbase://localhost/default?fetch_mutation_tokens=true')

            rvs = cb.upsert_multi({
                'foo': {'type': 'user', 'value': 'a foo value'},
                'bar': {'type': 'user', 'value': 'a bar value'}
            })

            nq = N1QLQuery('SELECT type, value FROM default WHERE type="user"')
            nq.consistent_with_ops(*rvs.values())
            for row in cb.n1ql_query(nq):
                # ...


        .. seealso:: :meth:`~consistent_with_all`
        """
        for op in ops:
            if not op._mutinfo:
                if kwargs.get('quiet'):
                    continue
                raise NotSupportedError.pyexc(
                    "OperationResult object missing mutation information. "
                    "Ensure that `fetch_mutation_tokens=true` was specified "
                    "in the connection string")
            self._add_scanvec(op._mutinfo)

    def consistent_with_all(self, bucket):
        """
        Ensures the query result is consistent with all prior
        mutations performed by a given bucket.

        Using this function is equivalent to keeping track of all
        mutations performed by the given bucket, and passing them to
        :meth:`~consistent_with_ops`

        :param bucket: A :class:`~couchbase.bucket.Bucket` object
            used for the mutations
        """
        for mt in bucket._mutinfo():
            self._add_scanvec(mt)

    # TODO: I really wish Sphinx were able to automatically
    # document instance vars
    @property
    def adhoc(self):
        """
        A non-`adhoc` query can be internally optimized so that repeated
        executions of the same query can be quicker. If this query is issued
        repeatedly in your application, then you should set this property to
        `False`.

        Note that this optimization involves an up-front "preparation"
        cost, and should only be used for queries that are issued multiple
        times.
        """
        return self._adhoc

    @adhoc.setter
    def adhoc(self, arg):
        self._adhoc = arg

    @property
    def timeout(self):
        """
        Optional per-query timeout. If set, this will limit the amount
        of time in which the query can be executed and waited for.

        .. note::

            The effective timeout for the query will be either this property
            or the value of :attr:`couchbase.bucket.Bucket.n1ql_timeout`
            property, whichever is *lower*.

        .. seealso:: couchbase.bucket.Bucket.n1ql_timeout
        """
        value = self._body.get('timeout', '0s')
        value = value[:-1]
        return float(value)

    @timeout.setter
    def timeout(self, value):
        if not value:
            self._body.pop('timeout', 0)
        else:
            value = float(value)
            self._body['timeout'] = '{0}s'.format(value)

    @property
    def encoded(self):
        """
        Get an encoded representation of the query.

        This is used internally by the client, and can be useful
        to debug queries.
        """
        return json.dumps(self._body)

    def __repr__(self):
        return ('<{cls} stmt={stmt} at {oid}>'.format(
            cls=self.__class__.__name__,
            stmt=repr(self._body),
            oid=id(self)))


class N1QLRequest(object):
    def __init__(self, params, parent, row_factory=lambda x: x):
        """
        Object representing the execution of the request on the
        server.

        .. warning::

            You should typically not call this constructor by
            yourself, rather use the :meth:`~.Bucket.n1ql_query`
            method (or one of its async derivatives).

        :param params: An :class:`N1QLQuery` object.
        :param parent: The parent :class:`~.couchbase.bucket.Bucket` object
        :param row_factory: Callable which accepts the raw dictionary
            of each row, and can wrap them in a customized class.
            The default is simply to return the dictionary itself.

        To actually receive results of the query, iterate over this
        object.
        """
        if isinstance(params, basestring):
            params = N1QLQuery(params)

        self._params = params
        self._parent = parent
        self.row_factory = row_factory
        self.errors = []
        self._mres = None
        self._do_iter = True
        self.__raw = False
        self.__meta_received = False

    def _start(self):
        if self._mres:
            return

        self._mres = self._parent._n1ql_query(self._params.encoded,
                                              not self._params.adhoc)
        self.__raw = self._mres[None]

    @property
    def raw(self):
        return self.__raw

    @property
    def meta(self):
        """
        Get metadata from the query itself. This is guaranteed to only
        return a Python dictionary.

        Note that if the query failed, the metadata might not be in JSON
        format, in which case there may be additional, non-JSON data
        which can be retrieved using the following

        .. code-block::

            raw_meta = req.raw.value

        :return: A dictionary containing the query metadata
        """
        if not self.__meta_received:
            raise RuntimeError(
                'This property only valid once all rows are received!')

        if isinstance(self.raw.value, dict):
            return self.raw.value
        return {}

    def _clear(self):
        del self._parent
        del self._mres

    def _handle_meta(self, value):
        self.__meta_received = True
        if not isinstance(value, dict):
            return
        if 'errors' in value:
            for err in value['errors']:
                raise N1QLError.pyexc('N1QL Execution failed', err)

    def _process_payload(self, rows):
        if rows:
            return [self.row_factory(row) for row in rows]

        elif self.raw.done:
            self._handle_meta(self.raw.value)
            self._do_iter = False
            return []
        else:
            # We can only get here if another concurrent query broke out the
            # event loop before we did.
            return []

    def execute(self):
        """
        Execute the statement and raise an exception on failure.

        This method is useful for statements which modify data or
        indexes, where the application does not need to extract any
        data, but merely determine success or failure.
        """
        for _ in self:
            pass

        return self

    def get_single_result(self):
        """
        Execute the statement and return its single result.

        This should only be used on statements which are intended to
        return only a single result.

        :return: The single result, as encapsulated by the
            `row_factory`
        """
        for r in self:
            return r

    def __iter__(self):
        if not self._do_iter:
            raise AlreadyQueriedError()

        self._start()
        while self._do_iter:
            raw_rows = self.raw.fetch(self._mres)
            for row in self._process_payload(raw_rows):
                yield row
