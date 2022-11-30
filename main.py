import streamlit as st
from src.plot import areaplot_google, areaplot_news
from src.form_handler import kw_search, keyword_val
from src.model import year_prediction
from st_pages import Page, show_pages, add_page_title
from PIL import Image
import pandas as pd

home = Image.open("./img/home.ico")
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
### Setting pages names:

show_pages([
    Page ("main.py", "Home", "🏚️"),
    Page ("pages/graphs.py", "Graphs", "📉"),
])

st.header("Keyword Research")

form = st.form(key='keyword-input')
keyword = form.text_input('Enter a keyword or short term')
submit = form.form_submit_button('Search')

if submit:
    if not keyword_val(keyword):
        st.write("Please insert a keyword or a short term (maximum 3 words)")
    st.header("Historical Data")
    df= kw_search(keyword)
    if type(df) == pd.core.frame.DataFrame:
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
        st.write(f'Sorry there was an error retrieving the historical data: {df}')
