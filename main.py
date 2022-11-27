import streamlit as st
from src.plot import areaplot_google
from src.form_handler import kw_search


st.set_page_config(
     page_title="Keyword Research Tool",
     page_icon="🏠",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get help': 'https://github.com/sborto86/final-project',
         'About': "https://www.linkedin.com/in/sergi-portoles-comeras/"
     }
 )

st.header("Keyword Research")

form = st.form(key='keyword-input')
keyword = form.text_input('Enter a keyword or short term')
submit = form.form_submit_button('Search')

if submit:
    df= kw_search(keyword)
    fig = areaplot_google(df)
    st.plotly_chart(fig)