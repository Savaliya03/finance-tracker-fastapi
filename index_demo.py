import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Load configuration file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create an authentication object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Create a login widget
authenticator.login('Login', 'main')

# Check authentication status
if st.session_state["authentication_status"]:
    # User is logged in
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    
    # Your main application code goes here
    st.write("Here goes your normal Streamlit app...")
    st.button("Click me")

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')