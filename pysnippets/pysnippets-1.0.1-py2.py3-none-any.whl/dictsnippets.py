#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2016 HQM <qiminis0801@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


from .compat import literal_eval


class DictSnippets(object):
    def __init__(self):
        self.separtor = ':'

    def eval_string(self, string):
        try:
            return literal_eval(string)
        except (SyntaxError, ValueError):
            return string

    def filter(self, obj, kvlist, exec_eval=True):
        _obj = {}
        for kv in kvlist:
            k, v = kv.split(self.separtor) if self.separtor in kv else [kv, '']
            _obj[k] = obj.get(k, self.eval_string(v) if exec_eval else v)
        return _obj


_global_instance = DictSnippets()
filter = _global_instance.filter
