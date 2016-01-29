# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /       
"""

from twilio.rest.api.v2010.account import AccountContext
from twilio.rest.api.v2010.account import AccountList
from twilio.version import Version


class V2010(Version):

    def __init__(self, domain):
        """
        Initialize the V2010 version of Api
        
        :returns: V2010 version of Api
        :rtype: V2010
        """
        super(V2010, self).__init__(domain)
        self.version = '2010-04-01'
        self._accounts = None
        self._account = None

    @property
    def accounts(self):
        """
        :rtype: AccountList
        """
        if self._accounts is None:
            self._accounts = AccountList(self)
        return self._accounts

    @property
    def account(self):
        """
        :returns: Account provided as the authenticating account
        :rtype: AccountContext
        """
        if self._account is None:
            self._account = AccountContext(self, self.domain.twilio.account_sid)
        return self._account

    @account.setter
    def account(self, value):
        """
        Setter to override the primary account
        
        :param AccountContext|AccountInstance value: account to use as primary account
        """
        self._account = value

    @property
    def addresses(self):
        """
        :rtype: AddressList
        """
        return self.account.addresses

    @property
    def applications(self):
        """
        :rtype: ApplicationList
        """
        return self.account.applications

    @property
    def authorized_connect_apps(self):
        """
        :rtype: AuthorizedConnectAppList
        """
        return self.account.authorized_connect_apps

    @property
    def available_phone_numbers(self):
        """
        :rtype: AvailablePhoneNumberCountryList
        """
        return self.account.available_phone_numbers

    @property
    def calls(self):
        """
        :rtype: CallList
        """
        return self.account.calls

    @property
    def conferences(self):
        """
        :rtype: ConferenceList
        """
        return self.account.conferences

    @property
    def connect_apps(self):
        """
        :rtype: ConnectAppList
        """
        return self.account.connect_apps

    @property
    def incoming_phone_numbers(self):
        """
        :rtype: IncomingPhoneNumberList
        """
        return self.account.incoming_phone_numbers

    @property
    def messages(self):
        """
        :rtype: MessageList
        """
        return self.account.messages

    @property
    def notifications(self):
        """
        :rtype: NotificationList
        """
        return self.account.notifications

    @property
    def outgoing_caller_ids(self):
        """
        :rtype: OutgoingCallerIdList
        """
        return self.account.outgoing_caller_ids

    @property
    def queues(self):
        """
        :rtype: QueueList
        """
        return self.account.queues

    @property
    def recordings(self):
        """
        :rtype: RecordingList
        """
        return self.account.recordings

    @property
    def sandbox(self):
        """
        :rtype: SandboxList
        """
        return self.account.sandbox

    @property
    def sip(self):
        """
        :rtype: SipList
        """
        return self.account.sip

    @property
    def sms(self):
        """
        :rtype: SmsList
        """
        return self.account.sms

    @property
    def tokens(self):
        """
        :rtype: TokenList
        """
        return self.account.tokens

    @property
    def transcriptions(self):
        """
        :rtype: TranscriptionList
        """
        return self.account.transcriptions

    @property
    def usage(self):
        """
        :rtype: UsageList
        """
        return self.account.usage

    @property
    def validation_requests(self):
        """
        :rtype: ValidationRequestList
        """
        return self.account.validation_requests

    def __repr__(self):
        """
        Provide a friendly representation
        
        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010>'
