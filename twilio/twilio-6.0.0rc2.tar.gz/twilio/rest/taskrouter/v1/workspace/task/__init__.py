# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /       
"""

from twilio import deserialize
from twilio import values
from twilio.instance_context import InstanceContext
from twilio.instance_resource import InstanceResource
from twilio.list_resource import ListResource
from twilio.page import Page
from twilio.rest.taskrouter.v1.workspace.task.reservation import ReservationList


class TaskList(ListResource):

    def __init__(self, version, workspace_sid):
        """
        Initialize the TaskList
        
        :param Version version: Version that contains the resource
        :param workspace_sid: The workspace_sid
        
        :returns: TaskList
        :rtype: TaskList
        """
        super(TaskList, self).__init__(version)
        
        # Path Solution
        self._solution = {
            'workspace_sid': workspace_sid,
        }
        self._uri = '/Workspaces/{workspace_sid}/Tasks'.format(**self._solution)

    def stream(self, priority=values.unset, assignment_status=values.unset,
               workflow_sid=values.unset, workflow_name=values.unset,
               task_queue_sid=values.unset, task_queue_name=values.unset,
               limit=None, page_size=None):
        """
        Streams TaskInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.
        
        :param unicode priority: The priority
        :param task.status assignment_status: The assignment_status
        :param unicode workflow_sid: The workflow_sid
        :param unicode workflow_name: The workflow_name
        :param unicode task_queue_sid: The task_queue_sid
        :param unicode task_queue_name: The task_queue_name
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
            priority=priority,
            assignment_status=assignment_status,
            workflow_sid=workflow_sid,
            workflow_name=workflow_name,
            task_queue_sid=task_queue_sid,
            task_queue_name=task_queue_name,
            page_size=limits['page_size'],
        )
        
        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, priority=values.unset, assignment_status=values.unset,
             workflow_sid=values.unset, workflow_name=values.unset,
             task_queue_sid=values.unset, task_queue_name=values.unset, limit=None,
             page_size=None):
        """
        Lists TaskInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.
        
        :param unicode priority: The priority
        :param task.status assignment_status: The assignment_status
        :param unicode workflow_sid: The workflow_sid
        :param unicode workflow_name: The workflow_name
        :param unicode task_queue_sid: The task_queue_sid
        :param unicode task_queue_name: The task_queue_name
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
            priority=priority,
            assignment_status=assignment_status,
            workflow_sid=workflow_sid,
            workflow_name=workflow_name,
            task_queue_sid=task_queue_sid,
            task_queue_name=task_queue_name,
            limit=limit,
            page_size=page_size,
        ))

    def page(self, priority=values.unset, assignment_status=values.unset,
             workflow_sid=values.unset, workflow_name=values.unset,
             task_queue_sid=values.unset, task_queue_name=values.unset,
             page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of TaskInstance records from the API.
        Request is executed immediately
        
        :param unicode priority: The priority
        :param task.status assignment_status: The assignment_status
        :param unicode workflow_sid: The workflow_sid
        :param unicode workflow_name: The workflow_name
        :param unicode task_queue_sid: The task_queue_sid
        :param unicode task_queue_name: The task_queue_name
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50
        
        :returns: Page of TaskInstance
        :rtype: Page
        """
        params = values.of({
            'Priority': priority,
            'AssignmentStatus': assignment_status,
            'WorkflowSid': workflow_sid,
            'WorkflowName': workflow_name,
            'TaskQueueSid': task_queue_sid,
            'TaskQueueName': task_queue_name,
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })
        
        response = self._version.page(
            'GET',
            self._uri,
            params=params,
        )
        
        return TaskPage(
            self._version,
            response,
            workspace_sid=self._solution['workspace_sid'],
        )

    def create(self, attributes, workflow_sid, timeout=values.unset,
               priority=values.unset):
        """
        Create a new TaskInstance
        
        :param unicode attributes: The attributes
        :param unicode workflow_sid: The workflow_sid
        :param unicode timeout: The timeout
        :param unicode priority: The priority
        
        :returns: Newly created TaskInstance
        :rtype: TaskInstance
        """
        data = values.of({
            'Attributes': attributes,
            'WorkflowSid': workflow_sid,
            'Timeout': timeout,
            'Priority': priority,
        })
        
        payload = self._version.create(
            'POST',
            self._uri,
            data=data,
        )
        
        return TaskInstance(
            self._version,
            payload,
            workspace_sid=self._solution['workspace_sid'],
        )

    def get(self, sid):
        """
        Constructs a TaskContext
        
        :param sid: The sid
        
        :returns: TaskContext
        :rtype: TaskContext
        """
        return TaskContext(
            self._version,
            workspace_sid=self._solution['workspace_sid'],
            sid=sid,
        )

    def __call__(self, sid):
        """
        Constructs a TaskContext
        
        :param sid: The sid
        
        :returns: TaskContext
        :rtype: TaskContext
        """
        return TaskContext(
            self._version,
            workspace_sid=self._solution['workspace_sid'],
            sid=sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation
        
        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Taskrouter.V1.TaskList>'


class TaskPage(Page):

    def __init__(self, version, response, workspace_sid):
        """
        Initialize the TaskPage
        
        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param workspace_sid: The workspace_sid
        
        :returns: TaskPage
        :rtype: TaskPage
        """
        super(TaskPage, self).__init__(version, response)
        
        # Path Solution
        self._solution = {
            'workspace_sid': workspace_sid,
        }

    def get_instance(self, payload):
        """
        Build an instance of TaskInstance
        
        :param dict payload: Payload response from the API
        
        :returns: TaskInstance
        :rtype: TaskInstance
        """
        return TaskInstance(
            self._version,
            payload,
            workspace_sid=self._solution['workspace_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation
        
        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Taskrouter.V1.TaskPage>'


class TaskContext(InstanceContext):

    def __init__(self, version, workspace_sid, sid):
        """
        Initialize the TaskContext
        
        :param Version version: Version that contains the resource
        :param workspace_sid: The workspace_sid
        :param sid: The sid
        
        :returns: TaskContext
        :rtype: TaskContext
        """
        super(TaskContext, self).__init__(version)
        
        # Path Solution
        self._solution = {
            'workspace_sid': workspace_sid,
            'sid': sid,
        }
        self._uri = '/Workspaces/{workspace_sid}/Tasks/{sid}'.format(**self._solution)
        
        # Dependents
        self._reservations = None

    def fetch(self):
        """
        Fetch a TaskInstance
        
        :returns: Fetched TaskInstance
        :rtype: TaskInstance
        """
        params = values.of({})
        
        payload = self._version.fetch(
            'GET',
            self._uri,
            params=params,
        )
        
        return TaskInstance(
            self._version,
            payload,
            workspace_sid=self._solution['workspace_sid'],
            sid=self._solution['sid'],
        )

    def update(self, attributes=values.unset, assignment_status=values.unset,
               reason=values.unset, priority=values.unset):
        """
        Update the TaskInstance
        
        :param unicode attributes: The attributes
        :param task.status assignment_status: The assignment_status
        :param unicode reason: The reason
        :param unicode priority: The priority
        
        :returns: Updated TaskInstance
        :rtype: TaskInstance
        """
        data = values.of({
            'Attributes': attributes,
            'AssignmentStatus': assignment_status,
            'Reason': reason,
            'Priority': priority,
        })
        
        payload = self._version.update(
            'POST',
            self._uri,
            data=data,
        )
        
        return TaskInstance(
            self._version,
            payload,
            workspace_sid=self._solution['workspace_sid'],
            sid=self._solution['sid'],
        )

    def delete(self):
        """
        Deletes the TaskInstance
        
        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete('delete', self._uri)

    @property
    def reservations(self):
        """
        Access the reservations
        
        :returns: ReservationList
        :rtype: ReservationList
        """
        if self._reservations is None:
            self._reservations = ReservationList(
                self._version,
                workspace_sid=self._solution['workspace_sid'],
                task_sid=self._solution['sid'],
            )
        return self._reservations

    def __repr__(self):
        """
        Provide a friendly representation
        
        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Taskrouter.V1.TaskContext {}>'.format(context)


class TaskInstance(InstanceResource):

    def __init__(self, version, payload, workspace_sid, sid=None):
        """
        Initialize the TaskInstance
        
        :returns: TaskInstance
        :rtype: TaskInstance
        """
        super(TaskInstance, self).__init__(version)
        
        # Marshaled Properties
        self._properties = {
            'account_sid': payload['account_sid'],
            'age': deserialize.integer(payload['age']),
            'assignment_status': payload['assignment_status'],
            'attributes': payload['attributes'],
            'date_created': deserialize.iso8601_datetime(payload['date_created']),
            'date_updated': deserialize.iso8601_datetime(payload['date_updated']),
            'priority': deserialize.integer(payload['priority']),
            'reason': payload['reason'],
            'sid': payload['sid'],
            'task_queue_sid': payload['task_queue_sid'],
            'timeout': deserialize.integer(payload['timeout']),
            'workflow_sid': payload['workflow_sid'],
            'workspace_sid': payload['workspace_sid'],
        }
        
        # Context
        self._context = None
        self._solution = {
            'workspace_sid': workspace_sid,
            'sid': sid or self._properties['sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context
        
        :returns: TaskContext for this TaskInstance
        :rtype: TaskContext
        """
        if self._context is None:
            self._context = TaskContext(
                self._version,
                workspace_sid=self._solution['workspace_sid'],
                sid=self._solution['sid'],
            )
        return self._context

    @property
    def account_sid(self):
        """
        :returns: The account_sid
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def age(self):
        """
        :returns: The age
        :rtype: unicode
        """
        return self._properties['age']

    @property
    def assignment_status(self):
        """
        :returns: The assignment_status
        :rtype: task.status
        """
        return self._properties['assignment_status']

    @property
    def attributes(self):
        """
        :returns: The attributes
        :rtype: unicode
        """
        return self._properties['attributes']

    @property
    def date_created(self):
        """
        :returns: The date_created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The date_updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def priority(self):
        """
        :returns: The priority
        :rtype: unicode
        """
        return self._properties['priority']

    @property
    def reason(self):
        """
        :returns: The reason
        :rtype: unicode
        """
        return self._properties['reason']

    @property
    def sid(self):
        """
        :returns: The sid
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def task_queue_sid(self):
        """
        :returns: The task_queue_sid
        :rtype: unicode
        """
        return self._properties['task_queue_sid']

    @property
    def timeout(self):
        """
        :returns: The timeout
        :rtype: unicode
        """
        return self._properties['timeout']

    @property
    def workflow_sid(self):
        """
        :returns: The workflow_sid
        :rtype: unicode
        """
        return self._properties['workflow_sid']

    @property
    def workspace_sid(self):
        """
        :returns: The workspace_sid
        :rtype: unicode
        """
        return self._properties['workspace_sid']

    def fetch(self):
        """
        Fetch a TaskInstance
        
        :returns: Fetched TaskInstance
        :rtype: TaskInstance
        """
        return self._proxy.fetch()

    def update(self, attributes=values.unset, assignment_status=values.unset,
               reason=values.unset, priority=values.unset):
        """
        Update the TaskInstance
        
        :param unicode attributes: The attributes
        :param task.status assignment_status: The assignment_status
        :param unicode reason: The reason
        :param unicode priority: The priority
        
        :returns: Updated TaskInstance
        :rtype: TaskInstance
        """
        return self._proxy.update(
            attributes=attributes,
            assignment_status=assignment_status,
            reason=reason,
            priority=priority,
        )

    def delete(self):
        """
        Deletes the TaskInstance
        
        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    @property
    def reservations(self):
        """
        Access the reservations
        
        :returns: reservations
        :rtype: reservations
        """
        return self._proxy.reservations

    def __repr__(self):
        """
        Provide a friendly representation
        
        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Taskrouter.V1.TaskInstance {}>'.format(context)
