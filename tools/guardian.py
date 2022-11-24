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
from tqdm import tqdm

##### GETTING PASSWORDS

GP = st.secrets["THE_GUARDIAN"]

def get_guardian_articles(query, datefrom=None, dateto=None):
    '''
    Function that get the number of articles published in The Guardian the last 2 years for a given query
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
        dateto = f"{dto.year}-{dto.month}-{dto.day}"
    else:
        d_ls = dateto.split("-")
        dto = datetime.datetime(int(d_ls[0]), int(d_ls[1]), int(d_ls[2]))
    if not datefrom:
        dfr = datetime.datetime.now()
        datefrom = f"{dfr.year-2}-{dfr.month}-{dfr.day}"
    else:
        d_ls = datefrom.split("-")
        dfr = datetime.datetime(int(d_ls[0]), int(d_ls[1]), int(d_ls[2]))    
    url = 'https://content.guardianapis.com/search?'
    parameters = {
        'api-key': GP,
        'q': query,
        'from-date': datefrom,
        'to-date': dateto,
        'order-by': 'newest',
        'page':1,
        'use-date':'published',
        'page-size': 100
    }
    url2 = url + urllib.parse.urlencode(parameters)
    try:
        response = requests.get(url2)
    except:
        print("Network error please check your internet connection")
        return []
    if response.status_code == 200:
        response = response.json()
        pages = response['response']['pages']
        #check if the number of pages are more than the number of days
        if pages > (dto-dfr).days:
            day = dfr
            for loop in tqdm(range((dfr-dto).days+1)):
                parameters['from-date'] = f"{day.year}-{day.month}-{day.day}"
                parameters['to-date'] = f"{day.year}-{day.month}-{day.day}"
                url2 = url + urllib.parse.urlencode(parameters)            
                try:
                    response = requests.get(url2)
                    if response.status_code == 200:
                        response = response.json()
                        dic_ = { "date": f"{day.year}-{day.month}-{day.day}",
                                "articles": response['response']['total'],
                                "query": query
                        }
                        articles.append(dic_)
                        day = day + datetime.timedelta(days=1)
                    else: 
                        print(f"Unable to fully retrieve articles from {query}, stopped at {day.year}-{day.month}-{day.day}: Error {response.status_code}: {response.text}")
                        return articles
                except:
                        print("Network error please check your internet connection, stopped at {day.year}-{day.month}-{day.day}")
                        return articles
        else:
            dic_dates = {}
            for i in tqdm(range(1, pages+1)):
                parameters['page'] = i
                url2 = url + urllib.parse.urlencode(parameters)
                try:
                    response = requests.get(url2)
                    if response.status_code == 200:
                        response = response.json()
                        results = response['response']['results']
                        for e in results:
                            pubdate = e['webPublicationDate'].split("T")[0]
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
    return articles
