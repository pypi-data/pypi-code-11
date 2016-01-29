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


class NotificationTestCase(IntegrationTestCase):

    def test_fetch_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.api.v2010.accounts(sid="ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                 .notifications(sid="NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").fetch()
        
        self.holodeck.assert_has_request(Request(
            'get',
            'https://api.twilio.com/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications/NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json',
        ))

    def test_fetch_response(self):
        self.holodeck.mock(Response(
            200,
            '''
            {
                "account_sid": "ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "api_version": "2008-08-01",
                "call_sid": "CAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "date_created": "Mon, 13 Sep 2010 20:02:01 +0000",
                "date_updated": "Mon, 13 Sep 2010 20:02:01 +0000",
                "error_code": "11200",
                "log": "0",
                "message_date": "Mon, 13 Sep 2010 20:02:00 +0000",
                "message_text": "EmailNotification=false&LogLevel=ERROR&sourceComponent=12000&Msg=&httpResponse=500&ErrorCode=11200&url=http%3A%2F%2Fvoiceforms4000.appspot.com%2Ftwiml",
                "more_info": "http://www.twilio.com/docs/errors/11200",
                "request_method": "get",
                "request_url": "https://voiceforms4000.appspot.com/twiml/9436/question/0",
                "request_variables": "AccountSid=ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&CallStatus=in-progress&ToZip=94937&ToCity=INVERNESS&ToState=CA&Called=%2B14156694923&To=%2B14156694923&ToCountry=US&CalledZip=94937&Direction=inbound&ApiVersion=2010-04-01&Caller=%2B17378742833&CalledCity=INVERNESS&CalledCountry=US&CallSid=CAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&CalledState=CA&From=%2B17378742833",
                "response_body": "blah blah",
                "response_headers": "Date=Mon%2C+13+Sep+2010+20%3A02%3A00+GMT&Content-Length=466&Connection=close&Content-Type=text%2Fhtml%3B+charset%3DUTF-8&Server=Google+Frontend",
                "sid": "NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "uri": "/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications/NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json"
            }
            '''
        ))
        
        actual = self.client.api.v2010.accounts(sid="ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                      .notifications(sid="NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").fetch()
        
        self.assertIsNotNone(actual)

    def test_delete_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.api.v2010.accounts(sid="ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                 .notifications(sid="NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").delete()
        
        self.holodeck.assert_has_request(Request(
            'delete',
            'https://api.twilio.com/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications/NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json',
        ))

    def test_delete_response(self):
        self.holodeck.mock(Response(
            204,
            None,
        ))
        
        actual = self.client.api.v2010.accounts(sid="ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                      .notifications(sid="NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").delete()
        
        self.assertTrue(actual)

    def test_list_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.api.v2010.accounts(sid="ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                 .notifications.list()
        
        self.holodeck.assert_has_request(Request(
            'get',
            'https://api.twilio.com/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications.json',
        ))

    def test_read_full_response(self):
        self.holodeck.mock(Response(
            200,
            '''
            {
                "end": 0,
                "first_page_uri": "/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications.json?PageSize=1&Page=0",
                "last_page_uri": "/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications.json?PageSize=1&Page=100",
                "next_page_uri": null,
                "notifications": [
                    {
                        "account_sid": "ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "api_version": "2008-08-01",
                        "call_sid": "CAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "date_created": "Thu, 30 Apr 2015 16:47:33 +0000",
                        "date_updated": "Thu, 30 Apr 2015 16:47:35 +0000",
                        "error_code": "21609",
                        "log": "1",
                        "message_date": "Thu, 30 Apr 2015 16:47:32 +0000",
                        "message_text": "LogLevel=WARN&invalidStatusCallbackUrl=&Msg=Invalid+Url+for+callSid%3A+CAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa+invalid+statusCallbackUrl%3A+&ErrorCode=21609",
                        "more_info": "https://www.twilio.com/docs/errors/21609",
                        "request_method": null,
                        "request_url": "",
                        "sid": "NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "uri": "/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications/NOaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    }
                ],
                "num_pages": 101,
                "page": 0,
                "page_size": 1,
                "previous_page_uri": null,
                "start": 0,
                "total": 101,
                "uri": "/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications.json?PageSize=1&Page=0"
            }
            '''
        ))
        
        actual = self.client.api.v2010.accounts(sid="ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                      .notifications.list()
        
        self.assertIsNotNone(actual)

    def test_read_empty_response(self):
        self.holodeck.mock(Response(
            200,
            '''
            {
                "end": 0,
                "first_page_uri": "/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications.json?PageSize=1&Page=0",
                "last_page_uri": "/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications.json?PageSize=1&Page=100",
                "next_page_uri": null,
                "notifications": [],
                "num_pages": 101,
                "page": 0,
                "page_size": 1,
                "previous_page_uri": null,
                "start": 0,
                "total": 101,
                "uri": "/2010-04-01/Accounts/ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Notifications.json?PageSize=1&Page=0"
            }
            '''
        ))
        
        actual = self.client.api.v2010.accounts(sid="ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                      .notifications.list()
        
        self.assertIsNotNone(actual)
