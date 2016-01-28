#!/usr/bin/env python3.4
#
# Copyright (c) 2015 by Ron Frederick <ronf@timeheart.net>.
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

import asyncio, asyncssh, sys

@asyncio.coroutine
def run_client():
    with (yield from asyncssh.connect('localhost')) as conn:
        with (yield from conn.start_sftp_client()) as sftp:
            yield from sftp.get('example.txt')

    yield from conn.wait_closed()

try:
    asyncio.get_event_loop().run_until_complete(run_client())
except (OSError, asyncssh.Error) as exc:
    sys.exit('SFTP operation failed: ' + str(exc))
