'''
:Author: Juti Noppornpitak

The module contains the package entity used to be an intermediate between :class:`imagination.locator.Locator`
and :class:`imagination.loader.Loader` and simulate the singleton class on the package in the Loader.

.. note::
    Copyright (c) 2012 Juti Noppornpitak

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
    of the Software, and to permit persons to whom the Software is furnished to do
    so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
    PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from imagination.common              import InterceptableObject
from imagination.decorator.validator import restrict_type
from imagination.loader              import Loader
from imagination.proxy               import Proxy

class CallbackProxy(object):
    """Callback Proxy

    .. codeauthor:: Juti Noppornpitak <juti_n@yahoo.co.jp>
    .. versionadded:: 1.6

    .. warning:: experimental feature
    """
    def __init__(self, callback, *args, **kwargs):
        if not callable(callback):
            raise ValueError('The callback object is required for {}.'.format(self.__class__.__name__))

        self.__callback = callback
        self.__args     = args
        self.__kwargs   = kwargs

    def __call__(self):
        return self.__callback(*self.__args, **self.__kwargs)

class Entity(InterceptableObject):
    '''
    Entity represents the package, reference and instance of the reference.

    :param `id`:     the service identifier (string).
    :param `loader`: a service loader which is an instance of :class:`imagination.loader.Loader`.
    :param `args`:   constructor's parameters
    :type args:      list or tuple
    :param `kwargs`: constructor's parameters
    :type args:      dict

    If the loader is not an instance of :class:`imagination.loader.Loader` or
    any classes based on :class:`imagination.loader.Loader`, the exception
    :class:`imagination.exception.UnknownLoaderError` will be thrown.

    .. note::
        This class is to similar to the decorator `tori.decorator.common.singleton`
        and `tori.decorator.common.singleton_with` from Tori Framework, except
        that it is not a singleton class and so any arbitrary class referenced
        by the *loader* only lasts as long as the entity lives.

    .. note::
        In version 1.5, the entity has the ability to fork an non-supervised
        instance of the reference.
    '''

    @restrict_type(None, Loader)
    def __init__(self, id, loader, *args, **kwargs):
        super(Entity, self).__init__()

        self._id       = id
        self._loader   = loader
        self._args     = args
        self._kwargs   = kwargs
        self._instance = None
        self._tags     = []
        self._prepared = False

    @property
    def id(self):
        '''
        Entity ID

        :rtype: strint or unicode or integer
        '''
        return self._id

    @property
    def loader(self):
        '''
        Package loader

        :rtype: imagination.loader.Loader
        '''
        return self._loader

    @property
    def argument_list(self):
        ''' Get the argument list. '''
        return self._args

    @property
    def argument_dictionary(self):
        ''' Get the argument dictionary. '''
        return self._kwargs

    @property
    def activated(self):
        '''
        Check if the entity is already activated.

        This will also inspects if the entity already loads a singleton instance into the memory.
        '''
        return self._instance is not None

    @property
    def tags(self):
        '''
        Retrieve the entity tags.

        :rtype: list
        '''
        return self._tags

    @tags.setter
    @restrict_type(list)
    def tags(self, tags):
        '''
        Define the entire entity tags.

        :param tags: new tags as replacements
        :type  tags: list or tuple
        '''
        if self.locked:
            raise LockedEntityException

        self._tags = tags

    @property
    def instance(self):
        ''' Get the singleton instance of the class defined for the loader. '''
        if not self._instance:
            self._instance = self.fork()

        return self._instance

    def fork(self):
        '''
        :Version: 1.5

        Fork an instance of the class defined for the loader.
        '''
        self.__prepare()

        instance = self._loader.package(*self._args, **self._kwargs)

        # Return the instance if this entity is not interceptable.
        if not self.interceptable:
            return instance

        # For each PUBLIC method, make it interceptable with Action.
        self._bind_interceptions(instance, self._interceptions)

        return instance

    def __prepare(self):
        if self._prepared or self._instance:
            return

        for i in range(len(self._args)):
            if isinstance(self._args[i], Proxy):
                self._args[i] = self._args[i].load()

        for i in self._kwargs:
            if isinstance(self._kwargs[i], Proxy):
                self._kwargs[i] = self._kwargs[i].load()

        self._prepared = True
