## IMPORTING LIBRARIES
from pytrends.request import TrendReq
if "datetime" not in dir():
    import datetime
    from dateutil.relativedelta import relativedelta

def trend_to_absolute(kws, avg, fr, to):
    '''
    Calculates the dayly search volume calculated from a reference search keyword
    Arguments:
        kws: list.
            list of keywords with the reference keyword in the first place (max: 5 keywords)
        avg: int. 
            Average monthly search volume for a reference keyword in a period
        fr: str.
            date in YYYY-MM-DD format (start date of the average monthy search volume)
        to: str.
            date in YYYY-MM-DD format (end date of the average monthy search volume)
    Returns a dataframe with absoulute search volume
    '''
    d_ls = to.split("-")
    dto = datetime.datetime(int(d_ls[0]), int(d_ls[1]), int(d_ls[2]))
    d_ls = fr.split("-")
    dfr = datetime.datetime(int(d_ls[0]), int(d_ls[1]), int(d_ls[2]))
    dif_date = relativedelta(dto,dfr)
    months = dif_date.months
    if dif_date.days > 15:
        months+=1
    total_search = avg*months
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=kws, timeframe=f'{fr} {to}')
    df = pytrend.interest_over_time()
    rel=int(total_search/df[kws[0]].sum())
    for kw in kws:
        df[kw] = df[kw]*rel
    return df


