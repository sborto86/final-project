from tools.sqlqueries import get_standard, get_average, query_list
from tools.google import trend_to_absolute
from pytrends.request import TrendReq
from pytrends import dailydata
from tools.guardian import get_guardian_articles
from tools.nytimes import get_nyt_articles
from pytrends.exceptions import ResponseError
import time
if "datetime" not in dir():
    import datetime
    from dateutil.relativedelta import relativedelta
if "pd" not in dir():
    import pandas as pd
    from config.sqlconnect import engine
    engine.connect()
def find_standard(keyword):
    '''
    Find a keyword stored in the gvolume database that have similar search volume in google trends
    Arguments:
        keyword: str.
            keyword to find a standard stored in the database
    Returns: dic. {
                    date: YYYY-MM-DD 
                    volume: int.
                    }        
    '''
    engine.connect()
    standard_list = query_list("gvolume")
    if keyword in standard_list or keyword.lower() in standard_list:
        engine.connect()
        query = f"SELECT volumerank FROM gvolume WHERE query = '{keyword}'"
        res = engine.execute(query).first()
        rank = res[0]
        volume_st = get_standard(rank)
        date_st = f'{volume_st[0].year}-{volume_st[0].strftime("%m")}-{volume_st[0].strftime("%d")}'
        return {'date': date_st, 'volume': volume_st[1]}
    isstandard=False
    loop=0
    rank = 5
    while isstandard == False and rank < 10 and rank > 1 and loop < 5:
        stdic = get_average(rank)
        standard = stdic['query']
        fr = f'{stdic["fromdate"].year}-{stdic["fromdate"].strftime("%m")}-{stdic["fromdate"].strftime("%d")}'
        to = f'{stdic["todate"].year}-{stdic["todate"].strftime("%m")}-{stdic["todate"].strftime("%d")}'
        kws = [standard, keyword]
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=kws, timeframe=f'{fr} {to}')
        try: 
            df = pytrend.interest_over_time()
        except:
            isstandard=True
        stsum = df[standard].sum()
        kwsum = df[keyword].sum()
        if kwsum == 0:
            rank += 1
        elif stsum == 0:
            rank -= 1
        elif kwsum/stsum < 0.03:
            rank += 1
        elif stsum/kwsum < 0.03:
            rank -= 1
        else:
            isstandard=True
        loop += 1
        time.sleep(3)
        print(f"standard rank: {rank}")
    volume_st = get_standard(rank)
    date_st = f'{volume_st[0].year}-{volume_st[0].strftime("%m")}-{volume_st[0].strftime("%d")}'
    kw_vol = (df[keyword][date_st]*volume_st[1])/df[standard][date_st]
    return {'date': date_st, 'volume': kw_vol} 

def get_google(keyword):
    '''
    Retrives the estimated search volume for the last two years from now
    Arguments: 
        keyword: str.
            keyword to calculate the search volume
    Returns: pandas.DataFrame object.
    '''
    #getting time range 
    dfr = datetime.datetime.now() - relativedelta(years=2)
    dto = datetime.datetime.now()
    #fetching relative google data
    try:
        df = dailydata.get_daily_data(keyword, int(dfr.year), int(dfr.month), int(dto.year),int(dto.month))
        df = df[[keyword]]
    except ResponseError:
        return "Google has bloqued your request imposible to retrive the historical data, try it again after some minutes"
    # getting estimated search value
    standard = find_standard(keyword)
    if df[keyword][standard['date']] == 0:
        df[keyword][standard['date']] = 0.9
    rel_vol = standard['volume']/df[keyword][standard['date']]
    #replacing 0 values for 0.9 
    df[keyword] = df[keyword].fillna(0)
    df[keyword] = df[keyword].replace(to_replace=0, value = 0.9)
    df[keyword] = df[keyword]*rel_vol
    df[keyword] = df[keyword].astype(int)
    return df 

def add_keyword(keyword):
    ################ ADD threaths
    '''
    Adds new keyword search volume to the search data database
    Arguments: 
        keyword: str.
            keyword to be added in the database
    Return: panadas.DataFrame
    '''
    df = get_google(keyword)
    # Check if error in retriving keyword
    if type(df)== str:
        return df
    df.columns = ["google"]
    df["query"] = keyword
    guardian = get_guardian_articles(keyword)
    guardian.columns = ["guardian"]
    df = df.join(guardian)
    nyt= get_nyt_articles(keyword)
    nyt.columns = ["nyt"]
    df = df.join(nyt)
    df.to_sql("searchdata",engine,if_exists='append',index_label="date", method='multi')
    return df

def update_keyword(keyword):
    '''
    Updates the data from a keyword already present in the database
    Arguments:
        keyword: str.
            keyword to be updated
    Returns: bool.
    '''
    try:
        today = datetime.date.today()
        engine.connect()
        sqlquery = f'''
            SELECT MAX(`date`) FROM searchdata
            WHERE query = '{keyword}'
            LIMIT 1'''
        # getting dates for the queries
        last_update = engine.execute(sqlquery).fetchall()[0][0]
        today = datetime.date.today()
        dfr = f'{last_update.year}-{last_update.strftime("%m")}-{last_update.strftime("%d")}'
        dto = f'{today.year}-{today.strftime("%m")}-{today.strftime("%d")}'
        laup= last_update - datetime.timedelta(days=10)
        dfr2 = f'{laup.year}-{laup.strftime("%m")}-{laup.strftime("%d")}'
        if today-datetime.timedelta(days=7) > last_update:
            # get search volume to standarize
            sqlquery = f'''
           SELECT `date`, google FROM searchdata
            WHERE google = 
                (SELECT MAX(google) FROM searchdata
                WHERE `date` > '{dfr2}' AND query = '{keyword}')
            AND
            `date` > '{dfr2}'
            LIMIT 1'''
            standard = engine.execute(sqlquery).fetchall()[0]
            pytrend = TrendReq()
            pytrend.build_payload(kw_list=[keyword], timeframe=f'{dfr2} {dto}')
            df = pytrend.interest_over_time()
            if df[keyword][standard[0]] == 0:
                rel_vol=[standard[1]]/0.9
            else:
                rel_vol = [standard[1]]/df[keyword][standard[0]]
            df[keyword] = df[keyword].replace(to_replace=0, value = 0.9)
            df[keyword] = df[keyword]*rel_vol
            df[keyword] = df[keyword].astype(int)
            df=df[[keyword]]
            df = df[df.index > dfr]
            df.columns = ["google"]
            guardian = get_guardian_articles(keyword)
            guardian.columns = ["guardian"]
            df = df.join(guardian)
            nyt= get_nyt_articles(keyword)
            nyt.columns = ["nyt"]
            df = df.join(nyt)
            df.to_sql("searchdata",engine,if_exists='append',index_label="date", method='multi')
            return True
        else: 
            return False
    except:
        return False