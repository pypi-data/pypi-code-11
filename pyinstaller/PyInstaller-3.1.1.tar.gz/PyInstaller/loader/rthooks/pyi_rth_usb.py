#-----------------------------------------------------------------------------
# Copyright (c) 2013-2016, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------


import ctypes
import glob
import os
import sys
# Pyusb changed these libusb module names in commit 2082e7.
try:
    import usb.backend.libusb10 as libusb10
except:
    import usb.backend.libusb1 as libusb10
try:
    import usb.backend.libusb01 as libusb01
except:
    import usb.backend.libusb0 as libusb01 
import usb.backend.openusb as openusb


def get_load_func(type, candidates):
    def _load_library(find_library=None):
        exec_path = sys._MEIPASS

        l = None
        for candidate in candidates:
            # Do linker's path lookup work to force load bundled copy.
            if os.name == 'posix' and sys.platform == 'darwin':
                libs = glob.glob("%s/%s*.dylib*" % (exec_path, candidate))
            elif sys.platform == 'win32' or sys.platform == 'cygwin':
                libs = glob.glob("%s\\%s*.dll" % (exec_path, candidate))
            else:
                libs = glob.glob("%s/%s*.so*" % (exec_path, candidate))
            for libname in libs:
                try:
                    # NOTE: libusb01 is using CDLL under win32.
                    # (see usb.backends.libusb01)
                    if sys.platform == 'win32' and type != 'libusb01':
                        l = ctypes.WinDLL(libname)
                    else:
                        l = ctypes.CDLL(libname)
                    if l is not None:
                        break
                except:
                    l = None
            if l is not None:
                break
        else:
            raise OSError('USB library could not be found')

        if type == 'libusb10':
            if not hasattr(l, 'libusb_init'):
                raise OSError('USB library could not be found')
        return l
    return _load_library


# NOTE: Need to keep in sync with future PyUSB updates.
if sys.platform == 'cygwin':
    libusb10._load_library = get_load_func('libusb10', ('cygusb-1.0', ))
    libusb01._load_library = get_load_func('libusb01', ('cygusb0', ))
    openusb._load_library = get_load_func('openusb', ('openusb', ))
else:
    libusb10._load_library = get_load_func('libusb10', ('usb-1.0', 'libusb-1.0', 'usb'))
    libusb01._load_library = get_load_func('libusb01', ('usb-0.1', 'usb', 'libusb0', 'libusb'))
    openusb._load_library = get_load_func('openusb', ('openusb', ))
