# -*- coding: utf-8 -*-

"""
    aerate.io.base
    ~~~~~~~~~~~
    Standard interface implemented by Aerate data layers.
    :copyright: (c) 2016 by Arable Labs, Inc.
    :license: BSD, see LICENSE for more details.
"""


class ConnectionException(Exception):
    """ Raised when DataLayer subclasses cannot find/activate to their
    database connection.
    :param driver_exception: the original exception raised by the source db
                             driver
    """
    def __init__(self, driver_exception=None):
        self.driver_exception = driver_exception

    def __str__(self):
        msg = ("Error initializing the driver. Make sure the database server"
               "is running. ")
        if self.driver_exception:
            msg += "Driver exception: %s" % repr(self.driver_exception)
        return msg


class DataLayer(object):
    """ Base data layer class. Defines the interface that actual data-access
    classes, being subclasses, must implement.

    """
    def __init__(self):
        self.driver = None
        self.init_driver()

    def init_driver(self):
        """ This is where you want to initialize the db driver so it will be
        alive through the whole instance lifespan.
        """
        raise NotImplementedError

    def retrieve(self, resource, req):
        """ Retrieves a set of documents (rows), matching the current request.
        Consumed when a request hits a collection/document endpoint
        (`/pets/`).
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the db collection/table and base query (filter), if
                         any.
        :param req: an instance of ``aerate.utils.ParsedRequest``. Contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). Be warned that `where` and `sort` expresions will
                    need proper parsing, according to the syntax that you want
                    to support in your driver. For example ``aerate.io.Mongo``
                    supports both Python and Mongo-like query syntaxes.
        """
        raise NotImplementedError

    def retrieve_list_of_ids(self, resource, ids):
        """ Retrieves a list of documents based on a list of primary keys
        The primary key is the field defined in `ID_FIELD`.
        This is a separate function to allow us to use per-database
        optimizations for this type of query.
        :param resource: resource name.
        :param ids: a list of ids corresponding to the documents
        to retrieve
        :return: a list of documents matching the ids in `ids` from the
        collection specified in `resource`
        """
        raise NotImplementedError

    def retrieve_one(self, resource, **lookup):
        """ Retrieves a single document/record. Consumed when a request hits an
        item endpoint (`/pets/{id}/`).
        :param resource: resource being accessed. You should then use the
                         ``datasource`` helper function to retrieve both the
                         db collection/table and base query (filter), if any.
        :param **lookup: the lookup fields. This will most likely be a record
                         id or, if alternate lookup is supported by the API,
                         the corresponding query.
        """
        raise NotImplementedError

    def retrieve_one_raw(self, resource, _id):
        """ Retrieves a single, raw document/record. No projections or
        datasource filters are being applied here. Just looking up the
        document by unique id.
        :param resource: resource name.
        :param id: unique id.
        """
        raise NotImplementedError

    def create(self, resource, doc_or_docs):
        """ Creates a document into a resource collection/table.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the actual datasource name.
        :param doc_or_docs: json document or list of json documents to be added
                            to the database.
        .. versionchanged:: 0.0.6
            'document' param renamed to 'doc_or_docs', making support for bulk
            inserts apparent.
        """
        raise NotImplementedError

    def update(self, resource, id_, updates, original):
        """ Updates a collection/table document/row.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.
        :param updates: json updates to be performed on the database document
                        (or row).
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        raise NotImplementedError

    def replace(self, resource, id_, document, original):
        """ Replaces a collection/table document/row.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.
        :param document: the new json document
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        raise NotImplementedError

    def delete_one(self, resource, id_):
        """ Deletes a document/row from a database collection/table.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.

        """
        raise NotImplementedError

    def delete(self, resource, lookup={}):
        """ Deletes a set of documents/rows from a database collection/table.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param lookup: a dict with the query that documents must match in order
                       to qualify for deletion. For single document deletes,
                       this is usually the unique id of the document to be
                       removed.
        """
        raise NotImplementedError
