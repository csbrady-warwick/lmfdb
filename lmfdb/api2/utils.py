import datetime
from lmfdb.api2 import __version__
import json
from bson.objectid import ObjectId
import lmfdb.base as base

api_version = __version__

api_type_searchers = 'API_SEARCHERS'
api_type_descriptions = 'API_DESCRIPTIONS'
api_type_records = 'API_RECORDS'

class test_obj:
    def _toJSON(self):
        return ['TEST','OBJECT']

class APIEncoder(json.JSONEncoder):
    def default(self, obj):
      try:
        return obj._toJSON()
      except:
          try:
              return str(obj)
          except:
              return json.JSONEncoder.default(self, obj)

def create_search_dict(database='', collection='', query=None, view_start=0):
    """
    Build an empty search dictionary
    """

    if query is None:
        query_alpha = {}
    else:
        query_alpha = query

    search = {'database':database, 'collection':collection, 'query':query_alpha, 'view_start':view_start}
    return search


def build_api_wrapper(api_key, api_type, data):
    """
    Build the outer wrapper of an API structure. This is used both for search results and for description queries.
    Is an outer structure so that it can be extended without collisions with data

    api_key -- Key name for API call. Is not checked for correctness
    api_type -- Type of the API data being returned, should be named constant as above (api_type_*)
    data -- Container holding the inner data, should match the format expected for api_type
    """

    return json.dumps({"key":api_key, 'built_at':str(datetime.datetime.now()), 
        'api_version':api_version, 'type':api_type, 'has_api2':False, 'data':data},
        indent=4, sort_keys=False, cls = APIEncoder)

def build_api_records(api_key, record_count, view_start, view_count, record_list, \
                        max_count=None):
    """
    Build an API object from a set of records. Automatically calculates point to start view to get next record.
    'View' is the concept of which part of all of the records returned by a query is contained in _this_ api response

    Arguments:
    api_key -- Named API key as registered with register_search_function
    record_count -- Total number of records returned by the query
    view_start -- Point at which the current view starts in records
    view_count -- Number of records in the current view. Must be less than max_count if max_count is specified
    record_list -- Dictionary containing the records in the current view

    Keyword arguments:
    max_count -- The maximum number of records in a view that a client can request. This should be the same as
                 is returned in the main API page unless this value cannot be inferred without context

    """
    view_count = min(view_count, record_count-view_start)
    next_block = view_start + view_count if view_start + view_count < record_count else -1
    keys = {"record_count":record_count, "view_start":view_start, "view_count":view_count, \
            "view_next":next_block,"records":record_list}
    if max_count: keys['api_max_count'] = max_count
    return build_api_wrapper(api_key, api_type_records, keys)

def build_api_search(api_key, search_dict, max_count=None):
    """
    Build an API object from a set of records. Automatically calculates point to start view to get next record.
    'View' is the concept of which part of all of the records returned by a query is contained in _this_ api response

    Arguments:
    api_key -- Named API key as registered with register_search_function
    search_dict -- Search dictionary compatible with simple_search

    Keyword arguments:
    max_count -- The maximum number of records in a view that a client can request. This should be the same as
                 is returned in the main API page unless this value cannot be inferred without context

    """

    metadata, data = simple_search(search_dict)
    return build_api_records(api_key, metadata['record_count'], search_dict['view_start'], 
        metadata['view_count'], data, max_count = max_count)

def build_api_searchers(names, human_names, descriptions):

    """
    Build an API response for the list of available searchers
    human_names -- List of human readable names
    names -- List of names of searchers
    descriptions -- List of descriptions for searchers
    """
    item_list = [{'name':n, 'human_name':h, 'desc':d} for n, h, d in zip(names, human_names, descriptions)]
    
    return build_api_wrapper('GLOBAL', api_type_searchers, item_list)



def build_api_descriptions(api_key, description_object):

    """
    Build an API response for the descriptions of individual searches provided by a searcher
    api_key -- Named API key as registered with register_search_function
    description_object -- Description object
    """
    return build_api_wrapper(api_key, api_type_descriptions, description_object)



