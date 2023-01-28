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

def build_table(df_week):
    header  = "|   |Lunedì  | Martedì | Mercoledì | Giovedì | Venerdì |"
    header += "\n|---|:---:|:---:|:---:|:---:|:---:|"
    table = header
    for nome in df_week.index:
        prenotazioni = df_week.loc[nome,:].values.tolist()
        if nome == st.session_state['name']:
            newrow = f'\n|**:blue[{nome}]**'
        else:
            newrow = f'\n|{nome}'
        for days in prenotazioni:
            if nome == st.session_state['name']:
                newrow += f'| **:blue[{days}]** '
            else:
                newrow += f'| {days} '
        newrow += '|'
        table += newrow
    return table

header_style = '''
    <style>
        th{
            background-color: rgb(240, 242, 246);
        }
        .css-a51556 {
            border-bottom: 1px solid rgba(49, 51, 63, 0.1);
            border-right: 1px solid rgba(49, 51, 63, 0.1);
            vertical-align: middle;
            padding: 0.25rem 0.375rem;
            font-weight: 400;
            color: rgba(49, 51, 63);
        }

        tr:hover{
            background-color: rgba(0, 104, 201, 0.1);
        }

    </style>
'''


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
    st.write(f' Settimana da lunedì {start_of_thisweek.strftime( "%d/%m/%y")} a venerdì {end_of_thisweek.strftime("%d/%m/%y")}')
    #st.table(df_thisweek)
    st.markdown(header_style+build_table(df_thisweek),unsafe_allow_html=True)

    st.markdown('<br>',unsafe_allow_html=True)

    st.subheader('Pianificazione settimana prossima')
    st.write(f'Settimana da lunedì { start_of_nextweek.strftime("%d/%m/%y")} a venerdì {end_of_nextweek.strftime("%d/%m/%y")}')
    #st.table(df_nextweek)
    st.markdown(header_style+build_table(df_nextweek),unsafe_allow_html=True)


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

#st.session_state

