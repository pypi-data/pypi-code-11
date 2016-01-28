import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hotdoc.core.alchemy_integration import Base
from hotdoc.core.comment_block import Comment, Tag
from hotdoc.core.symbols import Symbol

from hotdoc.utils.simple_signals import Signal


class DocDatabase(object):
    comment_updated_signal = Signal()
    symbol_updated_signal = Signal()

    def __init__(self, link_resolver):
        self.link_resolver = link_resolver

        self.__comments = {}
        self.__symbols = {}
        self.__incremental = False
        self.__session = None
        self.__engine = None

    def add_comment(self, comment):
        """
        Banana banana
        """
        self.__comments[comment.name] = comment
        """
        for validator in self.tag_validators.values():
            if validator.default and validator.name not in comment.tags:
                comment.tags[validator.name] = \
                    Tag(name=validator.name,
                        description=validator.default)
        """
        if self.__incremental:
            self.__update_symbol_comment(comment)

    def get_comment(self, name):
        """
        Banana banana
        """
        comment = self.__comments.get(name)
        if not comment:
            esym = self.get_symbol(name)
            if esym:
                comment = esym.comment
        return comment

    def get_or_create_symbol(self, type_, **kwargs):
        """
        Banana banana
        """
        unique_name = kwargs.get('unique_name')
        if not unique_name:
            unique_name = kwargs.get('display_name')
            kwargs['unique_name'] = unique_name

        filename = kwargs.get('filename')
        if filename:
            kwargs['filename'] = os.path.abspath(filename)

        if self.__incremental:
            symbol = self.__session.query(type_).filter(
                type_.unique_name == unique_name).first()
        else:
            symbol = None

        if not symbol:
            symbol = type_()
            self.__session.add(symbol)

        for key, value in kwargs.items():
            setattr(symbol, key, value)

        if not symbol.comment:
            symbol.comment = Comment(symbol.unique_name)
            self.add_comment(symbol.comment)

        symbol.resolve_links(self.link_resolver)

        if self.__incremental:
            self.symbol_updated_signal(self, symbol)

        self.__symbols[unique_name] = symbol

        return symbol

    # pylint: disable=unused-argument
    def get_symbol(self, name, prefer_class=False):
        """
        Banana banana
        """
        sym = self.__symbols.get(name)

        if not self.__incremental:
            if sym:
                sym.resolve_links(self.link_resolver)
            return sym

        if not sym:
            sym = self.__session.query(Symbol).filter(Symbol.unique_name ==
                                                    name).first()

        if sym:
            # Faster look up next time around
            self.__symbols[name] = sym
            sym.resolve_links(self.link_resolver)
        return sym

    def setup(self, db_folder):
        db_path = os.path.join(db_folder, 'hotdoc.db')

        if os.path.exists(db_path):
            self.__incremental = True

        self.__engine = create_engine('sqlite:///%s' % db_path)
        self.__session = sessionmaker(self.__engine)()
        self.__session.autoflush = False
        Base.metadata.create_all(self.__engine)

    def flush(self):
        self.__session.flush()

    def commit(self):
        self.__session.commit()

    def __update_symbol_comment(self, comment):
        self.__session.query(Symbol).filter(
            Symbol.unique_name ==
            comment.name).update({'comment': comment})
        esym = self.__symbols.get(comment.name)
        if esym:
            esym.comment = comment
        self.comment_updated_signal(self, comment)

    def close(self):
        self.__session.close()
