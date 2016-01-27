#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entry point module
"""
# pragma: no cover
from __future__ import print_function, unicode_literals

import os
import logging
import json
import sys
from io import open  #pylint:disable=redefined-builtin

import six
from guessit.jsonutils import GuessitEncoder

from guessit.__version__ import __version__
from guessit.options import argument_parser
from guessit import api


def guess_filename(filename, options):
    """
    Guess a single filename using given options
    """
    if not options.yaml and not options.json and not options.show_property:
        print('For:', filename)

    cmd_options = vars(options)
    cmd_options['implicit'] = True  # Force implicit option in CLI

    guess = api.guessit(filename, vars(options))

    if options.show_property:
        print(guess.get(options.show_property, ''))
        return

    if options.json:
        print(json.dumps(guess, cls=GuessitEncoder, ensure_ascii=False))
    elif options.yaml:
        import yaml
        from guessit import yamlutils

        ystr = yaml.dump({filename: dict(guess)}, Dumper=yamlutils.CustomDumper, default_flow_style=False,
                         allow_unicode=True)
        i = 0
        for yline in ystr.splitlines():
            if i == 0:
                print("? " + yline[:-1])
            elif i == 1:
                print(":" + yline[1:])
            else:
                print(yline)
            i += 1
    else:
        print('GuessIt found:', json.dumps(guess, cls=GuessitEncoder, indent=4, ensure_ascii=False))


def display_properties(options):
    """
    Display properties
    """
    properties = api.properties(options)

    if options.json:
        if options.values:
            print(json.dumps(properties, cls=GuessitEncoder, ensure_ascii=False))
        else:
            print(json.dumps(list(properties.keys()), cls=GuessitEncoder, ensure_ascii=False))
    elif options.yaml:
        import yaml
        from guessit import yamlutils
        if options.values:
            print(yaml.dump(properties, Dumper=yamlutils.CustomDumper, default_flow_style=False, allow_unicode=True))
        else:
            print(yaml.dump(list(properties.keys()), Dumper=yamlutils.CustomDumper, default_flow_style=False,
                            allow_unicode=True))
    else:
        print('GuessIt properties:')

        properties_list = list(sorted(properties.keys()))
        for property_name in properties_list:
            property_values = properties.get(property_name)
            print(2 * ' ' + '[+] %s' % (property_name,))
            if property_values and options.values:
                for property_value in property_values:
                    print(4 * ' ' + '[!] %s' % (property_value,))


def main(args=None):  # pylint:disable=too-many-branches
    """
    Main function for entry point
    """
    if six.PY2 and os.name == 'nt':  # pragma: no cover
        # see http://bugs.python.org/issue2128
        import locale

        for i, j in enumerate(sys.argv):
            sys.argv[i] = j.decode(locale.getpreferredencoding())

    if args is None:  # pragma: no cover
        options = argument_parser.parse_args()
    else:
        options = argument_parser.parse_args(args)
    if options.verbose:
        logging.basicConfig(stream=sys.stdout, format='%(message)s')
        logging.getLogger().setLevel(logging.DEBUG)

    help_required = True

    if options.version:
        print('+-------------------------------------------------------+')
        print('+                   GuessIt ' + __version__ + (28 - len(__version__)) * ' ' + '+')
        print('+-------------------------------------------------------+')
        print('|      Please report any bug or feature request at      |')
        print('|       https://github.com/wackou/guessit/issues.       |')
        print('+-------------------------------------------------------+')
        help_required = False

    if options.yaml:
        try:
            import yaml  # pylint:disable=unused-variable
        except ImportError:  # pragma: no cover
            options.yaml = False
            print('PyYAML is not installed. \'--yaml\' option will be ignored ...', file=sys.stderr)

    if options.properties or options.values:
        display_properties(options)
        help_required = False

    filenames = []
    if options.filename:
        for filename in options.filename:
            if not isinstance(filename, six.text_type):  # pragma: no cover
                encoding = sys.getfilesystemencoding()
                filename = filename.decode(encoding)
            filenames.append(filename)
    if options.input_file:
        input_file = open(options.input_file, 'r', encoding='utf-8')
        try:
            filenames.extend([line.strip() for line in input_file.readlines()])
        finally:
            input_file.close()

    filenames = list(filter(lambda f: f, filenames))

    if filenames:
        for filename in filenames:
            help_required = False
            guess_filename(filename, options)

    if help_required:  # pragma: no cover
        argument_parser.print_help()


if __name__ == '__main__':  # pragma: no cover
    main()
