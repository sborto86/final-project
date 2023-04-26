from tools.sqlqueries import get_standard, get_average, query_list
from tools.google import trend_to_absolute
from pytrends.request import TrendReq
from pytrends import dailydata
from tools.guardian import get_guardian_articles
from tools.nytimes import get_nyt_articles
from pytrends.exceptions import ResponseError
import time
from dateutil.relativedelta import relativedelta
if "datetime" not in dir():
    import datetime
if "pd" not in dir():
    import pandas as pd
    from config.sqlconnect import engine
    engine.connect()

def find_standard_new(keyword):
    '''
    Find a keyword stored in the gvolume database that have similar search volume in google trends and calculates the average mothly volume of the keyword
    
    Arguments:
        keyword: str.
            keyword to find a standard stored in the database
    Returns: dic. {
                    date: YYYY-MM-DD 
                    volume: int.
                    }        
    '''
    result = {'error': False}
    engine.connect()
    standard_list = query_list("gvolume")
    if keyword in standard_list or keyword.lower() in standard_list:
        engine.connect()
        query = f"SELECT `fromdate`, `todate`, `avgsearch` FROM gvolume WHERE query = '{keyword}'"
        res = engine.execute(query).first()
        return {'keyword': keyword, 'from_date': res[0], 'to_date': res[1], 'avg_vol': res[2], 'error': False}
    isstandard=False
    loop=0
    rank = 5
    pytrend = TrendReq()
    while isstandard == False and rank < 10 and rank > 1 and loop < 5:
        stdic = get_average(rank)
        standard = stdic['query']
        fr = f'{stdic["fromdate"].year}-{stdic["fromdate"].strftime("%m")}-{stdic["fromdate"].strftime("%d")}'
        to = f'{stdic["todate"].year}-{stdic["todate"].strftime("%m")}-{stdic["todate"].strftime("%d")}'
        kws = [standard, keyword]
        pytrend.build_payload(kw_list=kws, timeframe=f'{fr} {to}')
        resum=0
        try: 
            df = pytrend.interest_over_time()
            stsum = df[standard].sum()
            kwsum = df[keyword].sum()
            print(f"standard rank: {rank}, avg: {stdic['avg']}")
            if kwsum == 0:
                rank += 1
            elif stsum == 0:
                rank -= 1
            elif kwsum/stsum < 0.1:
                rank += 1
            elif stsum/kwsum < 0.1:
                rank -= 1
            else:
                isstandard=True
            loop += 1
            time.sleep(3)
        except Exception as e:
            print(e)
            result['error'] = True
            result['error_msg'] = "Google blocked the request during the find standard process"
            isstandard=True
    if 'kwsum' == 0:
        return False
    kw_avg_vol = kwsum/stsum * stdic['avg']
    if kw_avg_vol > 0 and result['error'] == False:
        query = f"""INSERT INTO `gvolume` (`query`, `avgsearch`, `fromdate`, `todate`)
                VALUES
                    ('{keyword.lower()}', {kw_avg_vol}, '{fr}', '{to}');"""
        engine.execute(query)
    result['keyword'] = keyword
    result ['from_date'] = stdic["fromdate"]
    result ['to_date'] = stdic["todate"]
    result['avg_vol'] = kw_avg_vol
    return result

def google_monthly(stdic):
    
    keyword= stdic['keyword']
    pytrends = TrendReq(hl='en-US', tz=360)
    kw_list=[keyword]
    try: 
        pytrends.build_payload(kw_list, timeframe='all')
    except Exception as e:
        print('Error:', e)   
    df = pytrends.interest_over_time()
    #### Calculate Months standard
    
    months_st = relativedelta(stdic['to_date']+datetime.timedelta(days=+1), stdic['from_date'])
    total_vol = months_st.months * stdic['avg_vol']
    total_perc = df[(df.index.date <= stdic['to_date'])&(df.index.date >= stdic['from_date'])]
    total_perc = total_perc[keyword].sum()
    if total_vol > 0 and total_perc > 0:
        ref_vol = total_vol/total_perc
    else: 
        return 'Error Calculating absolute data'
    df[keyword] = df[keyword]*ref_vol
    return df

