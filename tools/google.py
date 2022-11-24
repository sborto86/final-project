## IMPORTING LIBRARIES
from pytrends import dailydata
if "datetime" not in dir():
    import datetime
    from dateutil.relativedelta import relativedelta

def google_trends(query, fr=None, to=None):
    '''
    '''
    if not to:
        dto = datetime.datetime.now() - relativedelta(years=2)
    else:
        d_ls = to.split("-")
        dto = datetime.datetime(int(d_ls[0]), int(d_ls[1]), int(d_ls[2]))
    if not fr:
        dfr = datetime.datetime.now()
    else:
        d_ls = fr.split("-")
        dfr = datetime.datetime(int(d_ls[0]), int(d_ls[1]), int(d_ls[2]))
    try:
        trends = dailydata.get_daily_data('query', fr.year, fr.month, to.year, to.month)
    except:
        return False #REVIEW!!!!!!
    return trends


