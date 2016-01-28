# -*- coding: utf-8 -*-

from contextlib import contextmanager

from six import with_metaclass

from ...utils import pyv
from .query import QueryObject


def key(page_element):
    return page_element.__key__()


def query_set(page_element):
    return page_element.__query_set__()


class ProxyObject(object):

    def __init__(self, we):
        self.__we = we

    def __getattr__(self, item):
        return getattr(self.__we, item)

    def __repr__(self):
        return repr(self.__we)

    def __str__(self):
        return str(self.__we)

    def __dir__(self):
        return dir(self.__we)


class PageCache(dict):

    def __init__(self, *args, **kwargs):
        super(PageCache, self).__init__(*args, **kwargs)

        self.is_eternal = False

    @contextmanager
    def restore(self):
        current_data = self.copy()
        try:
            yield
        finally:
            self.update(current_data)

    def clear(self):
        if not self.is_eternal:
            super(PageCache, self).clear()


class PageElement(object):

    def __init__(self, *args, **options):
        assert bool(args), 'Element can not be created without arguments'

        self.__class = None
        self.__query_set = []

        self.__cached = options.get('cached', None)

        for a in args:
            if pyv.is_class_type(a):
                self.__class = a
                if self.__cached is not False:
                    self.__cached = True
                break
            elif isinstance(a, PageElement):
                self.__query_set.extend(query_set(a))
            elif isinstance(a, QueryObject):
                self.__query_set.append(a)
            else:
                raise ValueError(
                    'Incorrect page object argument {}'.format(a),
                )

        self.__key = options.get('key', None)
        self.__call = options.get('call', None)
        self.__index = options.get('index', None)
        self.__is_list = options.get('is_list', False)
        self.__property = options.get('property', None)
        self.__we_class = options.get('we_class', None)
        self.__list_class = options.get('list_class', None)
        self.__wait_timeout = options.get('wait_timeout', None)

        if self.__list_class and not self.__is_list:
            raise ValueError(
                '"list_class" can not usage without "is_list"',
            )

        if self.__call:
            if self.__list_class:
                self.__list_class = type(
                    self.__list_class.__name__,
                    (self.__list_class, ),
                    {'__call__': self.__call},
                )
            elif self.__we_class and not self.__is_list:
                self.__we_class = type(
                    self.__we_class.__name__,
                    (self.__we_class, ),
                    {'__call__': self.__call},
                )
            else:
                if self.__is_list:
                    self.__list_class = type(
                        'CallableObject',
                        (ProxyObject, ),
                        {'__call__': self.__call},
                    )
                else:
                    self.__we_class = type(
                        'CallableObject',
                        (ProxyObject, ),
                        {'__call__': self.__call},
                    )

    def __getattr__(self, item):
        # for IDE only
        raise AttributeError(item)

    def __make_object__(self, page):
        if self.__cached and id(self) in page.cache:
            result = page.cache[id(self)]
        else:
            if self.__class:
                result = self.__class(page.area)
            else:
                we = None

                for query_object in self.__query_set[:-1]:
                    if we:
                        we = query_object(we).first()
                    else:
                        we = query_object(page.area).first()

                query_object = self.__query_set[-1:][0]

                if we:
                    query_result = query_object(we)
                else:
                    query_result = query_object(page.area)

                if self.__wait_timeout:
                    query_result.wait(
                        self.__wait_timeout,
                    )

                if self.__is_list:
                    result = query_result.all()
                elif self.__index:
                    result = query_result.get(
                        self.__index,
                    )
                else:
                    result = query_result.first()

        if self.__cached:
            page.cache[id(self)] = result

        return result

    def __get__(self, instance, owner):
        if instance is None:
            return self

        obj = self.__make_object__(instance)

        if self.__we_class:
            if self.__is_list:
                for o in obj:
                    index = obj.index(o)
                    obj[index] = self.__we_class(o)
            else:
                obj = self.__we_class(obj)

        if self.__list_class:
            obj = self.__list_class(obj)

        if self.__property:
            return self.__property(obj)

        return obj

    def __set__(self, instance, value):
        raise TypeError('\'PageObject\' is not settable')

    def __key__(self):
        return self.__key

    def __query_set__(self):
        return self.__query_set


class PageApi(object):

    def __init__(self, page):
        self.__page = page

    @property
    def page(self):
        return self.__page


class PageMeta(type):
    """
    Factory for creating page object class
    """

    def __new__(mcs, name, bases, dct):
        cls = type.__new__(mcs, name, bases, dct)

        setattr(cls, '__dct__', {})

        page_objects = (
            (a, getattr(cls, a, None))
            for a in dir(cls)
            if not a.startswith('_')
            and
            isinstance(getattr(cls, a, None), PageElement)
        )

        for atr_name, page_object in page_objects:
            if key(page_object):
                cls.__dct__[key(page_object)] = atr_name

        return cls


class Page(with_metaclass(PageMeta, object)):

    __area__ = None
    __nested__ = True
    __url_path__ = None
    __api_class__ = PageApi

    def __init__(self, proxy=None):
        self.__proxy = proxy
        self.__cache = PageCache()
        self.__api = self.__api_class__(self)

    def __getitem__(self, item):
        try:
            return getattr(self, self.__class__.__dct__[item])
        except (KeyError, AttributeError):
            raise KeyError(item)

    def __getattr__(self, item):
        return getattr(self.area, item)

    @property
    def api(self):
        return self.__api

    @property
    def we(self):
        if self.__proxy and self.__proxy.is_web_element:
            return self.__proxy
        return None

    @property
    def area(self):
        proxy = self.__proxy if self.__nested__ else self.__proxy.driver

        if self.__area__:
            if not isinstance(self.__area__, QueryObject):
                raise TypeError(
                    '"__area__" can be instance of QueryObject only',
                )
            return self.__area__(proxy).first()

        return proxy

    @property
    def driver(self):
        if self.__proxy:
            return self.__proxy.driver
        return None

    @property
    def cache(self):
        return self.__cache

    def show(self, **kwargs):
        if self.__url_path__:
            self.__cache.clear()
            self.driver.router.go_to(
                self.__url_path__.format(**kwargs),
            )
        else:
            raise RuntimeError(
                'You should to set "__url_path__" attribute value for usage "show" method',
            )

    def bind_to(self, proxy):
        self.__proxy = proxy

    def refresh(self):
        self.__cache.clear()
        self.__proxy.driver.refresh()


PageItem = Page
