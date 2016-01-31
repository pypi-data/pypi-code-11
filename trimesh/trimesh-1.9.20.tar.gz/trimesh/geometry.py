import numpy as np

from .transformations import rotation_matrix
from .constants       import tol
from .util            import unitize, stack_lines

def plane_transform(origin, normal):
    '''
    Given the origin and normal of a plane, find the transform that will move 
    that plane to be coplanar with the XY plane
    '''
    transform        =  align_vectors(normal, [0,0,1])
    transform[0:3,3] = -np.dot(transform, np.append(origin, 1))[0:3]
    return transform
    
def transform_around(matrix, point):
    point = np.array(point)
    translate = np.eye(4)
    translate[0:3,3] = -point
    result = np.dot(matrix, translate)
    translate[0:3,3] = point
    result = np.dot(translate, result)

    return result


def align_vectors(vector_start, vector_end, return_angle=False):
    '''
    Returns the 4x4 transformation matrix which will rotate from 
    vector_start (3,) to vector_end (3,), ex:
    
    vector_end == np.dot(T, np.append(vector_start, 1))[0:3]
    '''
    
    vector_start = unitize(vector_start)
    vector_end   = unitize(vector_end)
    cross        = np.cross(vector_start, vector_end)
    # we clip the norm to 1, as otherwise floating point bs
    # can cause the arcsin to error
    norm         = np.clip(np.linalg.norm(cross), -1.0, 1.0)
    direction    = np.sign(np.dot(vector_start, vector_end))
  
    if norm < tol.zero:
        # if the norm is zero, the vectors are the same
        # and no rotation is needed
        T       = np.eye(4)
        T[0:3] *= direction
    else:  
        angle = np.arcsin(norm) 
        if direction < 0:
            angle = np.pi - angle
        T = rotation_matrix(angle, cross)
    if return_angle:
        return T, angle
    return T
    
def faces_to_edges(faces, return_index=False):
    '''
    Given a list of faces (n,3), return a list of edges (n*3,2)
    '''

    edges = np.column_stack((faces[:,(0,1)],
                             faces[:,(1,2)],
                             faces[:,(2,0)])).reshape(-1,2)
    if return_index:
        face_index = np.tile(np.arange(len(faces)), (3,1)).T.reshape(-1)
        return edges, face_index
    return edges

def triangulate_quads(quads):
    '''
    Given a set of quad faces, return them as triangle faces.
    '''
    quads = np.array(quads)
    faces = np.vstack((quads[:,[0,1,2]],
                       quads[:,[2,3,0]]))
    return faces

def nondegenerate_faces(faces):
    '''
    Returns a 1D boolean array where non-degenerate faces are 'True'                        
    Faces should be (n, m) where for Trimeshes m=3. Returns (n) array                       
    '''
    nondegenerate = np.all(np.diff(np.sort(faces, axis=1), axis=1) != 0, axis=1)
    return nondegenerate
    
def mean_vertex_normals(count, faces, face_normals):
    '''
    roduce approximate vertex normals based on the
    average normals of adjacent faces.
    
    If vertices are merged with no regard to normal angle, this is
    going to render with weird shading.
    '''
    vertex_normals = np.zeros((count, 3,3))
    vertex_normals[[faces[:,0],0]] = face_normals
    vertex_normals[[faces[:,1],1]] = face_normals
    vertex_normals[[faces[:,2],2]] = face_normals
    mean_normals        = vertex_normals.mean(axis=1)
    unit_normals, valid = unitize(mean_normals, check_valid=True)

    mean_normals[valid] = unit_normals
    # if the mean normal is zero, it generally means: 
    # a) the vertex is only shared by 2 faces (mesh is not watertight)
    # b) the two faces that share the vertex have 
    #    normals pointed exactly opposite each other. 
    # since this means the vertex normal isn't defined, just make it anything
    mean_normals[np.logical_not(valid)] = [1,0,0]
    
    return mean_normals

def medial_axis(samples, contains):
    '''
    Given a set of samples on a boundary, find the approximate medial axis based
    on a voronoi diagram and a containment function which can assess whether
    a point is inside or outside of the closed geometry. 

    Arguments
    ----------
    samples:    (n,d) set of points on the boundary of the geometry
    contains:   function which takes (m,d) points and returns an (m) bool array

    Returns
    ----------
    lines:     (n,2,2) set of line segments
    '''

    from scipy.spatial import Voronoi
    from .path.io.load import load_path

    # create the voronoi diagram, after vertically stacking the points
    # deque from a sequnce into a clean (m,2) array
    voronoi = Voronoi(samples)
    # which voronoi vertices are contained inside the original polygon
    contained = contains(voronoi.vertices)
    # ridge vertices of -1 are outside, make sure they are False
    contained = np.append(contained, False)
    inside = [i for i in voronoi.ridge_vertices if contained[i].all()]
    line_indices = np.vstack([stack_lines(i) for i in inside if len(i) >=2])
    lines = voronoi.vertices[line_indices]    
    return load_path(lines)
