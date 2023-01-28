import streamlit as st
from streamlit_authenticator import Authenticate
from streamlit_authenticator.exceptions import RegisterError
from datetime import datetime, timedelta

class MyAuthenticate(Authenticate):
    def __init__(self, credentials: dict, cookie_name: str, key: str, cookie_expiry_days: int = 30, preauthorized: list = None):
        super().__init__(credentials, cookie_name, key, cookie_expiry_days, preauthorized)


    def find_name_in_credentials(self,name):
        for user in self.credentials['usernames']:
            if name == self.credentials['usernames'][user]['name']:
                return True
        return False


    def register_user(self, form_name: str, location: str='main', preauthorization=True) -> bool:
        """
        Creates a password reset widget.
        Modified in order to check if also email and name are already used

        Parameters
        ----------
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        preauthorization: bool
            The pre-authorization requirement, True: user must be pre-authorized to register, 
            False: any user can register.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """
        if not self.preauthorized:
            raise ValueError("Pre-authorization argument must not be None")
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            register_user_form = st.form('Register user')
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('Register user')

        register_user_form.subheader(form_name)
        new_email = register_user_form.text_input('Email').lower()
        new_username = new_email
        new_name = register_user_form.text_input('Nome con cui verrà visualizzata la tua pianificazione')
        new_password = register_user_form.text_input('Password', type='password')
        new_password_repeat = register_user_form.text_input('Ripeti la password', type='password')

        if register_user_form.form_submit_button('Registrati'):
            if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
                if new_username not in self.credentials['usernames'] and not self.find_name_in_credentials(new_name):
                    if new_password == new_password_repeat:
                        if preauthorization:
                            if new_email in self.preauthorized['emails']:
                                self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
                                return True
                            else:
                                raise RegisterError('User not pre-authorized to register')
                        else:
                            self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
                            return True
                    else:
                        raise RegisterError('Le Password inserite sono differenti')
                else:
                    if new_username in self.credentials['usernames']:
                        raise RegisterError('Email già utilizzata')
                    elif self.find_name_in_credentials(new_name):
                        raise RegisterError('Nome per la pianificazione già utilizzato')

            else:
                raise RegisterError('Inserire email, nome e password')

    def _check_credentials(self, inplace: bool=True) -> bool:
        """
        Checks the validity of the entered credentials.
        Modified to accept either username or email as username

        Parameters
        ----------
        inplace: bool
            Inplace setting, True: authentication status will be stored in session state, 
            False: authentication status will be returned as bool.
        Returns
        -------
        bool
            Validity of entered credentials.
        """

        if self.username in self.credentials['usernames']:
            try:
                if self._check_pw():
                    if inplace:
                        st.session_state['name'] = self.credentials['usernames'][self.username]['name']
                        self.exp_date = self._set_exp_date()
                        self.token = self._token_encode()
                        self.cookie_manager.set(self.cookie_name, self.token,
                            expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days))
                        st.session_state['authentication_status'] = True
                    else:
                        return True
                else:
                    if inplace:
                        st.session_state['authentication_status'] = False
                    else:
                        return False
            except Exception as e:
                print(e)
        else:
            if inplace:
                st.session_state['authentication_status'] = False
            else:
                return False

    def login(self, form_name: str, location: str='main') -> tuple:
        """
        Creates a login widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the login form.
        location: str
            The location of the login form i.e. main or sidebar.
        Returns
        -------
        str
            Name of the authenticated user.
        bool
            The status of authentication, None: no credentials entered, 
            False: incorrect credentials, True: correct credentials.
        str
            Username of the authenticated user.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if not st.session_state['authentication_status']:
            self._check_cookie()
            if st.session_state['authentication_status'] != True:
                if location == 'main':
                    login_form = st.form('Login')
                elif location == 'sidebar':
                    login_form = st.sidebar.form('Login')

                login_form.subheader(form_name)
                self.username = login_form.text_input('Email').lower()
                st.session_state['username'] = self.username
                self.password = login_form.text_input('Password', type='password')

                if login_form.form_submit_button('Login'):
                    self._check_credentials()

        return st.session_state['name'], st.session_state['authentication_status'], st.session_state['username']

