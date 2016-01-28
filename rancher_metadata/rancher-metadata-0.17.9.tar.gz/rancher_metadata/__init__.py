#
# __init__.py
#
# Author: Matteo Cerutti <matteo.cerutti@hotmail.co.uk>
#

import requests
import json
import time
import collections
import re

class MetadataAPI:
  def __init__(self, **kwargs):
    if 'api_url' not in kwargs:
      self.api_url = ["http://rancher-metadata/2015-12-19"]
    else:
      if isinstance(kwargs['api_url'], list):
        api_url = kwargs['api_url']
      else:
        api_url = [kwargs['api_url']]

      self.api_url = []
      for url in api_url: 
        self.api_url.append(url.rstrip('/'))

    if 'max_attempts' in kwargs:
      self.max_attempts = kwargs['max_attempts']
    else:
      self.max_attempts = 3

  def is_error(self, data):
    if isinstance(data, dict):
      if 'code' in data and data['code'] == 404:
        return True

    return False

  def api_get(self, query):
    success = False
    i = 1

    while (i <= self.max_attempts and not success):
      for url in self.api_url:
        try:
          req = requests.get("%s%s" % (url, query), headers = {"Content-Type": "application/json", "Accept": "application/json"}).json()
          data = self.no_unicode(req)
          success = True
          break
        except Exception as e:
          print("Failed to query Rancher Metadata API on %s - Caught exception (%s)" % (url, str(e)))

      i = i + 1

    if not success:
      raise RuntimeError("Failed to query Rancher Metadata API (%d out of %d attempts failed)" % (i, self.max_attempts))

    if self.is_error(data):
      return None
    else:
      return data

  def get_services(self):
    return self.api_get("/services")

  def get_service(self, **kwargs):
    if not kwargs:
      return self.api_get("/self/service")
    else:
      if 'service_name' not in kwargs:
        raise ValueError("Must provide the service name")

      if 'stack_name' not in kwargs:
        return self.api_get("/self/stack/services/%s" % kwargs['service_name'])
      else:
        return self.api_get("/stacks/%s/services/%s" % (kwargs['stack_name'], kwargs['service_name']))

  def get_service_field(self, field, **kwargs):
    if not kwargs:
      return self.api_get("/self/service/%s" % field)
    else:
      if 'service_name' not in kwargs:
        raise ValueError("Must provide service name")

      if 'stack_name' not in kwargs:
        return self.api_get("/self/stack/services/%s/%s" % (kwargs['service_name'], field))
      else:
        return self.api_get("/stacks/%s/services/%s/%s" % (kwargs['stack_name'], kwargs['service_name'], field))

  def get_service_scale_size(self, **kwargs):
    return self.get_service_field("scale", **kwargs)

  def get_service_containers(self, **kwargs):
    containers = {}

    for container in self.get_service_field("containers", **kwargs):
      containers[container['name']] = container

      # FIXME: until https://github.com/rancher/cattle/pull/1197 gets merged
      if 'service_suffix' not in container:
        containers[container['name']]['service_suffix'] = self.get_container_service_suffix(container['name'])

    return containers

  def get_service_metadata(self, **kwargs):
    return self.get_service_field("metadata", **kwargs)

  def get_service_links(self, **kwargs):
    return self.get_service_field("links", **kwargs)

  def wait_service_containers(self, **kwargs):
    scale = self.get_service_scale_size(**kwargs)

    old = []
    while True:
      containers = self.get_service_containers(**kwargs)
      new = containers.keys()

      for name in list(set(new) - set(old)):
        # FIXME: until https://github.com/rancher/cattle/pull/1197 gets merged
        if 'service_suffix' not in containers[name]:
          containers[name]['service_suffix'] = self.get_container_service_suffix(name)

        yield (name, containers[name])

      old = new

      if (len(new) < scale):
        time.sleep(0.5)
      else:
        break

  def get_stacks(self):
    return self.api_get("/stacks")

  def get_stack(self, stack_name = None):
    if stack_name is None:
      return self.api_get("/self/stack")
    else:
      return self.api_get("/stacks/%s" % stack_name)

  def get_stack_services(self, stack_name = None):
    if stack_name is None:
      return self.api_get("/self/stack/services")
    else:
      return self.api_get("/stacks/%s/services" % stack_name)

  def get_containers(self):
    return self.api_get("/containers")

  def get_container(self, container_name = None):
    container = None

    if container_name is None:
      container = self.api_get("/self/container")
    else:
      container = self.api_get("/containers/%s" % container_name)

    # FIXME: until https://github.com/rancher/cattle/pull/1197 gets merged
    if container and 'service_suffix' not in container:
      container['service_suffix'] = self.get_container_service_suffix(container_name)

    return container

  def get_container_field(self, field, container_name):
    if container_name is None:
      return self.api_get("/self/container/%s" % field)
    else:
      return self.api_get("/containers/%s/%s" % (container_name, field))

  def get_container_id(self, container_name = None):
    self.get_container_create_index(container_name)

  def get_container_create_index(self, container_name = None):
    i = self.get_container_field("create_index", container_name)

    if i:
      return int(i)
    else:
      return None

  def get_container_ip(self, container_name = None):
    if container_name is None:
      # are we running within the rancher managed network?
      # FIXME: https://github.com/rancher/rancher/issues/2750
      if self.is_network_managed():
        return self.api_get("/self/container/primary_ip")
      else:
        return self.get_host_ip()
    else:
      return self.api_get("/containers/%s/primary_ip" % container_name)

  def get_container_name(self, container_name = None):
    return self.get_container_field("name", container_name)

  def get_container_service_name(self, container_name = None):
    return self.get_container_field("service_name", container_name)

  def get_container_stack_name(self, container_name = None):
    return self.get_container_field("stack_name", container_name)

  def get_container_hostname(self, container_name = None):
    return self.get_container_field("hostname", container_name)

  def get_container_service_id(self, container_name = None):
    return self.get_container_service_suffix(container_name)

  def get_container_service_suffix(self, container_name = None):
    index = None

    service_index = self.get_container_field("service_suffix", container_name)

    # use the container name index as the unique service index
    if service_index is None:
      m = re.search("(\d+)$", self.get_container_name(container_name))
      if m:
        index = int(m.group(1))
    else:
      index = int(service_index)

    return index

  def get_container_host_uuid(self, container_name = None):
    return self.get_container_field("host_uuid", container_name)

  def is_network_managed(self):
    # in managed network, we don't get to see any information about the container :(

    if self.get_container_id():
      return True
    else:
      return False

  def get_hosts(self):
    return self.api_get("/hosts")

  def get_host(self, host_name):
    if host_name is None:
      return self.api_get("/self/host")
    else:
      return self.api_get("/hosts/%s" % host_name)

  def get_host_field(self, field, host_name):
    if host_name is None:
      return self.api_get("/self/host/%s" % field)
    else:
      return self.api_get("/hosts/%s/%s" % (host_name, field))

  def get_host_ip(self, host_name = None):
    return self.get_host_field("agent_ip", host_name)

  def get_host_uuid(self, host_name = None):
    return self.get_host_field("uuid", host_name)

  def get_host_name(self, host_name = None):
    return self.get_host_field("name", host_name)

  def no_unicode(self, h):
    if isinstance(h, basestring):
      return str(h)
    elif isinstance(h, dict):
      return dict(map(self.no_unicode, h.iteritems()))
    elif isinstance(h, collections.Iterable):
      return type(h)(map(self.no_unicode, h))
    else:
      return h
