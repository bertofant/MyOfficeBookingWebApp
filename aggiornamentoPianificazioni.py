import pandas as pd
from datetime import datetime

date_obj = datetime.today()
# check if it is monday and the script must be executed
ismonday = (date_obj.weekday()==0)
if ismonday:
    ##check if the script has been already executed today
    # get today date
    todaydate = date_obj.strftime('%Y%m%d') 
    # read from file the date of the last execution of the script
    with open('ultimoaggiornamento.txt','r') as file:
        lastupdate = file.readline()
    # if the last time the script was executed is not today, run the script    
    if lastupdate != todaydate:
        df_presenze=pd.read_csv('presenzeUtenti.csv',index_col=0)
        df_nextweek=df_presenze.loc[:,'Lun2':'Ven2']
        df_presenze.loc[:,'Lun1':'Ven1'] = df_nextweek.values
        df_presenze.loc[:,'Lun2':'Ven2'] = ' '
        df_presenze.to_csv('presenzeUtenti.csv')
        # save on file the current date as the last time the script was executed
        with open('ultimoaggiornamento.txt','w') as file:
            file.write(todaydate)
