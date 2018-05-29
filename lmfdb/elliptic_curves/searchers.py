
from lmfdb.api2.utils import build_description

def get_searchers():

    desc = {}
    build_description(desc, name='test', h_name='test', type='', desc=None, 
        db_name='elliptic_curves', coll_name ='curves', field_name = 'label')

    return desc

