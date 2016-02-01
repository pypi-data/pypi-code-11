# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import psutil
import platform
import os
import stat
import sys
import struct

from gns3.qt import QtWidgets
from gns3.ui.doctor_dialog_ui import Ui_DoctorDialog
from gns3.servers import Servers
from gns3.local_config import LocalConfig
from gns3 import version
from gns3.modules.vmware import VMware

import logging
log = logging.getLogger(__name__)


class DoctorDialog(QtWidgets.QDialog, Ui_DoctorDialog):
    """
    This dialog allow user to detect error in his GNS3 installation.

    If you want to add a test add a method starting by check. The
    check return a tuple result and a message in case of failure.
    """

    def __init__(self, parent, console=False):

        super().__init__(parent)
        self._console = console
        self.setupUi(self)
        self.uiOkButton.clicked.connect(self._okButtonClickedSlot)
        for method in sorted(dir(self)):
            if method.startswith('check'):
                self.write(getattr(self, method).__doc__ + "...")
                (res, msg) = getattr(self, method)()
                if res == 0:
                    self.write('<span style="color: green"><strong>OK</strong></span>')
                elif res == 1:
                    self.write('<span style="color: orange"><strong>WARNING</strong> {}</span>'.format(msg))
                elif res == 2:
                    self.write('<span style="color: red"><strong>ERROR</strong> {}</span>'.format(msg))
                self.write("<br/>")

    def write(self, text):
        """
        Add text to the text windows
        """
        if self._console:
            print(text)
        self.uiDoctorResultTextEdit.setHtml(self.uiDoctorResultTextEdit.toHtml() + text)

    def _okButtonClickedSlot(self):
        self.accept()

    def checkLocalServerEnabled(self):
        """Checking if the local server is enabled"""
        if Servers.instance().shouldLocalServerAutoStart() is False:
            return (2, "The local server is disabled. Go to Preferences -> Server -> Local Server and enable the local server.")
        return (0, None)

    def checkDevVersionOfGNS3(self):
        """Checking for stable GNS3 version"""
        if version.__version_info__[3] != 0:
            return (1, "You are using a unstable version of GNS3.")
        return (0, None)

    def checkExperimentalFeaturesEnabled(self):
        """Checking if experimental features are not enabled"""
        if LocalConfig.instance().experimental():
            return (1, "Experimental features are enabled. Turn them off by going to Preferences -> General -> Miscellaneous.")
        return (0, None)

    def checkAVGInstalled(self):
        """Checking if AVG software is not installed"""

        for proc in psutil.process_iter():
            try:
                psinfo = proc.as_dict(["exe"])
                if psinfo["exe"] and "AVG\\" in psinfo["exe"]:
                    return (2, "AVG has known issues with GNS3, even after you disable it. You must whitelist dynamips.exe in the AVG preferences.")
            except psutil.NoSuchProcess:
                pass
        return (0, None)

    def checkFreeRam(self):
        """Checking for amount of free virtual memory"""

        if int(psutil.virtual_memory().available / (1024 * 1024)) < 600:
            return (2, "You have less than 600MB of available virtual memory, this could prevent nodes to start")
        return (0, None)

    def checkVmrun(self):
        """Checking if vmrun is installed"""
        vmrun = VMware.instance().findVmrun()
        if len(vmrun) == 0:
            return (1, "The vmrun executable could not be found, VMware VMs cannot be used")
        return (0, None)

    def check64Bit(self):
        """Check if processor is 64 bit"""
        if platform.architecture()[0] != "64bit":
            return (2, "The architecture {} is not supported.".format(platform.architecture()[0]))
        return (0, None)

    def checkUbridgePermission(self):
        """Check if ubridge has the correct permission"""
        if os.geteuid() == 0:
            # we are root, so we should have privileged access.
            return (0, None)

        path = Servers.instance().localServerSettings().get("ubridge_path")
        if path is None:
            return (0, None)

        request_setuid = False
        if sys.platform.startswith("linux"):
            if "security.capability" in os.listxattr(path):
                caps = os.getxattr(path, "security.capability")
                # test the 2nd byte and check if the 13th bit (CAP_NET_RAW) is set
                if not struct.unpack("<IIIII", caps)[1] & 1 << 13:
                    return(2, "Ubridge require CAP_NET_RAW. Run sudo setcap cap_net_admin,cap_net_raw=ep {path}".format(path=path))
            else:
                # capabilities not supported
                request_setuid = True

        if sys.platform.startswith("darwin") or request_setuid:
             if os.stat(path).st_uid != 0 or not os.stat(path).st_mode & stat.S_ISUID:
                return (2, "Ubridge should be setuid. Run sudo chown root {path} and sudo chmod 4755 {path}".format(path=path))
        return (0, None)

    def checkDynamipsPermission(self):
        """Check if dynamips has the correct permission"""
        if os.geteuid() == 0:
            # we are root, so we should have privileged access.
            return (0, None)

        path = Servers.instance().localServerSettings().get("dynamips_path")
        if path is None:
            return (0, None)

        if sys.platform.startswith("linux") and "security.capability" in os.listxattr(path):
            caps = os.getxattr(path, "security.capability")
            # test the 2nd byte and check if the 13th bit (CAP_NET_RAW) is set
            if not struct.unpack("<IIIII", caps)[1] & 1 << 13:
                return(2, "Dynamips require CAP_NET_RAW. Run sudo setcap cap_net_raw,cap_net_admin+eip {path}".format(path=path))
        return (0, None)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    dialog = DoctorDialog(main, console=True)
    #dialog.show()
    #exit_code = app.exec_()
