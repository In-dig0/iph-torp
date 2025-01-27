import streamlit

def display_app_info():
    """ Show app title and description """
    
    st.header(":blue[TORP Web Application]", divider="blue")
    st.subheader(
        """
        TORP - Technical Office Requests POC (Proof Of Concept), is a simple web application to manage requests to IPH Technical Office.
        """
    )
    st.markdown(f":grey[Version: {APPVERSION}]")
    st.divider()
    st.markdown("Powered with Streamlit :streamlit:")
