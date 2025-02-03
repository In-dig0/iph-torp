import streamlit as st

def display_app_info(app_name: str, app_version: str) -> None:
    """ Show app title and description """
    
    st.header(f":blue[{app_name} Web Application]", divider="grey")
    st.markdown(
    """
    <h3>A simple web application developed as a POC in order to manage requests<br>
    to IPH Technical Office.</h3>
    """,
    unsafe_allow_html=True
)
    st.markdown(f":grey[Version: {app_version}]")
    st.divider()
    with st.expander("System info", icon="🌐"):
        st.markdown(f":streamlit: Streamlit Cloud version {st.__version__}")
        st.markdown(f"⛃ Database SQLITE Cloud version {st.session_state.sqlite_version}")
