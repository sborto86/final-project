### FUNCTIONS TO ADD DATA TO THE STANDARD VOLUME TABLE
from tools.sqlqueries import query_list, get_average, ins_average, remove_duplicates
from tools.google import trend_to_absolute
if "datetime" not in dir():
    import datetime
    from dateutil.relativedelta import relativedelta
def add_standard(ref, standard):
    ref: str
    '''
    Adds a new keyword in the gvolume table (if doesn't exists) and adds a standard daily search volume
    Arguments:
        ref: str.
            reference keyword
        standard: str. / False
            keyword to add as a standard, if set to False the reference word will be added
    '''

    added_list = query_list('standardvolume')
    # check for possible duplicates
    duplicates = False
    if standard and standard in added_list:
        duplicates = True
    elif not standard and ref in added_list:
        duplicates = True
    # Getting reference data
    avg_dic = get_average(ref)
    if not avg_dic:
        ##### ERRROR HANDELING
        return False
    # creating keywords list
    values = ""
    if standard:
        kws = [ref, standard]
        # creating rows to insert in the database
        df = trend_to_absolute(kws,avg_dic['avg'],avg_dic['fromdate'].strftime("%Y-%m-%d"),avg_dic['todate'].strftime("%Y-%m-%d"))
        for i,row in df.iterrows():
            values+=f"('{i.to_pydatetime().date()}',{row[standard]},'{standard}'),"
        values = values[:-1]
        values+=";"
        # adding average to gvolume table
        dif_date = relativedelta(avg_dic['todate'], avg_dic['fromdate'])
        months = dif_date.months
        if dif_date.days > 15:
         months+=1
        print(df[standard].sum()/months)
        ins_average(standard, int(df[standard].sum()/months), avg_dic['fromdate'].strftime("%Y-%m-%d"), avg_dic['todate'].strftime("%Y-%m-%d"))
    else: 
        kws = [ref]
        # creating rows to insert in the database
        df = trend_to_absolute(kws,avg_dic['avg'],avg_dic['fromdate'].strftime("%Y-%m-%d"),avg_dic['todate'].strftime("%Y-%m-%d"))
        for i,row in df.iterrows():
            values+=f"('{i.to_pydatetime().date()}',{row[ref]},'{ref}'),"
        values = values[:-1]
        values+=";"
    #SQL query
    from config.sqlconnect import engine
    query='''INSERT INTO `standardvolume` (`date`, `searchvolume`, `query`)
            VALUES'''
    query+=values
    ########## ERROR HANDELING
    engine.execute(query)
    if duplicates:
        remove_duplicates('standardvolume')