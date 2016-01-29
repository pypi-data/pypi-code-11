#   -*- coding: utf-8 -*-
#
#   This file is part of PyBuilder
#
#   Copyright 2011-2015 PyBuilder Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    The PyBuilder vcs module.
    Provides version control system utilities.
"""

from pybuilder.utils import execute_command_and_capture_output
from pybuilder.errors import PyBuilderException


class VCSRevision(object):
    """
    An object representing the VCS revision of the current working directory.
    """

    @property
    def count(self):
        """
        Returns the current revision number as a string.
        """
        if self.is_a_git_repo():
            return self.get_git_revision_count()

        if self.is_a_svn_repo():
            return self.get_svn_revision_count()

        raise PyBuilderException(
            "Cannot determine VCS revision: project is neither a git nor a svn repo.")

    def get_git_revision_count(self):
        # NOTE: git rev-list HEAD --count does not work on RHEL6, hence we count ourselves.
        exit_code, stdout, stderr = execute_command_and_capture_output(
            "git", "rev-list", "HEAD")
        if exit_code != 0:
            raise PyBuilderException("Cannot determine git revision: git rev-list HEAD failed:\n{0}".
                                     format(stderr))
        return str(len(stdout.splitlines()))

    def get_svn_revision_count(self):
        exit_code, stdout, stderr = execute_command_and_capture_output(
            "svnversion")
        if exit_code != 0 or "Unversioned directory" in stdout or "Uncommitted" in stdout:
            raise PyBuilderException("Cannot determine svn revision: svnversion failed or unversioned directory:\n{0}".
                                     format(stderr))
        return stdout.strip().replace("M", "").replace("S", "").replace("P", "").split(":")[0]

    def is_a_git_repo(self):
        exit_code, _, __ = execute_command_and_capture_output("git", "status")
        if exit_code == 0:
            return True
        return False

    def is_a_svn_repo(self):
        exit_code, stdout, stderr = execute_command_and_capture_output("svn", "status")
        if "not a working copy" in stderr or exit_code != 0:
            return False

        return True
