from config.sqlconnect import engine
if "pd" not in dir():
    import pandas as pd
if "px" not in dir():
    import plotly.express as px
if "st" not in dir():
    import streamlit as st
import streamlit.components.v1 as components

st.markdown('''
            <style>
            p {
                font-size: 1.3rem;
                }
            </style>
            ''',unsafe_allow_html=True)

st.title("About the Project")

st.markdown('''## Table of contents

1. <a href="#background">Background</a>
2. <a href="#objectives">Objectives</a>
3. <a href="#limitations">Limitations</a>
4. <a href="#how-it-works">How it works?</a>
    - <a href="#data-acquisition">Data acquisition</a>
    - <a href="#data-processing">Data Processing</a>
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
            
<strong>First let's see what google trends offers us</strong>:
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
