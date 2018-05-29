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
    h_names=[]
    descs=[]
    for el in searchers:
        names.append(el)
        h_names.append(searchers[el]['name'])
        descs.append(searchers[el]['desc'])
    return Response(utils.build_api_searchers(names, h_names, descs), mimetype='application/json')


@api2_page.route("/description/<db>")
def list_descriptions(db):
    dbstr = normalize('NFKD', db).encode('ascii','ignore')
    print(searchers)
    try:
        val = searchers[dbstr]
        print('FOUND!')
    except KeyError:
        val = None

    if (val):
        fn = val['info']
        lst = fn()
    else:
        lst = ['ERROR']
    return Response(utils.build_api_descriptions(dbstr, lst), mimetype='application/json')
