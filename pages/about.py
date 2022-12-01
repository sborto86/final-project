from config.sqlconnect import engine
if "pd" not in dir():
    import pandas as pd
if "px" not in dir():
    import plotly.express as px
if "st" not in dir():
    import streamlit as st
import streamlit.components.v1 as components
from src.plot import areaplot_google, areaplot_news
from src.form_handler import kw_search
from src.model import year_prediction

st.markdown('''
            <style>
            p {
                font-size: 1.3rem;
                }
            </style>
            ''',unsafe_allow_html=True)

st.title("About the Project")
st.image("img/code.png")
st.markdown('''## Table of contents

1. <a href="#background">Background</a>
2. <a href="#objectives">Objectives</a>
3. <a href="#limitations">Limitations</a>
4. <a href="#how-it-works">How it works?</a>
    - <a href="#data-acquisition">Data acquisition</a>
    - <a href="#data-processing">Data Processing</a>
    - <a href="#creating-standards">Creating standards</a>
    - <a href="#getting-the-historical-data">Getting the historical data</a>
    - <a href="#getting-everything-toghether">Getting everything toghether</a>
    - <a href="#data-storage">Data Storage</a>
    - <a href="#modeling-and-prediction">Modeling and prediction</a>
6. <a href="#future-improvements">Future Improvements</a>

<h2>Background</h2>

To design a good SEO strategy, access to big amounts of data is essential. However, access to quality data is getting harder and harder.

At the present moment, SEO tools available are expensive or offer low-quality data.

<h2>Objectives</h2>

**1. Proof of concept**: 

Design a minimum working application for SEO keyword research with a limited time (around a week) and 0 budget.

**2. Easy to deploy application**: 

Design an application that can be deployed online by anyone with only few commands.

**3. Prove that news can be a good predictor of search behavior abnormalities**: 

The search behavior of the users is usually predictable and easy to forecast. However, sometimes there are sudden spikes in searches that affect the quality of the prediction models.

This project pretends to show that we can combine, data extracted from the news and the historical behavior of the users, to improve the quality of the prediction models.
            
<h2>Limitations</h2>

Most of the limitations of this application come from the difficulty of getting good and reliable data

1. **News are only extracted from only two sources**, The Guardian and The New York Times

2. **Google search data is global**, regional data is not abaviable

3. **The application is optimized for English keywords**, other languages can be used, but the predictions will have a higher degree of inaccuracy.

4. **Low search keywords will not generate results**,  the estimated lower limit of detection is about 1.000 - 2.000 searches per day.

5. **Only short keywords are accepted** , maximum 3 words lengh are accepted.

6. **The data acquisition might be slow**, 3 - 5 minutes per new  keyword.

7. **The historical data is limited to two years**

8. **Google might block the request**, the acquisition of data requires multiple calls to the google trends website that might trigger the firewall.

9. **Search volume values are estimations**

<h2>How it works?</h2>
''', unsafe_allow_html=True)

st.image("img/app-schema.png")

st.markdown('''*A simple schema of the application structure*  

<h3>Data acquisition</h3>

Sources of data used in this application:

1. **Google Trends**: Web scrapping using the library pytrends.''', unsafe_allow_html=True)
st.image("img/google.png")
st.markdown('''2. **The Guardian**: Live API calls.''')
st.image("img/guardian.png")
st.markdown("3. **The New York Times**: News archives of the last two years are stored in the database, and the missing data will be updated (if necessary) in every call.")
st.image("img/nyt.png")
st.markdown('''<h3>Data Processing</h3>
            
<h4>1. Getting Google trends data</h4>
            
**First let's see what google trends offers us**:
''', unsafe_allow_html=True)

components.html('''<script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/3140_RC01/embed_loader.js"></script> 
            <script type="text/javascript"> trends.embed.renderExploreWidget("TIMESERIES", 
            {"comparisonItem":[{"keyword":"youtube","geo":"","time":"2020-01-12 2022-01-12"}],"category":0,"property":""}, 
            {"exploreQuery":"date=2020-01-12%202022-01-12&q=youtube","guestPath":"https://trends.google.es:443/trends/embed/"}); </script>''', height=450)

st.markdown('''
The information that we obtain is only a weekly average relative to the maximum 
<h4>2. From relative data to absolute data</h4>

To convert from relative to absolute data, the information provided by Semrush (one of the most renowned SEO tools) was used.  
            ''', unsafe_allow_html=True)

st.image("img/semrush.png")
st.markdown('''
            You can read the full article by [clicking here](https://www.semrush.com/blog/most-searched-keywords-google/)

The information we get from this article is the average monthly search of the term "youtube" from January through August 2022 (see bellow):
            ''', unsafe_allow_html=True)
st.image("img/semrush2.png")

st.markdown('''
<h4>3. Creating standards</h4>
Then with this information, we get an array of keywords from high-volume search keywords to reach the limit of detection of Google Trends: 
''', unsafe_allow_html=True)

