import streamlit as st
from src.plot import areaplot_google, areaplot_news
from src.form_handler import kw_search, keyword_val
from src.model import year_prediction
from st_pages import Page, show_pages, add_page_title
import streamlit.components.v1 as components
import pandas as pd
import time

st.set_page_config(
     page_title="Keyword Research Tool",
     page_icon="📉",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get help': 'https://github.com/sborto86/final-project/issues',
         'About': "https://github.com/sborto86/final-project"
     }
 )

st.title("A Simple Keyword Research Tool")
st.image('img/seo.png')

### Setting pages names:

show_pages([
    Page ("main.py", "Keyword Research Tool", "📉"),
    Page ("pages/about.py", "About the Project", ":grey_question:"),
    Page ("pages/installation.py", "How to Install and Deploy", "⚙️")
])

form = st.form(key='keyword-input')
keyword = form.text_input('Enter a keyword or short term')
submit = form.form_submit_button('Search')

if submit:
    if not keyword_val(keyword):
        st.write("Please insert a keyword or a short term (maximum 3 words)")
    tstart = time.time()
    with st.spinner("Retrieving historical data, please wait..."):
        df= kw_search(keyword)
    tend = time.time()
    time_pass= tend-tstart
    
    if type(df) == pd.core.frame.DataFrame:
        st.success(f"Hitorical data retrived succefully in {time_pass} seconds")
        st.header("Historical Data")
        fig = areaplot_google(df, keyword)
        st.plotly_chart(fig)
        fig2= areaplot_news(df, keyword)
        st.plotly_chart(fig2)
        st.header("Prediction Models")
        figures = year_prediction(keyword)
        st.subheader("One Year Prediction")
        st.plotly_chart(figures[2])
        st.subheader("Trends and Seasonality")
        st.plotly_chart(figures[3], use_container_width=600)
    else:
        st.error(f'Sorry there was an error retrieving the historical data: {df}')

# Adding some CSS

st.markdown('''
                <style>
                    .css-1v0mbdj {
                        margin: auto;
                        }
                    h1 {
                        text-align: center;
                        color: white;
                        padding-top: 1.5rem;
                        background-color: #2f8ad3;
                        margin: revert;
                    }
                    .css-18e3th9 {
                        padding: 1rem 1rem 10rem;
                    }
                    .css-12ttj6m {
                        background-color: #2f8ad3;
                    }
                    .css-184tjsw p {
                        font-size: 18px;
                        color: white;
                        font-weight: 700;
                    }
                </style>
                ''', unsafe_allow_html=True)
