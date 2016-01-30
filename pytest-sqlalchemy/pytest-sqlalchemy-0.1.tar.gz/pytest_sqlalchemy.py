#!/usr/bin/env python
# encoding: utf-8

import pytest

@pytest.fixture(scope="module")
def engine(request, sqlalchemy_connect_url, app_config):
    if app_config:
        from sqlalchemy import engine_from_config
        engine = engine_from_config(app_config)
    elif sqlalchemy_connect_url:
        from sqlalchemy.engine import create_engine
        engine = create_engine(sqlalchemy_connect_url)
    else:
        raise RuntimeError("Can not establish a connection to the database")

    def fin():
        print ("Disposing engine")
        engine.dispose()

    request.addfinalizer(fin)
    return engine


@pytest.fixture(scope="module")
def connection(request, engine):
    connection = engine.connect()

    def fin():
        print ("Closing connection")
        connection.close()

    request.addfinalizer(fin)
    return connection


@pytest.fixture()
def transaction(request, connection):
    """Will start a transaction on the connection. The connection will
    be rolled back after it leaves its scope."""
    transaction = connection.begin()

    def fin():
        print ("Rollback")
        transaction.rollback()

    request.addfinalizer(fin)
    return connection


@pytest.fixture()
def dbsession(request, connection):
    from sqlalchemy.orm import sessionmaker
    return sessionmaker()(bind=connection)


# Config options
@pytest.fixture(scope="session")
def sqlalchemy_connect_url(request):
    return request.config.getoption("--sqlalchemy-connect-url")


def pytest_addoption(parser):
    parser.addoption("--sqlalchemy-connect-url", action="store",
                     default=None,
                     help="Name of the database to connect to")
