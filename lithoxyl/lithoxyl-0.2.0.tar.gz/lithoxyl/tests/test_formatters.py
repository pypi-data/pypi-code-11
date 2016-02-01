# -*- coding: utf-8 -*-

from lithoxyl.logger import Record, DEBUG
from lithoxyl.formatters import Formatter
from lithoxyl.formatutils import DeferredValue


template = ('{status_char}{record_warn_char}{begin_timestamp}'
            ' - {begin_local_iso8601} - {begin_iso8601}'
            ' - {logger_name} - {status_str} - {record_name}')


RECS = [Record('Riker', DEBUG).success('Hello, Thomas.')]


TCS = [[('{logger_name}', '{logger_name}'),
        ('{status_str}', 'success'),
        ('{level_number}', '20'),
        ('{record_name}', '"Riker"'),
        ('{message}', '"Hello, Thomas."')]
       ]


def test_formatter_basic():
    riker = Record('hello_thomas', DEBUG).success('')
    forming = Formatter(template)
    output = forming.format_record(riker)
    expected = '{logger_name} - success - "hello_thomas"'
    print output
    assert output[-len(expected):] == expected

    rec = Record('Wharf')
    robf = Formatter(template)
    rec.success('Mr. Wolf')
    ret = robf.format_record(rec)
    print ret
    return ret


def test_individual_fields():
    for record, field_pairs in zip(RECS, TCS):
        for field_tmpl, result in field_pairs:
            forming = Formatter(field_tmpl)
            output = forming.format_record(record)
            assert output == result
    return


def test_deferred():
    DV = DeferredValue
    expensive_ops = [(lambda: 5, '"oh, 5"'),
                     (lambda: 'hi', '"oh, hi"'),
                     (lambda: 2.0, '"oh, 2.0"')]
    formatter = Formatter('{message}')

    for eo, expected in expensive_ops:
        record = Record('spendy_op', DEBUG).success('oh, {dv}', dv=DV(eo))
        output = formatter.format_record(record)
        assert output == expected
    return


"""
Formatter tests todos

* no args/kwargs
* sufficient, correct args/kwargs
* anonymous args
* missing kwarg
* missing arg
* type mismatch args
* type mismatch kwargs
* usage of "builtin" fields
"""
