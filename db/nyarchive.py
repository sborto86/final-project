#### This Script creates a SQL table with the last 2 years of New York Times News

import requests
import pandas as pd
import datetime
import time
from streamlit import secrets
from tqdm import tqdm
import os, sys
from dateutil.relativedelta import relativedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.sqlqueries import engine
NY = secrets["NYT"]
engine.connect()
date = datetime.datetime.now()

for l in tqdm(range(24)):
    url = f'https://api.nytimes.com/svc/archive/v1/{date.year}/{date.month}.json?api-key={NY}'
    content = requests.get(url)
    content = content.json()
    news_list=[{"date": news['pub_date'].split("T")[0],"text": news['abstract']+news['headline']['main']+news['headline']['print_headline']+news['lead_paragraph']} for news in content["response"]["docs"]]
    df = pd.DataFrame(news_list)
    df['date'] = df["date"].astype('datetime64[ns]')
    df.to_sql("nytarchive",engine,index=False, if_exists='append', method='multi')
    date = date - relativedelta(months=1)
print("NYT Archive Database Created")