"""Module containing the tests for requests_toolbelt.threaded.thread."""
try:
    import queue  # Python 3
except ImportError:
    import Queue as queue
import threading
import unittest
import uuid

import mock
import requests.exceptions

from requests_toolbelt.threaded import thread


def _make_mocks():
    return (mock.MagicMock() for _ in range(4))


def _initialize_a_session_thread(session=None, job_queue=None,
                                 response_queue=None, exception_queue=None):
    with mock.patch.object(threading, 'Thread') as Thread:
        thread_instance = mock.MagicMock()
        Thread.return_value = thread_instance
        st = thread.SessionThread(
            initialized_session=session,
            job_queue=job_queue,
            response_queue=response_queue,
            exception_queue=exception_queue,
            )

    return (st, thread_instance, Thread)


class TestSessionThread(unittest.TestCase):

    """Tests for requests_toolbelt.threaded.thread.SessionThread."""

    def test_thread_initialization(self):
        """Test the way a SessionThread is initialized.

        We want to ensure that we creat a thread with a name generated by the
        uuid module, and that we pass the right method to use as a target.
        """
        with mock.patch.object(uuid, 'uuid4', return_value='test'):
            (st, thread_instance, Thread) = _initialize_a_session_thread()

        Thread.assert_called_once_with(target=st._make_request, name='test')
        assert thread_instance.daemon is True
        assert thread_instance._state is 0
        thread_instance.start.assert_called_once_with()

    def test_is_alive_proxies_to_worker(self):
        """Test that we proxy the is_alive method to the Thread."""
        with mock.patch.object(threading, 'Thread') as Thread:
            thread_instance = mock.MagicMock()
            Thread.return_value = thread_instance
            st = thread.SessionThread(None, None, None, None)

        st.is_alive()
        thread_instance.is_alive.assert_called_once_with()

    def test_join_proxies_to_worker(self):
        """Test that we proxy the join method to the Thread."""
        st, thread_instance, _ = _initialize_a_session_thread()

        st.join()
        thread_instance.join.assert_called_once_with()

    def test_handle_valid_request(self):
        """Test that a response is added to the right queue."""
        session, job_queue, response_queue, exception_queue = _make_mocks()
        response = mock.MagicMock()
        session.request.return_value = response

        st, _, _ = _initialize_a_session_thread(
            session, job_queue, response_queue, exception_queue)

        st._handle_request({'method': 'GET', 'url': 'http://example.com'})
        session.request.assert_called_once_with(
            method='GET',
            url='http://example.com'
        )

        response_queue.put.assert_called_once_with(
            ({'method': 'GET', 'url': 'http://example.com'}, response)
        )
        assert exception_queue.put.called is False
        assert job_queue.get.called is False
        assert job_queue.get_nowait.called is False
        assert job_queue.get_nowait.called is False
        assert job_queue.task_done.called is True

    def test_handle_invalid_request(self):
        """Test that exceptions from requests are added to the right queue."""
        session, job_queue, response_queue, exception_queue = _make_mocks()
        exception = requests.exceptions.InvalidURL()

        def _side_effect(*args, **kwargs):
            raise exception

        # Make the request raise an exception
        session.request.side_effect = _side_effect

        st, _, _ = _initialize_a_session_thread(
            session, job_queue, response_queue, exception_queue)

        st._handle_request({'method': 'GET', 'url': 'http://example.com'})
        session.request.assert_called_once_with(
            method='GET',
            url='http://example.com'
        )

        exception_queue.put.assert_called_once_with(
            ({'method': 'GET', 'url': 'http://example.com'}, exception)
        )
        assert response_queue.put.called is False
        assert job_queue.get.called is False
        assert job_queue.get_nowait.called is False
        assert job_queue.get_nowait.called is False
        assert job_queue.task_done.called is True

    def test_make_request(self):
        """Test that _make_request exits when the queue is Empty."""
        job_queue = next(_make_mocks())
        job_queue.get_nowait.side_effect = queue.Empty()

        st, _, _ = _initialize_a_session_thread(job_queue=job_queue)
        st._make_request()

        job_queue.get_nowait.assert_called_once_with()
