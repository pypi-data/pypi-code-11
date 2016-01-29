# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""Response parsers for the various protocol types.

The module contains classes that can take an HTTP response, and given
an output shape, parse the response into a dict according to the
rules in the output shape.

There are many similarities amongst the different protocols with regard
to response parsing, and the code is structured in a way to avoid
code duplication when possible.  The diagram below is a diagram
showing the inheritance hierarchy of the response classes.

::



                                 +--------------+
                                 |ResponseParser|
                                 +--------------+
                                    ^    ^    ^
               +--------------------+    |    +-------------------+
               |                         |                        |
    +----------+----------+       +------+-------+        +-------+------+
    |BaseXMLResponseParser|       |BaseRestParser|        |BaseJSONParser|
    +---------------------+       +--------------+        +--------------+
              ^         ^          ^           ^           ^        ^
              |         |          |           |           |        |
              |         |          |           |           |        |
              |        ++----------+-+       +-+-----------++       |
              |        |RestXMLParser|       |RestJSONParser|       |
        +-----+-----+  +-------------+       +--------------+  +----+-----+
        |QueryParser|                                          |JSONParser|
        +-----------+                                          +----------+


The diagram above shows that there is a base class, ``ResponseParser`` that
contains logic that is similar amongst all the different protocols (``query``,
``json``, ``rest-json``, ``rest-xml``).  Amongst the various services there
is shared logic that can be grouped several ways:

* The ``query`` and ``rest-xml`` both have XML bodies that are parsed in the
  same way.
* The ``json`` and ``rest-json`` protocols both have JSON bodies that are
  parsed in the same way.
* The ``rest-json`` and ``rest-xml`` protocols have additional attributes
  besides body parameters that are parsed the same (headers, query string,
  status code).

This is reflected in the class diagram above.  The ``BaseXMLResponseParser``
and the BaseJSONParser contain logic for parsing the XML/JSON body,
and the BaseRestParser contains logic for parsing out attributes that
come from other parts of the HTTP response.  Classes like the
``RestXMLParser`` inherit from the ``BaseXMLResponseParser`` to get the
XML body parsing logic and the ``BaseRestParser`` to get the HTTP
header/status code/query string parsing.

Return Values
=============

Each call to ``parse()`` returns a dict has this form::

    Standard Response

    {
      "ResponseMetadata": {"RequestId": <requestid>}
      <response keys>
    }

    Error response

    {
      "ResponseMetadata": {"RequestId": <requestid>}
      "Error": {
        "Code": <string>,
        "Message": <string>,
        "Type": <string>,
        <additional keys>
      }
    }

