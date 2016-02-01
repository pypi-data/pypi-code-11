"""
Copyright (c) 2014 Maciej Nabozny

This file is part of CloudOver project.

CloudOver is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pycore.utils import request, calc_hash
from pycore.models.base_model import BaseModel

class Permission(BaseModel):
    def __init__(self, address, login, password, seed, permission_dict, debug=False):
        self.login = login
        self.password = password
        self.oc_address = address
        self.seed = seed
        self.debug = debug

        self.token = None
        tokens = request(self.oc_address, '/user/token/get_list/', {'login': self.login,
                                                                    'pw_hash': calc_hash(self.password, self.seed),
                                                                    'name': 'pycloud'}, self.debug)
        if len(tokens) == 0:
            self.token = request(self.oc_address, '/user/token/create/', {'login': self.login,
                                                                          'pw_hash': calc_hash(self.password, self.seed),
                                                                          'name': 'pycloud'}, self.debug)['token']
        else:
            self.token = tokens[0]['token']

        BaseModel.__init__(self, self.oc_address, self.token, permission_dict)


    def __str__(self):
        return self.function


    def attach(self, token):
        request(self.oc_address, '/user/permission/attach/', {'login': self.login,
                                                         'pw_hash': calc_hash(self.password, self.seed),
                                                         'function': self.function,
                                                         'token_id': token.id})


    def detach(self, token):
        request(self.oc_address, '/user/permission/detach/', {'login': self.login,
                                                         'pw_hash': calc_hash(self.password, self.seed),
                                                         'function': self.function,
                                                         'token_id': token.id})
