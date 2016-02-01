from collections import OrderedDict
from graphql.core.type.definition import GraphQLField, GraphQLArgument, GraphQLInputObjectField, GraphQLEnumValue
from graphql.core.utils.schema_printer import print_schema, print_introspection_schema
from graphql.core.type import (
    GraphQLSchema,
    GraphQLInputObjectType,
    GraphQLScalarType,
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLUnionType,
    GraphQLEnumType,
    GraphQLString,
    GraphQLInt,
    GraphQLBoolean,
    GraphQLList,
    GraphQLNonNull,
)


def print_for_test(schema):
    return '\n' + print_schema(schema)


def print_single_field_schema(field_config):
    Root = GraphQLObjectType(
        name='Root',
        fields={
            'singleField': field_config
        }
    )
    return print_for_test(GraphQLSchema(Root))


def test_prints_string_field():
    output = print_single_field_schema(GraphQLField(GraphQLString))
    assert output == '''
type Root {
  singleField: String
}
'''


def test_prints_list_string_field():
    output = print_single_field_schema(GraphQLField(GraphQLList(GraphQLString)))
    assert output == '''
type Root {
  singleField: [String]
}
'''


def test_prints_non_null_list_string_field():
    output = print_single_field_schema(GraphQLField(GraphQLNonNull(GraphQLList(GraphQLString))))
    assert output == '''
type Root {
  singleField: [String]!
}
'''


def test_prints_list_non_null_string_field():
    output = print_single_field_schema(GraphQLField((GraphQLList(GraphQLNonNull(GraphQLString)))))
    assert output == '''
type Root {
  singleField: [String!]
}
'''


def test_prints_non_null_list_non_null_string_field():
    output = print_single_field_schema(GraphQLField(GraphQLNonNull(GraphQLList(GraphQLNonNull(GraphQLString)))))
    assert output == '''
type Root {
  singleField: [String!]!
}
'''


def test_prints_object_field():
    FooType = GraphQLObjectType(
        name='Foo',
        fields={
            'str': GraphQLField(GraphQLString)
        }
    )

    Root = GraphQLObjectType(
        name='Root',
        fields={
            'foo': GraphQLField(FooType)
        }
    )

    Schema = GraphQLSchema(Root)

    output = print_for_test(Schema)

    assert output == '''
type Foo {
  str: String
}

type Root {
  foo: Foo
}
'''


def test_prints_string_field_with_int_arg():
    output = print_single_field_schema(GraphQLField(
        type=GraphQLString,
        args={'argOne': GraphQLArgument(GraphQLInt)}
    ))
    assert output == '''
type Root {
  singleField(argOne: Int): String
}
'''


def test_prints_string_field_with_int_arg_with_default():
    output = print_single_field_schema(GraphQLField(
        type=GraphQLString,
        args={'argOne': GraphQLArgument(GraphQLInt, default_value=2)}
    ))
    assert output == '''
type Root {
  singleField(argOne: Int = 2): String
}
'''


def test_prints_string_field_with_non_null_int_arg():
    output = print_single_field_schema(GraphQLField(
        type=GraphQLString,
        args={'argOne': GraphQLArgument(GraphQLNonNull(GraphQLInt))}
    ))
    assert output == '''
type Root {
  singleField(argOne: Int!): String
}
'''


def test_prints_string_field_with_multiple_args():
    output = print_single_field_schema(GraphQLField(
        type=GraphQLString,
        args=OrderedDict([
            ('argOne', GraphQLArgument(GraphQLInt)),
            ('argTwo', GraphQLArgument(GraphQLString))
        ])
    ))

    assert output == '''
type Root {
  singleField(argOne: Int, argTwo: String): String
}
'''


def test_prints_string_field_with_multiple_args_first_is_default():
    output = print_single_field_schema(GraphQLField(
        type=GraphQLString,
        args=OrderedDict([
            ('argOne', GraphQLArgument(GraphQLInt, default_value=1)),
            ('argTwo', GraphQLArgument(GraphQLString)),
            ('argThree', GraphQLArgument(GraphQLBoolean))
        ])
    ))

    assert output == '''
type Root {
  singleField(argOne: Int = 1, argTwo: String, argThree: Boolean): String
}
'''


def test_prints_string_field_with_multiple_args_second_is_default():
    output = print_single_field_schema(GraphQLField(
        type=GraphQLString,
        args=OrderedDict([
            ('argOne', GraphQLArgument(GraphQLInt)),
            ('argTwo', GraphQLArgument(GraphQLString, default_value="foo")),
            ('argThree', GraphQLArgument(GraphQLBoolean))
        ])
    ))

    assert output == '''
type Root {
  singleField(argOne: Int, argTwo: String = "foo", argThree: Boolean): String
}
'''


def test_prints_string_field_with_multiple_args_last_is_default():
    output = print_single_field_schema(GraphQLField(
        type=GraphQLString,
        args=OrderedDict([
            ('argOne', GraphQLArgument(GraphQLInt)),
            ('argTwo', GraphQLArgument(GraphQLString)),
            ('argThree', GraphQLArgument(GraphQLBoolean, default_value=False))
        ])
    ))

    assert output == '''
type Root {
  singleField(argOne: Int, argTwo: String, argThree: Boolean = false): String
}
'''


def test_prints_interface():
    FooType = GraphQLInterfaceType(
        name='Foo',
        resolve_type=lambda *_: None,
        fields={
            'str': GraphQLField(GraphQLString)
        }
    )

    BarType = GraphQLObjectType(
        name='Bar',
        fields={
            'str': GraphQLField(GraphQLString),
        },
        interfaces=[FooType]
    )

    Root = GraphQLObjectType(
        name='Root',
        fields={
            'bar': GraphQLField(BarType)
        }
    )

    Schema = GraphQLSchema(Root)
    output = print_for_test(Schema)

    assert output == '''
type Bar implements Foo {
  str: String
}

interface Foo {
  str: String
}

type Root {
  bar: Bar
}
'''


