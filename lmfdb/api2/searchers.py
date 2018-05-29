searchers = {}

def register_search_function(name, human_name, description, info, search):
    """
    Register a search function with the contextual API system

    Arguments:
    name -- Name of the api_key. This is used to uniquely identify a search function
    human_name -- Name of the API entry presented to users
    description -- Description of the search feature that is enabled by this API key
    info -- Function that is called to get information about a searcher. Returns JSON document
    search -- Search function to be called when a query is made through the API. Returns an api_structure (see api2/utils.py)

    """
    global searchers
    searchers[name] = {'name':human_name, 'desc':description, 'info':info, 'search':search}
