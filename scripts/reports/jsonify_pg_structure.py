from bson.code import Code
import dbtools
import id_object
from lmfdb.base import getDBConnection
from lmfdb.db_backend import db
import datetime
import threading
import bson
import time

__version__ = '1.0.0'

def _is_good_table(name):
    """ Function to test if a database is one to scan """
    if '.' in name: return False
    return True

def merge_dicts(d1, d2):
    """ Merge two dictionaries into one """
    for key, value2 in d2.items():
        if key in d1:
            if type(value2) is dict:
                merge_dicts(d1[key], value2)
        else:
            d1[key] = value2

def _get_db_records(table):

    """ Routine to get the keys for a specified table """

    results = db[table]._search_cols
    return results

def _jsonify_collection_info(table):

    """Private function to turn information about one collection into base 
       JSON """

    results = _get_db_records(table)

    json_db_data = {}
    json_db_data['dbinfo'] ={}
    json_db_data['dbinfo']['name'] = table
    json_db_data['records'] = {}
    json_db_data['fields'] = {}

    for doc in results:
        try:
            rls = dbtools.get_pg_sample_record(table, str(doc))
            try:
                typedesc = id_object.get_description(rls[str(doc)])
            except:
                typedesc = 'Type cannot be identified (' \
                           + str(type(rls[str(doc)])) + ')'
            try:
                strval =  str(rls[str(doc)]).decode('unicode_escape').\
                          encode('ascii','ignore')
            except:
                strval = 'Record cannot be stringified'
        except:
            typedesc = 'Record cannot be found containing key'
            strval = 'N/A'

        lstr = len(strval)
        strval = strval.replace('\n',' ').replace('\r','')
        strval = '`' + strval[:100].strip() + '`'
        if lstr > 100:
            strval = strval + ' ...'
        json_db_data['fields'][str(doc)] = {}
        json_db_data['fields'][str(doc)]['type'] = typedesc
        json_db_data['fields'][str(doc)]['example'] = strval


    indices = db[table].list_indexes()
    json_db_data['indices'] = {}
    for recordid, index in enumerate(indices):
        json_db_data['indices'][recordid] = {}
        json_db_data['indices'][recordid]['name'] = index
        json_db_data['indices'][recordid]['keys'] = indices[index]['columns']

    return json_db_data

def parse_collection_info_to_json(table, retval = None, date = None):

    """ Front end routine to create JSON information about a collection """

    name_list = table.split("_",1)
    db = name_list[0]
    coll = name_list[1]

    json_raw = _jsonify_collection_info(table)
    json_wrap = {db:{coll:json_raw}}
    if not date:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    json_wrap[db][coll]['scrape_date'] = date
    if retval is not None: retval['data'] = json_wrap
    return json_wrap
