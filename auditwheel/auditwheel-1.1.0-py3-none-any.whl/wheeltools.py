""" General tools for working with wheels

Tools that aren't specific to delocation
"""

import os
from os.path import (join as pjoin, abspath, relpath, exists, sep as psep,
                     splitext, basename, dirname)
import glob
import hashlib
import csv
from itertools import product

from wheel.util import urlsafe_b64encode, open_for_csv, native
from wheel.pkginfo import read_pkg_info, write_pkg_info
from wheel.install import WheelFile, WHEEL_INFO_RE

from .tmpdirs import InTemporaryDirectory
from .tools import unique_by_index, zip2dir, dir2zip


class WheelToolsError(Exception):
    pass


def _dist_info_dir(bdist_dir):
    """Get the .dist-info directort from an unpacked wheel

    Parameters
    ----------
    bdist_dir : str
        Path of unpacked wheel file
    """

    info_dirs = glob.glob(pjoin(bdist_dir, '*.dist-info'))
    if len(info_dirs) != 1:
        raise WheelToolsError("Should be exactly one `*.dist_info` directory")
    return info_dirs[0]


def rewrite_record(bdist_dir):
    """ Rewrite RECORD file with hashes for all files in `wheel_sdir`

    Copied from :method:`wheel.bdist_wheel.bdist_wheel.write_record`

    Will also unsign wheel

    Parameters
    ----------
    bdist_dir : str
        Path of unpacked wheel file
    """
    info_dir = _dist_info_dir(bdist_dir)
    record_path = pjoin(info_dir, 'RECORD')
    record_relpath = relpath(record_path, bdist_dir)
    # Unsign wheel - because we're invalidating the record hash
    sig_path = pjoin(info_dir, 'RECORD.jws')
    if exists(sig_path):
        os.unlink(sig_path)

    def walk():
        for dir, dirs, files in os.walk(bdist_dir):
            for f in files:
                yield pjoin(dir, f)

    def skip(path):
        """Wheel hashes every possible file."""
        return (path == record_relpath)

    with open_for_csv(record_path, 'w+') as record_file:
        writer = csv.writer(record_file)
        for path in walk():
            relative_path = relpath(path, bdist_dir)
            if skip(relative_path):
                hash = ''
                size = ''
            else:
                with open(path, 'rb') as f:
                    data = f.read()
                digest = hashlib.sha256(data).digest()
                hash = 'sha256=' + native(urlsafe_b64encode(digest))
                size = len(data)
            record_path = relpath(path, bdist_dir).replace(psep, '/')
            writer.writerow((record_path, hash, size))


class InWheel(InTemporaryDirectory):
    """ Context manager for doing things inside wheels

    On entering, you'll find yourself in the root tree of the wheel.  If you've
    asked for an output wheel, then on exit we'll rewrite the wheel record and
    pack stuff up for you.
    """

    def __init__(self, in_wheel, out_wheel=None, ret_self=False):
        """ Initialize in-wheel context manager

        Parameters
        ----------
        in_wheel : str
            filename of wheel to unpack and work inside
        out_wheel : None or str:
            filename of wheel to write after exiting.  If None, don't write and
            discard
        ret_self : bool, optional
            If True, return ``self`` from ``__enter__``, otherwise return the
            directory path.
        """
        self.in_wheel = abspath(in_wheel)
        self.out_wheel = None if out_wheel is None else abspath(out_wheel)
        super(InWheel, self).__init__()

    def __enter__(self):
        zip2dir(self.in_wheel, self.name)
        return super(InWheel, self).__enter__()

    def __exit__(self, exc, value, tb):
        if self.out_wheel is not None:
            rewrite_record(self.name)
            dir2zip(self.name, self.out_wheel)
        return super(InWheel, self).__exit__(exc, value, tb)


class InWheelCtx(InWheel):
    """ Context manager for doing things inside wheels

    On entering, you'll find yourself in the root tree of the wheel.  If you've
    asked for an output wheel, then on exit we'll rewrite the wheel record and
    pack stuff up for you.

    The context manager returns itself from the __enter__ method, so you can
    set things like ``out_wheel``.  This is useful when processing in the wheel
    will dicate what the output wheel name is, or whether you want to save at
    all.

    The current path of the wheel contents is set in the attribute
    ``wheel_path``.
    """

    def __init__(self, in_wheel, out_wheel=None):
        """ Init in-wheel context manager returning self from enter

        Parameters
        ----------
        in_wheel : str
            filename of wheel to unpack and work inside
        out_wheel : None or str:
            filename of wheel to write after exiting.  If None, don't write and
            discard
        """
        super(InWheelCtx, self).__init__(in_wheel, out_wheel)
        self.path = None

    def __enter__(self):
        self.path = super(InWheelCtx, self).__enter__()
        return self

    def iter_files(self):
        record_names = glob.glob(os.path.join(self.path, '*.dist-info/RECORD'))
        if len(record_names) != 1:
            raise ValueError("Should be exactly one `*.dist_info` directory")

        with open(record_names[0]) as f:
            record = f.read()
        reader = csv.reader((native(r) for r in record.splitlines()))
        for row in reader:
            filename = row[0]
            yield filename


def add_platforms(wheel_ctx, platforms):
    """Add platform tags `platforms` to a wheel

    Add any platform tags in `platforms` that are missing
    to wheel_ctx's filename and ``WHEEL`` file.

    Parameters
    ----------
    wheel_ctx : InWheelCtx
        An open wheel context
    platforms : iterable
        platform tags to add to wheel filename and WHEEL tags - e.g.
        ``('macosx_10_9_intel', 'macosx_10_9_x86_64')
    """
    info_fname = pjoin(_dist_info_dir(wheel_ctx.path), 'WHEEL')
    info = read_pkg_info(info_fname)
    if info['Root-Is-Purelib'] == 'true':
        raise WheelToolsError('Cannot add platforms to pure wheel')

    # Check what tags we have
    if wheel_ctx.out_wheel is None:
        in_wheel = wheel_ctx.in_wheel
    else:
        raise NotImplementedError()

    parsed_fname = WHEEL_INFO_RE(basename(in_wheel))
    in_fname_tags = parsed_fname.groupdict()['plat'].split('.')
    extra_fname_tags = [tag for tag in platforms if tag not in in_fname_tags]
    in_wheel_base, ext = splitext(basename(in_wheel))
    out_wheel_base = '.'.join([in_wheel_base] + list(extra_fname_tags))
    out_wheel = out_wheel_base + ext

    in_info_tags = [tag for name, tag in info.items() if name == 'Tag']
    # Python version, C-API version combinations
    pyc_apis = ['-'.join(tag.split('-')[:2]) for tag in in_info_tags]
    # unique Python version, C-API version combinations
    pyc_apis = unique_by_index(pyc_apis)
    # Add new platform tags for each Python version, C-API combination
    required_tags = ['-'.join(tup) for tup in product(pyc_apis, platforms)]
    needs_write = False
    for req_tag in required_tags:
        if req_tag in in_info_tags:
            continue
        needs_write = True
        info.add_header('Tag', req_tag)
    if needs_write:
        write_pkg_info(info_fname, info)
        # Tell context manager to write wheel on exit by setting filename
        wheel_ctx.out_wheel = out_wheel
    return wheel_ctx.out_wheel
