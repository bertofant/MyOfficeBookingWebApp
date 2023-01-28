import pandas as pd

df_presenze=pd.read_csv('presenzeUtenti.csv',index_col=0)
df_nextweek=df_presenze.loc[:,'Lun2':'Ven2']
df_presenze.loc[:,'Lun1':'Ven1'] = df_nextweek.values
df_presenze.loc[:,'Lun2':'Ven2'] = ' '

df_presenze.to_csv('presenzeUtenti.csv')
