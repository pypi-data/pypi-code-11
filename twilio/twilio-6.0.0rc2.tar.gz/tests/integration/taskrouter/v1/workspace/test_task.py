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


class TaskTestCase(IntegrationTestCase):

    def test_fetch_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                     .tasks(sid="WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").fetch()
        
        self.holodeck.assert_has_request(Request(
            'get',
            'https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks/WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        ))

    def test_fetch_response(self):
        self.holodeck.mock(Response(
            200,
            '''
            {
                "account_sid": "ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "age": 25200,
                "assignment_status": "pending",
                "attributes": "{\\"body\\": \\"hello\\"}",
                "date_created": "2014-05-14T10:50:02Z",
                "date_updated": "2014-05-14T23:26:06Z",
                "priority": 0,
                "reason": "Test Reason",
                "sid": "WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "task_queue_sid": "WQaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "timeout": 60,
                "url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks/WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "workflow_sid": "WFaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "workspace_sid": "WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            }
            '''
        ))
        
        actual = self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                          .tasks(sid="WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").fetch()
        
        self.assertIsNotNone(actual)

    def test_update_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                     .tasks(sid="WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").update()
        
        self.holodeck.assert_has_request(Request(
            'post',
            'https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks/WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        ))

    def test_update_response(self):
        self.holodeck.mock(Response(
            200,
            '''
            {
                "account_sid": "ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "age": 25200,
                "assignment_status": "pending",
                "attributes": "{\\"body\\": \\"hello\\"}",
                "date_created": "2014-05-14T10:50:02Z",
                "date_updated": "2014-05-14T23:26:06Z",
                "priority": 0,
                "reason": "Test Reason",
                "sid": "WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "task_queue_sid": "WQaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "timeout": 60,
                "url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks/WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "workflow_sid": "WFaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "workspace_sid": "WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            }
            '''
        ))
        
        actual = self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                          .tasks(sid="WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").update()
        
        self.assertIsNotNone(actual)

    def test_delete_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                     .tasks(sid="WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").delete()
        
        self.holodeck.assert_has_request(Request(
            'delete',
            'https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks/WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        ))

    def test_delete_response(self):
        self.holodeck.mock(Response(
            204,
            None,
        ))
        
        actual = self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                          .tasks(sid="WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").delete()
        
        self.assertTrue(actual)

    def test_list_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                     .tasks.list()
        
        self.holodeck.assert_has_request(Request(
            'get',
            'https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks',
        ))

    def test_read_full_response(self):
        self.holodeck.mock(Response(
            200,
            '''
            {
                "meta": {
                    "first_page_url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks?PageSize=50&Page=0",
                    "key": "tasks",
                    "last_page_url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks?PageSize=50&Page=0",
                    "next_page_url": null,
                    "page": 0,
                    "page_size": 50,
                    "previous_page_url": null,
                    "url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks?PageSize=50&Page=0"
                },
                "tasks": [
                    {
                        "account_sid": "ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "age": 25200,
                        "assignment_status": "pending",
                        "attributes": "{\\"body\\": \\"hello\\"}",
                        "date_created": "2014-05-14T14:26:54Z",
                        "date_updated": "2014-05-15T16:03:42Z",
                        "priority": 0,
                        "reason": "Test Reason",
                        "sid": "WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "task_queue_sid": "WQaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "timeout": 60,
                        "url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks/WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "workflow_sid": "WFaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "workspace_sid": "WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    }
                ]
            }
            '''
        ))
        
        actual = self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                          .tasks.list()
        
        self.assertIsNotNone(actual)

    def test_read_empty_response(self):
        self.holodeck.mock(Response(
            200,
            '''
            {
                "meta": {
                    "first_page_url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks?PageSize=50&Page=0",
                    "key": "tasks",
                    "last_page_url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks?PageSize=50&Page=0",
                    "next_page_url": null,
                    "page": 0,
                    "page_size": 50,
                    "previous_page_url": null,
                    "url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks?PageSize=50&Page=0"
                },
                "tasks": []
            }
            '''
        ))
        
        actual = self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                          .tasks.list()
        
        self.assertIsNotNone(actual)

    def test_create_request(self):
        self.holodeck.mock(Response(500, ''))
        
        with self.assertRaises(TwilioException):
            self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                     .tasks.create(attributes="attributes", workflow_sid="WFaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        
        values = {
            'Attributes': "attributes",
            'WorkflowSid': "WFaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        }
        
        self.holodeck.assert_has_request(Request(
            'post',
            'https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks',
            data=values,
        ))

    def test_create_response(self):
        self.holodeck.mock(Response(
            200,
            '''
            {
                "account_sid": "ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "age": 25200,
                "assignment_status": "pending",
                "attributes": "{\\"body\\": \\"hello\\"}",
                "date_created": "2014-05-14T10:50:02Z",
                "date_updated": "2014-05-14T23:26:06Z",
                "priority": 0,
                "reason": "Test Reason",
                "sid": "WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "task_queue_sid": "WQaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "timeout": 60,
                "url": "https://taskrouter.twilio.com/v1/Workspaces/WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/Tasks/WTaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "workflow_sid": "WFaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "workspace_sid": "WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            }
            '''
        ))
        
        actual = self.client.taskrouter.v1.workspaces(sid="WSaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") \
                                          .tasks.create(attributes="attributes", workflow_sid="WFaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        
        self.assertIsNotNone(actual)