def get_google_new(keyword, from_date=None):
    '''
    Retrives the estimated search volume for the last two years from now
    Arguments: 
        keyword: str.
            keyword to calculate the search volume
    Returns: pandas.DataFrame object.
    '''
    #getting time range
    dfr = datetime.datetime.now() - relativedelta(years=2)
    if from_date and from_date > dfr.date():
        dfr = datetime.datetime(from_date.year, from_date.month, from_date.day)
    dfr = datetime.datetime(dfr.year, dfr.month, 1)
    dto = datetime.datetime.now()
    #fetching standards
    stdic = find_standard_new(keyword)
    if stdic:
        try: 
            month_volume = google_monthly(stdic)
            if type(month_volume) == str:
                return month_volume
        except Exception as e:
            print(e)
            return 'Google Trends has bloqued your request imposible to retrive the historical data (monthly realtive searches), try it again after some minutes'
    else:
        return 'Google Trends has bloqued your request imposible to retrive the historical data (average monthly searches), try it again after some minutes' 
    #fetching google data
    time.sleep(3)
    pytrend = TrendReq(hl='en-US', tz=360)
    df = pd.DataFrame()
    while dfr < dto:
        dto_partial = dfr + relativedelta(months=3)
        
        if dto_partial > dto:
            dfr_partial = datetime.datetime(dto.year,dto.month,1)- relativedelta(months=2)
            fr = f'{dfr_partial.year}-{dfr_partial.strftime("%m")}-{dfr_partial.strftime("%d")}'
            to = f'{dto.year}-{dto.strftime("%m")}-{dto.strftime("%d")}'
            partial = True
        else:
            fr = f'{dfr.year}-{dfr.strftime("%m")}-{dfr.strftime("%d")}'
            to = f'{dto_partial.year}-{dto_partial.strftime("%m")}-{dto_partial.strftime("%d")}'
            partial =False
        kws = [ keyword]
        pytrend.build_payload(kw_list=kws, timeframe=f'{fr} {to}')
        try: 
            rel_data = pytrend.interest_over_time()
        except Exception as e:
            print(e)
            break
        ### getting realtive to absolute
        if partial:
            to_full = f'{dto.year}-{dto.strftime("%m")}-01'
            ref_vol = month_volume.loc[fr:to_full][keyword].sum() / (rel_data.loc[fr:to_full][keyword].sum())
        else:
            ref_vol = month_volume.loc[fr:to][keyword].sum() / (rel_data.loc[fr:to][keyword].sum())
        rel_data = rel_data[[keyword]]
        rel_data[keyword] = rel_data[keyword].fillna(0)
        rel_data[keyword] = rel_data[keyword].replace(to_replace=0, value = 0.9)
        rel_data[keyword] = rel_data[keyword]*ref_vol
        rel_data[keyword] = rel_data[keyword].astype(int)       
        df = pd.concat([df,rel_data])
        print(f"Retrived {keyword} search volumne data from {fr} to {to}")
        dfr = dto_partial
        time.sleep(5)
    if df.empty:
        return 'Google Trends has bloqued your request imposible to retrive the historical data (daily searches), try it again after some minutes'       
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
    df = get_google_new(keyword)
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
        if today-datetime.timedelta(days=7) > last_update:
            print('updating...')
            date_from = f'{last_update.year}-{last_update.strftime("%m")}-{last_update.strftime("%d")}'
            date_to = f'{today.year}-{today.strftime("%m")}-{today.strftime("%d")}'
            df = get_google_new(keyword, last_update)
            if type(df) == str:
                return False
            df.columns = ["google"]
            df["query"] = keyword
            guardian = get_guardian_articles(keyword, datefrom=date_from, dateto=date_to)
            guardian.columns = ["guardian"]
            df = df.join(guardian)
            nyt= get_nyt_articles(keyword)
            nyt.columns = ["nyt"]
            df = df.join(nyt)
            df.to_sql("searchdata",engine,if_exists='append',index_label="date", method='multi')
            return True
        else: 
            return False
    except ValueError:
        return False

####################### OLD SCRIPTS WITH DAYDATA ####################

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
            print("Google blocked the request during the find standard process")
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

