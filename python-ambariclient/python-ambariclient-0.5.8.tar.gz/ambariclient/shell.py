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

import argparse
import functools
import json
import logging
import os
import six
import sys
import traceback

from ambariclient.client import Ambari, ENTRY_POINTS
from ambariclient import events, base, models, utils

logging.basicConfig(level=logging.CRITICAL)
LOG = logging.getLogger(__name__)
LOG.addHandler(utils.NullHandler())


def model_event(event, event_state, obj, **kwargs):
    # pylint: disable=unused-argument
    line_end = "\n" if event_state == events.states.FINISHED else ""
    six.print_("%s %s '%s': %s%s" % (utils.normalize_underscore_case(event),
                                     utils.normalize_camel_case(obj.__class__.__name__),
                                     obj.identifier, event_state, line_end))


def request_progress(request, **kwargs):
    # pylint: disable=unused-argument
    six.print_("Wait for %s: %.2f%%" % (request.request_context, request.progress_percent))


def request_done(request, **kwargs):
    # pylint: disable=unused-argument
    six.print_("Wait for %s: FINISHED\n" % (request.request_context))


def bootstrap_progress(bootstrap, **kwargs):
    # pylint: disable=unused-argument
    hostnames = [x.host_name for x in bootstrap.hosts]
    six.print_("Wait for Bootstrap Hosts %s: %s" % (hostnames, bootstrap.status))


def bootstrap_done(bootstrap, **kwargs):
    # pylint: disable=unused-argument
    hostnames = [x.host_name for x in bootstrap.hosts]
    six.print_("Wait for Bootstrap Hosts %s: FINISHED\n" % (hostnames))


def host_progress(host, **kwargs):
    # pylint: disable=unused-argument
    six.print_("Wait for %s: %s/%s" % (host.host_name, host.host_status, host.host_state))


def host_done(host, **kwargs):
    # pylint: disable=unused-argument
    six.print_("Wait for %s: FINISHED\n" % host.host_name)


def reference(model_class=None, stack=None):
    if stack is None:
        stack = ['ambari']

    if model_class:
        relationships = model_class.relationships
    else:
        relationships = ENTRY_POINTS

    for rel in sorted(relationships.keys()):
        new_stack = list(stack)
        new_stack.append(rel)
        six.print_('.'.join(new_stack))
        rel_model_class = relationships[rel]
        if rel_model_class.primary_key is not None:
            new_stack[-1] = "%s(%s)" % (new_stack[-1], rel_model_class.primary_key)
            six.print_('.'.join(new_stack))
            reference(model_class=rel_model_class, stack=new_stack)


def get_default_config():
    return {
        "host": "http://c6401.ambari.apache.org:8080",
        "username": "admin",
        "password": "admin",
        "logger": logging.CRITICAL,
    }


def parse_config_file():
    config_path = os.path.expanduser('~/.ambari')
    if os.path.isfile(config_path):
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    return {}


def parse_cli_opts():
    args = os.environ.get('AMBARI_SHELL_ARGS')
    if args:
        parser = argparse.ArgumentParser(prog='ambari-shell')
        parser.add_argument('--host',
                            help='hostname for the ambari server '
                                 '(i.e. ambari.apache.org or http://ambari.apache.org:8080)')
        parser.add_argument('--port', type=int,
                            help='port for the ambari server '
                                 '(can be included in the host)')
        parser.add_argument('--protocol', choices=['http', 'https'],
                            help='protocol for the ambari server '
                                 '(can be included in the host)')
        parser.add_argument('--no-validate-ssl', action='store_const', const=True,
                            help='disable ssl certificate validation')
        parser.add_argument('--username',
                            help='username for the ambari server')
        parser.add_argument('--password',
                            help='password for the ambari server')
        parser.add_argument('--logger',
                            help='default logger level (default is CRITICAL)')
        opts = vars(parser.parse_args(args.split()))
        return dict((x, opts[x]) for x in opts if opts[x] is not None)

    return {}


def log(level):
    six.print_("Logging level set to %s" % level)
    logging.getLogger().setLevel(level)


if os.environ.get('PYTHONSTARTUP', '') == __file__:
    # Invoke IPython shell
    try:
        from IPython.terminal.embed import InteractiveShellEmbed
    except ImportError:
        six.print_('''
Error: IPython is not installed. Try running:

    pip install IPython
''', file=sys.stderr)
        sys.exit(1)

    for event_name in ['create', 'update', 'delete']:
        for state in [events.states.STARTED, events.states.FINISHED]:
            callback = functools.partial(model_event, event_name, state)
            events.subscribe(base.Model, event_name, callback, state)

    events.subscribe(models.Request, 'wait', request_progress, events.states.PROGRESS)
    events.subscribe(models.Request, 'wait', request_done, events.states.FINISHED)
    events.subscribe(models.Bootstrap, 'wait', bootstrap_progress, events.states.PROGRESS)
    events.subscribe(models.Bootstrap, 'wait', bootstrap_done, events.states.FINISHED)
    events.subscribe(models.Host, 'wait', host_progress, events.states.PROGRESS)
    events.subscribe(models.Host, 'wait', host_done, events.states.FINISHED)

    config = get_default_config()
    config.update(parse_config_file())
    config.update(parse_cli_opts())

    config['validate_ssl'] = not config.pop('no_validate_ssl', False)

    if 'logger' in config:
        log(config.pop('logger'))

    ambari = Ambari(**config)

    try:
        version = ambari.version
    except Exception:  # pylint: disable=broad-except
        traceback.print_exc()
        six.print_("\nCould not connect to Ambari server - aborting!", file=sys.stderr)
        sys.exit(1)

    shell_help = "\n".join([
        "Ambari client available as 'ambari'",
        " - Ambari Server is %s" % ambari.base_url,
        " - Ambari Version is %s\n" % utils.version_str(version),
        " - log(new_level) will reset the logger level",
        " - ambari_ref() will show you all available client method chains",
    ])
    shell = InteractiveShellEmbed(user_ns={'ambari': ambari, 'log': log, 'ambari_ref': reference})
    shell(shell_help)
    sys.exit(0)
