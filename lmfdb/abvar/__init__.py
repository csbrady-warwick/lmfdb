# -*- coding: utf-8 -*-
from lmfdb.base import app
from lmfdb.utils import make_logger
from flask import Blueprint
from lmfdb.api2.searchers import register_search_function

abvar_page = Blueprint("abvar", __name__, template_folder='templates', static_folder="static")
abvar_logger = make_logger(abvar_page)


@abvar_page.context_processor
def body_class():
    return {'body_class': 'abvar'}

app.register_blueprint(abvar_page, url_prefix="/Variety/Abelian")

register_search_function("elliptic_curves_q", "Elliptic Curves over Rationals",
    "Search over elliptic curves defined over rationals", auto_search=['elliptic_curves','curves'])