components.html(''' <script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/3140_RC01/embed_loader.js"></script> 
                <script type="text/javascript"> trends.embed.renderExploreWidget("TIMESERIES", 
                {"comparisonItem":[{"keyword":"youtube","geo":"","time":"2022-01-01 2022-08-31"},
                {"keyword":"food","geo":"","time":"2022-01-01 2022-08-31"},
                {"keyword":"cheap flights","geo":"","time":"2022-01-01 2022-08-31"},
                {"keyword":"doctor","geo":"","time":"2022-01-01 2022-08-31"},
                {"keyword":"dentist","geo":"","time":"2022-01-01 2022-08-31"}
                ],
                "category":0,"property":""}, 
                {"exploreQuery":"date=2022-01-01%202022-08-31&q=youtube,food,doctor,dentist,cheap%20flights","guestPath":"https://trends.google.es:443/trends/embed/"}
                ); </script>
                ''',
    height=450)

st.markdown('''Finally, by performing successive pair comparisons we obtain an estimation of the absolute search volume of each keyword:''', unsafe_allow_html=True)

engine.connect()
query='''
    SELECT * FROM standardvolume
    WHERE query != 'Ukraine' AND query != 'amazon'
    '''
df = pd.read_sql(query,engine)
fig = px.line(df, x='date', y="searchvolume", color="query", log_y=True)
fig.update_layout(
    title='Daily Google Search Volume by Keyword',
    xaxis_title="Date",
    yaxis_title="Search Volume",
    legend_title_text='Keyword',
    title_x=0.5,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey', tickvals=[10000000, 1000000, 100000, 10000,1000, 100,])
fig.update_traces(line=dict(width=3))
st.plotly_chart(fig)

st.markdown(''' 
Once these standards are created, we can proceed to extrapolate the absolute volume data of any keyword.

<h4>4. Getting the historical data</h4>
To get the calculated absolute search volume of a new keyword, the following process is going to performed:

1. **Find the most silimar standard**: By comparing each standard and the keyword in Google Trends we get the standard that have a similar search volume than the keyword.

2. **Convert the relative volume to absolute volume**: We use the standard to extrapolate the keyword search volume.

3. **Retrive the historical data**: Once we have the search volume from the window of the standards (January to August 2022), we get the last two years historical data for the keyword from Google Trends (relative data). 

4. **Obtain the absolute historical data** : Finally we use the absolute data obtained in the second step to calculate the historical data.
            
For example if search for "pizza" we get the following result:
            ''', unsafe_allow_html=True)
engine.connect()
query='''
    SELECT * FROM searchdata
    WHERE query = 'pizza';
    '''
df2 = pd.read_sql(query,engine)
fig = px.line(df2, x='date', y="google")
fig.update_layout(
    title='Daily Google Search Volume',
    xaxis_title="Date",
    yaxis_title="Search Volume",
    legend_title_text='Keyword',
    title_x=0.5,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
fig.update_traces(line=dict(width=3))
st.plotly_chart(fig)

st.markdown('''
Now that we have the google historical data we can proceed to scrape the newspapers (The Guardian and The New York Times)

The process is simple we check the number of news published every day that the keyword is found in the headline or the summary. 

Using the same example as before we obtain something like this:            
            ''', unsafe_allow_html=True)

engine.connect()
query='''
    SELECT `date`, `guardian`, `nyt`, `query` FROM searchdata
    WHERE query = 'pizza';
    '''
df3 = pd.read_sql(query,engine)
st.dataframe(df3)
st.markdown('''
<h4>5. Getting everything toghether</h4>

After putting all the data together, we are ready to proceed to the next step, forecasting.

But first, let's see another example, if we search for Covid-19:
''', unsafe_allow_html=True)
df4= kw_search('covid-19')
fig = areaplot_google(df4, 'covid-19')
st.plotly_chart(fig)
fig2= areaplot_news(df4, 'covid-19')
st.plotly_chart(fig2)
st.markdown('''
As we can see here there is a good correlation between the peaks of news published and the peaks of the searches in google.

Looks like we are on the right track...

<h3 id="section-6c">Data Storage</h3>

All the extracted and processed data is stored in a simple SQL database. The schema is shown below:
''', unsafe_allow_html=True)

st.image("img/sqldb.png")

st.markdown('''
<h3>Modeling and prediction</h3>
''', unsafe_allow_html=True)
st.image("img/prophet.png")

st.markdown('''
In order, to fit our data into a model and perform forecasting the Facebook Prophet algorithm is used. There are sevral reasons to choose this algorithm, the main reasons are exposed bellow:

1. **It is fast**: We need a model that don't delay to much the processing time as the web scrapping process is already slow.

2. **It is less sensible to outliers than other models**: Compare to other predictive models is less to abnormal peaks in search volume (outliers)

3. **Good predicting yearly and weekly seasonability**: The algorithm was designed specially to predict seasonability,

4. **Can ignore periods of data**: This is one of the most important features to choose this model. As we want to exclude the periods where peaks are detected on news.

But let's see one example, if we search for Ukraine we obtain the following results:
            ''')
df5= kw_search('ukraine')
fig = areaplot_google(df5, 'ukraine')
st.plotly_chart(fig)
fig2= areaplot_news(df5, 'ukraine')
st.plotly_chart(fig2)
figures = year_prediction('ukraine')
st.plotly_chart(figures[2])
st.plotly_chart(figures[3], use_container_width=600)

st.markdown('''
<h2>Future Improvements</h2>

1. **Improve speed**:  Implement asynchronous calls by modifying the pytrends library to work with threads and use a random IP from a proxy list (to avoid being blocked by google).

2. **Improve stability**: The code has been written with a limited amount of time and might need some debugging processes.

3. **Include other sources of data** to get better estimations of searches and news trends.         
            ''', unsafe_allow_html=True)