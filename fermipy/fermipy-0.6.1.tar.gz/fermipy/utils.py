import os
import copy
from collections import OrderedDict

import numpy as np
from hpx_utils import HPX
import xml.etree.cElementTree as et
from astropy import units as u
from astropy.coordinates import SkyCoord
import astropy.io.fits as pyfits
import astropy.wcs as pywcs
import scipy.special as specialfn
from scipy.interpolate import UnivariateSpline


class Map_Base(object):
    """ Abstract representation of a 2D or 3D counts map."""

    def __init__(self, counts):
        self._counts = counts

    @property
    def counts(self):
        return self._counts


class Map(Map_Base):
    """ Representation of a 2D or 3D counts map using WCS. """

    def __init__(self, counts, wcs):
        """
        Parameters
        ----------
        counts : `~numpy.ndarray`
          Counts array.
        """
        Map_Base.__init__(self, counts)
        self._wcs = wcs

    @property
    def wcs(self):
        return self._wcs

    @staticmethod
    def create_from_fits(fitsfile, **kwargs):
        hdu = kwargs.get('hdu', 0)

        hdulist = pyfits.open(fitsfile)
        header = hdulist[hdu].header
        data = hdulist[hdu].data
        header = pyfits.Header.fromstring(header.tostring())
        wcs = pywcs.WCS(header)
        return Map(data, wcs)


class HpxMap(Map_Base):
    """ Representation of a 2D or 3D counts map using HEALPix. """

    def __init__(self, counts, hpx):
        Map_Base.__init__(self, counts)
        self._hpx = hpx

    @property
    def hpx(self):
        return self._hpx


def format_filename(outdir, basename, prefix=None, extension=None):
    filename = ''
    if prefix is not None:
        for t in prefix:
            if t: filename += '%s_' % t

    filename += basename

    if extension is not None:

        if extension.startswith('.'):
            filename += extension
        else:
            filename += '.' + extension

    return os.path.join(outdir, filename)


def gal2eq(l, b):
    RA_NGP = np.radians(192.859508333333)
    DEC_NGP = np.radians(27.1283361111111)
    L_CP = np.radians(122.932)
    L_0 = L_CP - np.pi / 2.
    RA_0 = RA_NGP + np.pi / 2.

    l = np.array(l, ndmin=1)
    b = np.array(b, ndmin=1)

    l, b = np.radians(l), np.radians(b)

    sind = np.sin(b) * np.sin(DEC_NGP) + np.cos(b) * np.cos(DEC_NGP) * np.sin(
        l - L_0)

    dec = np.arcsin(sind)

    cosa = np.cos(l - L_0) * np.cos(b) / np.cos(dec)
    sina = (np.cos(b) * np.sin(DEC_NGP) * np.sin(l - L_0) - np.sin(b) * np.cos(
        DEC_NGP)) / np.cos(dec)

    dec = np.degrees(dec)

    cosa[cosa<-1.0] = -1.0
    cosa[cosa>1.0] = 1.0
    
    ra = np.arccos(cosa)
    ra[np.where(sina < 0.)] = -ra[np.where(sina < 0.)]

    ra = np.degrees(ra + RA_0)

    ra = np.mod(ra, 360.)
    dec = np.mod(dec + 90., 180.) - 90.

    return ra, dec


def eq2gal(ra, dec):
    RA_NGP = np.radians(192.859508333333)
    DEC_NGP = np.radians(27.1283361111111)
    L_CP = np.radians(122.932)
    L_0 = L_CP - np.pi / 2.
    RA_0 = RA_NGP + np.pi / 2.
    DEC_0 = np.pi / 2. - DEC_NGP

    ra = np.array(ra, ndmin=1)
    dec = np.array(dec, ndmin=1)

    ra, dec = np.radians(ra), np.radians(dec)

    np.sinb = np.sin(dec) * np.cos(DEC_0) - np.cos(dec) * np.sin(
        ra - RA_0) * np.sin(DEC_0)

    b = np.arcsin(np.sinb)

    cosl = np.cos(dec) * np.cos(ra - RA_0) / np.cos(b)
    sinl = (np.sin(dec) * np.sin(DEC_0) + np.cos(dec) * np.sin(
        ra - RA_0) * np.cos(DEC_0)) / np.cos(b)

    b = np.degrees(b)

    cosl[cosl<-1.0] = -1.0
    cosl[cosl>1.0] = 1.0
    
    l = np.arccos(cosl)
    l[np.where(sinl < 0.)] = - l[np.where(sinl < 0.)]

    l = np.degrees(l + L_0)

    l = np.mod(l, 360.)
    b = np.mod(b + 90., 180.) - 90.

    return l, b


