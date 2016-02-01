import sys
import argparse

from dockervolume.log import setup_logging
from dockervolume.core import VolumeCommand
from dockervolume.bootstraps import bootstrap
from dockervolume.utils import (
    DEFAULT_CONF,
    DEFAULT_MACHINE_NAME,
    search_docker_voluem_yml,
    )


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('volumes', nargs='*')
    parser.add_argument('-m', '--machine', default=DEFAULT_MACHINE_NAME)
    parser.add_argument('--conf', default=DEFAULT_CONF)
    parser.add_argument('--dry-run', default=False, action='store_true')
    args = parser.parse_args(argv)

    machine = args.machine
    volumes = args.volumes
    conf = search_docker_voluem_yml(args.conf)
    dry_run = args.dry_run

    setup_logging()
    registry = bootstrap(name=machine, conf=conf, dry_run=dry_run)
    execute = VolumeCommand(registry)
    execute('directory', *volumes)

if __name__ == '__main__':
    sys.exit(main())
