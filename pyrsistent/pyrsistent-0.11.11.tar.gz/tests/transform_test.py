from pyrsistent import freeze, inc, discard, rex, ny, field, PClass


def test_callable_command():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    m.transform(['foo', 'bar', 'baz'], inc) == {'foo': {'bar': {'baz': 2}}}


def test_predicate():
    m = freeze({'foo': {'bar': {'baz': 1}, 'qux': {'baz': 1}}})
    assert m.transform(['foo', lambda x: x.startswith('b'), 'baz'], inc) == {'foo': {'bar': {'baz': 2}, 'qux': {'baz': 1}}}


def test_remove():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    assert m.transform(['foo', 'bar', 'baz'], discard) == {'foo': {'bar': {}}}


def test_remove_pvector():
    m = freeze({'foo': [1, 2, 3]})
    assert m.transform(['foo', 1], discard) == {'foo': [1, 3]}


def test_remove_pclass():
    class MyClass(PClass):
        a = field()
        b = field()

    m = freeze({'foo': MyClass(a=1, b=2)})
    assert m.transform(['foo', 'b'], discard) == {'foo': MyClass(a=1)}


def test_predicate_no_match():
    m = freeze({'foo': {'bar': {'baz': 1}}})
    assert m.transform(['foo', lambda x: x.startswith('c'), 'baz'], inc) == m


def test_rex_predicate():
    m = freeze({'foo': {'bar': {'baz': 1},
                        'bof': {'baz': 1}}})
    assert m.transform(['foo', rex('^bo.*'), 'baz'], inc) == {'foo': {'bar': {'baz': 1},
                                                                      'bof': {'baz': 2}}}


def test_rex_with_non_string_key():
    m = freeze({'foo': 1, 5: 2})
    assert m.transform([rex(".*")], 5) == {'foo': 5, 5: 2}


def test_ny_predicated_matches_any_key():
    m = freeze({'foo': 1, 5: 2})
    assert m.transform([ny], 5) == {'foo': 5, 5: 5}


def test_new_elements_created_when_missing():
    m = freeze({})
    assert m.transform(['foo', 'bar', 'baz'], 7) == {'foo': {'bar': {'baz': 7}}}


def test_mixed_vector_and_map():
    m = freeze({'foo': [1, 2, 3]})
    assert m.transform(['foo', 1], 5) == freeze({'foo': [1, 5, 3]})


def test_vector_predicate_callable_command():
    v = freeze([1, 2, 3, 4, 5])
    assert v.transform([lambda i: 0 < i < 4], inc) == freeze(freeze([1, 3, 4, 5, 5]))


def test_vector_insert_map_one_step_beyond_end():
    v = freeze([1, 2])
    assert v.transform([2, 'foo'], 3) == freeze([1, 2, {'foo': 3}])


def test_multiple_transformations():
    v = freeze([1, 2])
    assert v.transform([2, 'foo'], 3, [2, 'foo'], inc) == freeze([1, 2, {'foo': 4}])


def test_no_transformation_returns_the_same_structure():
    v = freeze([{'foo': 1}, {'bar': 2}])
    assert v.transform([ny, ny], lambda x: x) is v