def apply_minmax_selection(val, val_minmax):
    if val_minmax is None:
        return True

    if val_minmax[0] is None:
        min_cut = True
    elif np.isfinite(val) and val >= val_minmax[0]:
        min_cut = True
    else:
        min_cut = False

    if val_minmax[1] is None:
        max_cut = True
    elif np.isfinite(val) and val <= val_minmax[1]:
        max_cut = True
    else:
        max_cut = False

    return (min_cut and max_cut)


def create_source_name(skydir):
    hms = skydir.icrs.ra.hms
    dms = skydir.icrs.dec.dms
    
    return 'PS J%02.f%04.1f%+03.f%02.f' % (hms.h,
                                           hms.m+hms.s/60.,
                                           dms.d, dms.m+dms.s/60.)


def create_model_name(src):
    """Generate a name for a source object given its spatial/spectral
    properties.

    Parameters
    ----------
    src : `~fermipy.roi_model.Source`
          A source object.

    Returns
    -------
    name : str
           A source name.
    """
    o = ''
    spatial_type = src['SpatialModel'].lower()
    o += spatial_type

    if spatial_type == 'gaussian':
        o += '_s%04.2f' % src['SpatialWidth']

    if src['SpectrumType'] == 'PowerLaw':
        o += '_powerlaw_%04.2f' % float(src.spectral_pars['Index']['value'])

    return o


def edge_to_center(edges):
    return 0.5 * (edges[1:] + edges[:-1])


def edge_to_width(edges):
    return (edges[1:] - edges[:-1])


def val_to_bin(edges, x):
    """Convert axis coordinate to bin index."""
    ibin = np.digitize(np.array(x, ndmin=1), edges) - 1
    return ibin


def val_to_edge(edges, x):
    """Convert axis coordinate to bin index."""
    edges = np.array(edges)
    w = edges[1:] - edges[:-1]
    w = np.insert(w, 0, w[0])
    ibin = np.digitize(np.array(x, ndmin=1), edges - 0.5 * w) - 1
    ibin[ibin < 0] = 0
    return ibin


def val_to_bin_bounded(edges, x):
    """Convert axis coordinate to bin index."""
    nbins = len(edges) - 1
    ibin = val_to_bin(edges, x)
    ibin[ibin < 0] = 0
    ibin[ibin > nbins - 1] = nbins - 1
    return ibin


def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def fits_recarray_to_dict(table):
    """Convert a FITS recarray to a python dictionary."""

    cols = {}
    for icol, col in enumerate(table.columns.names):

        col_data = table.data[col]
        #            print icol, col, type(col_data[0])

        if type(col_data[0]) == np.float32:
            cols[col] = np.array(col_data, dtype=float)
        elif type(col_data[0]) == np.float64:
            cols[col] = np.array(col_data, dtype=float)
        elif type(col_data[0]) == str:
            cols[col] = np.array(col_data, dtype=str)
        elif type(col_data[0]) == np.string_:
            cols[col] = np.array(col_data, dtype=str)
        elif type(col_data[0]) == np.int16:
            cols[col] = np.array(col_data, dtype=int)
        elif type(col_data[0]) == np.ndarray:
            cols[col] = np.array(col_data)
        else:
            print col, col_data
            raise Exception(
                'Unrecognized column type: %s %s' % (col, str(type(col_data))))

    return cols


def create_xml_element(root, name, attrib):
    el = et.SubElement(root, name)
    for k, v in attrib.iteritems(): el.set(k, v)
    return el


