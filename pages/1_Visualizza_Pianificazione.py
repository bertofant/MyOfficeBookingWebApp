import streamlit as st
import myauthenticator as stauth
import pandas as pd
import yaml
from yaml import SafeLoader


if 'registerExpanded' not in st.session_state:
    st.session_state['registerExpanded'] = False

if 'successoRegistrazione' not in st.session_state:
    st.session_state['successoRegistrazione'] = False

if 'sidebarState' not in st.session_state or st.session_state["authentication_status"]==None:
    st.session_state['sidebarState'] = 'collapsed'


st.set_page_config(page_title="Visualizza la Pianificazione",initial_sidebar_state=st.session_state['sidebarState'])
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

    df_presenze=pd.read_csv('presenzeUtenti.csv',index_col=0)
    days=['Lun', 'Mar', 'Mer', 'Gio', 'Ven']
    df_thisweek=df_presenze.loc[:,'Lun1':'Ven1']
    df_thisweek.columns = days

    df_nextweek=df_presenze.loc[:,'Lun2':'Ven2']
    df_nextweek.columns = days

    st.subheader('Pianificazione settimana corrente')
    st.table(df_thisweek)

    st.subheader('Pianificazione settimana prossima')
    st.table(df_nextweek)
elif authentication_status==False:
    st.error('Username/password is incorrect')
elif authentication_status==None:
    with st.expander('Nuovo utente? Registrati qui', expanded=st.session_state['registerExpanded']):
        try:
            if authenticator.register_user('Register user', location='main', preauthorization=False):
                st.session_state['successoRegistrazione'] = True
                st.session_state['RegisterExpanded'] = False
                with open('./users.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.experimental_rerun()
            
        except Exception as e:
            st.error(e)

