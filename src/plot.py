### PLOTTING FUNCTIONS

if "pd" not in dir():
    import pandas as pd
import plotly.express as px

def  areaplot_google(df, keyword):
    fig = px.area(df, x='date', y="google")
    fig.update_layout(
        title=f'Daily Google Search Volume for the Keyword "{keyword}"',
        xaxis_title="Date",
        yaxis_title="Search Volume",
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_traces(line=dict(width=3))
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig
def areaplot_news(df, keyword):
    df['news']=df['guardian']+df['nyt']
    fig = px.area(df, x='date', y="news")
    fig.update_layout(
        title=f'Daily Articles Published for the Keyword "{keyword}"',
        xaxis_title="Date",
        yaxis_title="Articles Published",
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_traces(line=dict(width=3, color="#FF3935"))
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig