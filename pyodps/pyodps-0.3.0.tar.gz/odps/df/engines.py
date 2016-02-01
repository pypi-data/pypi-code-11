#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from enum import Enum

from .backends.odpssql.engine import ODPSEngine
from .errors import NoBackendFound
from ..models import Table
from ..config import options
from .. import ODPS


class Engines(Enum):
    ODPS = 'ODPS'


def available_engines(expr):
    engines = set()

    for src in expr.data_source():
        if isinstance(src, Table):
            engines.add(Engines.ODPS)

    return engines


def _build_odps_from_table(table):
    client = table._client

    account = client.account
    endpoint = client.endpoint
    project = client.project

    return ODPS(account.access_id, account.secret_access_key,
                project, endpoint=endpoint)


def get_default_engine(expr):
    for src in expr.data_source():
        if isinstance(src, Table):
            return ODPSEngine(_build_odps_from_table(src))

    raise NoBackendFound('No backend found for expression: %s' % expr)
