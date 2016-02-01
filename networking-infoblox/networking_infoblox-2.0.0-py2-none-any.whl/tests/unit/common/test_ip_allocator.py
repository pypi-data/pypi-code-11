# Copyright 2015 Infoblox Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from infoblox_client import objects as ib_objects

from networking_infoblox.neutron.common import ip_allocator
from networking_infoblox.tests import base


class FixedAddressAllocatorTestCase(base.TestCase):
    def setUp(self):
        super(FixedAddressAllocatorTestCase, self).setUp()
        self.ib_mock = mock.Mock()

        self.extattrs = 'test-extattrs'
        self.netview = 'some-test-net-view'
        self.mac = 'de:ad:be:ef:00:00'
        self.ip = '192.168.1.1'
        self.dnsview = 'some-dns-view'
        self.zone_auth = 'zone-auth'
        self.hostname = 'host1'
        self.dhcp_enabled = True

        options = {'use_host_record': False}

        self.allocator = ip_allocator.IPAllocator(self.ib_mock, options)

    def test_creates_fixed_address_on_allocate_ip(self):
        self.allocator.allocate_given_ip(
            self.netview, self.dnsview, self.zone_auth,
            self.hostname, self.mac, self.ip, self.extattrs)

        self.ib_mock.create_fixed_address_for_given_ip.assert_called_once_with(
            self.netview, self.mac, self.ip, self.extattrs)

    def test_creates_fixed_address_range_on_range_allocation(self):
        first_ip = '192.168.1.1'
        last_ip = '192.168.1.123'

        self.allocator.allocate_ip_from_range(
            self.netview, self.dnsview, self.zone_auth, self.hostname,
            self.mac, first_ip, last_ip, self.extattrs)

        self.ib_mock.create_fixed_address_from_range.assert_called_once_with(
            self.netview, self.mac, first_ip, last_ip, self.extattrs)

    def test_deletes_fixed_address(self):
        self.allocator.deallocate_ip(self.netview, self.dnsview, self.ip)

        self.ib_mock.delete_fixed_address.assert_called_once_with(self.netview,
                                                                  self.ip)


class HostRecordAllocatorTestCase(base.TestCase):

    def _test_creates_host_record_on_allocate_ip(self, use_dhcp):
        ib_mock = mock.MagicMock()

        netview = 'some-test-net-view'
        dnsview = 'some-dns-view'
        zone_auth = 'zone-auth'
        hostname = 'host1'
        mac = 'de:ad:be:ef:00:00'
        ip = '192.168.1.1'

        ib_mock.find_hostname.return_value = None
        options = {'use_host_record': True,
                   'configure_for_dhcp': use_dhcp}

        allocator = ip_allocator.IPAllocator(ib_mock, options)
        allocator.allocate_given_ip(netview, dnsview, zone_auth, hostname,
                                    mac, ip)

        ib_mock.create_host_record_for_given_ip.assert_called_once_with(
            dnsview, zone_auth, hostname, mac, ip, mock.ANY, use_dhcp)

    def test_creates_host_record_on_allocate_ip_use_dhcp(self):
        self._test_creates_host_record_on_allocate_ip(True)

    def test_creates_host_record_on_allocate_ip_no_dhcp(self):
        self._test_creates_host_record_on_allocate_ip(False)

    def _test_creates_host_record_range_on_range_allocation(self, use_dhcp):
        ib_mock = mock.MagicMock()

        netview = 'some-test-net-view'
        dnsview = 'some-dns-view'
        zone_auth = 'zone-auth'
        hostname = 'host1'
        mac = 'de:ad:be:ef:00:00'
        first_ip = '192.168.1.2'
        last_ip = '192.168.1.254'

        ib_mock.find_hostname.return_value = None
        options = {'use_host_record': True,
                   'configure_for_dhcp': use_dhcp}

        allocator = ip_allocator.IPAllocator(ib_mock, options)
        allocator.allocate_ip_from_range(
            netview, dnsview, zone_auth, hostname, mac, first_ip, last_ip)

        ib_mock.create_host_record_from_range.assert_called_once_with(
            dnsview, netview, zone_auth, hostname,
            mac, first_ip, last_ip, mock.ANY, use_dhcp)

    def test_creates_host_record_range_on_range_allocation_use_dhcp(self):
        self._test_creates_host_record_range_on_range_allocation(True)

    def _test_creates_host_record_range_on_range_allocation_no_dhcp(self):
        self._test_creates_host_record_range_on_range_allocation(False)

    def test_deletes_host_record(self):
        ib_mock = mock.MagicMock()

        netview = 'some-test-net-view'
        dnsview = 'some-dns-view'
        ip_1 = ['192.168.1.2', 'de:ad:be:ef:00:00']
        ip_2 = ['192.168.1.3', 'ff:ee:be:ae:12:00']

        options = {'use_host_record': True}

        allocator = ip_allocator.IPAllocator(ib_mock, options)
        host_record_mock = mock.Mock()
        ip_obj_1 = ib_objects.IP.create(ip=ip_1[0], mac=ip_1[1])
        ip_obj_2 = ib_objects.IP.create(ip=ip_2[0], mac=ip_2[1])
        host_record_mock.ip = [ip_obj_1, ip_obj_2]
        allocator.manager.get_host_record = mock.Mock()
        allocator.manager.get_host_record.return_value = host_record_mock

        allocator.deallocate_ip(netview, dnsview, ip_1[0])

        ib_mock.delete_ip_from_host_record.assert_called_once_with(
            host_record_mock, ip_1[0])
