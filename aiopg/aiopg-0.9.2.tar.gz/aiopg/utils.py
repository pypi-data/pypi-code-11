import asyncio
import sys


PY_35 = sys.version_info >= (3, 5)
if PY_35:
    from collections.abc import Coroutine
    base = Coroutine
else:
    base = object


class _ContextManager(base):

    __slots__ = ('_coro', '_obj')

    def __init__(self, coro):
        self._coro = coro
        self._obj = None

    def send(self, value):
        return self._coro.send(value)

    def throw(self, typ, val=None, tb=None):
        if val is None:
            return self._coro.throw(typ)
        elif tb is None:
            return self._coro.throw(typ, val)
        else:
            return self._coro.throw(typ, val, tb)

    def close(self):
        return self._coro.close()

    @property
    def gi_frame(self):
        return self._coro.gi_frame

    @property
    def gi_running(self):
        return self._coro.gi_running

    @property
    def gi_code(self):
        return self._coro.gi_code

    def __next__(self):
        return self.send(None)

    @asyncio.coroutine
    def __iter__(self):
        resp = yield from self._coro
        return resp

    if PY_35:
        def __await__(self):
            resp = yield from self._coro
            return resp

        @asyncio.coroutine
        def __aenter__(self):
            self._obj = yield from self._coro
            return self._obj

        @asyncio.coroutine
        def __aexit__(self, exc_type, exc, tb):
            self._obj.close()
            self._obj = None


class _SAConnectionContextManager(_ContextManager):

    if PY_35:  # pragma: no branch
        @asyncio.coroutine
        def __aiter__(self):
            result = yield from self._coro
            return result


class _PoolContextManager(_ContextManager):

    if PY_35:
        @asyncio.coroutine
        def __aexit__(self, exc_type, exc, tb):
            self._obj.close()
            yield from self._obj.wait_closed()
            self._obj = None


class _TransactionContextManager(_ContextManager):

    if PY_35:

        @asyncio.coroutine
        def __aexit__(self, exc_type, exc, tb):
            if exc_type:
                yield from self._obj.rollback()
            else:
                if self._obj.is_active:
                    yield from self._obj.commit()
            self._obj = None


class _PoolAcquireContextManager(_ContextManager):

    __slots__ = ('_coro', '_conn', '_pool')

    def __init__(self, coro, pool):
        self._coro = coro
        self._conn = None
        self._pool = pool

    if PY_35:
        @asyncio.coroutine
        def __aenter__(self):
            self._conn = yield from self._coro
            return self._conn

        @asyncio.coroutine
        def __aexit__(self, exc_type, exc, tb):
            yield from self._pool.release(self._conn)
            self._pool = None
            self._conn = None


class _PoolConnectionContextManager:
    """Context manager.

    This enables the following idiom for acquiring and releasing a
    connection around a block:

        with (yield from pool) as conn:
            cur = yield from conn.cursor()

    while failing loudly when accidentally using:

        with pool:
            <block>
    """

    __slots__ = ('_pool', '_conn')

    def __init__(self, pool, conn):
        self._pool = pool
        self._conn = conn

    def __enter__(self):
        assert self._conn
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._pool.release(self._conn)
        finally:
            self._pool = None
            self._conn = None

    if PY_35:
        @asyncio.coroutine
        def __aenter__(self):
            assert not self._conn
            self._conn = yield from self._pool.acquire()
            return self._conn

        @asyncio.coroutine
        def __aexit__(self, exc_type, exc_val, exc_tb):
            try:
                yield from self._pool.release(self._conn)
            finally:
                self._pool = None
                self._conn = None


class _PoolCursorContextManager:
    """Context manager.

    This enables the following idiom for acquiring and releasing a
    cursor around a block:

        with (yield from pool.cursor()) as cur:
            yield from cur.execute("SELECT 1")

    while failing loudly when accidentally using:

        with pool:
            <block>
    """

    __slots__ = ('_pool', '_conn', '_cur')

    def __init__(self, pool, conn, cur):
        self._pool = pool
        self._conn = conn
        self._cur = cur

    def __enter__(self):
        return self._cur

    def __exit__(self, *args):
        try:
            self._cur.close()
            self._pool.release(self._conn)
        finally:
            self._pool = None
            self._conn = None
            self._cur = None


if not PY_35:
    try:
        from asyncio import coroutines
        coroutines._COROUTINE_TYPES += (_ContextManager,)
    except:
        pass
