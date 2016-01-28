#!/usr/bin/env python3.4
#
# Copyright (c) 2013-2015 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

# To run this program, the file ``ssh_host_key`` must exist with an SSH
# private key in it to use as a server host key. An SSH host certificate
# can optionally be provided in the file ``ssh_host_key-cert.pub``.
#
# Authentication requires the directory authorized_keys to exist with
# files in it named based on the username containing the client keys
# and certificate authority keys which are accepted for that user.

import asyncio, asyncssh, sys

class MySSHServerSession(asyncssh.SSHServerSession):
    def connection_made(self, chan):
        self._chan = chan

    def shell_requested(self):
        return True

    def session_started(self):
        self._chan.write('Welcome to my SSH server, %s!\r\n' %
                             self._chan.get_extra_info('username'))
        self._chan.exit(0)

class MySSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self._conn = conn

    def begin_auth(self, username):
        try:
            self._conn.set_authorized_keys('authorized_keys/%s' % username)
        except IOError:
            pass

        return True

    def session_requested(self):
        return MySSHServerSession()

@asyncio.coroutine
def start_server():
    yield from asyncssh.create_server(MySSHServer, '', 8022,
                                      server_host_keys=['ssh_host_key'])

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()
