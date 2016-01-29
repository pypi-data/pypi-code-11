# -*- coding: utf-8 -*-

# ########################## Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
#                                                                              #
# This file is part of PyGithub. http://jacquev6.github.com/PyGithub/          #
#                                                                              #
# PyGithub is free software: you can redistribute it and/or modify it under    #
# the terms of the GNU Lesser General Public License as published by the Free  #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# PyGithub is distributed in the hope that it will be useful, but WITHOUT ANY  #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS    #
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more #
# details.                                                                     #
#                                                                              #
# You should have received a copy of the GNU Lesser General Public License     #
# along with PyGithub. If not, see <http://www.gnu.org/licenses/>.             #
#                                                                              #
# ##############################################################################

import github.GithubObject


class GitignoreTemplate(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents GitignoreTemplates as returned for example by http://developer.github.com/v3/todo
    """

    @property
    def source(self):
        """
        :type: string
        """
        return self._source.value

    @property
    def name(self):
        """
        :type: string
        """
        return self._name.value

    def _initAttributes(self):
        self._source = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "source" in attributes:  # pragma no branch
            self._source = self._makeStringAttribute(attributes["source"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
