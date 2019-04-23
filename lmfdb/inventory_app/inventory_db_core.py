import inventory_helpers as ih
import lmfdb_inventory as inv
import datetime as dt
from lmfdb.utils import comma
from lmfdb.backend.database import db

#Table creation routines -------------------------------------------------------------

def get_db_id(name):
    """ Get database id by name

    name -- Name of db to retrieve
    """

    table_to_search = "inv_dbs"
    exists_at = db[table_to_search].search({'name':name}, limit=1)
    if len(exists_at) > 0:
        _id = exists_at[0]['_id']
    else:
        _id = 0
    return {'err':False, 'id':_id, 'exist':(len(exists_at)>0)}

def get_coll_id(db_id, name):
    """ Get collection id by name.

    db_id -- ID of the database this connection is in
    name -- Name of collection to retrieve
    """

    table_to_search = "inv_tables"
    exists_at = db[table_to_search].search({'db_id':db_id, 'name':name}, limit=1)
    if len(exists_at) > 0:
        _id = exists_at[0]['_id']
    else:
        _id = 0

    return {'err':False, 'id':_id, 'exist':(len(exists_at)>0)}

def get_db_name(db_id):
    """Get db name from db id"""

    table_to_search = "inv_dbs"
    exists_at = db[table_to_search].search({'_id':db_id}, limit=1)
    if len(exists_at) > 0:
        name = exists_at[0]['name']
    else:
        name = ''
    return {'err':False, 'name':name, 'exist':(len(exists_at)>0)}

def get_coll_name(coll_id):
    """ Get collection name from id.

    coll_id -- ID of collection to retrieve
    """

    table_to_search = "inv_tables"
    exists_at = db[table_to_search].search({'_id':coll_id}, limit=1)
    if len(exists_at) > 0:
        name = exists_at[0]['name']
    else:
        name = ''
    return {'err':False, 'name':name, 'exist':(len(exists_at)>0)}

def get_db(name):
    """ Get database record by name """

    table_to_search = "inv_dbs"
    exists_at = db[table_to_search].search({'name':name}, limit=1)
    if len(exists_at) > 0:
        _id = exists_at[0]['_id']
        data = exists_at[0]
        err = False
    else:
        _id = 0
        data = None
        err = True

    return {'err':err, 'id':_id, 'exist':(len(exists_at)>0), 'data':data}

def set_db(name, nice_name):
    """ Insert a new DB with given name and optional nice name (defaults to equal name), or return id if this exists. """
#TODO refill body
    return {'err':True, 'id':_id, 'exist':False}

def update_db(db_id, name=None, nice_name=None):
    """"Update DB name or nice_name info by db id"""
#TODO refill body
    return {'err':True, 'id':db_id, 'exist':False}

def get_coll(db_id, name):
    """Return a collection entry.

    db_id -- ID of db this collection is part of
    name -- Collection name to return
    """

    table_to_search = "inv_tables"
    exists_at = db[table_to_search].search({'name':name, 'db_id':db_id}, limit=1)
    if len(exists_at) > 0:
        _id = exists_at[0]['_id']
        data = exists_at[0]
        err = False
    else:
        _id = 0
        data = None
        err = True

    return {'err':err, 'id':_id, 'exist':(len(exists_at)>0), 'data':data}

def get_coll_by_id(id):
    """Return a collection entry.

    id -- ID of collection
    """
    table_to_search = "inv_tables"
    exists_at = db[table_to_search].search({'_id':id}, limit=1)
    if len(exists_at) > 0:
        _id = exists_at[0]['_id']
        data = exists_at[0]
        err = False
    else:
        _id = 0
        data = None
        err = True

    return {'err':err, 'id':_id, 'exist':(len(exists_at)>0), 'data':data}

def set_coll(db_id, name, nice_name, notes, info, status):
    """Create or update a collection entry.

    db_id -- ID of db this collection is part of
    name -- Collection name to update
    notes -- The collection's Notes
    info -- The collection's Info
    status -- Collection's status code
    """

    coll_fields = inv.ALL_STRUC.coll_ids[inv.STR_CONTENT]
    rec_find = {coll_fields[1]:db_id, coll_fields[2]:name}
    rec_set = {}
    if nice_name is not None:
        rec_set[coll_fields[3]] = nice_name
    if notes is not None:
        rec_set[coll_fields[4]] = notes
    if info is not None:
        rec_set[coll_fields[5]] = info
    if status is not None:
        rec_set[coll_fields[7]] = status

    return upsert_and_check(db['inv_tables'], rec_find, rec_set)

