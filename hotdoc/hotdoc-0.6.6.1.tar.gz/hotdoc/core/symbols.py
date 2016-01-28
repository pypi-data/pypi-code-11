# -*- coding: utf-8 -*-

from sqlalchemy import (Column, String, Integer, Boolean,
        ForeignKey, PickleType)

from hotdoc.core.links import Link
from hotdoc.core.alchemy_integration import *
from hotdoc.core.comment_block import comment_from_tag


class Symbol (Base):
    __tablename__ = 'symbols'

    id = Column(Integer, primary_key=True)
    comment = Column(PickleType)
    unique_name = Column(String)
    display_name = Column(String)
    filename = Column(String)
    lineno = Column(Integer)
    location = Column(PickleType)
    _type_ = Column(String)
    extension_contents = Column(MutableDict.as_mutable(PickleType))
    extension_attributes = Column(MutableDict.as_mutable(PickleType))
    link = Column(Link.as_mutable(PickleType))
    skip = Column(Boolean)

    __mapper_args__ = {
            'polymorphic_identity': 'symbol',
            'polymorphic_on': _type_,
    }

    def __init__(self, **kwargs):
        self.extension_contents = {}
        self.extension_attributes = {}
        self.skip = False

        Base.__init__(self, **kwargs)

    # FIXME: this is a bit awkward to use.
    def add_extension_attribute (self, ext_name, key, value):
        attributes = self.extension_attributes.pop (ext_name, {})
        attributes[key] = value
        self.extension_attributes[ext_name] = attributes

    def get_extension_attribute (self, ext_name, key):
        attributes = self.extension_attributes.get (ext_name)
        if not attributes:
            return None
        return attributes.get (key)

    def get_children_symbols (self):
        return []

    def update_children_comments(self):
        for sym in self.get_children_symbols():
            if type(sym) == ParameterSymbol:
                sym.comment = self.comment.params.get(sym.argname)
            elif type(sym) == FieldSymbol:
                sym.comment = self.comment.params.get(sym.member_name)
            elif type(sym) == ReturnValueSymbol:
                tag = self.comment.tags.get('returns')
                sym.comment = comment_from_tag(tag)
            elif type(sym) == Symbol:
                sym.comment = self.comment.params.get(sym.display_name)

    def _make_name (self):
        return self.display_name

    def get_extra_links (self):
        return []

    def get_type_name (self):
        return ''

    def resolve_links(self, link_resolver):
        if self.link is None:
            self.link = Link(self.unique_name, self._make_name(),
                        self.unique_name)
        self.link = link_resolver.upsert_link(self.link, overwrite_ref=True)

class QualifiedSymbol (MutableObject):
    def __init__(self, type_tokens=[]):
        self.input_tokens = type_tokens
        self.comment = None
        self.extension_attributes = MutableDict()
        self.constructed()
        MutableObject.__init__(self)

    def add_extension_attribute (self, ext_name, key, value):
        attributes = self.extension_attributes.pop (ext_name, {})
        attributes[key] = value
        self.extension_attributes[ext_name] = attributes

    def get_extension_attribute (self, ext_name, key):
        attributes = self.extension_attributes.get (ext_name)
        if not attributes:
            return None
        return attributes.get (key)

    def get_children_symbols(self):
        return []

    def get_type_link (self):
        return self.type_link

    def resolve_links(self, link_resolver):
        self.type_link = None
        self.type_tokens = []

        for tok in self.input_tokens:
            if isinstance(tok, Link):
                self.type_link = link_resolver.get_named_link(tok.id_)
                if not self.type_link:
                    self.type_link = link_resolver.upsert_link(tok)
                self.type_tokens.append (self.type_link)
            else:
                self.type_tokens.append (tok)

    def constructed(self):
        self.extension_contents = {}

    def __setstate__(self, state):
        MutableObject.__setstate__(self, state)
        self.constructed()

class ReturnValueSymbol (QualifiedSymbol):
    def __init__(self, comment=None, **kwargs):
        QualifiedSymbol.__init__(self, **kwargs)
        self.comment = comment

class ParameterSymbol (QualifiedSymbol):
    def __init__(self, argname='', comment=None, **kwargs):
        QualifiedSymbol.__init__(self, **kwargs)
        # FIXME: gir specific
        self.array_nesting = 0
        self.argname = argname
        self.comment = comment

class FieldSymbol (QualifiedSymbol):
    def __init__(self, member_name='', is_function_pointer=False,
            comment=None, **kwargs):
        QualifiedSymbol.__init__(self, **kwargs)
        self.member_name = member_name
        self.is_function_pointer = is_function_pointer
        self.comment = comment

    def _make_name (self):
        return self.member_name

    def get_type_name (self):
        return "Attribute"

