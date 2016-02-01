# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Change JSON data type from TEXT to LONGTEXT."""

from invenio_upgrader.api import op
from sqlalchemy.dialects import mysql

depends_on = [u'oauthclient_2014_03_02_initial']


def info():
    """Info."""
    return "Change JSON data type from TEXT to LONGTEXT"


def do_upgrade():
    """Do upgrade."""
    op.alter_column(
        u'remoteACCOUNT', 'extra_data',
        existing_type=mysql.TEXT(),
        type_=mysql.LONGTEXT(),
        nullable=True
    )


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1
