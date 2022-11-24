from config.sqlconnect import engine
if "pd" not in dir():
    import pandas as pd
import datetime

def get_average(rank):
    '''
    Gets the average searches per month for a given rank
    Arguments:
        rank: int.
            number from 1 to 14 ordered by monthly volume search
    Returns a dic with {query, avg, fromdate, todate}
    '''
    query = f"""
            SELECT query, avgsearch AS avg, fromdate, todate 
            FROM gvolume
            WHERE volumerank = {rank}
            """
    df = pd.read_sql_query(query, engine)
    return df.to_dict(orient="records")[0]