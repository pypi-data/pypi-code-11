
# This file is part of PyEMMA.
#
# Copyright (c) 2015, 2014 Computational Molecular Biology Group, Freie Universitaet Berlin (GER)
#
# PyEMMA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
Created on 30.08.2015

@author: marscher
'''
from __future__ import absolute_import

from logging import getLogger
import weakref
from itertools import count

__all__ = ['Loggable']


class Loggable(object):
    # counting instances of Loggable, incremented by name property.
    __ids = count(0)
    # holds weak references to instances of this, to clean up logger instances.
    __refs = {}

    @property
    def name(self):
        """The name of this instance"""
        try:
            return self._name
        except AttributeError:
            self._name = "%s.%s[%i]" % (self.__module__,
                                        self.__class__.__name__,
                                        next(Loggable.__ids))
            return self._name

    @property
    def logger(self):
        """The logger for this class instance """
        try:
            return self._logger_instance
        except AttributeError:
            self.__create_logger()
            return self._logger_instance

    @property
    def _logger(self):
        return self.logger

    def __create_logger(self):
        _weak_logger_refs = Loggable.__refs
        # creates a logger based on the the attribe "name" of self
        self._logger_instance = getLogger(self.name)

        # store a weakref to this instance to clean the logger instance.
        logger_id = id(self._logger_instance)
        r = weakref.ref(self, Loggable._cleanup_logger(logger_id, self.name))
        _weak_logger_refs[logger_id] = r

    @staticmethod
    def _cleanup_logger(logger_id, logger_name):
        # callback function used in conjunction with weakref.ref
        # removes logger from root manager

        def remove_logger(weak):
            d = getLogger().manager.loggerDict
            del d[logger_name]
            del Loggable.__refs[logger_id]
        return remove_logger

    def __getstate__(self):
        # do not pickle the logger instance
        d = dict(self.__dict__)
        try:
            del d['_logger_instance']
        except KeyError:
            pass
        return d