def update_coll(id, name=None, nice_name=None, status=None):
    """Update a collection entry. Collection must exist.

    id -- ID of collection

    Optional args:
    name -- new name for collection
    nice_name -- new nice_name for collection
    status -- status code
    """

    coll_fields = inv.ALL_STRUC.coll_ids[inv.STR_CONTENT]
    rec_find = {coll_fields[0]:id}
    rec_set = {}
    if name is not None:
        rec_set[coll_fields[2]] = name
    if nice_name is not None:
        rec_set[coll_fields[3]] = nice_name
    if status is not None:
        rec_set[coll_fields[7]] = status
    if rec_set:
        return update_and_check(db['inv_tables'], rec_find, rec_set)
    else:
        return {'err':False, 'id':id, 'exist':True}

def update_coll_data(db_id, name, item, field, content):
    """Update a collection entry. Collection must exist.

    db_id -- ID of db this collection is part of
    item -- The collection info this specifies
    field -- The piece of information specified (for example, type, description, example)
    content -- The new value for field
    """

    coll_fields = inv.ALL_STRUC.coll_ids[inv.STR_CONTENT]
    rec_find = {coll_fields[1]:db_id, coll_fields[2]:name, item+'.'+field:{"$exists":True}}
    rec_set = {item+'.'+field:content}

    return update_and_check(db['inv_tables'], rec_find, rec_set)

def set_coll_scrape_date(coll_id, scrape_date):
    """Update the last scanned date for given collection"""

    try:
        assert(isinstance(scrape_date, dt.datetime))
    except Exception as e:
        inv.log_dest.error("Invalid scrape_date, expected datetime.datetime "+str(e))
        return {'err':True, 'id':0, 'exist':False}

    coll_fields = inv.ALL_STRUC.coll_ids[inv.STR_CONTENT]
    rec_find = {coll_fields[0]:coll_id}
    rec_set = {coll_fields[6]:scrape_date}

    return update_and_check(db['inv_tables'], rec_find, rec_set)

def set_coll_status(coll_id, status):
    """Update the status code for given collection"""

    coll_fields = inv.ALL_STRUC.coll_ids[inv.STR_CONTENT]
    rec_find = {coll_fields[0]:coll_id}
    rec_set = {coll_fields[7]:status}

    return update_and_check(db['inv_tables'], rec_find, rec_set)

def get_field(coll_id, name, type='auto'):
    """ Return a fields entry.

    coll_id -- ID of collection field belongs to
    name -- The lmfdb key to fetch
    type -- Specifies human or autogenerated table
    """

    table_to_search = "inv_fields_"+type
    exists_at = db[table_to_search].search({'name':name, 'table_id':coll_id}, limit=1)
    if len(exists_at) > 0:
        _id = exists_at[0]['_id']
        data = exists_at[0]
        err = False
    else:
        _id = 0
        data = None
        err = True

    return {'err':err, 'id':_id, 'exist':(len(exists_at)>0), 'data':data}

def set_field(coll_id, name, data, type='auto'):
    """ Add or update a fields entry.

    coll_id -- ID of collection field belongs to
    name -- The lmfdb key this describes
    data -- Collection data ({field: content, ...} formatted)
    type -- Specifies human or autogenerated table
    """
    #fields_auto = {STR_NAME : 'fields_auto', STR_CONTENT : ['_id', 'coll_id', 'name', 'data']}

    fields_fields = inv.ALL_STRUC.get_fields(type)[inv.STR_CONTENT]
    rec_find = {fields_fields[1]:coll_id, fields_fields[2]:name}
    data = ih.null_all_empty_fields(data)
    rec_set = {fields_fields[3]:data}

    return upsert_and_check(db['inv_fields'], rec_find, rec_set)

