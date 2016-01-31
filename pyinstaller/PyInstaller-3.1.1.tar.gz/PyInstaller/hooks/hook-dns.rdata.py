#-----------------------------------------------------------------------------
# Copyright (c) 2013-2016, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------


# This is hook for DNS python package dnspython.

hiddenimports = [
    "dns.rdtypes.*",
    "dns.rdtypes.ANY.*"
]
