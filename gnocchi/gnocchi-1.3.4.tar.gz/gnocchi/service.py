# Copyright (c) 2013 Mirantis Inc.
# Copyright (c) 2015 eNovance
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import multiprocessing

from oslo_config import cfg
from oslo_db import options as db_options
from oslo_log import log
from oslo_policy import opts as policy_opts

from gnocchi import archive_policy
from gnocchi import opts

LOG = log.getLogger(__name__)


def prepare_service(args=None):
    conf = cfg.ConfigOpts()
    # FIXME(jd) Use the pkg_entry info to register the options of these libs
    log.register_options(conf)
    db_options.set_defaults(conf)
    policy_opts.set_defaults(conf)

    # Register our own Gnocchi options
    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == "DEFAULT" else group)

    # HACK(jd) I'm not happy about that, fix AP class to handle a conf object?
    archive_policy.ArchivePolicy.DEFAULT_AGGREGATION_METHODS = (
        conf.archive_policy.default_aggregation_methods
    )

    try:
        default_workers = multiprocessing.cpu_count() or 1
    except NotImplementedError:
        default_workers = 1

    conf.set_default("workers", default_workers, group="api")
    conf.set_default("workers", default_workers, group="metricd")

    conf(args, project='gnocchi', validate_default_values=True)
    log.setup(conf, 'gnocchi')
    conf.log_opt_values(LOG, logging.DEBUG)

    return conf