def test_prints_multiple_interfaces():
    FooType = GraphQLInterfaceType(
        name='Foo',
        resolve_type=lambda *_: None,
        fields={
            'str': GraphQLField(GraphQLString)
        }
    )
    BaazType = GraphQLInterfaceType(
        name='Baaz',
        resolve_type=lambda *_: None,
        fields={
            'int': GraphQLField(GraphQLInt)
        }
    )

    BarType = GraphQLObjectType(
        name='Bar',
        fields=OrderedDict([
            ('str', GraphQLField(GraphQLString)),
            ('int', GraphQLField(GraphQLInt))
        ]),
        interfaces=[FooType, BaazType]
    )

    Root = GraphQLObjectType(
        name='Root',
        fields={
            'bar': GraphQLField(BarType)
        }
    )

    Schema = GraphQLSchema(Root)
    output = print_for_test(Schema)

    assert output == '''
interface Baaz {
  int: Int
}

type Bar implements Foo, Baaz {
  str: String
  int: Int
}

interface Foo {
  str: String
}

type Root {
  bar: Bar
}
'''


def test_prints_unions():
    FooType = GraphQLObjectType(
        name='Foo',
        fields={
            'bool': GraphQLField(GraphQLBoolean),
        },
    )

    BarType = GraphQLObjectType(
        name='Bar',
        fields={
            'str': GraphQLField(GraphQLString),
        },
    )

    SingleUnion = GraphQLUnionType(
        name='SingleUnion',
        resolve_type=lambda *_: None,
        types=[FooType]
    )

    MultipleUnion = GraphQLUnionType(
        name='MultipleUnion',
        resolve_type=lambda *_: None,
        types=[FooType, BarType],
    )

    Root = GraphQLObjectType(
        name='Root',
        fields=OrderedDict([
            ('single', GraphQLField(SingleUnion)),
            ('multiple', GraphQLField(MultipleUnion)),
        ])
    )

    Schema = GraphQLSchema(Root)
    output = print_for_test(Schema)

    assert output == '''
type Bar {
  str: String
}

type Foo {
  bool: Boolean
}

union MultipleUnion = Foo | Bar

type Root {
  single: SingleUnion
  multiple: MultipleUnion
}

union SingleUnion = Foo
'''


def test_prints_input_type():
    InputType = GraphQLInputObjectType(
        name='InputType',
        fields={
            'int': GraphQLInputObjectField(GraphQLInt)
        }
    )

    Root = GraphQLObjectType(
        name='Root',
        fields={
            'str': GraphQLField(GraphQLString, args={'argOne': GraphQLArgument(InputType)})
        }
    )

    Schema = GraphQLSchema(Root)
    output = print_for_test(Schema)

    assert output == '''
input InputType {
  int: Int
}

type Root {
  str(argOne: InputType): String
}
'''


def test_prints_custom_scalar():
    OddType = GraphQLScalarType(
        name='Odd',
        serialize=lambda v: v if v % 2 == 1 else None
    )

    Root = GraphQLObjectType(
        name='Root',
        fields={
            'odd': GraphQLField(OddType)
        }
    )

    Schema = GraphQLSchema(Root)
    output = print_for_test(Schema)

    assert output == '''
scalar Odd

type Root {
  odd: Odd
}
'''


def test_print_enum():
    RGBType = GraphQLEnumType(
        name='RGB',
        values=OrderedDict([
            ('RED', GraphQLEnumValue(0)),
            ('GREEN', GraphQLEnumValue(1)),
            ('BLUE', GraphQLEnumValue(2))
        ])
    )

    Root = GraphQLObjectType(
        name='Root',
        fields={
            'rgb': GraphQLField(RGBType)
        }
    )

    Schema = GraphQLSchema(Root)
    output = print_for_test(Schema)

    assert output == '''
enum RGB {
  RED
  GREEN
  BLUE
}

type Root {
  rgb: RGB
}
'''


def test_prints_introspection_schema():
    Root = GraphQLObjectType(
        name='Root',
        fields={
            'onlyField': GraphQLField(GraphQLString)
        }
    )

    Schema = GraphQLSchema(Root)
    output = '\n' + print_introspection_schema(Schema)

    assert output == '''
type __Directive {
  name: String!
  description: String
  args: [__InputValue!]!
  onOperation: Boolean!
  onFragment: Boolean!
  onField: Boolean!
}

type __EnumValue {
  name: String!
  description: String
  isDeprecated: Boolean!
  deprecationReason: String
}

type __Field {
  name: String!
  description: String
  args: [__InputValue!]!
  type: __Type!
  isDeprecated: Boolean!
  deprecationReason: String
}

type __InputValue {
  name: String!
  description: String
  type: __Type!
  defaultValue: String
}

type __Schema {
  types: [__Type!]!
  queryType: __Type!
  mutationType: __Type
  subscriptionType: __Type
  directives: [__Directive!]!
}

type __Type {
  kind: __TypeKind!
  name: String
  description: String
  fields(includeDeprecated: Boolean = false): [__Field!]
  interfaces: [__Type!]
  possibleTypes: [__Type!]
  enumValues(includeDeprecated: Boolean = false): [__EnumValue!]
  inputFields: [__InputValue!]
  ofType: __Type
}

enum __TypeKind {
  SCALAR
  OBJECT
  INTERFACE
  UNION
  ENUM
  INPUT_OBJECT
  LIST
  NON_NULL
}
'''
