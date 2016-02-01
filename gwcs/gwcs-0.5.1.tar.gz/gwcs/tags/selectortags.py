# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

from collections import OrderedDict
import numpy as np
from numpy.testing import assert_array_equal
from astropy.modeling import models
from astropy.utils.misc import isiterable

from pyasdf import yamlutil
from pyasdf.tags.transform.basic import TransformType
from pyasdf.tags.core.ndarray import NDArrayType

from ..selector import *


__all__ = ['LabelMapperType', 'RegionsSelectorType']


class LabelMapperType(TransformType):
    name = "transform/label_mapper"
    types = [LabelMapperArray, LabelMapperDict, LabelMapperRange]

    @classmethod
    def from_tree_transform(cls, node, ctx):
        inputs_mapping = node.get('inputs_mapping', None)
        if inputs_mapping is not None and not isinstance(inputs_mapping, models.Mapping):
            raise TypeError("inputs_mapping must be an instance"
                            "of astropy.modeling.models.Mapping.")
        mapper = node['mapper']

        if isinstance(mapper, NDArrayType):
            if mapper.ndim != 2:
                raise NotImplementedError(
                    "GWCS currently only supports 2x2 masks ")
            return LabelMapperArray(mapper, inputs_mapping)
        else:
            inputs = node.get('inputs', None)
            if inputs is not None:
                inputs = tuple(inputs)
            labels = mapper.get('labels')
            if isiterable(labels[0]):
                labels = [tuple(l) for l in labels]
            transforms = mapper.get('models')
            dict_mapper = dict(zip(labels, transforms))
            return LabelMapperDict(inputs, dict_mapper, inputs_mapping)

    @classmethod
    def to_tree_transform(cls, model, ctx):
        node = OrderedDict()
        if isinstance(model, LabelMapperArray):
            node['mapper'] = model.mapper
        if isinstance(model, (LabelMapperDict, LabelMapperRange)):
            mapper = OrderedDict()
            labels = list(model.mapper)

            transforms = []
            for k in labels:
                transforms.append(model.mapper[k])
            if isiterable(labels[0]):
                labels = [list(l) for l in labels]
            mapper['labels'] = labels
            mapper['models'] = transforms
            node['mapper'] = mapper
            node['inputs'] = list(model.inputs)
        if model.inputs_mapping is not None:
            node['inputs_mapping'] = model.inputs_mapping

        return yamlutil.custom_tree_to_tagged_tree(node, ctx)

    @classmethod
    def assert_equal(cls, a, b):
        # TODO: If models become comparable themselves, remove this.
        assert (a.__class__ == b.__class__)
        if isinstance(a.mapper, dict):
            assert(a.mapper.__class__ == b.mapper.__class__)
            assert(all(np.in1d(list(a.mapper), list(b.mapper))))
            for k in a.mapper:
                assert (a.mapper[k].__class__  == b.mapper[k].__class__)
                assert(all(a.mapper[k].parameters == b.mapper[k].parameters))
            assert (a.inputs == b.inputs)
            assert (a.inputs_mapping.mapping == b.inputs_mapping.mapping)
        else:
            assert_array_equal(a.mapper, b.mapper)


class RegionsSelectorType(TransformType):
    name = "transform/regions_selector"
    types = [RegionsSelector]

    @classmethod
    def from_tree_transform(cls, node, ctx):
        inputs = node['inputs']
        outputs = node['outputs']
        label_mapper = node['label_mapper']
        undefined_transform_value = node['undefined_transform_value']
        sel = node['selector']
        sel = dict(zip(sel['labels'], sel['transforms']))
        return RegionsSelector(inputs, outputs,
                               sel, label_mapper, undefined_transform_value)

    @classmethod
    def to_tree_transform(cls, model, ctx):
        selector = OrderedDict()
        node = OrderedDict()
        labels = list(model.selector)
        values = []
        for l in labels:
            values.append(model.selector[l])
        selector['labels'] = labels
        selector['transforms'] = values
        node['inputs']= list(model.inputs)
        node['outputs'] = list(model.outputs)
        node['selector'] = selector
        node['label_mapper'] =  model.label_mapper
        node['undefined_transform_value'] = model.undefined_transform_value
        return yamlutil.custom_tree_to_tagged_tree(node, ctx)

    @classmethod
    def assert_equal(cls, a, b):
        # TODO: If models become comparable themselves, remove this.
        assert (a.__class__ == b.__class__)
        LabelMapperType.assert_equal(a.label_mapper, b.label_mapper)
        assert_array_equal(a.inputs, b.inputs)
        assert_array_equal(a.outputs, b.outputs)
        assert_array_equal(a.selector.keys(), b.selector.keys())
        for key in a.selector:
            assert_array_equal(a.selector[key].parameters, b.selector[key].parameters)
        assert_array_equal(a.undefined_transform_value, b.undefined_transform_value)
