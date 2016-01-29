# -*- coding: utf-8 -*-
import logging

from chanjo.store import Gene
from flask import Blueprint, render_template

from chanjo_report.server.extensions import api

logger = logging.getLogger(__name__)
index_bp = Blueprint('index', __name__, template_folder='templates',
                     static_folder='static', static_url_path='/static/report')


@index_bp.route('/')
def index():
    sample_objs = api.samples()
    gene_objs = api.query(Gene).limit(50)
    return render_template('index/index.html', samples=sample_objs,
                           genes=gene_objs)
