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

class Connection(BaseModel):
    def detach(self):
        request(self.oc_address, '/vpn/network/detach/', {'token': self.token,
                                                          'connection_id': self.id})
