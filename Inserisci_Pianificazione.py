import streamlit as st
import myauthenticator as stauth
import pandas as pd
import yaml
from yaml import SafeLoader
from datetime import datetime, timedelta

date_obj = datetime.today()
start_of_thisweek = date_obj - timedelta(days=date_obj.weekday())  # This Monday
end_of_thisweek = start_of_thisweek + timedelta(days=4)  # This Friday
start_of_nextweek = start_of_thisweek + timedelta(days=7) # Next Monday
end_of_nextweek = start_of_nextweek + timedelta(days=4) # Next Friday

if 'registerExpanded' not in st.session_state:
    st.session_state['registerExpanded'] = False

if 'successoRegistrazione' not in st.session_state:
    st.session_state['successoRegistrazione'] = False

if 'sidebarState' not in st.session_state or st.session_state["authentication_status"]==None:
    st.session_state['sidebarState'] = 'collapsed'


st.set_page_config(page_title="Inserisci la tua Pianificazione",initial_sidebar_state=st.session_state['sidebarState'])

def registraDati():
    utente={}
    utente['nome'] = st.session_state.nominativo1
    utente['presenze'] = []
    for days in daykeys:
        if st.session_state[days]:
            utente['presenze'].append(days)
    try:
        df_presenze=pd.read_csv('presenzeUtenti.csv',index_col=0)
    except:
        df_presenze=pd.DataFrame(columns=daykeys)
        print(df_presenze)
    df_presenze.loc[utente['nome'],:] = " "
    for day in utente['presenze']:
        df_presenze.loc[utente['nome'],day]="X"
    print(df_presenze)
    df_presenze.to_csv('presenzeUtenti.csv')

with open('./users.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.MyAuthenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

if st.session_state['successoRegistrazione']:
    st.success('Utente registrato con successo. Effettua il login')
    st.session_state['successoRegistrazione'] = False

name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status==True:
    authenticator.logout('Logout', 'sidebar')
    st.session_state['sidebarState'] = 'expanded'
    st.header('Inserisci la tua pianificazione')
    thisweek, nextweek = st.tabs(['Settimana corrente', 'Settimana prossima'])
    dayname = ('Lun','Mar','Mer','Gio','Ven')
    daykeys = ('Lun1','Mar1','Mer1','Gio1','Ven1','Lun2','Mar2','Mer2','Gio2','Ven2')


    with thisweek:
        st.write(f'La tua pianificazione di questa settimana, da lunedì {start_of_thisweek.strftime( "%d/%m/%y")} a venerdì {end_of_thisweek.strftime("%d/%m/%y")}')
        st.write('Spunta i giorni in cui sarai in ufficio:')
        name1, mon1, tue1, wed1, thur1, fri1 =st.columns((3,1,1,1,1,1))

        days1 = (mon1, tue1, wed1, thur1,fri1)
        daykey1 = daykeys[:5]

        with name1:
            st.text_input(label="Inserisci il tuo nome",label_visibility='hidden',value=st.session_state['name'], key= 'nominativo1', disabled=True)
        for i,day in enumerate(days1):
            with day:
                st.write(f"{dayname[i]}")
                if dayname[i]=='Ven':
                    st.checkbox(label=dayname[i],key=daykey1[i],disabled=True,label_visibility='hidden')
                else:
                    st.checkbox(label=dayname[i],key=daykey1[i],label_visibility='hidden')


    with nextweek:
        st.write(f'La tua pianificazione della settimana prossima, da lunedì {start_of_nextweek.strftime( "%d/%m/%y")} a venerdì {end_of_nextweek.strftime("%d/%m/%y")}')
        st.write('Spunta i giorni in cui sarai in ufficio:')
        name2, mon2, tue2, wed2, thur2, fri2 =st.columns((3,1,1,1,1,1))
        days2 = (mon2, tue2, wed2, thur2,fri2)
        daykey2 = daykeys[5:]


        with name2:
            st.text_input(label="Il tuo nome",label_visibility='hidden',value=st.session_state.nominativo1, key= 'nominativo2', disabled=True)
        for i,day in enumerate(days2):
            with day:
                st.write(f"{dayname[i]}")
                if dayname[i]=='Ven':
                    st.checkbox(label=dayname[i],key=daykey2[i],disabled=True, label_visibility='hidden')
                else:
                    st.checkbox(label=dayname[i],key=daykey2[i],label_visibility='hidden')


    _,_,_,_,_,col = st.columns((3,1,1,1,1,1))
    col.button('Salva', on_click=registraDati)
elif authentication_status==False:
    st.error('Username/password is incorrect')    
elif authentication_status==None:
    with st.expander('Nuovo utente? Registrati qui', expanded=st.session_state['registerExpanded']):
        try:
            if authenticator.register_user('Registrazione Nuovo Utente', location='main', preauthorization=False):
                st.session_state['successoRegistrazione'] = True
                st.session_state['RegisterExpanded'] = False
                with open('./users.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.experimental_rerun()
            
        except Exception as e:
            st.error(e)


