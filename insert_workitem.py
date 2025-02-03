import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
# Internal app module
import servant

def insert_workitem(conn):
    
        # Load data into session state if not already present
    session_data = {
        'df_depts': sqlite_db.load_dept_data,
        'df_users': sqlite_db.load_users_data,
        'df_pline': sqlite_db.load_pline_data,
        'df_pfamily': sqlite_db.load_pfamily_data,
        'df_category': sqlite_db.load_category_data,
        'df_type': sqlite_db.load_type_data,
        'df_lk_type_category': sqlite_db.load_lk_type_category_data,
        'df_lk_category_detail': sqlite_db.load_lk_category_detail_data,
        'df_lk_pline_tdtl': sqlite_db.load_lk_pline_tdtl_data,
        'df_detail': sqlite_db.load_detail_data,
        'df_requests': sqlite_db.load_requests_data,
        'df_reqassignedto': sqlite_db.load_reqassignedto_data,
        'df_attachments': sqlite_db.load_attachments_data,
        'df_workorder': sqlite_db.load_workorder_data,
        'df_woassignedto': sqlite_db.load_woassignedto_data,
        'df_workitem': sqlite_db.load_workitem_data,
    }

    for key, loader in session_data.items():
        if key not in st.session_state:
            st.session_state[key] = loader(conn)

    
    st.sidebar.divider()
    st.sidebar.header(f":orange[Filters]")
    if df_woassignedto is None or df_woassignedto.empty:
        st.warning("No work order assignment data available. Please check your data source")
        st.stop() # Stop execution of the script
    else:    
        unique_usernames = df_woassignedto['USERNAME'].unique()
        sorted_usernames = sorted(unique_usernames)
        wo_username_options = list(sorted_usernames)
    
    selected_username = st.sidebar.selectbox(label=":blue[Tech Deparment Specialist]", options=wo_username_options, index=None)
    #st.write(selected_username)
    
    df_wo_usercode = df_woassignedto[df_woassignedto['USERNAME'] == selected_username]["USERID"].unique()
    wo_usercode = list(df_wo_usercode)

    if selected_username:
        st.session_state.selected_username = True
        wo_woid = df_woassignedto[df_woassignedto['USERNAME'] == selected_username]['WOID']
        unique_woid = wo_woid.unique()
        sorted_woid = sorted(unique_woid)
        wo_woid_options = list(sorted_woid)
    else:
        wo_woid_options = []