# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /       
"""

from tests.integration import IntegrationTestCase
from tests.integration.holodeck import Request
from twilio.exceptions import TwilioException
from twilio.http.response import Response


class CredentialTestCase(IntegrationTestCase):

    def test_list_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.ip_messaging.v1.credentials.list()
        
        self.holodeck.assert_has_request(Request(
            'get',
            'https://ip-messaging.twilio.com/v1/Credentials',
        ))

    def test_create_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.ip_messaging.v1.credentials.create(friendly_name="friendly_name", type="gcm")
        
        values = {
            'FriendlyName': "friendly_name",
            'Type': "gcm",
        }
        
        self.holodeck.assert_has_request(Request(
            'post',
            'https://ip-messaging.twilio.com/v1/Credentials',
            data=values,
        ))

    def test_fetch_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.ip_messaging.v1.credentials(sid="CRaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").fetch()
        
        self.holodeck.assert_has_request(Request(
            'get',
            'https://ip-messaging.twilio.com/v1/Credentials/CRaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        ))

    def test_update_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.ip_messaging.v1.credentials(sid="CRaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").update(friendly_name="friendly_name", type="gcm")
        
        values = {
            'FriendlyName': "friendly_name",
            'Type': "gcm",
        }
        
        self.holodeck.assert_has_request(Request(
            'post',
            'https://ip-messaging.twilio.com/v1/Credentials/CRaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            data=values,
        ))

    def test_delete_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.ip_messaging.v1.credentials(sid="CRaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").delete()
        
        self.holodeck.assert_has_request(Request(
            'delete',
            'https://ip-messaging.twilio.com/v1/Credentials/CRaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        ))
