## IMPORTING LIBRARIES
if "requests" not in dir():
    import requests
if "urllib" not in dir ():
    import urllib.parse
if "st" not in dir():
    import streamlit as st
if "datetime" not in dir():
    import datetime
    from dateutil.relativedelta import relativedelta
from unidecode import unidecode
if "tqdm" not in dir():
    from tqdm import tqdm
if "ceil" not in dir():
    from math import ceil
if "pd" not in dir():
    import pandas as pd
if "engine" not in dir():
    from config.sqlconnect import engine

##### GETTING PASSWORDS

NY = st.secrets["NYT"]


def get_nyt_articles(query, datefrom=None, dateto=None):
    '''
    Function that get the number of articles published in The New York Times the last 2 years for a given query
    Arguments:
        query: str. 
                query to retreive the article number
        datefrom(optional): str. (format: YYYY-DD-MM)
        dateto(optional): str. (format: YYYY-DD-MM)
    Returns: pd.DataFrame
    '''
    # Generating date variables
    if not dateto:
        dto = datetime.datetime.now() 
        dateto = f"{dto.year}-{dto.month}-{dto.day}"
    if not datefrom:
        dfr = datetime.datetime.now() - relativedelta(years=2)
        datefrom = f"{dfr.year}-{dfr.month}-01"
    #Check if database is updated
    engine.connect()
    sqlquery = '''
            SELECT MAX(`date`) FROM nytarchive
            LIMIT 1'''
    last_update = engine.execute(sqlquery).fetchall()[0][0]
    print(last_update)
    
    today = datetime.date.today()
    if today > last_update:
        print('Updating NYT database...')
        # Deleting records of the last update month
        stdate = datetime.date(last_update.year,last_update.month,1)
        sqlquery = f'''
                    DELETE FROM nytarchive
                    WHERE `date`
                    BETWEEN '{last_update.year}-{last_update.month}-{last_update.day}' AND {stdate.year}-{stdate.month}-{stdate.day}
        
        '''
        engine.execute(sqlquery)
        # Updating
        mo_update = (relativedelta(today, last_update) + relativedelta(months=1)).months
        for i in range(mo_update):
            url = f'https://api.nytimes.com/svc/archive/v1/{today.year}/{today.month}.json?api-key={NY}'
            content = requests.get(url)
            content = content.json()
            news_list=[{"date": news['pub_date'].split("T")[0],"text": news['abstract']+news['headline']['main']+news['headline']['print_headline']+news['lead_paragraph']} for news in content["response"]["docs"]]
            df = pd.DataFrame(news_list)
            df['date'] = df["date"].astype('datetime64[ns]')
            df.to_sql("nytarchive",engine, index=False, if_exists='append', method='multi')
            print ('Upadating NYT Database', today.month, today.year)
            today = today - relativedelta(months=1)
    #quering the database
    sqlquery = f'''SELECT `date`, COUNT(`text`) FROM nytarchive
            WHERE `text` LIKE '%{query}%'
            AND `date` BETWEEN '{datefrom}' AND '{dateto}'
            GROUP BY `date`
            '''
    df = pd.read_sql(sqlquery,engine)
    idx = pd.date_range(datefrom, dateto)
    df = df.set_index(df['date'])
    df.index = pd.DatetimeIndex(data=df.index)
    df.columns = ["date", "articles"]
    df = df[["articles"]]
    df = df.reindex(idx, fill_value=0)
    return df

#### DEPRECIATED FUNCTION BECAUSE QUERY QUOTA LIMIT
def get_nyt_articles_old(query, datefrom=None, dateto=None):
    '''
    Function that get the number of articles published in The New York Times the last 2 years for a given query
    Arguments:
        query: str. 
                query to retreive the article number
        datefrom(optional): str. (format: YYYY-DD-MM)
        dateto(optional): str. (format: YYYY-DD-MM)
    Returns: list of dictionaries
    '''
    articles = []
    if not dateto:
        dto = datetime.datetime.now() - relativedelta(years=2)
    else:
        d_ls = dateto.split("-")
        dto = datetime.datetime(int(d_ls[0]), int(d_ls[1]), int(d_ls[2]))
    if not datefrom:
        dfr = datetime.datetime.now()
    else:
        d_ls = datefrom.split("-")
        dfr = datetime.datetime(int(d_ls[0]), int(d_ls[1]), int(d_ls[2]))    
    url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?'
    parameters = {
        'begin_date': f"{dfr.year}{dfr.month}{dfr.day}",
        'end_date': f"{dto.year}{dto.month}{dto.day}",
        'facet': "false",
        'q': query,
        'sort': 'newest',
        'api-key': NY
    }
    url2 = url + urllib.parse.urlencode(parameters)
    try:
        response = requests.get(url2)
    except:
        ("Neprinttwork error please check your internet connection")
        return []
    if response.status_code == 200:
        response = response.json()
        pages = ceil(response['response']['meta']['hits']/10)
        if pages > (dto-dfr).days:
            day = dfr
            for loop in tqdm(range((dfr-dto).days+1)):
                parameters['begin_date'] = f"{day.year}{day.month}{day.day}"
                parameters['end_date'] = f"{day.year}{day.month}{day.day}"
                url2 = url + urllib.parse.urlencode(parameters)      
                try:
                    response = requests.get(url2)
                    if response.status_code == 200:
                        response = response.json()
                        dic_ = { "date": f"{day.year}-{day.month}-{day.day}",
                                "articles": response['response']['meta']['hits'],
                                "query": query
                        }
                        articles.append(dic_)
                        day = day + datetime.timedelta(days=1)
                    else: 
                        print(f"Unable to fully retrieve articles from {query}, stopped at {day.year}-{day.month}-{day.day}: Error {response.status_code}: {response.text}")
                        pass
                except:
                        print("Network error please check your internet connection, stopped at {day.year}-{day.month}-{day.day}")
                        pass
        else:
            dic_dates = {}
            for i in tqdm(range(0, pages)):
                parameters['page'] = i
                url2 = url + urllib.parse.urlencode(parameters)
                try:
                    response = requests.get(url2)
                    if response.status_code == 200:
                        response = response.json()
                        results = response['response']['docs']
                        for e in results:
                            pubdate = e['pub_date'].split("T")[0]
                            if pubdate in dic_dates:
                                dic_dates[pubdate] +=1
                            else:
                                dic_dates[pubdate] =1
                    else: 
                        print(f"Unable to retrieve articles from page {i} of {query}: Error {response.status_code}: {response.text}")
                except:
                    print("Network error please check your internet connection, Unable to retrieve articles from page {i} of {query}")
            for dat, value in dic_dates.items():
                art = {
                    "date": dat,
                    "articles": value,
                    "query": query
                }
                articles.append(art)       
    else:
        print(f"There was a problem with your request, {response.status_code}: {response.reason}")
    df = pd.DataFrame(articles)
    if len(df[df.date == datefrom])==0:
        row = pd.DataFrame([{'date':datefrom, 'articles': 0, 'query':query}])
        df = pd.concat([df,row], ignore_index=True)
    if len(df[df.date == dateto])==0:
        row = pd.DataFrame([{'date':dateto, 'articles': 0, 'query':query}])
        df = pd.concat([df,row], ignore_index=True)
    df = df.set_index(df['date'])
    df.index = pd.DatetimeIndex(data=df.index)
    df = df.resample('1D').mean().fillna(0)
    return df