import streamlit as st
import streamlit_authenticator as stauth

names = ["Admin"]
usernames = ["admin"]
passwords = ["your_password_here"]  # Replace with hashed passwords in prod

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    "spectra_guardian_cookie", "some_signature_key", cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if not authentication_status:
    st.warning("Please enter your username and password")
    st.stop()

if authentication_status:
    authenticator.logout("Logout", "main")
    st.write(f"Welcome *{name}*")

st.title("Spectra Guardian Monitoring Dashboard")

# ... (rest of your dashboard code here)
