# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/bigtable/admin/cluster/v1/bigtable_cluster_service.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from gcloud.bigtable._generated import bigtable_cluster_data_pb2 as google_dot_bigtable_dot_admin_dot_cluster_dot_v1_dot_bigtable__cluster__data__pb2
from gcloud.bigtable._generated import bigtable_cluster_service_messages_pb2 as google_dot_bigtable_dot_admin_dot_cluster_dot_v1_dot_bigtable__cluster__service__messages__pb2
from google.longrunning import operations_pb2 as google_dot_longrunning_dot_operations__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='google/bigtable/admin/cluster/v1/bigtable_cluster_service.proto',
  package='google.bigtable.admin.cluster.v1',
  syntax='proto3',
  serialized_pb=b'\n?google/bigtable/admin/cluster/v1/bigtable_cluster_service.proto\x12 google.bigtable.admin.cluster.v1\x1a\x1cgoogle/api/annotations.proto\x1a<google/bigtable/admin/cluster/v1/bigtable_cluster_data.proto\x1aHgoogle/bigtable/admin/cluster/v1/bigtable_cluster_service_messages.proto\x1a#google/longrunning/operations.proto\x1a\x1bgoogle/protobuf/empty.proto2\x8f\t\n\x16\x42igtableClusterService\x12\x99\x01\n\tListZones\x12\x32.google.bigtable.admin.cluster.v1.ListZonesRequest\x1a\x33.google.bigtable.admin.cluster.v1.ListZonesResponse\"#\x82\xd3\xe4\x93\x02\x1d\x12\x1b/v1/{name=projects/*}/zones\x12\x9e\x01\n\nGetCluster\x12\x33.google.bigtable.admin.cluster.v1.GetClusterRequest\x1a).google.bigtable.admin.cluster.v1.Cluster\"0\x82\xd3\xe4\x93\x02*\x12(/v1/{name=projects/*/zones/*/clusters/*}\x12\xb0\x01\n\x0cListClusters\x12\x35.google.bigtable.admin.cluster.v1.ListClustersRequest\x1a\x36.google.bigtable.admin.cluster.v1.ListClustersResponse\"1\x82\xd3\xe4\x93\x02+\x12)/v1/{name=projects/*}/aggregated/clusters\x12\xa5\x01\n\rCreateCluster\x12\x36.google.bigtable.admin.cluster.v1.CreateClusterRequest\x1a).google.bigtable.admin.cluster.v1.Cluster\"1\x82\xd3\xe4\x93\x02+\"&/v1/{name=projects/*/zones/*}/clusters:\x01*\x12\x9a\x01\n\rUpdateCluster\x12).google.bigtable.admin.cluster.v1.Cluster\x1a).google.bigtable.admin.cluster.v1.Cluster\"3\x82\xd3\xe4\x93\x02-\x1a(/v1/{name=projects/*/zones/*/clusters/*}:\x01*\x12\x91\x01\n\rDeleteCluster\x12\x36.google.bigtable.admin.cluster.v1.DeleteClusterRequest\x1a\x16.google.protobuf.Empty\"0\x82\xd3\xe4\x93\x02**(/v1/{name=projects/*/zones/*/clusters/*}\x12\xab\x01\n\x0fUndeleteCluster\x12\x38.google.bigtable.admin.cluster.v1.UndeleteClusterRequest\x1a\x1d.google.longrunning.Operation\"?\x82\xd3\xe4\x93\x02\x39\"1/v1/{name=projects/*/zones/*/clusters/*}:undelete:\x04nullBF\n$com.google.bigtable.admin.cluster.v1B\x1c\x42igtableClusterServicesProtoP\x01\x62\x06proto3'
  ,
  dependencies=[google_dot_api_dot_annotations__pb2.DESCRIPTOR,google_dot_bigtable_dot_admin_dot_cluster_dot_v1_dot_bigtable__cluster__data__pb2.DESCRIPTOR,google_dot_bigtable_dot_admin_dot_cluster_dot_v1_dot_bigtable__cluster__service__messages__pb2.DESCRIPTOR,google_dot_longrunning_dot_operations__pb2.DESCRIPTOR,google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)





DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), b'\n$com.google.bigtable.admin.cluster.v1B\034BigtableClusterServicesProtoP\001')
import abc
from grpc.beta import implementations as beta_implementations
from grpc.early_adopter import implementations as early_adopter_implementations
from grpc.framework.alpha import utilities as alpha_utilities
from grpc.framework.common import cardinality
from grpc.framework.interfaces.face import utilities as face_utilities
class EarlyAdopterBigtableClusterServiceServicer(object):
  """<fill me in later!>"""
  __metaclass__ = abc.ABCMeta
  @abc.abstractmethod
  def ListZones(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def GetCluster(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def ListClusters(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def CreateCluster(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def UpdateCluster(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def DeleteCluster(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def UndeleteCluster(self, request, context):
    raise NotImplementedError()
class EarlyAdopterBigtableClusterServiceServer(object):
  """<fill me in later!>"""
  __metaclass__ = abc.ABCMeta
  @abc.abstractmethod
  def start(self):
    raise NotImplementedError()
  @abc.abstractmethod
  def stop(self):
    raise NotImplementedError()
class EarlyAdopterBigtableClusterServiceStub(object):
  """<fill me in later!>"""
  __metaclass__ = abc.ABCMeta
  @abc.abstractmethod
  def ListZones(self, request):
    raise NotImplementedError()
  ListZones.async = None
  @abc.abstractmethod
  def GetCluster(self, request):
    raise NotImplementedError()
  GetCluster.async = None
  @abc.abstractmethod
  def ListClusters(self, request):
    raise NotImplementedError()
  ListClusters.async = None
  @abc.abstractmethod
  def CreateCluster(self, request):
    raise NotImplementedError()
  CreateCluster.async = None
  @abc.abstractmethod
  def UpdateCluster(self, request):
    raise NotImplementedError()
  UpdateCluster.async = None
  @abc.abstractmethod
  def DeleteCluster(self, request):
    raise NotImplementedError()
  DeleteCluster.async = None
  @abc.abstractmethod
  def UndeleteCluster(self, request):
    raise NotImplementedError()
  UndeleteCluster.async = None
def early_adopter_create_BigtableClusterService_server(servicer, port, private_key=None, certificate_chain=None):
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import google.protobuf.empty_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import google.longrunning.operations_pb2
  method_service_descriptions = {
    "CreateCluster": alpha_utilities.unary_unary_service_description(
      servicer.CreateCluster,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.CreateClusterRequest.FromString,
      gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.SerializeToString,
    ),
    "DeleteCluster": alpha_utilities.unary_unary_service_description(
      servicer.DeleteCluster,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.DeleteClusterRequest.FromString,
      google.protobuf.empty_pb2.Empty.SerializeToString,
    ),
    "GetCluster": alpha_utilities.unary_unary_service_description(
      servicer.GetCluster,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.GetClusterRequest.FromString,
      gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.SerializeToString,
    ),
    "ListClusters": alpha_utilities.unary_unary_service_description(
      servicer.ListClusters,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListClustersRequest.FromString,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListClustersResponse.SerializeToString,
    ),
    "ListZones": alpha_utilities.unary_unary_service_description(
      servicer.ListZones,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListZonesRequest.FromString,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListZonesResponse.SerializeToString,
    ),
    "UndeleteCluster": alpha_utilities.unary_unary_service_description(
      servicer.UndeleteCluster,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.UndeleteClusterRequest.FromString,
      google.longrunning.operations_pb2.Operation.SerializeToString,
    ),
    "UpdateCluster": alpha_utilities.unary_unary_service_description(
      servicer.UpdateCluster,
      gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.FromString,
      gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.SerializeToString,
    ),
  }
  return early_adopter_implementations.server("google.bigtable.admin.cluster.v1.BigtableClusterService", method_service_descriptions, port, private_key=private_key, certificate_chain=certificate_chain)
def early_adopter_create_BigtableClusterService_stub(host, port, metadata_transformer=None, secure=False, root_certificates=None, private_key=None, certificate_chain=None, server_host_override=None):
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import google.protobuf.empty_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import google.longrunning.operations_pb2
  method_invocation_descriptions = {
    "CreateCluster": alpha_utilities.unary_unary_invocation_description(
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.CreateClusterRequest.SerializeToString,
      gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.FromString,
    ),
    "DeleteCluster": alpha_utilities.unary_unary_invocation_description(
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.DeleteClusterRequest.SerializeToString,
      google.protobuf.empty_pb2.Empty.FromString,
    ),
    "GetCluster": alpha_utilities.unary_unary_invocation_description(
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.GetClusterRequest.SerializeToString,
      gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.FromString,
    ),
    "ListClusters": alpha_utilities.unary_unary_invocation_description(
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListClustersRequest.SerializeToString,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListClustersResponse.FromString,
    ),
    "ListZones": alpha_utilities.unary_unary_invocation_description(
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListZonesRequest.SerializeToString,
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListZonesResponse.FromString,
    ),
    "UndeleteCluster": alpha_utilities.unary_unary_invocation_description(
      gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.UndeleteClusterRequest.SerializeToString,
      google.longrunning.operations_pb2.Operation.FromString,
    ),
    "UpdateCluster": alpha_utilities.unary_unary_invocation_description(
      gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.SerializeToString,
      gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.FromString,
    ),
  }
  return early_adopter_implementations.stub("google.bigtable.admin.cluster.v1.BigtableClusterService", method_invocation_descriptions, host, port, metadata_transformer=metadata_transformer, secure=secure, root_certificates=root_certificates, private_key=private_key, certificate_chain=certificate_chain, server_host_override=server_host_override)

class BetaBigtableClusterServiceServicer(object):
  """<fill me in later!>"""
  __metaclass__ = abc.ABCMeta
  @abc.abstractmethod
  def ListZones(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def GetCluster(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def ListClusters(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def CreateCluster(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def UpdateCluster(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def DeleteCluster(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def UndeleteCluster(self, request, context):
    raise NotImplementedError()

class BetaBigtableClusterServiceStub(object):
  """The interface to which stubs will conform."""
  __metaclass__ = abc.ABCMeta
  @abc.abstractmethod
  def ListZones(self, request, timeout):
    raise NotImplementedError()
  ListZones.future = None
  @abc.abstractmethod
  def GetCluster(self, request, timeout):
    raise NotImplementedError()
  GetCluster.future = None
  @abc.abstractmethod
  def ListClusters(self, request, timeout):
    raise NotImplementedError()
  ListClusters.future = None
  @abc.abstractmethod
  def CreateCluster(self, request, timeout):
    raise NotImplementedError()
  CreateCluster.future = None
  @abc.abstractmethod
  def UpdateCluster(self, request, timeout):
    raise NotImplementedError()
  UpdateCluster.future = None
  @abc.abstractmethod
  def DeleteCluster(self, request, timeout):
    raise NotImplementedError()
  DeleteCluster.future = None
  @abc.abstractmethod
  def UndeleteCluster(self, request, timeout):
    raise NotImplementedError()
  UndeleteCluster.future = None

def beta_create_BigtableClusterService_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import google.protobuf.empty_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import google.longrunning.operations_pb2
  request_deserializers = {
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'CreateCluster'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.CreateClusterRequest.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'DeleteCluster'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.DeleteClusterRequest.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'GetCluster'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.GetClusterRequest.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListClusters'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListClustersRequest.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListZones'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListZonesRequest.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UndeleteCluster'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.UndeleteClusterRequest.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UpdateCluster'): gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.FromString,
  }
  response_serializers = {
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'CreateCluster'): gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'DeleteCluster'): google.protobuf.empty_pb2.Empty.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'GetCluster'): gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListClusters'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListClustersResponse.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListZones'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListZonesResponse.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UndeleteCluster'): google.longrunning.operations_pb2.Operation.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UpdateCluster'): gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.SerializeToString,
  }
  method_implementations = {
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'CreateCluster'): face_utilities.unary_unary_inline(servicer.CreateCluster),
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'DeleteCluster'): face_utilities.unary_unary_inline(servicer.DeleteCluster),
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'GetCluster'): face_utilities.unary_unary_inline(servicer.GetCluster),
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListClusters'): face_utilities.unary_unary_inline(servicer.ListClusters),
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListZones'): face_utilities.unary_unary_inline(servicer.ListZones),
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UndeleteCluster'): face_utilities.unary_unary_inline(servicer.UndeleteCluster),
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UpdateCluster'): face_utilities.unary_unary_inline(servicer.UpdateCluster),
  }
  server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
  return beta_implementations.server(method_implementations, options=server_options)

def beta_create_BigtableClusterService_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_data_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import google.protobuf.empty_pb2
  import gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2
  import google.longrunning.operations_pb2
  request_serializers = {
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'CreateCluster'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.CreateClusterRequest.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'DeleteCluster'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.DeleteClusterRequest.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'GetCluster'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.GetClusterRequest.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListClusters'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListClustersRequest.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListZones'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListZonesRequest.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UndeleteCluster'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.UndeleteClusterRequest.SerializeToString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UpdateCluster'): gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.SerializeToString,
  }
  response_deserializers = {
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'CreateCluster'): gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'DeleteCluster'): google.protobuf.empty_pb2.Empty.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'GetCluster'): gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListClusters'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListClustersResponse.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'ListZones'): gcloud.bigtable._generated.bigtable_cluster_service_messages_pb2.ListZonesResponse.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UndeleteCluster'): google.longrunning.operations_pb2.Operation.FromString,
    ('google.bigtable.admin.cluster.v1.BigtableClusterService', 'UpdateCluster'): gcloud.bigtable._generated.bigtable_cluster_data_pb2.Cluster.FromString,
  }
  cardinalities = {
    'CreateCluster': cardinality.Cardinality.UNARY_UNARY,
    'DeleteCluster': cardinality.Cardinality.UNARY_UNARY,
    'GetCluster': cardinality.Cardinality.UNARY_UNARY,
    'ListClusters': cardinality.Cardinality.UNARY_UNARY,
    'ListZones': cardinality.Cardinality.UNARY_UNARY,
    'UndeleteCluster': cardinality.Cardinality.UNARY_UNARY,
    'UpdateCluster': cardinality.Cardinality.UNARY_UNARY,
  }
  stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
  return beta_implementations.dynamic_stub(channel, 'google.bigtable.admin.cluster.v1.BigtableClusterService', cardinalities, options=stub_options)
# @@protoc_insertion_point(module_scope)
