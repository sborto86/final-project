### PLOTTING FUNCTIONS

if "pd" not in dir():
    import pandas as pd
import plotly.express as px

def  areaplot_google(df):
    fig = px.area(df, x='date', y="google")
    fig.update_layout(
        title='Google Search Volume Keyword "Ukranie"',
        xaxis_title="Date",
        yaxis_title="Search Volume",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        ),
        title_x=0.5,
        title_y=1
    )
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