# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/logging/type/http_request.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='google/logging/type/http_request.proto',
  package='google.logging.type',
  syntax='proto3',
  serialized_pb=b'\n&google/logging/type/http_request.proto\x12\x13google.logging.type\x1a\x1cgoogle/api/annotations.proto\"\xe8\x01\n\x0bHttpRequest\x12\x16\n\x0erequest_method\x18\x01 \x01(\t\x12\x13\n\x0brequest_url\x18\x02 \x01(\t\x12\x14\n\x0crequest_size\x18\x03 \x01(\x03\x12\x0e\n\x06status\x18\x04 \x01(\x05\x12\x15\n\rresponse_size\x18\x05 \x01(\x03\x12\x12\n\nuser_agent\x18\x06 \x01(\t\x12\x11\n\tremote_ip\x18\x07 \x01(\t\x12\x0f\n\x07referer\x18\x08 \x01(\t\x12\x11\n\tcache_hit\x18\t \x01(\x08\x12$\n\x1cvalidated_with_origin_server\x18\n \x01(\x08\x42-\n\x17\x63om.google.logging.typeB\x10HttpRequestProtoP\x01\x62\x06proto3'
  ,
  dependencies=[google_dot_api_dot_annotations__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_HTTPREQUEST = _descriptor.Descriptor(
  name='HttpRequest',
  full_name='google.logging.type.HttpRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='request_method', full_name='google.logging.type.HttpRequest.request_method', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='request_url', full_name='google.logging.type.HttpRequest.request_url', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='request_size', full_name='google.logging.type.HttpRequest.request_size', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='google.logging.type.HttpRequest.status', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='response_size', full_name='google.logging.type.HttpRequest.response_size', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='user_agent', full_name='google.logging.type.HttpRequest.user_agent', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='remote_ip', full_name='google.logging.type.HttpRequest.remote_ip', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='referer', full_name='google.logging.type.HttpRequest.referer', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cache_hit', full_name='google.logging.type.HttpRequest.cache_hit', index=8,
      number=9, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='validated_with_origin_server', full_name='google.logging.type.HttpRequest.validated_with_origin_server', index=9,
      number=10, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=94,
  serialized_end=326,
)

DESCRIPTOR.message_types_by_name['HttpRequest'] = _HTTPREQUEST

HttpRequest = _reflection.GeneratedProtocolMessageType('HttpRequest', (_message.Message,), dict(
  DESCRIPTOR = _HTTPREQUEST,
  __module__ = 'google.logging.type.http_request_pb2'
  # @@protoc_insertion_point(class_scope:google.logging.type.HttpRequest)
  ))
_sym_db.RegisterMessage(HttpRequest)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), b'\n\027com.google.logging.typeB\020HttpRequestProtoP\001')
# @@protoc_insertion_point(module_scope)