def load_xml_elements(root, path):
    o = {}
    for p in root.findall(path):

        if 'name' in p.attrib:
            o[p.attrib['name']] = copy.deepcopy(p.attrib)
        else:
            o.update(p.attrib)
    return o


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element.
    """
    from xml.dom import minidom
    import xml.etree.cElementTree as et

    rough_string = et.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def merge_dict(d0, d1, add_new_keys=False, append_arrays=False):
    """Recursively merge the contents of python dictionary d0 with
    the contents of another python dictionary, d1.

    add_new_keys : Do not skip keys that only exist in d1.

    append_arrays : If an element is a numpy array set the value of
    that element by concatenating the two arrays.
    """

    if d1 is None:
        return d0
    elif d0 is None:
        return d1
    elif d0 is None and d1 is None:
        return {}

    od = {}

    for k, v in d0.items():

        t0 = None
        t1 = None

        if k in d0: t0 = type(d0[k])
        if k in d1: t1 = type(d1[k])

        if k not in d1:
            od[k] = copy.deepcopy(d0[k])
        elif isinstance(v, dict) and isinstance(d1[k], dict):
            od[k] = merge_dict(d0[k], d1[k], add_new_keys, append_arrays)
        elif isinstance(v, list) and isinstance(d1[k], str):
            od[k] = d1[k].split(',')
        elif isinstance(v, np.ndarray) and append_arrays:
            od[k] = np.concatenate((v, d1[k]))
        elif (d0[k] is not None and d1[k] is not None) and t0 != t1:

            if t0 == dict or t0 == list:
                raise Exception('Conflicting types in dictionary merge for '
                                'key %s %s %s' % (k, t0, t1))
            od[k] = t0(d1[k])
        else:
            od[k] = copy.copy(d1[k])

    if add_new_keys:
        for k, v in d1.iteritems():
            if k not in d0:
                od[k] = copy.deepcopy(d1[k])

    return od


def tolist(x):
    """ convenience function that takes in a
        nested structure of lists and dictionaries
        and converts everything to its base objects.
        This is useful for dupming a file to yaml.

        (a) numpy arrays into python lists

            >>> type(tolist(np.asarray(123))) == int
            True
            >>> tolist(np.asarray([1,2,3])) == [1,2,3]
            True

        (b) numpy strings into python strings.

            >>> tolist([np.asarray('cat')])==['cat']
            True

        (c) an ordered dict to a dict

            >>> ordered=OrderedDict(a=1, b=2)
            >>> type(tolist(ordered)) == dict
            True

        (d) converts unicode to regular strings

            >>> type(u'a') == str
            False
            >>> type(tolist(u'a')) == str
            True

        (e) converts numbers & bools in strings to real represntation,
            (i.e. '123' -> 123)

            >>> type(tolist(np.asarray('123'))) == int
            True
            >>> type(tolist('123')) == int
            True
            >>> tolist('False') == False
            True
    """
    if isinstance(x, list):
        return map(tolist, x)
    elif isinstance(x, dict):
        return dict((tolist(k), tolist(v)) for k, v in x.items())
    elif isinstance(x, np.ndarray) or isinstance(x, np.number):
        # note, call tolist again to convert strings of numbers to numbers
        return tolist(x.tolist())
    elif isinstance(x, OrderedDict):
        return dict(x)
    elif isinstance(x, np.bool_):
        return bool(x)
    elif isinstance(x, basestring) or isinstance(x, np.str):
        x = str(x)  # convert unicode & numpy strings
        try:
            return int(x)
        except:
            try:
                return float(x)
            except:
                if x == 'True':
                    return True
                elif x == 'False':
                    return False
                else:
                    return x
    else:
        return x


def extract_mapcube_region(infile, skydir, outfile, maphdu=0):
    """Extract a region out of an all-sky mapcube file.

    Parameters
    ----------

    infile : str
        Path to mapcube file.
    
    skydir : `~astropy.coordinates.SkyCoord`

    """

    h = pyfits.open(os.path.expandvars(infile))

    npix = 200
    shape = list(h[maphdu].data.shape)
    shape[1] = 200
    shape[2] = 200

    wcs = pywcs.WCS(h[maphdu].header)
    skywcs = pywcs.WCS(h[maphdu].header, naxis=[1, 2])
    coordsys = get_coordsys(skywcs)

    region_wcs = wcs.deepcopy()

    if coordsys == 'CEL':
        region_wcs.wcs.crval[0] = skydir.ra.deg
        region_wcs.wcs.crval[1] = skydir.dec.deg
    elif coordsys == 'GAL':
        region_wcs.wcs.crval[0] = skydir.galactic.l.deg
        region_wcs.wcs.crval[1] = skydir.galactic.b.deg
    else:
        raise Exception('Unrecognized coordinate system.')

    region_wcs.wcs.crpix[0] = npix // 2 + 0.5
    region_wcs.wcs.crpix[1] = npix // 2 + 0.5

    from reproject import reproject_interp
    data, footprint = reproject_interp(h, region_wcs.to_header(), hdu_in=maphdu,
                                       shape_out=shape)

    hdu_image = pyfits.PrimaryHDU(data, header=region_wcs.to_header())
    hdulist = pyfits.HDUList([hdu_image, h['ENERGIES']])
    hdulist.writeto(outfile, clobber=True)


def create_wcs(skydir, coordsys='CEL', projection='AIT',
               cdelt=1.0, crpix=1., naxis=2):
    """Create a WCS object.

    Parameters
    ----------

    skydir : `~astropy.coordinates.SkyCoord`
        Sky coordinate of the WCS reference point.

    """

    from astropy import wcs

    w = wcs.WCS(naxis=naxis)
    #    w = wcs.WCS()

    if coordsys == 'CEL':
        w.wcs.ctype[0] = 'RA---%s' % (projection)
        w.wcs.ctype[1] = 'DEC--%s' % (projection)
        w.wcs.crval[0] = skydir.ra.deg
        w.wcs.crval[1] = skydir.dec.deg
    elif coordsys == 'GAL':
        w.wcs.ctype[0] = 'GLON-%s' % (projection)
        w.wcs.ctype[1] = 'GLAT-%s' % (projection)
        w.wcs.crval[0] = skydir.galactic.l.deg
        w.wcs.crval[1] = skydir.galactic.b.deg
    else:
        raise Exception('Unrecognized coordinate system.')

    w.wcs.crpix[0] = crpix
    w.wcs.crpix[1] = crpix
    w.wcs.cdelt[0] = -cdelt
    w.wcs.cdelt[1] = cdelt

    w = wcs.WCS(w.to_header())
    return w


def create_hpx_disk_region_string(skyDir, coordsys, radius, inclusive=0):
    """
    """
    if coordsys == "GAL":
        xref = skyDir.galactic.l.deg
        yref = skyDir.galactic.b.deg
    elif coordsys == "CEL":
        xref = skyDir.ra.deg
        yref = skyDir.dec.deg
    else:
        raise Exception("Unrecognized coordinate system %s" % coordsys)

    if inclusive:
        val = "DISK_INC(%.3f,%.3f,%.3f,%i)" % (xref, yref, radius, inclusive)
    else:
        val = "DISK(%.3f,%.3f,%.3f)" % (xref, yref, radius)
    return val


def create_hpx(nside, nest, coordsys='CEL', order=-1, region=None, ebins=None):
    """Create a HPX object.

    Parameters
    ----------

    nside    : int
      HEALPix nside paramter
    nest     : bool
      True for HEALPix "NESTED" indexing scheme, False for "RING" scheme.
    coordsys : str
      "CEL" or "GAL"
    order    : int
      nside = 2**order  
    region   : Allows for partial-sky mappings
    ebins    : Energy bin edges
    """
    return HPX(nside, nest, coordsys, order, region, ebins)


def get_coordsys(wcs):
    if 'RA' in wcs.wcs.ctype[0]:
        return 'CEL'
    elif 'GLON' in wcs.wcs.ctype[0]:
        return 'GAL'
    else:
        raise Exception('Unrecognized WCS coordinate system.')


def skydir_to_pix(skydir, wcs):
    """Convert skydir object to pixel coordinates."""

    if 'RA' in wcs.wcs.ctype[0]:
        xpix, ypix = wcs.wcs_world2pix(skydir.ra.deg, skydir.dec.deg, 0)
    elif 'GLON' in wcs.wcs.ctype[0]:
        xpix, ypix = wcs.wcs_world2pix(skydir.galactic.l.deg,
                                       skydir.galactic.b.deg, 0)
    else:
        raise Exception('Unrecognized WCS coordinate system.')

    return xpix, ypix


def pix_to_skydir(xpix, ypix, wcs):
    """Convert pixel coordinates to a skydir object."""

    if 'RA' in wcs.wcs.ctype[0]:
        ra, dec = wcs.wcs_pix2world(xpix, ypix, 0)
        return SkyCoord(ra, dec, unit=u.deg)
    elif 'GLON' in wcs.wcs.ctype[0]:
        glon, glat = wcs.wcs_pix2world(xpix, ypix, 0)
        return SkyCoord(glon, glat, unit=u.deg,
                        frame='galactic').transform_to('icrs')
    else:
        raise Exception('Unrecognized WCS coordinate system.')


def offset_to_sky(skydir, offset_lon, offset_lat,
                  coordsys='CEL', projection='AIT'):
    """Convert a cartesian offset (X,Y) in the given projection into
    a spherical coordinate."""

    offset_lon = np.array(offset_lon, ndmin=1)
    offset_lat = np.array(offset_lat, ndmin=1)

    w = create_wcs(skydir, coordsys, projection)
    pixcrd = np.vstack((offset_lon, offset_lat)).T

    return w.wcs_pix2world(pixcrd, 0)


def offset_to_skydir(skydir, offset_lon, offset_lat,
                     coordsys='CEL', projection='AIT'):
    """Convert a cartesian offset (X,Y) in the given projection into
    a spherical coordinate."""

    offset_lon = np.array(offset_lon, ndmin=1)
    offset_lat = np.array(offset_lat, ndmin=1)

    w = create_wcs(skydir, coordsys, projection)
    return SkyCoord.from_pixel(offset_lon, offset_lat, w, 0)


def sky_to_offset(skydir, lon, lat, coordsys='CEL', projection='AIT'):
    """Convert sky coordinates to a projected offset.  This function
    is the inverse of offset_to_sky."""

    w = create_wcs(skydir, coordsys, projection)
    skycrd = np.vstack((lon, lat)).T

    return w.wcs_world2pix(skycrd, 0)


def wcs_to_axes(w, npix):
    """Generate a sequence of bin edge vectors corresponding to the
    axes of a WCS object."""

    npix = npix[::-1]

    x = np.linspace(-(npix[0]) / 2., (npix[0]) / 2.,
                    npix[0] + 1) * np.abs(w.wcs.cdelt[0])
    y = np.linspace(-(npix[1]) / 2., (npix[1]) / 2.,
                    npix[1] + 1) * np.abs(w.wcs.cdelt[1])

    cdelt2 = np.log10((w.wcs.cdelt[2] + w.wcs.crval[2]) / w.wcs.crval[2])

    z = (np.linspace(0, npix[2], npix[2] + 1)) * cdelt2
    z += np.log10(w.wcs.crval[2])

    return x, y, z


def hpx_to_axes(h, npix):
    """ Generate a sequence of bin edge vectors corresponding to the
    axes of a HPX object."""
    x = h.ebins
    z = np.arange(npix[-1] + 1)

    return x, z


def wcs_to_coords(w, shape):
    """Generate an N x D list of pixel center coordinates where N is
    the number of pixels and D is the dimensionality of the map."""

    z, y, x = wcs_to_axes(w, shape)

    x = 0.5 * (x[1:] + x[:-1])
    y = 0.5 * (y[1:] + y[:-1])
    z = 0.5 * (z[1:] + z[:-1])

    x = np.ravel(np.ones(shape) * x[:, np.newaxis, np.newaxis])
    y = np.ravel(np.ones(shape) * y[np.newaxis, :, np.newaxis])
    z = np.ravel(np.ones(shape) * z[np.newaxis, np.newaxis, :])

    return np.vstack((x, y, z))


def hpx_to_coords(h, shape):
    """ Generate an N x D list of pixel center coordinates where N is
    the number of pixels and D is the dimensionality of the map."""

    x, z = hpx_to_axes(h, shape)

    x = np.sqrt(x[0:-1] * x[1:])
    z = z[:-1] + 0.5

    x = np.ravel(np.ones(shape) * x[:, np.newaxis])
    z = np.ravel(np.ones(shape) * z[np.newaxis, :])

    return np.vstack((x, z))


def get_target_skydir(config,default=None):
    radec = config.get('radec', None)

    if isinstance(radec, str):
        return SkyCoord(radec, unit=u.deg)
    elif isinstance(radec, list):
        return SkyCoord(radec[0], radec[1], unit=u.deg)

    ra = config.get('ra', None)
    dec = config.get('dec', None)

    if ra is not None and dec is not None:
        return SkyCoord(ra, dec, unit=u.deg)

    glon = config.get('glon', None)
    glat = config.get('glat', None)

    if glon is not None and glat is not None:
        return SkyCoord(glon, glat, unit=u.deg,
                        frame='galactic').transform_to('icrs')

    return default


def convolve2d_disk(fn, r, sig, nstep=100):
    """Evaluate the convolution f'(r) = f(r) * g(r) where f(r) is
    azimuthally symmetric function in two dimensions and g is a
    step function given by:

    g(r) = H(1-r/s)

    Parameters
    ----------

    fn : function
      Input function that takes a single radial coordinate parameter.

    r :  `~numpy.ndarray`
      Array of points at which the convolution is to be evaluated.

    sig : float
      Radius parameter of the step function.

    nstep : int
      Number of sampling point for numeric integration.
    """

    r = np.array(r, ndmin=1)
    sig = np.array(sig, ndmin=1)

    rmin = r - sig
    rmax = r + sig
    rmin[rmin < 0] = 0
    delta = (rmax - rmin) / nstep

    redge = rmin[:, np.newaxis] + delta[:, np.newaxis] * np.linspace(0, nstep,
                                                                     nstep + 1)[
                                                         np.newaxis, :]
    rp = 0.5 * (redge[:, 1:] + redge[:, :-1])
    dr = redge[:, 1:] - redge[:, :-1]
    fnv = fn(rp)

    r = r.reshape(r.shape + (1,))
    saxis = 1

    cphi = -np.ones(dr.shape)
    m = ((rp + r) / sig < 1) | (r == 0)

    rrp = r * rp
    sx = r ** 2 + rp ** 2 - sig ** 2
    cphi[~m] = sx[~m] / (2 * rrp[~m])
    dphi = 2 * np.arccos(cphi)
    v = rp * fnv * dphi * dr / (np.pi * sig * sig)
    s = np.sum(v, axis=saxis)

    return s


def convolve2d_gauss(fn, r, sig, nstep=100):
    """Evaluate the convolution f'(r) = f(r) * g(r) where f(r) is
    azimuthally symmetric function in two dimensions and g is a
    gaussian given by:

    g(r) = 1/(2*pi*s^2) Exp[-r^2/(2*s^2)]

    Parameters
    ----------

    fn : function
      Input function that takes a single radial coordinate parameter.

    r :  `~numpy.ndarray`
      Array of points at which the convolution is to be evaluated.

    sig : float
      Width parameter of the gaussian.

    nstep : int
      Number of sampling point for numeric integration.

    """
    r = np.array(r, ndmin=1)
    sig = np.array(sig, ndmin=1)

    rmin = r - 10 * sig
    rmax = r + 10 * sig
    rmin[rmin < 0] = 0
    delta = (rmax - rmin) / nstep

    redge = (rmin[:, np.newaxis] +
             delta[:, np.newaxis] *
             np.linspace(0, nstep, nstep + 1)[np.newaxis, :])

    rp = 0.5 * (redge[:, 1:] + redge[:, :-1])
    dr = redge[:, 1:] - redge[:, :-1]
    fnv = fn(rp)

    r = r.reshape(r.shape + (1,))
    saxis = 1

    sig2 = sig * sig
    x = r * rp / (sig2)

    if 'je_fn' not in convolve2d_gauss.__dict__:
        t = 10 ** np.linspace(-8, 8, 1000)
        t = np.insert(t, 0, [0])
        je = specialfn.ive(0, t)
        convolve2d_gauss.je_fn = UnivariateSpline(t, je, k=2, s=0)

    je = convolve2d_gauss.je_fn(x.flat).reshape(x.shape)
    #    je2 = specialfn.ive(0,x)
    v = (
    rp * fnv / (sig2) * je * np.exp(x - (r * r + rp * rp) / (2 * sig2)) * dr)
    s = np.sum(v, axis=saxis)

    return s


def make_pixel_offset(npix, xpix=0.0, ypix=0.0):
    """Make a 2D array with the distance of each pixel from a
    reference direction in pixel coordinates.  Pixel coordinates are
    defined such that (0,0) is located at the center of the coordinate
    grid."""

    dx = np.abs(np.linspace(0, npix - 1, npix) - (npix - 1) / 2. - xpix)
    dy = np.abs(np.linspace(0, npix - 1, npix) - (npix - 1) / 2. - ypix)
    dxy = np.zeros((npix, npix))
    dxy += np.sqrt(dx[np.newaxis, :] ** 2 + dy[:, np.newaxis] ** 2)

    return dxy


def make_gaussian_kernel(sigma, npix=501, cdelt=0.01, xpix=0.0, ypix=0.0):
    """Make kernel for a 2D gaussian.

    Parameters
    ----------

    sigma : float
      68% containment radius in degrees.
    """

    sigma /= 1.5095921854516636
    sigma /= cdelt

    fn = lambda t, s: 1. / (2 * np.pi * s ** 2) * np.exp(
        -t ** 2 / (s ** 2 * 2.0))
    dxy = make_pixel_offset(npix, xpix, ypix)
    k = fn(dxy, sigma)
    k /= (np.sum(k) * np.radians(cdelt) ** 2)

    return k


def make_disk_kernel(sigma, npix=501, cdelt=0.01, xpix=0.0, ypix=0.0):
    """Make kernel for a 2D disk.
    
    Parameters
    ----------

    sigma : float
      Disk radius in deg.
    """

    sigma /= cdelt
    fn = lambda t, s: 0.5 * (np.sign(s - t) + 1.0)

    dxy = make_pixel_offset(npix, xpix, ypix)
    k = fn(dxy, sigma)
    k /= (np.sum(k) * np.radians(cdelt) ** 2)

    return k


def make_cdisk_kernel(psf, sigma, npix, cdelt, xpix, ypix):
    """Make a kernel for a PSF-convolved 2D disk.

    Parameters
    ----------

    sigma : float
      68% containment radius in degrees.
    """

    dtheta = psf.dtheta
    egy = psf.energies

    x = make_pixel_offset(npix, xpix, ypix)
    x *= cdelt

    k = np.zeros((len(egy), npix, npix))
    for i in range(len(egy)):
        fn = lambda t: 10 ** np.interp(t, dtheta, np.log10(psf.val[:, i]))
        psfc = convolve2d_disk(fn, dtheta, sigma)
        k[i] = np.interp(np.ravel(x), dtheta, psfc).reshape(x.shape)
        k[i] /= (np.sum(k[i]) * np.radians(cdelt) ** 2)

    return k


def make_cgauss_kernel(psf, sigma, npix, cdelt, xpix, ypix):
    """Make a kernel for a PSF-convolved 2D gaussian.

    Parameters
    ----------

    sigma : float
      68% containment radius in degrees.
    """

    sigma /= 1.5095921854516636

    dtheta = psf.dtheta
    egy = psf.energies

    x = make_pixel_offset(npix, xpix, ypix)
    x *= cdelt

    k = np.zeros((len(egy), npix, npix))
    for i in range(len(egy)):
        fn = lambda t: 10 ** np.interp(t, dtheta, np.log10(psf.val[:, i]))
        psfc = convolve2d_gauss(fn, dtheta, sigma)
        k[i] = np.interp(np.ravel(x), dtheta, psfc).reshape(x.shape)
        k[i] /= (np.sum(k[i]) * np.radians(cdelt) ** 2)

    return k


def make_psf_kernel(psf, npix, cdelt, xpix, ypix):
    dtheta = psf.dtheta
    egy = psf.energies

    x = make_pixel_offset(npix, xpix, ypix)
    x *= cdelt
    
    k = np.zeros((len(egy), npix, npix))
    for i in range(len(egy)):
        k[i] = 10 ** np.interp(np.ravel(x), dtheta,
                               np.log10(psf.val[:, i])).reshape(x.shape)
        k[i] /= (np.sum(k[i]) * np.radians(cdelt) ** 2)

    return k


def rebin_map(k, nebin, npix, rebin):
    if rebin > 1:
        k = np.sum(k.reshape((nebin, npix * rebin, npix, rebin)), axis=3)
        k = k.swapaxes(1, 2)
        k = np.sum(k.reshape(nebin, npix, npix, rebin), axis=3)
        k = k.swapaxes(1, 2)

    k /= rebin ** 2

    return k


def make_srcmap(skydir, psf, spatial_model, sigma, npix=500, xpix=0.0, ypix=0.0,
                cdelt=0.01, rebin=1):
    """Compute the source map for a given spatial model."""

    energies = psf.energies
    nebin = len(energies)

    if spatial_model == 'GaussianSource':
        k = make_cgauss_kernel(psf, sigma, npix * rebin, cdelt / rebin,
                               xpix * rebin, ypix * rebin)
    elif spatial_model == 'DiskSource':
        k = make_cdisk_kernel(psf, sigma, npix * rebin, cdelt / rebin,
                              xpix * rebin, ypix * rebin)
    elif spatial_model == 'PSFSource':
        k = make_psf_kernel(psf, npix * rebin, cdelt / rebin,
                            xpix * rebin, ypix * rebin)
    else:
        raise Exception('Unrecognized spatial model: %s' % spatial_model)

    if rebin > 1:
        k = rebin_map(k, nebin, npix, rebin)

    k *= psf.exp[:, np.newaxis, np.newaxis] * np.radians(cdelt) ** 2

    return k


def make_cgauss_mapcube(skydir, psf, sigma, outfile, npix=500, cdelt=0.01,
                        rebin=1):
    energies = psf.energies
    nebin = len(energies)

    k = make_cgauss_kernel(psf, sigma, npix * rebin, cdelt / rebin)

    if rebin > 1:
        k = rebin_map(k, nebin, npix, rebin)
    w = create_wcs(skydir, cdelt=cdelt, crpix=npix / 2. + 0.5, naxis=3)

    w.wcs.crpix[2] = 1
    w.wcs.crval[2] = 10 ** energies[0]
    w.wcs.cdelt[2] = energies[1] - energies[0]
    w.wcs.ctype[2] = 'Energy'

    ecol = pyfits.Column(name='Energy', format='D', array=10 ** energies)
    hdu_energies = pyfits.BinTableHDU.from_columns([ecol], name='ENERGIES')

    hdu_image = pyfits.PrimaryHDU(np.zeros((nebin, npix, npix)),
                                  header=w.to_header())

    hdu_image.data[...] = k

    hdu_image.header['CUNIT3'] = 'MeV'

    hdulist = pyfits.HDUList([hdu_image, hdu_energies])
    hdulist.writeto(outfile, clobber=True)


def make_psf_mapcube(skydir, psf, outfile, npix=500, cdelt=0.01, rebin=1):
    energies = psf.energies
    nebin = len(energies)

    k = make_psf_kernel(psf, npix * rebin, cdelt / rebin)

    if rebin > 1:
        k = rebin_map(k, nebin, npix, rebin)
    w = create_wcs(skydir, cdelt=cdelt, crpix=npix / 2. + 0.5, naxis=3)

    w.wcs.crpix[2] = 1
    w.wcs.crval[2] = 10 ** energies[0]
    w.wcs.cdelt[2] = energies[1] - energies[0]
    w.wcs.ctype[2] = 'Energy'

    ecol = pyfits.Column(name='Energy', format='D', array=10 ** energies)
    hdu_energies = pyfits.BinTableHDU.from_columns([ecol], name='ENERGIES')

    hdu_image = pyfits.PrimaryHDU(np.zeros((nebin, npix, npix)),
                                  header=w.to_header())

    hdu_image.data[...] = k

    hdu_image.header['CUNIT3'] = 'MeV'

    hdulist = pyfits.HDUList([hdu_image, hdu_energies])
    hdulist.writeto(outfile, clobber=True)


def make_gaussian_spatial_map(skydir, sigma, outfile, npix=501, cdelt=0.01):
    w = create_wcs(skydir, cdelt=cdelt, crpix=npix / 2. + 0.5)
    hdu_image = pyfits.PrimaryHDU(np.zeros((npix, npix)),
                                  header=w.to_header())

    hdu_image.data[:, :] = make_gaussian_kernel(sigma, npix=npix, cdelt=cdelt)
    hdulist = pyfits.HDUList([hdu_image])
    hdulist.writeto(outfile, clobber=True)


def make_disk_spatial_map(skydir, sigma, outfile, npix=501, cdelt=0.01):
    w = create_wcs(skydir, cdelt=cdelt, crpix=npix / 2. + 0.5)

    hdu_image = pyfits.PrimaryHDU(np.zeros((npix, npix)),
                                  header=w.to_header())

    hdu_image.data[:, :] = make_disk_kernel(sigma, npix=npix, cdelt=cdelt)
    hdulist = pyfits.HDUList([hdu_image])
    hdulist.writeto(outfile, clobber=True)


def make_coadd_map(maps, proj, shape):
    from astropy import wcs
    if isinstance(proj, wcs.WCS):
        return make_coadd_wcs(maps, proj, shape)
    elif isinstance(proj, HPX):
        return make_coadd_hpx(maps, proj, shape)
    else:
        raise Exception("Can't co-add map of unknown type %s" % type(proj))


def make_coadd_wcs(maps, wcs, shape):
    data = np.zeros(shape)
    axes = wcs_to_axes(wcs, shape)

    for m in maps:
        c = wcs_to_coords(m.wcs, m.counts.shape)
        o = np.histogramdd(c.T, bins=axes[::-1], weights=np.ravel(m.counts))[0]
        data += o

    return Map(data, copy.deepcopy(wcs))


def make_coadd_hpx(maps, hpx, shape):
    data = np.zeros(shape)
    axes = hpx_to_axes(hpx, shape)
    for m in maps:
        c = hpx_to_coords(m.hpx, m.counts.shape)
        o = np.histogramdd(c.T, bins=axes, weights=np.ravel(m.counts))[0]
        data += o
    return HpxMap(data, copy.deepcopy(hpx))


def write_fits_image(data, wcs, outfile):
    hdu_image = pyfits.PrimaryHDU(data, header=wcs.to_header())
    #        hdulist = pyfits.HDUList([hdu_image,h['GTI'],h['EBOUNDS']])
    hdulist = pyfits.HDUList([hdu_image])
    hdulist.writeto(outfile, clobber=True)


def write_hpx_image(data, hpx, outfile, extname="SKYMAP"):
    hpx.write_fits(data, outfile, extname, clobber=True)


def delete_source_map(srcmap_file, name, logger=None):
    hdulist = pyfits.open(srcmap_file)
    hdunames = [hdu.name.upper() for hdu in hdulist]

    if not name.upper() in hdunames:
        return

    del hdulist[name.upper()]

    hdulist.writeto(srcmap_file, clobber=True)


def update_source_maps(srcmap_file, srcmaps, logger=None):
    hdulist = pyfits.open(srcmap_file)
    hdunames = [hdu.name.upper() for hdu in hdulist]

    for name, data in srcmaps.items():

        if not name.upper() in hdunames:

            for hdu in hdulist[1:]:
                if hdu.header['XTENSION'] == 'IMAGE':
                    break

            newhdu = pyfits.ImageHDU(data, hdu.header, name=name)
            newhdu.header['EXTNAME'] = name
            hdulist.append(newhdu)

        if logger is not None:
            logger.info('Updating source map for %s' % name)

        hdulist[name].data[...] = data
    hdulist.writeto(srcmap_file, clobber=True)