def update_field(coll_id, item, field, content, type='auto'):
    """ Update an existing field entry. Item must exist

    coll_id -- ID of collection field belongs to
    item -- The lmfdb key this describes
    field -- The piece of information specified (for example, type, description, example)
    content -- The new value for field
    type -- Specifies human or autogenerated table
    """
    #fields_auto = {STR_NAME : 'fields_auto', STR_CONTENT : ['_id', 'coll_id', 'name', 'data']}

    fields_fields = inv.ALL_STRUC.get_fields(type)[inv.STR_CONTENT]
    rec_find = {fields_fields[1]:coll_id, fields_fields[2]:item}
    dat = list(db['inv_fields_'+type].search(rec_find))[0][fields_fields[3]]
    dat[field] = content
    rec_set = {fields_fields[3]:dat}

    return update_and_check(db['inv_fields_'+type], rec_find, rec_set)

def add_index(coll_id, index_data):
    """Add an index entry for given coll_id"""
    #indexes = {STR_NAME : 'indexes', STR_CONTENT :['_id', 'name', 'coll_id', 'keys']}

    indexes_fields = inv.ALL_STRUC.indexes[inv.STR_CONTENT]
    record = {indexes_fields[1]:index_data['name'], indexes_fields[2]:coll_id}
    #If record exists, just return its ID
    exists_at = db['inv_indices'].lookup(record)
    if exists_at is not None:
        inv.log_dest.debug("Index exists")
        _id = exists_at['_id']
    else:
        record[indexes_fields[2]] = coll_id
        record[indexes_fields[3]] = index_data['keys']
        try:
            upsert_and_check(db['inv_indices'], {}, record)
        except Exception as e:
            inv.log_dest.error("Error inserting new index" +str(e))
            return {'err':True, 'id':0, 'exist':False}

    return {'err':False, 'id':_id, 'exist':(exists_at is not None)}

def get_all_indices(coll_id):
    """ Return a list of all indices for coll_id.

    coll_id -- ID of collection field belongs to
    """
    #indexes = {STR_NAME : 'indexes', STR_CONTENT :['_id', 'name', 'coll_id', 'keys']}

    table_to_search = "inv_indices"

    indexes_fields = inv.ALL_STRUC.indexes[inv.STR_CONTENT]
    rec_find = {indexes_fields[2]:coll_id}
    try:
        data = list(db[table_to_search].search(rec_find))
        return {'err':False, 'id':-1, 'exist':True, 'data':data}
    except Exception as e:
        inv.log_dest.error("Error getting data "+str(e))
        return {'err':True, 'id':0, 'exist':True, 'data':None}

def upsert_and_check(table, rec_find, rec_set):
    """Upsert (insert/update) into given coll

    table -- table to upsert into (not name)
    rec_find -- query to identify possibly existing record
    rec_set -- new data to set

    """
    try:
        result = table.upsert(rec_find, rec_set)
#        if 'upserted' in result['lastErrorObject']:
#            _id = result['lastErrorObject']['upserted']
#        elif 'value' in result:
#            _id = result['value']['_id']
        _id = None
        upserted = False
    except Exception as e:
        inv.log_dest.error("Error inserting new record "+ str(e))
        return {'err':True, 'id':0, 'exist':False}
    return {'err':False, 'id':_id, 'exist':(not upserted)}

def update_and_check(table, rec_find, rec_set):
    """Update record in given coll

    table -- table to upsert into
    rec_find -- query to identify existing record
    rec_set -- new data to set

    """

    try:
        result = table.upsert(rec_find, rec_set)
#        _id = result['value']['_id']
        _id = None
        exist = False
    except Exception as e:
#        inv.log_dest.error("Error updating record "+str(rec_find)+' '+ str(e))
        return {'err':True, 'id':0, 'exist':False}
    return {'err':False, 'id':_id, 'exist':exist}

#End table creation routines -------------------------------------------------------------

#Ops stuff ------------------------------------------------------------------------------

def search_ops_table(rec_find):

    table_to_search = "inv_ops"
    try:
        result = db[table_to_search].search(rec_find)
        return result
    except:
        return []

def add_to_ops_table(rec_set):

    table_to_change = "inv_ops"
    try:
        db[table_to_change].upsert(rec_set, rec_set)
        return {'err':False}
    except:
        return {'err':True}

#End ops ---------------------------------------------------------------------------------

#Table sync ------------------------------------------------------------------------------