"""
import re
import base64
import json
import xml.etree.cElementTree
import logging

from botocore.compat import six, XMLParseError

from botocore.utils import parse_timestamp, merge_dicts

LOG = logging.getLogger(__name__)

DEFAULT_TIMESTAMP_PARSER = parse_timestamp


class ResponseParserFactory(object):
    def __init__(self):
        self._defaults = {}

    def set_parser_defaults(self, **kwargs):
        """Set default arguments when a parser instance is created.

        You can specify any kwargs that are allowed by a ResponseParser
        class.  There are currently two arguments:

            * timestamp_parser - A callable that can parse a timetsamp string
            * blob_parser - A callable that can parse a blob type

        """
        self._defaults.update(kwargs)

    def create_parser(self, protocol_name):
        parser_cls = PROTOCOL_PARSERS[protocol_name]
        return parser_cls(**self._defaults)


def create_parser(protocol):
    return ResponseParserFactory().create_parser(protocol)


def _text_content(func):
    # This decorator hides the difference between
    # an XML node with text or a plain string.  It's used
    # to ensure that scalar processing operates only on text
    # strings, which allows the same scalar handlers to be used
    # for XML nodes from the body and HTTP headers.
    def _get_text_content(self, shape, node_or_string):
        if hasattr(node_or_string, 'text'):
            text = node_or_string.text
            if text is None:
                # If an XML node is empty <foo></foo>,
                # we want to parse that as an empty string,
                # not as a null/None value.
                text = ''
        else:
            text = node_or_string
        return func(self, shape, text)
    return _get_text_content


class ResponseParserError(Exception):
    pass


class ResponseParser(object):
    """Base class for response parsing.

    This class represents the interface that all ResponseParsers for the
    various protocols must implement.

    This class will take an HTTP response and a model shape and parse the
    HTTP response into a dictionary.

    There is a single public method exposed: ``parse``.  See the ``parse``
    docstring for more info.

    """
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, timestamp_parser=None, blob_parser=None):
        if timestamp_parser is None:
            timestamp_parser = DEFAULT_TIMESTAMP_PARSER
        self._timestamp_parser = timestamp_parser
        if blob_parser is None:
            blob_parser = self._default_blob_parser
        self._blob_parser = blob_parser

    def _default_blob_parser(self, value):
        # Blobs are always returned as bytes type (this matters on python3).
        # We don't decode this to a str because it's entirely possible that the
        # blob contains binary data that actually can't be decoded.
        return base64.b64decode(value)

    def parse(self, response, shape):
        """Parse the HTTP response given a shape.

        :param response: The HTTP response dictionary.  This is a dictionary
            that represents the HTTP request.  The dictionary must have the
            following keys, ``body``, ``headers``, and ``status_code``.

        :param shape: The model shape describing the expected output.
        :return: Returns a dictionary representing the parsed response
            described by the model.  In addition to the shape described from
            the model, each response will also have a ``ResponseMetadata``
            which contains metadata about the response, which contains at least
            two keys containing ``RequestId`` and ``HTTPStatusCode``.  Some
            responses may populate additional keys, but ``RequestId`` will
            always be present.

        """
        LOG.debug('Response headers: %s', response['headers'])
        LOG.debug('Response body:\n%s', response['body'])
        if response['status_code'] >= 301:
            parsed = self._do_error_parse(response, shape)
        else:
            parsed = self._do_parse(response, shape)
        # Inject HTTPStatusCode key in the response metadata if the
        # response metadata exists.
        if isinstance(parsed, dict) and 'ResponseMetadata' in parsed:
            parsed['ResponseMetadata']['HTTPStatusCode'] = (
                response['status_code'])
        return parsed

    def _do_parse(self, response, shape):
        raise NotImplementedError("%s._do_parse" % self.__class__.__name__)

    def _do_error_parse(self, response, shape):
        raise NotImplementedError(
            "%s._do_error_parse" % self.__class__.__name__)

    def _parse_shape(self, shape, node):
        handler = getattr(self, '_handle_%s' % shape.type_name,
                          self._default_handle)
        return handler(shape, node)

    def _handle_list(self, shape, node):
        # Enough implementations share list serialization that it's moved
        # up here in the base class.
        parsed = []
        member_shape = shape.member
        for item in node:
            parsed.append(self._parse_shape(member_shape, item))
        return parsed

    def _default_handle(self, shape, value):
        return value


class BaseXMLResponseParser(ResponseParser):
    def __init__(self, timestamp_parser=None, blob_parser=None):
        super(BaseXMLResponseParser, self).__init__(timestamp_parser,
                                                    blob_parser)
        self._namespace_re = re.compile('{.*}')

    def _handle_map(self, shape, node):
        parsed = {}
        key_shape = shape.key
        value_shape = shape.value
        key_location_name = key_shape.serialization.get('name') or 'key'
        value_location_name = value_shape.serialization.get('name') or 'value'
        if shape.serialization.get('flattened') and not isinstance(node, list):
            node = [node]
        for keyval_node in node:
            for single_pair in keyval_node:
                # Within each <entry> there's a <key> and a <value>
                tag_name = self._node_tag(single_pair)
                if tag_name == key_location_name:
                    key_name = self._parse_shape(key_shape, single_pair)
                elif tag_name == value_location_name:
                    val_name = self._parse_shape(value_shape, single_pair)
                else:
                    raise ResponseParserError("Unknown tag: %s" % tag_name)
            parsed[key_name] = val_name
        return parsed

    def _node_tag(self, node):
        return self._namespace_re.sub('', node.tag)

    def _handle_list(self, shape, node):
        # When we use _build_name_to_xml_node, repeated elements are aggregated
        # into a list.  However, we can't tell the difference between a scalar
        # value and a single element flattened list.  So before calling the
        # real _handle_list, we know that "node" should actually be a list if
        # it's flattened, and if it's not, then we make it a one element list.
        if shape.serialization.get('flattened') and not isinstance(node, list):
            node = [node]
        return super(BaseXMLResponseParser, self)._handle_list(shape, node)

    def _handle_structure(self, shape, node):
        parsed = {}
        members = shape.members
        xml_dict = self._build_name_to_xml_node(node)
        for member_name in members:
            member_shape = members[member_name]
            if 'location' in member_shape.serialization:
                # All members with locations have already been handled,
                # so we don't need to parse these members.
                continue
            xml_name = self._member_key_name(member_shape, member_name)
            member_node = xml_dict.get(xml_name)
            if member_node is not None:
                parsed[member_name] = self._parse_shape(
                    member_shape, member_node)
            elif member_shape.serialization.get('xmlAttribute'):
                attribs = {}
                location_name = member_shape.serialization['name']
                for key, value in node.attrib.items():
                    new_key = self._namespace_re.sub(
                        location_name.split(':')[0] + ':', key)
                    attribs[new_key] = value
                if location_name in attribs:
                    parsed[member_name] = attribs[location_name]
        return parsed

    def _member_key_name(self, shape, member_name):
        # This method is needed because we have to special case flattened list
        # with a serialization name.  If this is the case we use the
        # locationName from the list's member shape as the key name for the
        # surrounding structure.
        if shape.type_name == 'list' and shape.serialization.get('flattened'):
            list_member_serialized_name = shape.member.serialization.get(
                'name')
            if list_member_serialized_name is not None:
                return list_member_serialized_name
        serialized_name = shape.serialization.get('name')
        if serialized_name is not None:
            return serialized_name
        return member_name

    def _build_name_to_xml_node(self, parent_node):
        # If the parent node is actually a list. We should not be trying
        # to serialize it to a dictionary. Instead, return the first element
        # in the list.
        if isinstance(parent_node, list):
            return self._build_name_to_xml_node(parent_node[0])
        xml_dict = {}
        for item in parent_node:
            key = self._node_tag(item)
            if key in xml_dict:
                # If the key already exists, the most natural
                # way to handle this is to aggregate repeated
                # keys into a single list.
                # <foo>1</foo><foo>2</foo> -> {'foo': [Node(1), Node(2)]}
                if isinstance(xml_dict[key], list):
                    xml_dict[key].append(item)
                else:
                    # Convert from a scalar to a list.
                    xml_dict[key] = [xml_dict[key], item]
            else:
                xml_dict[key] = item
        return xml_dict

    def _parse_xml_string_to_dom(self, xml_string):
        try:
            parser = xml.etree.cElementTree.XMLParser(
                target=xml.etree.cElementTree.TreeBuilder(),
                encoding=self.DEFAULT_ENCODING)
            parser.feed(xml_string)
            root = parser.close()
        except XMLParseError as e:
            raise ResponseParserError(
                "Unable to parse response (%s), "
                "invalid XML received:\n%s" % (e, xml_string))
        return root

    def _replace_nodes(self, parsed):
        for key, value in parsed.items():
            if value.getchildren():
                sub_dict = self._build_name_to_xml_node(value)
                parsed[key] = self._replace_nodes(sub_dict)
            else:
                parsed[key] = value.text
        return parsed

    @_text_content
    def _handle_boolean(self, shape, text):
        if text == 'true':
            return True
        else:
            return False

    @_text_content
    def _handle_float(self, shape, text):
        return float(text)

    @_text_content
    def _handle_timestamp(self, shape, text):
        return self._timestamp_parser(text)

    @_text_content
    def _handle_integer(self, shape, text):
        return int(text)

    @_text_content
    def _handle_string(self, shape, text):
        return text

    @_text_content
    def _handle_blob(self, shape, text):
        return self._blob_parser(text)

    _handle_character = _handle_string
    _handle_double = _handle_float
    _handle_long = _handle_integer


class QueryParser(BaseXMLResponseParser):

    def _do_error_parse(self, response, shape):
        xml_contents = response['body']
        root = self._parse_xml_string_to_dom(xml_contents)
        parsed = self._build_name_to_xml_node(root)
        self._replace_nodes(parsed)
        # Once we've converted xml->dict, we need to make one or two
        # more adjustments to extract nested errors and to be consistent
        # with ResponseMetadata for non-error responses:
        # 1. {"Errors": {"Error": {...}}} -> {"Error": {...}}
        # 2. {"RequestId": "id"} -> {"ResponseMetadata": {"RequestId": "id"}}
        if 'Errors' in parsed:
            parsed.update(parsed.pop('Errors'))
        if 'RequestId' in parsed:
            parsed['ResponseMetadata'] = {'RequestId': parsed.pop('RequestId')}
        return parsed

    def _do_parse(self, response, shape):
        xml_contents = response['body']
        root = self._parse_xml_string_to_dom(xml_contents)
        parsed = {}
        if shape is not None:
            start = root
            if 'resultWrapper' in shape.serialization:
                start = self._find_result_wrapped_shape(
                    shape.serialization['resultWrapper'],
                    root)
            parsed = self._parse_shape(shape, start)
        self._inject_response_metadata(root, parsed)
        return parsed

    def _find_result_wrapped_shape(self, element_name, xml_root_node):
        mapping = self._build_name_to_xml_node(xml_root_node)
        return mapping[element_name]

    def _inject_response_metadata(self, node, inject_into):
        mapping = self._build_name_to_xml_node(node)
        child_node = mapping.get('ResponseMetadata')
        if child_node is not None:
            sub_mapping = self._build_name_to_xml_node(child_node)
            for key, value in sub_mapping.items():
                sub_mapping[key] = value.text
            inject_into['ResponseMetadata'] = sub_mapping


class EC2QueryParser(QueryParser):

    def _inject_response_metadata(self, node, inject_into):
        mapping = self._build_name_to_xml_node(node)
        child_node = mapping.get('requestId')
        if child_node is not None:
            inject_into['ResponseMetadata'] = {'RequestId': child_node.text}

    def _do_error_parse(self, response, shape):
        # EC2 errors look like:
        # <Response>
        #   <Errors>
        #     <Error>
        #       <Code>InvalidInstanceID.Malformed</Code>
        #       <Message>Invalid id: "1343124"</Message>
        #     </Error>
        #   </Errors>
        #   <RequestID>12345</RequestID>
        # </Response>
        # This is different from QueryParser in that it's RequestID,
        # not RequestId
        original = super(EC2QueryParser, self)._do_error_parse(response, shape)
        original['ResponseMetadata'] = {
            'RequestId': original.pop('RequestID')
        }
        return original


class BaseJSONParser(ResponseParser):

    def _handle_structure(self, shape, value):
        member_shapes = shape.members
        if value is None:
            # If the comes across the wire as "null" (None in python),
            # we should be returning this unchanged, instead of as an
            # empty dict.
            return None
        final_parsed = {}
        for member_name in member_shapes:
            member_shape = member_shapes[member_name]
            json_name = member_shape.serialization.get('name', member_name)
            raw_value = value.get(json_name)
            if raw_value is not None:
                final_parsed[member_name] = self._parse_shape(
                    member_shapes[member_name],
                    raw_value)
        return final_parsed

    def _handle_map(self, shape, value):
        parsed = {}
        key_shape = shape.key
        value_shape = shape.value
        for key, value in value.items():
            actual_key = self._parse_shape(key_shape, key)
            actual_value = self._parse_shape(value_shape, value)
            parsed[actual_key] = actual_value
        return parsed

    def _handle_blob(self, shape, value):
        return self._blob_parser(value)

    def _handle_timestamp(self, shape, value):
        return self._timestamp_parser(value)

    def _do_error_parse(self, response, shape):
        body = json.loads(response['body'].decode(self.DEFAULT_ENCODING))
        error = {"Error": {}, "ResponseMetadata": {}}
        # Error responses can have slightly different structures for json.
        # The basic structure is:
        #
        # {"__type":"ConnectClientException",
        #  "message":"The error message."}
        # Code, Type

        # The error message can either come in the 'message' or 'Message' key
        # so we need to check for both.
        error['Error']['Message'] = body.get('message', body.get('Message'))
        code = body.get('__type')
        if code is not None:
            # code has a couple forms as well:
            # * "com.aws.dynamodb.vAPI#ProvisionedThroughputExceededException"
            # * "ResourceNotFoundException"
            if '#' in code:
                code = code.rsplit('#', 1)[1]
            error['Error']['Code'] = code
        self._inject_response_metadata(error, response['headers'])
        return error

    def _inject_response_metadata(self, parsed, headers):
        if 'x-amzn-requestid' in headers:
            parsed.setdefault('ResponseMetadata', {})['RequestId'] = (
                headers['x-amzn-requestid'])


class JSONParser(BaseJSONParser):
    """Response parse for the "json" protocol."""
    def _do_parse(self, response, shape):
        # The json.loads() gives us the primitive JSON types,
        # but we need to traverse the parsed JSON data to convert
        # to richer types (blobs, timestamps, etc.
        parsed = {}
        if shape is not None:
            body = response['body'].decode(self.DEFAULT_ENCODING)
            original_parsed = json.loads(body)
            parsed = self._parse_shape(shape, original_parsed)
        self._inject_response_metadata(parsed, response['headers'])
        return parsed


class BaseRestParser(ResponseParser):

    def _do_parse(self, response, shape):
        final_parsed = {}
        final_parsed['ResponseMetadata'] = self._populate_response_metadata(
            response)
        if shape is None:
            return final_parsed
        member_shapes = shape.members
        self._parse_non_payload_attrs(response, shape,
                                      member_shapes, final_parsed)
        self._parse_payload(response, shape, member_shapes, final_parsed)
        return final_parsed

    def _populate_response_metadata(self, response):
        metadata = {}
        headers = response['headers']
        if 'x-amzn-requestid' in headers:
            metadata['RequestId'] = headers['x-amzn-requestid']
        elif 'x-amz-request-id' in headers:
            metadata['RequestId'] = headers['x-amz-request-id']
            # HostId is what it's called whenver this value is returned
            # in an XML response body, so to be consistent, we'll always
            # call is HostId.
            metadata['HostId'] = headers.get('x-amz-id-2', '')
        return metadata

    def _parse_payload(self, response, shape, member_shapes, final_parsed):
        if 'payload' in shape.serialization:
            # If a payload is specified in the output shape, then only that
            # shape is used for the body payload.
            payload_member_name = shape.serialization['payload']
            body_shape = member_shapes[payload_member_name]
            if body_shape.type_name in ['string', 'blob']:
                # This is a stream
                body = response['body']
                if isinstance(body, bytes):
                    body = body.decode(self.DEFAULT_ENCODING)
                final_parsed[payload_member_name] = body
            else:
                original_parsed = self._initial_body_parse(response['body'])
                final_parsed[payload_member_name] = self._parse_shape(
                    body_shape, original_parsed)
        else:
            original_parsed = self._initial_body_parse(response['body'])
            body_parsed = self._parse_shape(shape, original_parsed)
            final_parsed.update(body_parsed)

    def _parse_non_payload_attrs(self, response, shape,
                                 member_shapes, final_parsed):
        headers = response['headers']
        for name in member_shapes:
            member_shape = member_shapes[name]
            location = member_shape.serialization.get('location')
            if location is None:
                continue
            elif location == 'statusCode':
                final_parsed[name] = self._parse_shape(
                    member_shape, response['status_code'])
            elif location == 'headers':
                final_parsed[name] = self._parse_header_map(member_shape,
                                                            headers)
            elif location == 'header':
                header_name = member_shape.serialization.get('name', name)
                if header_name in headers:
                    final_parsed[name] = self._parse_shape(
                        member_shape, headers[header_name])

    def _parse_header_map(self, shape, headers):
        # Note that headers are case insensitive, so we .lower()
        # all header names and header prefixes.
        parsed = {}
        prefix = shape.serialization.get('name', '').lower()
        for header_name in headers:
            if header_name.lower().startswith(prefix):
                # The key name inserted into the parsed hash
                # strips off the prefix.
                name = header_name[len(prefix):]
                parsed[name] = headers[header_name]
        return parsed

    def _initial_body_parse(self, body_contents):
        # This method should do the initial xml/json parsing of the
        # body.  We we still need to walk the parsed body in order
        # to convert types, but this method will do the first round
        # of parsing.
        raise NotImplementedError("_initial_body_parse")


class RestJSONParser(BaseRestParser, BaseJSONParser):

    def _initial_body_parse(self, body_contents):
        if not body_contents:
            return {}
        body = body_contents.decode(self.DEFAULT_ENCODING)
        original_parsed = json.loads(body)
        return original_parsed

    def _do_error_parse(self, response, shape):
        body = self._initial_body_parse(response['body'])
        error = super(RestJSONParser, self)._do_error_parse(response, shape)
        error['Error']['Message'] = body.get('message',
                                             body.get('Message', ''))
        if 'x-amzn-errortype' in response['headers']:
            code = response['headers']['x-amzn-errortype']
            # Could be:
            # x-amzn-errortype: ValidationException:
            code = code.split(':')[0]
            error['Error']['Code'] = code
        elif 'code' in body or 'Code' in body:
            error['Error']['Code'] = body.get(
                'code', body.get('Code', ''))
        return error


class RestXMLParser(BaseRestParser, BaseXMLResponseParser):

    def _initial_body_parse(self, xml_string):
        if not xml_string:
            return xml.etree.cElementTree.Element('')
        return self._parse_xml_string_to_dom(xml_string)

    def _do_error_parse(self, response, shape):
        # We're trying to be service agnostic here, but S3 does have a slightly
        # different response structure for its errors compared to other
        # rest-xml serivces (route53/cloudfront).  We handle this by just
        # trying to parse both forms.
        # First:
        # <ErrorResponse xmlns="...">
        #   <Error>
        #     <Type>Sender</Type>
        #     <Code>InvalidInput</Code>
        #     <Message>Invalid resource type: foo</Message>
        #   </Error>
        #   <RequestId>request-id</RequestId>
        # </ErrorResponse>
        if response['body']:
            # If the body ends up being invalid xml, the xml parser should not
            # blow up. It should at least try to pull information about the
            # the error response from other sources like the HTTP status code.
            try:
                return self._parse_error_from_body(response)
            except ResponseParserError as e:
                LOG.debug(
                    'Exception caught when parsing error response body:',
                    exc_info=True)
        return self._parse_error_from_http_status(response)

    def _parse_error_from_http_status(self, response):
        return {
            'Error': {
                'Code': str(response['status_code']),
                'Message': six.moves.http_client.responses.get(
                    response['status_code'], ''),
            },
            'ResponseMetadata': {
                'RequestId': response['headers'].get('x-amz-request-id', ''),
                'HostId': response['headers'].get('x-amz-id-2', ''),
            }
        }

    def _parse_error_from_body(self, response):
        xml_contents = response['body']
        root = self._parse_xml_string_to_dom(xml_contents)
        parsed = self._build_name_to_xml_node(root)
        self._replace_nodes(parsed)
        if root.tag == 'Error':
            # This is an S3 error response.  First we'll populate the
            # response metadata.
            metadata = self._populate_response_metadata(response)
            # The RequestId and the HostId are already in the
            # ResponseMetadata, but are also duplicated in the XML
            # body.  We don't need these values in both places,
            # we'll just remove them from the parsed XML body.
            parsed.pop('RequestId', '')
            parsed.pop('HostId', '')
            return {'Error': parsed, 'ResponseMetadata': metadata}
        elif 'RequestId' in parsed:
            # Other rest-xml serivces:
            parsed['ResponseMetadata'] = {'RequestId': parsed.pop('RequestId')}
        default = {'Error': {'Message': '', 'Code': ''}}
        merge_dicts(default, parsed)
        return default


PROTOCOL_PARSERS = {
    'ec2': EC2QueryParser,
    'query': QueryParser,
    'json': JSONParser,
    'rest-json': RestJSONParser,
    'rest-xml': RestXMLParser,
}
