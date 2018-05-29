from unicodedata import normalize
from lmfdb.api2 import api2_page
from flask import render_template, request, url_for, current_app, Response
from lmfdb.api2.searchers import searchers
import utils

@api2_page.route("/")
def index():
    title = "Structure API"
    return render_template("api.html", **locals())


@api2_page.route("/description/searchers")
def list_searchers():
    names=[]
    descs=[]
    for el in searchers:
        names.append(el)
        descs.append(searchers[el]['desc'])
    return Response(utils.build_api_searchers(names, descs), mimetype='application/json')


@api2_page.route("/description/<db>")
def description(db):
    dbstr = normalize('NFKD', db).encode('ascii','ignore')
    try:
        val = searchers[dbstr]
    except KeyError:
        val = None

    if (val):
        fn = val['info']
        lst = fn()
    else:
        lst = ['ERROR']
    return Response(str(lst), mimetype='application/json')
