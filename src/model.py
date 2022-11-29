#### GENERATE THE TIME SERIES FROM THE DATABASE
from config.sqlconnect import engine
if "pd" not in dir():
    import pandas as pd
import datetime  
from datetime import timedelta 
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

def news_peaks(query):
    '''
    Function to find peaks in news publications to exclude from predictions
    Arguments:
        query: str.
            query to be analysed
        Returns: pandas.DataFrame
            Formatted to add to Facebook Phrophet model
    '''
    
    #Generating and formatting the news dataframe from 
    
    engine.connect()
    df = pd.read_sql(f"SELECT * FROM searchdata WHERE query='{query}'", engine)
    df['news']=df['guardian']+df['nyt']
    df = df.set_index('date')
    df.index = pd.DatetimeIndex(df.index)
    # Finding the dates that the mean of news published published in span of 6 days are 3 folds over the mean 
    
    mean_news = df["news"].mean()
    dates = []
    for i in range (0,len(df)):
        time = pd.DatetimeIndex(df.index).date
        start = df.index[i] - datetime.timedelta(days=3)
        end = df.index[i] + datetime.timedelta(days=3)
        test = df[(df.index > start) & (df.index < end)]
        if test["news"].mean() > 3*mean_news:
            dates.append(time[i])
    
    # Defining periods of the peaks:
    periods = []
    peaks = []
    if dates:
        periods = []
        for d in dates:
            included = False
            for p in periods:
                if p[0] <= d and p[1] >= d:
                    included = True
            if not included:
                end = d
                while end in dates:
                    end = end + datetime.timedelta(days=1)
                periods.append((d,end))
                peak = {
                    'holiday': f'News Peak {len(periods)}', 
                    'ds': d - datetime.timedelta(days=1), 
                    'lower_window': 0, 
                    'upper_window': (end-d).days
                    }
                peaks.append(peak)
        return pd.DataFrame(peaks)
    else: 
        return None            

def year_prediction(query, sus_news=True):
    '''
    
    '''
    #getting the search data from the sql database
    engine.connect()
    dfsql = pd.read_sql(f"SELECT * FROM searchdata WHERE query='{query}'", engine)
    if len(dfsql) == 0:
        return None
    dfsql = dfsql.set_index('date')
    dfsql.index = pd.DatetimeIndex(dfsql.index)
    #generating dataframe for modeling:
    min_search = dfsql['google'].min()/100 #defining a bootom for the model prediction
    max_search = dfsql['google'].max()*100 #defining a maximum for the model prediction
    df = pd.DataFrame()
    df['y']=dfsql['google']
    df['ds']=dfsql.index
    df['cap']=max_search
    df=df.reset_index(drop=True)
    # Getting peaks from the news published
    if sus_news:
        peaks = news_peaks(query)
    # modeling
    if sus_news and peaks:
        model = Prophet(holidays=peaks, growth='logistic')
    else:
        model = Prophet(growth='logistic')
    model.fit(df)
    future = model.make_future_dataframe(periods=365)
    future['floor']=min_search
    future['cap']=max_search
    forecast = model.predict(future)
    fig1 = model.plot(forecast, xlabel='date', ylabel='Google Search Volume',plot_cap=False)
    fig2 = model.plot_components(forecast,plot_cap=False)
    fig3 = plot_plotly(model, forecast, plot_cap=False, xlabel='date', ylabel='Google Search Volume')
    fig4 = plot_components_plotly(model, forecast, plot_cap=False,)
    return(fig1,fig2,fig3,fig4)






############### DEPRECIATED FUNCTIONS

def google_series():
    '''
    Function to generate a dataframe with the time series of google search
    Arguments:
        df: df
            pandas dataframe containing de data stored in searchdata datatable
    Returns: pandas.DataFrame
    '''
    df = pd.read_sql("SELECT * FROM searchdata", engine)
    query_list = list(df['query'].unique())
    google = pd.DataFrame()
    google[query_list[0]]=df[df['query']==query_list[0]][['google', 'date']].set_index('date')
    q2 = query_list[1:]
    for e in q2:
        dft = pd.DataFrame()
        dft[e]=df[df['query']==e][['google', 'date']].set_index('date')
        google = google.join(dft)
    google.index = pd.DatetimeIndex(google.index)
    return google
     
def news_series():
    '''
    Function to generate a dataframe with the time series of google search
    Arguments:
        df: df
            pandas dataframe containing de data stored in searchdata datatable
    Returns: pandas.DataFrame
    '''
    df = pd.read_sql("SELECT * FROM searchdata", engine)
    query_list = list(df['query'].unique())
    df['news']=df['guardian']+df['nyt']
    news = pd.DataFrame()
    news[query_list[0]]=df[df['query']==query_list[0]][['news', 'date']].set_index('date')
    q2 = query_list[1:]
    for e in q2:
        dft = pd.DataFrame()
        dft[e]=df[df['query']==e][['news', 'date']].set_index('date')
        news = news.join(dft)
    news.index = pd.DatetimeIndex(news.index)
    return news