class FunctionSymbol (Symbol):
    __tablename__ = 'functions'
    id = Column(Integer, ForeignKey('symbols.id'), primary_key=True)
    parameters = Column(MutableList.as_mutable(PickleType))
    return_value = Column(ReturnValueSymbol.as_mutable(PickleType))
    is_method = Column(Boolean)
    throws = Column(Boolean)
    __mapper_args__ = {
            'polymorphic_identity': 'functions',
    }

    def __init__(self, **kwargs):
        self.parameters = []
        self.throws = False
        self.is_method = False
        Symbol.__init__(self, **kwargs)

    def get_children_symbols(self):
        return self.parameters + [self.return_value]

    def get_type_name (self):
        if self.is_method:
            return 'Method'
        return 'Function'

class SignalSymbol (FunctionSymbol):
    __tablename__ = 'signals'
    id = Column(Integer, ForeignKey('functions.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'signals',
    }
    flags = Column(PickleType)

    def __init__(self, **kwargs):
        # FIXME: flags are gobject-specific
        self.flags = []
        FunctionSymbol.__init__(self, **kwargs)

    def get_type_name (self):
        return "Signal"

class VFunctionSymbol (FunctionSymbol):
    __tablename__ = 'vfunctions'
    id = Column(Integer, ForeignKey('functions.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'vfunctions',
    }
    flags = Column(PickleType)

    def __init__(self, **kwargs):
        self.flags = []
        FunctionSymbol.__init__(self, **kwargs)

    def get_type_name (self):
        return "Virtual Method"

class PropertySymbol (Symbol):
    __tablename__ = 'properties'
    id = Column(Integer, ForeignKey('symbols.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'properties',
    }
    prop_type = Column(PickleType)

    def get_children_symbols(self):
        return [self.prop_type]

class CallbackSymbol (FunctionSymbol):
    __tablename__ = 'callbacks'
    id = Column(Integer, ForeignKey('functions.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'callbacks',
    }

    def get_type_name (self):
        return "Callback"

class EnumSymbol (Symbol):
    __tablename__ = 'enums'
    id = Column(Integer, ForeignKey('symbols.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'enums',
    }
    members = Column(PickleType)

    def __init__(self, **kwargs):
        self.members = {}
        Symbol.__init__(self, **kwargs)

    def get_children_symbols(self):
        return self.members

    def get_extra_links (self):
        return [m.link for m in self.members]

    def get_type_name (self):
        return "Enumeration"

class StructSymbol (Symbol):
    __tablename__ = 'structs'
    id = Column(Integer, ForeignKey('symbols.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'structs',
    }
    members = Column(PickleType)
    raw_text = Column(String)

    def __init__(self, **kwargs):
        self.members = {}
        Symbol.__init__(self, **kwargs)

    def get_children_symbols(self):
        return self.members

    def get_type_name (self):
        return "Structure"

# FIXME: and this is C-specific
class MacroSymbol (Symbol):
    __tablename__ = 'macros'
    id = Column(Integer, ForeignKey('symbols.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'macros',
    }
    original_text = Column(String)

class FunctionMacroSymbol (MacroSymbol):
    __tablename__ = 'function_macros'
    id = Column(Integer, ForeignKey('macros.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'function_macros',
    }

    parameters = Column(MutableList.as_mutable(PickleType))
    return_value = Column(PickleType)

    def __init__(self, **kwargs):
        self.parameters = []
        MacroSymbol.__init__(self, **kwargs)

    def get_children_symbols(self):
        return self.parameters + [self.return_value]

    def get_type_name (self):
        return "Function macro"

class ConstantSymbol (MacroSymbol):
    __tablename__ = 'constants'
    id = Column(Integer, ForeignKey('macros.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'constants',
    }

    def get_type_name (self):
        return "Constant"


class ExportedVariableSymbol (MacroSymbol):
    __tablename__ = 'exported_variables'
    id = Column(Integer, ForeignKey('macros.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'exported_variables',
    }
    type_qs = Column(PickleType)

    def get_type_name (self):
        return "Exported variable"

    def get_children_symbols(self):
        return [self.type_qs]

class AliasSymbol (Symbol):
    __tablename__ = 'aliases'
    id = Column(Integer, ForeignKey('symbols.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'aliases',
    }
    aliased_type = Column(PickleType)

    def get_type_name (self):
        return "Alias"

    def get_children_symbols(self):
        return [self.aliased_type]

class ClassSymbol (Symbol):
    __tablename__ = 'classes'
    id = Column(Integer, ForeignKey('symbols.id'), primary_key=True)
    __mapper_args__ = {
            'polymorphic_identity': 'classes',
    }
    # FIXME: multiple inheritance
    hierarchy = Column(PickleType)
    children = Column(PickleType)

    def __init__(self, **kwargs):
        self.hierarchy = []
        self.children = {}
        Symbol.__init__(self, **kwargs)

    def get_type_name (self):
        return "Class"

    def get_children_symbols(self):
        return self.hierarchy + list(self.children.values())
