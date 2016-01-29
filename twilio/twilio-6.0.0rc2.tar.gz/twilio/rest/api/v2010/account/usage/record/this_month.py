# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /       
"""

from twilio import deserialize
from twilio import values
from twilio.instance_resource import InstanceResource
from twilio.list_resource import ListResource
from twilio.page import Page


class ThisMonthList(ListResource):

    def __init__(self, version, account_sid):
        """
        Initialize the ThisMonthList
        
        :param Version version: Version that contains the resource
        :param account_sid: A 34 character string that uniquely identifies this resource.
        
        :returns: ThisMonthList
        :rtype: ThisMonthList
        """
        super(ThisMonthList, self).__init__(version)
        
        # Path Solution
        self._solution = {
            'account_sid': account_sid,
        }
        self._uri = '/Accounts/{account_sid}/Usage/Records/ThisMonth.json'.format(**self._solution)

    def stream(self, limit=None, page_size=None):
        """
        Streams ThisMonthInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.
        
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)
        
        :returns: Generator that will yield up to limit results
        :rtype: generator
        """
        limits = self._version.read_limits(limit, page_size)
        
        page = self.page(
            page_size=limits['page_size'],
        )
        
        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists ThisMonthInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.
        
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)
        
        :returns: Generator that will yield up to limit results
        :rtype: generator
        """
        return list(self.stream(
            limit=limit,
            page_size=page_size,
        ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of ThisMonthInstance records from the API.
        Request is executed immediately
        
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50
        
        :returns: Page of ThisMonthInstance
        :rtype: Page
        """
        params = values.of({
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })
        
        response = self._version.page(
            'GET',
            self._uri,
            params=params,
        )
        
        return ThisMonthPage(
            self._version,
            response,
            account_sid=self._solution['account_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation
        
        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.ThisMonthList>'


class ThisMonthPage(Page):

    def __init__(self, version, response, account_sid):
        """
        Initialize the ThisMonthPage
        
        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param account_sid: A 34 character string that uniquely identifies this resource.
        
        :returns: ThisMonthPage
        :rtype: ThisMonthPage
        """
        super(ThisMonthPage, self).__init__(version, response)
        
        # Path Solution
        self._solution = {
            'account_sid': account_sid,
        }

    def get_instance(self, payload):
        """
        Build an instance of ThisMonthInstance
        
        :param dict payload: Payload response from the API
        
        :returns: ThisMonthInstance
        :rtype: ThisMonthInstance
        """
        return ThisMonthInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation
        
        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.ThisMonthPage>'


class ThisMonthInstance(InstanceResource):

    def __init__(self, version, payload, account_sid):
        """
        Initialize the ThisMonthInstance
        
        :returns: ThisMonthInstance
        :rtype: ThisMonthInstance
        """
        super(ThisMonthInstance, self).__init__(version)
        
        # Marshaled Properties
        self._properties = {
            'account_sid': payload['account_sid'],
            'api_version': payload['api_version'],
            'category': payload['category'],
            'count': payload['count'],
            'count_unit': payload['count_unit'],
            'description': payload['description'],
            'end_date': deserialize.iso8601_datetime(payload['end_date']),
            'price': deserialize.decimal(payload['price']),
            'price_unit': payload['price_unit'],
            'start_date': deserialize.iso8601_datetime(payload['start_date']),
            'subresource_uris': payload['subresource_uris'],
            'uri': payload['uri'],
            'usage': payload['usage'],
            'usage_unit': payload['usage_unit'],
        }
        
        # Context
        self._context = None
        self._solution = {
            'account_sid': account_sid,
        }

    @property
    def account_sid(self):
        """
        :returns: The account_sid
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def api_version(self):
        """
        :returns: The api_version
        :rtype: unicode
        """
        return self._properties['api_version']

    @property
    def category(self):
        """
        :returns: The category
        :rtype: this_month.category
        """
        return self._properties['category']

    @property
    def count(self):
        """
        :returns: The count
        :rtype: unicode
        """
        return self._properties['count']

    @property
    def count_unit(self):
        """
        :returns: The count_unit
        :rtype: unicode
        """
        return self._properties['count_unit']

    @property
    def description(self):
        """
        :returns: The description
        :rtype: unicode
        """
        return self._properties['description']

    @property
    def end_date(self):
        """
        :returns: The end_date
        :rtype: datetime
        """
        return self._properties['end_date']

    @property
    def price(self):
        """
        :returns: The price
        :rtype: unicode
        """
        return self._properties['price']

    @property
    def price_unit(self):
        """
        :returns: The price_unit
        :rtype: unicode
        """
        return self._properties['price_unit']

    @property
    def start_date(self):
        """
        :returns: The start_date
        :rtype: datetime
        """
        return self._properties['start_date']

    @property
    def subresource_uris(self):
        """
        :returns: The subresource_uris
        :rtype: unicode
        """
        return self._properties['subresource_uris']

    @property
    def uri(self):
        """
        :returns: The uri
        :rtype: unicode
        """
        return self._properties['uri']

    @property
    def usage(self):
        """
        :returns: The usage
        :rtype: unicode
        """
        return self._properties['usage']

    @property
    def usage_unit(self):
        """
        :returns: The usage_unit
        :rtype: unicode
        """
        return self._properties['usage_unit']

    def __repr__(self):
        """
        Provide a friendly representation
        
        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.ThisMonthInstance>'
