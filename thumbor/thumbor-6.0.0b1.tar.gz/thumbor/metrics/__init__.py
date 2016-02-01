#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


class BaseMetrics(object):

    def __init__(self, config):
        self.config = config

    def incr(self, metricname, value=1):
        raise NotImplementedError()

    def timing(self, metricname, value):
        raise NotImplementedError()
