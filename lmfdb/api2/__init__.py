# -*- coding: utf-8 -*-
from lmfdb.base import app
from lmfdb.utils import make_logger
from flask import Blueprint

__version__ = "1.0.0"

api2_page = Blueprint("API2", __name__, template_folder='templates', static_folder="static")

import api2
assert api2

#@api2_page.route('/')
#def main_page():
#  return "<html>HELLO!</html>"

app.register_blueprint(api2_page, url_prefix="/api2")
