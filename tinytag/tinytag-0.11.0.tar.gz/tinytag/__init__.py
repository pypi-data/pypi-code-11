#!/usr/bin/python
# -*- coding: utf-8 -*-
from .tinytag import TinyTag, TinyTagException, ID3, Ogg, Wave, Flac


__version__ = '0.11.0'

if __name__ == '__main__':
    print(TinyTag.get(sys.argv[1]))