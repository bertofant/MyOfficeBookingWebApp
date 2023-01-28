import streamlit as st
import myauthenticator as stauth
import pandas as pd
import yaml
from yaml import SafeLoader

##### Define styles for HTML dataframe rendering
th_props = [
  ('font-size', '14px'),
  ('text-align', 'left'),
  ('font-weight', 'bold'),
  ('color', '#6d6d6d'),
  ('background-color', '#eeeeef'),
  ('border','1px solid #eeeeef'),
  #('padding','12px 35px')
]

td_props = [
  ('font-size', '14px'),
  ('text-align', 'center'),
]

cell_hover_props = [  # for row hover use <tr> instead of <td>
    ('background-color', '#eeeeef')
]

headers_props = [
    ('text-align','center'),
    ('font-size','1.1em')
]
#dict(selector='th:not(.index_name)',props=headers_props)

styles = [
    dict(selector="th", props=th_props),
    dict(selector="td", props=td_props),
    dict(selector="tr:hover",props=cell_hover_props),
    dict(selector='th.col_heading',props=headers_props),
    dict(selector='th.col_heading.level0',props=headers_props),
    dict(selector='th.col_heading.level1',props=td_props)
]
#####

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
    st.table(df_thisweek)
    st.markdown(header_style+build_table(df_thisweek),unsafe_allow_html=True)
    st.markdown(df_thisweek.style.set_table_styles(styles).to_html(),unsafe_allow_html=True)

    st.subheader('Pianificazione settimana prossima')
    st.table(df_nextweek)
    st.markdown(header_style+build_table(df_nextweek),unsafe_allow_html=True)
    st.markdown(df_nextweek.style.set_table_styles(styles).to_html(),unsafe_allow_html=True)
    df=df_nextweek.style.set_table_styles(styles,overwrite=False).set_properties(**{'text-align':'center'})
    st.table(df)
    df=df_nextweek.style.set_table_styles(styles)
    st.table(df)

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

st.session_state

