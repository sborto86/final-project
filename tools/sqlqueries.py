from config.sqlconnect import engine
if "pd" not in dir():
    import pandas as pd
import datetime

def get_average(rank):
    '''
    Gets the average searches per month for a given rank
    Arguments:
        rank: int. str.
            number from 1 to 20 ordered by monthly volume search or query
    Returns a dic with {query, avg, fromdate, todate}
    '''
    query = """
            SELECT query, avgsearch AS avg, fromdate, todate 
            FROM gvolume
            """
    if type(rank) == int:
        query+=f'WHERE volumerank = {rank};'
    elif type(rank) == str:
        query+=f"WHERE query = '{rank}';"
    df = pd.read_sql_query(query, engine)
    return df.to_dict(orient="records")[0]

def ins_average(q, avg, fr, to, rank=None):
    '''
    Insert or update a reference keyword in the database
    Arguments:
        q: str.
            Keyword
        avg: int.
            average monthly searches for a given period
        fr:

    '''
    ############ ADD DATA VALIDATION
    # checking if keword already exists
    query = f"SELECT * FROM gvolume WHERE query = '{q}'"
    ############# ADD ERROR HANDELING
    q_exists=engine.execute(query).fetchall()
    if q_exists and rank:
        query=f'''
                UPDATE gvolume
                SET avgsearch = {avg}, fromdate={fr}, todate={to}, volumerank = {rank}
                WHERE query = '{q}';      
            '''
    elif q_exists and not rank:
        query=f'''
                UPDATE gvolume
                SET avgsearch = {avg}, fromdate='{fr}', todate='{to}'
                WHERE query = '{q}';      
            '''
    else:
        query=f'''
                INSERT INTO `gvolume` (`query`, `avgsearch`, `fromdate`, `todate`, `volumerank`)
                VALUES
                ('{q}',{avg},'{fr}','{to}',{rank})
            '''
    return f'{q} succesfully added to the database'

def remove_duplicates(database):
    '''
    Remove duplicates from database
    Arguments:
        database: str.
            Name of the database to remove duplicates
    Returns bool
    '''
    if database == 'standardvolume':
        id = 'idstandardvolume'
    elif database == 'searchdata':
        id = 'idsearch'
    else:
        return False ##### ERROR HANDELING?
    query = f'''
        DELETE FROM {database}
        WHERE {id} NOT IN
            (
            SELECT MIN({id}) AS MinID
            FROM {database}
            GROUP BY query, 
                    date,
        );
        '''
    try: 
        engine.execute(query)
        return True
    except:
        return False

def query_list(database):
    query = f"SELECT DISTINCT query FROM {database};"
    unique = engine.execute(query).fetchall()
    return [query for ls in unique for query in ls]

