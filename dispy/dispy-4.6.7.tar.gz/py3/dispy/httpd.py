"""
This file is part of dispy project.
See http://dispy.sourceforge.net for details.
"""

__author__ = "Giridhar Pemmasani (pgiri@yahoo.com)"
__email__ = "pgiri@yahoo.com"
__copyright__ = "Copyright 2015, Giridhar Pemmasani"
__contributors__ = []
__maintainer__ = "Giridhar Pemmasani (pgiri@yahoo.com)"
__license__ = "MIT"
__url__ = "http://dispy.sourceforge.net"

__all__ = ['DispyHTTPServer']

import sys
import os
import threading
import json
import cgi
import time
import socket
import ssl
import re
import functools
import copy
import traceback

if sys.version_info.major > 2:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import urlparse

import dispy
from dispy import DispyJob


class DispyHTTPServer(object):

    class _ClusterInfo(object):

        def __init__(self, cluster):
            self.cluster = cluster
            self.jobs_submitted = 0
            self.jobs_done = 0
            self.jobs_pending = 0
            self.jobs = {}
            self.status = {}
            # TODO: maintain updates for each client separately, so
            # multiple clients can view the status?
            self.updates = {}

    class _HTTPRequestHandler(BaseHTTPRequestHandler):
        def __init__(self, ctx, DocumentRoot, *args):
            self._dispy_ctx = ctx
            self._dispy_ctx._http_handler = self
            self.DocumentRoot = DocumentRoot
            BaseHTTPRequestHandler.__init__(self, *args)

        def log_message(self, fmt, *args):
            # dispy.logger.debug('HTTP client %s: %s' % (self.client_address[0], fmt % args))
            return

        def do_GET(self):
            if self.path == '/cluster_updates':
                self._dispy_ctx._cluster_lock.acquire()
                updates = [
                    {'name': name,
                     'jobs': {'submitted': cluster.jobs_submitted, 'done': cluster.jobs_done},
                     'nodes': [node.__dict__ for node in cluster.updates.values()]
                     } for name, cluster in self._dispy_ctx._clusters.items()
                    ]
                for cluster in self._dispy_ctx._clusters.values():
                    cluster.updates = {}
                self._dispy_ctx._cluster_lock.release()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(updates).encode())
                return
            elif self.path == '/cluster_status':
                self._dispy_ctx._cluster_lock.acquire()
                status = [
                    {'name': name,
                     'jobs': {'submitted': cluster.jobs_submitted, 'done': cluster.jobs_done},
                     'nodes': [node.__dict__ for node in cluster.status.values()]
                     } for name, cluster in self._dispy_ctx._clusters.items()
                    ]
                self._dispy_ctx._cluster_lock.release()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(status).encode())
                return
            elif self.path == '/nodes':
                self._dispy_ctx._cluster_lock.acquire()
                clusters = [
                    {'name': name,
                     'nodes': [node.__dict__ for node in cluster.status.values()]
                     } for name, cluster in self._dispy_ctx._clusters.items()
                    ]
                self._dispy_ctx._cluster_lock.release()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(clusters).encode())
                return
            else:
                parsed_path = urlparse(self.path)
                path = parsed_path.path.lstrip('/')
                if path == '' or path == 'index.html':
                    path = 'monitor.html'
                path = os.path.join(self.DocumentRoot, path)
                try:
                    f = open(path)
                    data = f.read()
                    if path.endswith('.html'):
                        if path.endswith('monitor.html') or path.endswith('node.html'):
                            data = data % {'TIMEOUT': str(self._dispy_ctx._poll_sec)}
                        content_type = 'text/html'
                    elif path.endswith('.js'):
                        content_type = 'text/javascript'
                    elif path.endswith('.css'):
                        content_type = 'text/css'
                    elif path.endswith('.ico'):
                        content_type = 'image/x-icon'
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    if content_type == 'text/css' or content_type == 'text/javascript':
                        self.send_header('Cache-Control', 'private, max-age=86400')
                    self.end_headers()
                    self.wfile.write(data.encode())
                    f.close()
                    return
                except:
                    dispy.logger.warning('HTTP client %s: Could not read/send "%s"',
                                         self.client_address[0], path)
                    dispy.logger.debug(traceback.format_exc())
                self.send_error(404)
                return
            dispy.logger.debug('Bad GET request from %s: %s' % (self.client_address[0], self.path))
            self.send_error(400)
            return

        def do_POST(self):
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST'})
            if self.path == '/node_jobs':
                ip_addr = None
                for item in form.list:
                    if item.name == 'host':
                        # if it looks like IP address, skip resolving
                        if re.match('^\d+[\.\d]+$', item.value):
                            ip_addr = item.value
                        else:
                            try:
                                ip_addr = socket.gethostbyname(item.value)
                            except:
                                ip_addr = item.value
                        break
                self._dispy_ctx._cluster_lock.acquire()
                cluster_infos = [(name, cluster_info) for name, cluster_info in
                                 self._dispy_ctx._clusters.items()]
                self._dispy_ctx._cluster_lock.release()
                jobs = []
                node = None
                for name, cluster_info in cluster_infos:
                    cluster_node = cluster_info.status.get(ip_addr, None)
                    if not cluster_node:
                        continue
                    if node:
                        node.jobs_done += cluster_node.jobs_done
                        node.cpu_time += cluster_node.cpu_time
                        node.update_time = max(node.update_time, cluster_node.update_time)
                    else:
                        node = copy.copy(cluster_node)
                    cluster_jobs = cluster_info.cluster.node_jobs(ip_addr)
                    # args and kwargs are sent as strings in Python,
                    # so an object's __str__ or __repr__ is used if provided;
                    # TODO: check job is in _dispy_ctx's jobs?
                    jobs.extend([{'uid': id(job), 'job_id': str(job.id),
                                  'args': ', '.join(str(arg) for arg in job.args),
                                  'kwargs': ', '.join('%s=%s' % (key, val)
                                                      for key, val in job.kwargs.items()),
                                  'sched_time_ms': int(1000 * job.start_time),
                                  'cluster': name}
                                 for job in cluster_jobs])
                if node:
                    node = node.__dict__
                else:
                    node = {}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'node': node, 'jobs': jobs}).encode())
                return
            elif self.path == '/cancel_jobs':
                uids = []
                for item in form.list:
                    if item.name == 'uid':
                        try:
                            uids.append(int(item.value))
                        except ValueError:
                            dispy.logger.debug('Cancel job uid "%s" is invalid' % item.value)

                self._dispy_ctx._cluster_lock.acquire()
                cluster_jobs = [(cluster_info.cluster, cluster_info.jobs.get(uid, None))
                                for cluster_info in self._dispy_ctx._clusters.values()
                                for uid in uids]
                self._dispy_ctx._cluster_lock.release()
                cancelled = []
                for cluster, job in cluster_jobs:
                    if not job:
                        continue
                    if cluster.cancel(job) == 0:
                        cancelled.append(id(job))
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(cancelled).encode())
                return
            elif self.path == '/add_node':
                node = {'host': '', 'port': None, 'cpus': 0, 'cluster': None}
                node_id = None
                cluster = None
                for item in form.list:
                    if item.name == 'host':
                        node['host'] = item.value
                    elif item.name == 'cluster':
                        node['cluster'] = item.value
                    elif item.name == 'port':
                        node['port'] = item.value
                    elif item.name == 'cpus':
                        try:
                            node['cpus'] = int(item.value)
                        except:
                            pass
                    elif item.name == 'id':
                        node_id = item.value
                if node['host']:
                    self._dispy_ctx._cluster_lock.acquire()
                    clusters = [cluster_info.cluster for name, cluster_info in
                                self._dispy_ctx._clusters.items()
                                if name == node['cluster'] or not node['cluster']]
                    self._dispy_ctx._cluster_lock.release()
                    for cluster in clusters:
                        cluster.allocate_node(node)
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    node['id'] = node_id
                    self.wfile.write(json.dumps(node).encode())
                    return
            elif self.path == '/set_poll_sec':
                for item in form.list:
                    if item.name != 'timeout':
                        continue
                    try:
                        timeout = int(item.value)
                        if timeout < 1:
                            timeout = 0
                    except:
                        dispy.logger.warning('HTTP client %s: invalid timeout "%s" ignored',
                                             self.client_address[0], item.value)
                        timeout = 0
                    self._dispy_ctx._poll_sec = timeout
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    return
            elif self.path == '/set_cpus':
                node_cpus = {}
                for item in form.list:
                    self._dispy_ctx._cluster_lock.acquire()
                    for cluster_info in self._dispy_ctx._clusters.values():
                        node = cluster_info.status.get(item.name, None)
                        if node:
                            node_cpus[item.name] = cluster_info.cluster.set_node_cpus(
                                item.name, item.value)
                            if node_cpus[item.name] >= 0:
                                break
                    self._dispy_ctx._cluster_lock.release()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(node_cpus).encode())
                return

            dispy.logger.debug('Bad POST request from %s: %s' % (self.client_address[0], self.path))
            self.send_error(400)
            return

    def __init__(self, cluster, host='', port=8181, poll_sec=10, DocumentRoot=None,
                 keyfile=None, certfile=None):
        self._cluster_lock = threading.Lock()
        self._clusters = {}
        if cluster:
            cluster_info = self.__class__._ClusterInfo(cluster)
            self._clusters[cluster.name] = cluster_info
            if cluster.status_callback is None:
                cluster.status_callback = functools.partial(self.cluster_status, cluster_info)
        if not DocumentRoot:
            DocumentRoot = os.path.join(os.path.dirname(__file__), 'data')
        if poll_sec < 1:
            dispy.logger.warning('invalid poll_sec value %s; it must be at least 1' % poll_sec)
            poll_sec = 1
        self._poll_sec = poll_sec
        self._http_handler = None
        self._server = HTTPServer((host, port), lambda *args:
                                  self.__class__._HTTPRequestHandler(self, DocumentRoot, *args))
        if certfile:
            self._server.socket = ssl.wrap_socket(self._server.socket, keyfile=keyfile,
                                                  certfile=certfile, server_side=True)
        self._httpd_thread = threading.Thread(target=self._server.serve_forever)
        self._httpd_thread.daemon = True
        self._httpd_thread.start()
        dispy.logger.info('Started HTTP%s server at %s' %
                          ('s' if certfile else '', str(self._server.socket.getsockname())))

    def cluster_status(self, cluster_info, status, node, job):
        """This method is called by JobCluster/SharedJobCluster
        whenever there is a change in cluster as it is set to
        cluster's 'status' parameter (unless it is already set to
        another method, in which case, this method should be called
        through chaining).
        """
        if status == DispyJob.Created:
            self._cluster_lock.acquire()
            cluster_info.jobs_submitted += 1
            cluster_info.jobs[id(job)] = job
            self._cluster_lock.release()
            return
        if status == DispyJob.Finished or status == DispyJob.Terminated or \
           status == DispyJob.Cancelled or status == DispyJob.Abandoned:
            self._cluster_lock.acquire()
            cluster_info.jobs_done += 1
            cluster_info.jobs.pop(id(job), None)
            self._cluster_lock.release()

        if node is not None:
            # even if node closed, keep it; let UI decide how to indicate status
            self._cluster_lock.acquire()
            cluster_info.status[node.ip_addr] = node
            cluster_info.updates[node.ip_addr] = node
            self._cluster_lock.release()

    def shutdown(self, wait=True):
        """This method should be called by user program to close the
        http server.
        """
        if wait:
            dispy.logger.info(
                'HTTP server waiting for %s seconds for client updates before quitting',
                self._poll_sec)
            time.sleep(self._poll_sec)
        self._server.shutdown()
        self._server.server_close()

    def add_cluster(self, cluster):
        """If more than one cluster is used in a program, they can be
        added to http server for monitoring.
        """
        if cluster.name in self._clusters:
            dispy.logger.warning('Cluster "%s" is already registered' % (cluster.name))
            return
        cluster_info = self.__class__._ClusterInfo(cluster)
        self._clusters[cluster.name] = cluster_info
        if cluster.status_callback is None:
            cluster.status_callback = functools.partial(self.cluster_status, cluster_info)

    def del_cluster(self, cluster):
        """When a cluster is no longer needed to be monitored with
        http server, the cluster can be removed from http server with
        this method.
        """
        self._clusters.pop(cluster.name)
