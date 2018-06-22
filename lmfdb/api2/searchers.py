searchers = {}
singletons = {}

def register_search_function(name, human_name, description, auto_search=None, full_info=None, full_search=None):
    """
    Register a search function with the contextual API system

    Arguments:
    name -- Name of the api_key. This is used to uniquely identify a search function
    human_name -- Name of the API entry presented to users
    description -- Description of the search feature that is enabled by this API key
    auto_search -- two element list containing ['database', 'collection']. Should be filled if this searcher is just an
    inventory mediated search on a single database and collection
    full_info -- Function that is called to get information about a searcher. Returns JSON document. Only populate if you
    need to have full control over the info
    full_search -- Search function to be called when a query is made through the API. Returns an api_structure (see api2/utils.py).
    Only populate if you want to have full control over the search return

    """
    global searchers
    searchers[name] = {'name':human_name, 'desc':description, 'auto':auto_search, 'info':full_info, 'search':full_search}

def register_singleton(url, database, collection, key, simple_search = None, full_search = None):
    """
    Register an API singleton. This is a search that should find a single item
    from a label or similar key

    Arguments:
    url -- The URL of the singleton in the main LMFDB. This will become /api2/singletons/{url}
    database -- The database to search in
    collection -- The collection to search in
    key -- The field in the database to search in
    simple_search -- A function that modifies a query object to make it search for the requested object
    full_search -- A function that performs a search itself and returns the results
    """

    global singletons
    singletons[url] = {'database':database, 'collection':collection, 'key':key, 
        'simple_search':simple_search, 'full_search':full_search}
