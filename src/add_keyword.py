from tools.sqlqueries import get_standard, get_average
from tools.google import trend_to_absolute
from pytrends.request import TrendReq
from pytrends import dailydata
from tools.guardian import get_guardian_articles
from tools.nytimes import get_nyt_articles
if "datetime" not in dir():
    import datetime
    from dateutil.relativedelta import relativedelta
if "pd" not in dir():
    import pandas as pd
    from config.sqlconnect import engine
def find_standard(keyword):
    ############### ADD DOCUMENTATION
    '''
    
    '''
    isstandard=False
    loop=0
    rank = 6
    while isstandard == False or rank == 12 or rank==1 or loop < 5:
        stdic = get_average(rank)
        standard = stdic['query']
        fr = f'{stdic["fromdate"].year}-{stdic["fromdate"].month}-{stdic["fromdate"].day}'
        to = f'{stdic["todate"].year}-{stdic["todate"].month}-{stdic["todate"].day}'
        kws = [standard, keyword]
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=kws, timeframe=f'{fr} {to}')
        df = pytrend.interest_over_time()
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
    volume_st = get_standard(rank)
    date_st = f'{volume_st[0].year}-{volume_st[0].month}-{volume_st[0].day}'
    kw_vol = (df[keyword][date_st]*volume_st[1])/df[standard][date_st]
    return {'date': date_st, 'volume': kw_vol} 

def get_google(keyword):
    ################ADD DOCUMENTATION
    '''
    
    '''
    #getting time range 
    dfr = datetime.datetime.now() - relativedelta(years=2)
    dto = datetime.datetime.now()
    #fetching relative google data
    df = dailydata.get_daily_data(keyword, int(dfr.year), int(dfr.month), int(dto.year),int(dto.month))
    df = df[[keyword]]
    # getting estimated search value
    standard = find_standard(keyword)
    rel_vol = standard['volume']/df[keyword][standard['date']]
    print(rel_vol)
    print(df)
    #replacing 0 values for 0.9 
    df[keyword] = df[keyword].replace(to_replace=0, value = 0.9)
    df[keyword] = df[keyword]*rel_vol
    df[keyword] = df[keyword].astype(int)
    return df 

def add_keyword(keyword):
    ################ADD DOCUMENTATION, ADD threaths
    '''
    
    '''
    df = get_google(keyword)
    df.columns = ["google"]
    df["query"] = keyword
    guardian = get_guardian_articles(keyword)
    guardian.columns = ["guardian"]
    df.join(guardian)
    nyt= get_nyt_articles(keyword)
    nyt.columns = ["nytimes"]
    df.join(nyt)
    df.to_sql("searchdata",engine,if_exists='append',index_label="date", method='multi')

