# Functions to handler form submissions

# Import Libraries and functions

from tools.sqlqueries import query_list
from src.add_keyword import add_keyword, update_keyword
import pandas as pd
from config.sqlconnect import engine

def kw_search (keyword):
    '''
    Get the search data of the last two years from a given keyword if not in the database will added
    Arguments:
        keyword: str.
    Returns: pandas DataFrame
    '''
    engine.connect()
    kw_list = query_list('searchdata')
    kw_list = [x.lower() for x in kw_list]
    kw = keyword.lower()
    if kw not in kw_list:
        add_keyword(keyword)
    else:
        # update_keyword(keyword)
        pass # NOT TESTED YET
    query = f'''
    SELECT * FROM searchdata
    WHERE query='{keyword}';
    '''
    df = pd.read_sql(query,engine)
    return df