from unicodedata import normalize
from lmfdb.api2 import api2_page
from flask import render_template, request, url_for, current_app, Response
from lmfdb.api2.searchers import searchers
import utils

@api2_page.route("/")
def index():
    title = "Structure API"
    return render_template("api2.html", **locals())


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


@api2_page.route("/description/<searcher>")
def list_descriptions(searcher):
    dbstr = normalize('NFKD', searcher).encode('ascii','ignore')
    try:
        val = searchers[dbstr]
    except KeyError:
        val = None

    if (val):
        fn = val['info']
        lst = fn()
    else:
        lst = ['ERROR']
    return Response(utils.build_api_descriptions(dbstr, lst), mimetype='application/json')

@api2_page.route("/data/<searcher>")
def get_data(searcher):
    dbstr = normalize('NFKD', searcher).encode('ascii','ignore')
    try:
        val = searchers[dbstr]
    except KeyError:
        val = None

    data = val['info']()
    els = {}
    for el in request.args:
        if el in data:
            els[el] = data[el]

    db_name = None
    for el in els:
        if db_name:
            if compare_db_strings(el['db_name'], db_name):
                return Response(utils.build_api_error(dbstr, api_err_incompat_search))
        else:
            db_name = el['db_name']

    splits = db_name.split('/')

    search = {}
    #Recover the database name and collection name
    search['db_name'] = splits[0]
    search['coll_name'] = splits[1]
    search['fields'] = []

#    for el in els:
#        search['fields'].append({
    

    return Response(els)