def build_description(objlist, name, desc, type, h_name, 
    db_name=None, coll_name=None, field_name=None):

    """
    Build a description object by specifying a new searchable field
    If this maps to searching a single database field then the user should supply
    the db_name, coll_name and field_name objects
    objlist -- searcher object(dictionary) that is being built
    name -- Name of search key, must be unique
    desc -- Description of searcher, if None will be obtained from inventory if is search on single field
    type -- type of search that can be performed. Not used yet
    h_name -- Short human readable name for search
    db_name -- Name of database to be searched by this searcher. Optional
    coll_name -- Name of collection to be searched by this searcher. Optional
    field_name -- Name of field to be searched by this searcher. Optional
    """
    

    objlist[name] = {}
    objlist[name]['human_name'] = h_name
    if (db_name and coll_name and field_name):
        objlist[name]['db_name'] = db_name + '/' + coll_name + '/' + field_name
    else:
        objlist[name]['db_name'] = '@@SPECIAL@@'
    if desc is None:
        desc_obj = test_obj()
    else:
        desc_obj = desc
    objlist[name]['desc'] = desc_obj
    objlist[name]['type'] = type


def default_projection(info):
    """
    Build a projection from an info dictionary as returned by flask. _id always excluded

    Keywords of info dict used:
    exclude -- logical for whether to build an inclusive or exclusive projection (default False)
    fields -- comma separated list of fields to include (exclude if keyword set)

    """
    try:
        fields = info['fields'].split(',')
        exclude = False
        try:
            info['exclude']
            exclude = True
        except:
            pass
        project = build_query_projection(fields, exclude = exclude)
    except KeyError:
        project = None
    return project

def build_query_projection(field_list, exclude=False):
    """
    Builds a PyMongo compatible query projection dictionary

    Arguments:
    field_list -- List of fields to include (exclude if keyword set)

    Keyword arguments:
    exclude -- logical for whether to build an inclusive or exclusive projection (default False)

    """
    keys = {"_id":0}
    val = 1
    if exclude: val = 0
    for el in field_list:
        keys[el] = val
    return keys

def compare_db_strings(str1, str2):
    """
    Compare two database strings for compatability. Same db and collection, not same field
    str1 -- First database string to compare
    str2 -- Second database string to compare
    """

    splt1 = str1.split('/')
    splt2 = str2.split('/')

    if (len(splt1) < 3 or len(splt2) < 3): return False
    return (splt1[0] == splt2[0]) and (splt1[1] == splt2[1])

def interpret(query, qkey, qval):

    """
    Try to interpret a user supplied value into a mongo query
    query -- Existing (can be blank) dictionary to build the query in
    qkey -- Key (field to be searched in)
    qval -- Value (taken from user)
    
    """

    DELIM = ','

    from ast import literal_eval
    try:
        if qkey.startswith("_"):
            pass
        elif qval.startswith("s"):
            qval = qval[1:]
        elif qval.startswith("i"):
            qval = int(qval[1:])
        elif qval.startswith("f"):
            qval = float(qval[1:])
        elif qval.startswith("o"):
            qval = ObjectId(qval[1:])
        elif qval.startswith("ls"):      # indicator, that it might be a list of strings
            qval = qval[2:].split(DELIM)
        elif qval.startswith("li"):
            qval = [int(_) for _ in qval[2:].split(DELIM)]
        elif qval.startswith("lf"):
            qval = [float(_) for _ in qval[2:].split(DELIM)]
        elif qval.startswith("py"):     # literal evaluation
            qval = literal_eval(qval[2:])
        elif qval.startswith("cs"):     # containing string in list
            qval = { "$in" : [qval[2:]] }
        elif qval.startswith("ci"):
            qval = { "$in" : [int(qval[2:])] }
        elif qval.startswith("cf"):
            qval = { "$in" : [float(qval[2:])] }
        elif qval.startswith("cpy"):
            qval = { "$in" : [literal_eval(qval[3:])] }
    except:
        # no suitable conversion for the value, keep it as string
        pass
    query[qkey] = qval


def simple_search(search_dict):
    """
    Perform a simple search from a request
    """

    try:
        offset = search_dict['view_start']
    except:
        offset = 0

    try:
        rcount = search_dict['rcount']
    except:
        rcount = 100

    metadata = {}
    C = base.getDBConnection()
    data = C[search_dict['database']][search_dict['collection']].find(search_dict['query']).max_time_ms(10000)
    metadata['record_count'] = data.count()
    data_out = list(data.skip(offset).limit(rcount))
#    data_out = list(data)
    metadata['view_count'] = len(data_out)
    return metadata, list(data_out)