def trim_human_table(inv_db_toplevel, db_id, coll_id):
    """Trims elements from the human-readable table which do not match the canonical structure table

    inv_db_toplevel -- connection to LMFDB inventory database (no table)
    db_id -- id of database to strip
    coll_id -- id of collection to strip
    """
    invalidated_keys = []
    a_tbl = db['inv_fields_auto']
    h_tbl = db['inv_fields_human']

    fields_fields = inv.ALL_STRUC.get_fields('human')[inv.STR_CONTENT]
    rec_find = {fields_fields[1]:coll_id}
    human_cursor = h_tbl.search(rec_find)
    for record in human_cursor:
        rec_find = {fields_fields[1]:coll_id, fields_fields[2]: record['name']}
        auto_record = a_tbl.search(rec_find)
        if auto_record is None:
            invalidated_keys.append({'name':record['name'], 'data':record['data']})
            h_tbl.delete(record)
    return invalidated_keys

def complete_human_table(inv_db_toplevel, db_id, coll_id):
    """Add missing entries into human-readable table. 'Missing' means anything
    present in the auto-generated data but not in the human, AND adds keys present only in the
    human data in also (currently, description)

    inv_db_toplevel -- connection to LMFDB inventory database (no table)
    db_id -- id of database to strip
    coll_id -- id of collection to strip
    """
    h_db = inv_db_toplevel[inv.ALL_STRUC.fields_human[inv.STR_NAME]]
    a_db = inv_db_toplevel[inv.ALL_STRUC.fields_auto[inv.STR_NAME]]
    fields_fields = inv.ALL_STRUC.get_fields('human')[inv.STR_CONTENT]
    rec_find = {fields_fields[1]:coll_id}
    auto_cursor = a_db.search(rec_find)
    for record in auto_cursor:
        rec_find = {fields_fields[1]:coll_id, fields_fields[2]: record['name']}
        human_record = h_db.search(rec_find)
        #Should never be two records with same coll-id and name
        alter = False
        try:
            rec_set = human_record['data']
        except:
            rec_set = {}
        for field in inv.base_editable_fields:
            try:
                a = human_record['data'][field]
                assert(a or not a) #Use a for Pyflakes, but we don't care what is is
            except:
                rec_set[field] = None
                alter = True
        #Rec_set is now original data plus any missing base_editable_fields
        if alter:
            #Creates if absent, else updates with missing fields
            set_field(coll_id, record['name'], rec_set, type='human')

def cleanup_records(coll_id, record_list):
    """Trims records for this collection that no longer exist

    coll_id -- id of collection to strip
    record_list -- List of all existing records
    """
    table_to_search = "inv_records"

    try:
        records_fields = inv.ALL_STRUC.record_types[inv.STR_CONTENT]
        rec_find = {records_fields[1]:coll_id}
        db_record_list = db[table_to_search].search(rec_find)
        extant_hashes = []
        for key in record_list:
            item = record_list[key]
            extant_hashes.append(ih.hash_record_schema(item['schema']))
        for item in db_record_list:
            if item['hash'] not in extant_hashes:
                db[table_to_search].delete(item)

    except Exception as e:
        inv.log_dest.error("Error cleaning records "+str(e))
        return {'err':True}

#End table sync --------------------------------------------------------------------------
#Assorted helper access functions --------------------------------------------------------

def count_colls(db_id):
    """Count collections with given db_id
    """

    table_to_search = "inv_tables"
    info = {}
    exists_at = db[table_to_search].search({'db_id':db_id}, count_only=True, info=info)
    return info['number']

def get_all_colls(db_id=None):
    """Fetch all collections with given db_id
    """

    table_to_search = "inv_tables"
    if db_id is not None:
        values = db[table_to_search].search({'db_id':db_id}, count_only=True)
    else:
        values = db[table_to_search].search(count_only=True)
    return list(values)

def count_records_and_types(coll_id, as_string=False):
    """ Count the number of record types in given collection.
    If as_string is true, return a formatted string pair rather than a pair of ints
    """
    counts = (-1, -1)
    try:
        tbl = 'inv_records'
        recs = list(db[tbl].search({'table_id': coll_id}))
        n_types = len(recs)
        n_rec = sum([rec['count'] for rec in recs])
        counts = (n_rec, n_types)
    except Exception as e:
        inv.log_dest.error("Error getting counts "+str(e))
    if as_string:
        counts = (comma(counts[0]), comma(counts[1]))
    return counts
#End assorted helper access functions ----------------------------------------------------
