from config.sqlconnect import engine
if "pd" not in dir():
    import pandas as pd
if "px" not in dir():
    import plotly.express as px
if "st" not in dir():
    import streamlit as st
import streamlit.components.v1 as components

st.title("Google Search Volume Standardization")

st.header("Keywords used as standard to calculate google search volume")

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
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
fig.update_traces(line=dict(width=3))
st.plotly_chart(fig)

st.header("Google Trends Data")

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
    height=600,)