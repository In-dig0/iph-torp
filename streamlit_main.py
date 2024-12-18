import streamlit as st
import sqlitecloud
import pytz 
import io
import hmac

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.title("📝 :blue[TORP App Login]")
            st.divider()
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

def display_app_info():
    """ Show app title and description """
    
    import streamlit as st

    st.title("🧿 :blue[TORP Application]")
    st.write(
        """
        TORP - Technical Office Requests POC (Proof Of Concept), is a simple application to manage request to IPH Technical Office.
        """
    )
    st.markdown("Powered with Streamlit :streamlit:")
    st.divider()

def insert_request():
  pass

def view_request():
  pass

def main():
  if not check_password():
      st.stop()
  page_names_to_funcs = {
    "—": display_app_info,
    "Insert Request": insert_request,
    "View Request": view_request
}    
  demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()
if __name__ == "__main__":
    main()
