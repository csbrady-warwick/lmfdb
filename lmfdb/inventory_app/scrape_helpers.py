import lmfdb_inventory as inv
import inventory_db_core as idc
import datetime
#from lmfdb.base import getDBConnection
from scrape_frontend import get_scrape_progress

#Max time before scrape is considered to have failed
DEFAULT_MAX_TIME = 6

def check_scrapes_on(spec=None):
    """If collection given, check for scrapes in progress or
    queued on it. If only db, check all collections in it. If spec is None, check everything"""
    try:
        spec_ids = {}
        if spec is not None:
            db_id = idc.get_db_id(spec['db'])
            spec_ids = {'db':db_id['id']}
            if spec['coll']:
                coll_id = idc.get_coll_id(db_id['id'], spec['coll'])
                spec_ids['coll'] = coll_id['id']
        result = check_if_scraping(spec_ids) or check_if_scraping_queued(spec_ids)
        return result
    except Exception as e:
        return False

def check_scrapes_by_coll_id(coll_id):
    """Check for scrapes queued or in progress for coll_id"""
    try:
        spec_ids = {'coll':coll_id}
        result = check_if_scraping(spec_ids) or check_if_scraping_queued(spec_ids)
        return result
    except:
        return False

def register_scrape(db, coll, uid):
    """Create a suitable inventory entry for the scrape"""

    inv.log_dest.warning(db+' '+coll+' '+str(uid))
    try:
        db_id = idc.get_db_id(db)
        inv.log_dest.warning(str(db_id))
        db_id = db_id['id']
        inprog = False
        had_err = False
        if not coll:
            all_colls = idc.get_all_colls(db_id)
            for coll in all_colls:
                coll_id = coll['_id']
                tmp = check_and_insert_scrape_record(db_id, coll_id, uid)
                inprog = tmp['inprog'] and inprog
                had_err = tmp['err'] and had_err
        else:
            coll_id = idc.get_coll_id(db_id, coll)
            inv.log_dest.warning(str(coll_id))
            coll_id = coll_id['id']
            tmp = check_and_insert_scrape_record(db_id, coll_id, uid)
            inprog = tmp['inprog'] and inprog
            had_err = tmp['err'] and had_err

    except Exception as e:
        #Either failed to connect etc, or are already scraping
        inv.log_dest.warning('Error resistering scrape '+str(e))
        return {'err':True, 'inprog':False}

    return {'err':had_err, 'inprog':inprog}

def check_if_scraping(record):

    record['running'] = True
    result = idc.search_ops_table(record)

    return result is not None

def check_if_scraping_queued(record):

    record['running'] = False
    record['complete'] = False
    result = idc.search_ops_table(record)

    return result is not None

def check_if_scraping_done(record):

    record['running'] = False
    record['complete'] = True
    result = idc.search_ops_table(record)

    return result is not None

def check_and_insert_scrape_record(db_id, coll_id, uid):

    record = {'db':db_id, 'coll':coll_id}
    #Is this either scraping or queued
    is_scraping = check_if_scraping(record) or check_if_scraping_queued(record)
    inv.log_dest.warning(is_scraping)
    if is_scraping : return {'err':False, 'inprog':True, 'ok':False}

    time = datetime.datetime.now()
    record = {'db':db_id, 'coll':coll_id, 'uid':uid, 'time':time, 'running':False, 'complete':False}
    #Db and collection ids. UID for scrape process. Time triggered. If this COLL is being scraped. If this coll hass been done
    try:
        insert_scrape_record(record)
        result = {'err':False, 'inprog':False, 'ok':True}
    except Exception as e:
        inv.log_dest.warning('Failed to insert scrape '+str(e))
        result = {'err':True, 'inprog':False, 'ok':False}
    return result

def insert_scrape_record(record):
    """Insert the scraped record"""

    result = idc.add_to_ops_table(record)
    return result

#----- Helpers handling old etc scrape records

def null_all_scrapes(db, coll):
    """Update all scrapes on db.coll to be 'complete' """

    try:
        db_id = idc.get_db_id(db)
        coll_id = idc.get_coll_id(db_id['id'], coll)
        rec_find = {'db':db_id['id'], 'coll':coll_id['id']}
        rec_set = {}
        rec_set['complete'] = True
        rec_set['running'] = False

        # TODO fix this line inv_db['ops'].update_many(rec_find, {"$set":rec_set})
    except Exception as e:
        inv.log_dest.error("Error updating progress "+ str(e))
        return False

def null_old_scrapes(time=DEFAULT_MAX_TIME):
    """Update any old, incomplete AND not running scrapes to be 'complete'"""


    lst = get_live_scrapes_older_than(time)
    new_lst = check_scrapes_running(lst)
    null_scrapes_by_list(new_lst)
    return {'err':False, 'found':len(new_lst)}

def get_live_scrapes_older_than(min_hours_old=DEFAULT_MAX_TIME, db_id=None, coll_id=None):
    """Get all scrapes that are not marked complete and are at least min_hour_old

    Generally we expect scrapes to take only a few hours so an entire DB scrape should
    not take more than 4-6 hours at worst.

    min_hour_old -- Find only records older than this many hours

    Optional:
    db_id -- Find only records relating to this db id
    coll_id -- Find only records relating to this coll id

    """

    try:
        start = datetime.datetime.now() - datetime.timedelta(hours=min_hours_old)
        #Currently this is enough to identify scrape records
        rec_test = {'time':{"$lt":start}, 'complete':False}
        if db_id: rec_test['db'] = db_id
        if coll_id: rec_test['coll'] = coll_id
        curs = idc.search_ops_table(rec_test)
        return list(curs)
    except Exception as e:
        inv.log_dest.warning('Failed to get old scrapes '+str(e))
        return []

def check_scrapes_running(scrape_list):
    """Given a list of scrapes, check for actual running state and
    return a new list containing only those which are NOT running"""

    new_list = []
    for item in scrape_list:
        try:
            db_name = idc.get_db_name(item['db'])['name']
            coll_name = idc.get_coll_name(item['coll'])['name']
#            prog = get_scrape_progress(db_name, coll_name, getDBConnection())
            if prog == (-1, -1):
                new_list.append(item)
        except Exception as e:
            inv.log_dest.warning('Failed to get progress '+db_name+' '+coll_name+' '+str(e))
    return new_list

def null_scrapes_by_list(scrape_list):
    """Given a list of scrape records, nullify each
    Since we can't delete them, we set Running False and Complete True
    """
    try:
        for item in scrape_list:
            #TODO write function below to update_ops(rec_find, rec_set, upsert)
            idc.update_ops({'_id':item['_id']}, {"$set": {'running':False, 'complete':True}}, upsert=False)
    except Exception as e:
        inv.log_dest.warning('Failed to nullify scrapes '+str(e))

def get_completed_scrapes(n_days=7):
    """Get successfully completed scrapes from the last n days
    """

    try:
        start = datetime.datetime.now() - datetime.timedelta(days=n_days)
        #Currently this is enough to identify scrape records
        rec_test = {'time':{"$gt":start}, 'complete':True}
        curs = idc.search_ops_table(rec_test)
        return list(curs)
    except Exception as e:
        inv.log_dest.warning('Failed to get completed scrapes '+str(e))
        return []
