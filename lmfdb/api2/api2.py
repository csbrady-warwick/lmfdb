from unicodedata import normalize
from lmfdb.api2 import api2_page
from flask import render_template, request, Response, make_response
from lmfdb.api2.searchers import searchers, singletons
import utils

@api2_page.route("api.css")
def api_css():
    response = make_response(render_template("api.css"))
    response.headers['Content-type'] = 'text/css'
    # don't cache css file, if in debug mode.
    if True:
        response.headers['Cache-Control'] = 'no-cache, no-store'
    else:
        response.headers['Cache-Control'] = 'public, max-age=600'
    return response

@api2_page.route("/")
def index():
    title = "Structure API"
    return render_template("api2.html", **locals())

@api2_page.route("/live/<db>/<coll>")
def live_page(db, coll):
    search = utils.create_search_dict(database=db, collection = coll, request = request)
    return Response(utils.build_api_search(db+'/'+coll, search, request = request), mimetype='application/json')

@api2_page.route("/pretty/<path:path_var>")
def prettify_live(path_var):
    bread = []
    return render_template('view.html', data_url=path_var, bread=bread)


@api2_page.route("/singletons/<path:path_var>")
def handle_singletons(path_var):
    val = path_var.rpartition('/')
    label = val[2]
    baseurl = val[0]
    while baseurl not in singletons:
       val = baseurl.rpartition('/')
       if val[0] == '': break
       baseurl = val[0]
       label = val[2] + '/' + label

    if baseurl in singletons:
        search = utils.create_search_dict(database = singletons[baseurl]['database'],
            collection = singletons[baseurl]['collection'], request = request)
        if singletons[baseurl]['full_search']:
            return Response(singletons[baseurl]['full_search'], mimetype='application/json')
        elif singletons[baseurl]['simple_search']:
            singletons[baseurl]['simple_search'](search, baseurl, label)
        else:
            search['query'] = {singletons[baseurl]['key']:label}
        return Response(utils.build_api_search(path_var, search, request = request), mimetype='application/json')
    return Response(utils.build_api_error(path_var), mimetype='application/json')

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
        if val.get('info', None): 
            lst = val['info']()
        else:
            lst = utils.get_filtered_fields(val['auto'])
    else:
        return Response(utils.build_api_error(searcher), mimetype='application/json')
    if list:
        return Response(utils.build_api_descriptions(dbstr, lst, request=request), mimetype='application/json')

@api2_page.route("/data/<searcher>")
def get_data(searcher):
    dbstr = normalize('NFKD', searcher).encode('ascii','ignore')
    try:
        val = searchers[dbstr]
    except KeyError:
        val = None

    if not val : return Response(utils.build_api_error(searcher), mimetype='application/json')

    splits = val['auto']

    search = utils.create_search_dict(database=splits[0], collection = splits[1], request = request)

    for el in request.args:
        utils.interpret(search['query'], el, request.args[el])
    return Response(utils.build_api_search('/data/'+searcher, search, request=request), mimetype='application/json')
#    return Response(utils.simple_search(search))
