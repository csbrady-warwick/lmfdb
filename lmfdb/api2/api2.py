from unicodedata import normalize
from lmfdb.api2 import api2_page
from flask import render_template, request, Response
from lmfdb.api2.searchers import searchers, singletons
import utils

@api2_page.route("/")
def index():
    title = "Structure API"
    return render_template("api2.html", **locals())

@api2_page.route("/live/<db>/<coll>")
def live_page(db, coll):
    search = utils.create_search_dict(database=db, collection = coll, request = request)
    return Response(utils.build_api_search(db+'/'+coll, search), mimetype='application/json')

@api2_page.route("/singletons/<path:path_var>")
def handle_singletons(path_var):
    val = path_var.rpartition('/')
    label = val[2]
    baseurl = val[0]
    while baseurl not in singletons:
       val = baseurl.rpartition('/')
       baseurl = val[0]
       label = val[2] + '/' + label

    if baseurl in singletons:
        search = utils.create_search_dict(database = singletons[baseurl]['database'], 
            collection = singletons[baseurl]['collection'], request = request)
        if singletons[baseurl]['full_search']:
            pass
        elif singletons[baseurl]['simple_search']:
            singletons[baseurl]['simple_search'](search, baseurl, label)
        else:
            search['query'] = {singletons[baseurl]['key']:label}
        return Response(utils.build_api_search(path_var, search), mimetype='application/json')


@api2_page.route("/description/searchers")
def list_searchers():
    names=[]
    h_names=[]
    descs=[]
    for el in searchers:
        names.append(el)
        h_names.append(searchers[el]['name'])
        descs.append(searchers[el]['desc'])
    return Response(utils.build_api_searchers(names, h_names, descs, request=request), mimetype='application/json')


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
    return Response(utils.build_api_descriptions(dbstr, lst, request=request), mimetype='application/json')

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
            if utils.compare_db_strings(els[el]['db_name'], db_name):
                return Response(utils.build_api_error(dbstr, utils.api_err_incompat_search))
        else:
            db_name = els[el]['db_name']

    splits = db_name.split('/')

    search = utils.create_search_dict(database=splits[0], collection = splits[1], request = request)

    for el in els:
        utils.interpret(search['query'], el, request.args[el])

    return Response(utils.simple_search(search))
