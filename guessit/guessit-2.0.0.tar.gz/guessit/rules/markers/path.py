#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Path markers
"""
from __future__ import unicode_literals

from rebulk import Rebulk

from rebulk.utils import find_all


def path():
    """
    Builder for rebulk object.
    :return: Created Rebulk object
    :rtype: Rebulk
    """
    rebulk = Rebulk()
    rebulk.defaults(name="path", marker=True)

    def mark_path(input_string, context):
        """
        Functional pattern to mark path elements.

        :param input_string:
        :return:
        """
        ret = []
        if context.get('name_only', False):
            ret.append((0, len(input_string)))
        else:
            indices = list(find_all(input_string, '/'))
            indices += list(find_all(input_string, r'\\'))
            indices += [-1, len(input_string)]

            indices.sort()

            for i in range(0, len(indices) - 1):
                ret.append((indices[i] + 1, indices[i + 1]))

        return ret

    rebulk.functional(mark_path)
    return rebulk
