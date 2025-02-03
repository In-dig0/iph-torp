import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
# Internal app module
import servant

def insert_workitems(conn):
    
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
        'df_workorders': sqlite_db.load_workorders_data,
        'df_woassignedto': sqlite_db.load_woassignedto_data,
        'df_workitems': sqlite_db.load_workitems_data,
    }

    for key, loader in session_data.items():
        if key not in st.session_state:
            st.session_state[key] = loader(conn)

    
    st.sidebar.divider()
    st.sidebar.header(f":orange[Filters]")
    if st.session_state.df_woassignedto is None or st.session_state.df_woassignedto.empty:
        st.warning("No work order assignment data available. Please check your data source")
        st.stop() # Stop execution of the script
    else:    
        unique_usernames = st.session_state.df_woassignedto['USERNAME'].unique()
        sorted_usernames = sorted(unique_usernames)
        wo_username_options = list(sorted_usernames)
    
    selected_username = st.sidebar.selectbox(label=":blue[Tech Department Specialist]", options=wo_username_options, index=None)
    #st.write(selected_username)
    
    df_wo_usercode = st.session_state.df_woassignedto[st.session_state.df_woassignedto['USERNAME'] == selected_username]["USERID"].unique()
    wo_usercode = list(df_wo_usercode)

    if selected_username:
        st.session_state.selected_username = True
        df_selected_usercode = st.session_state.df_users[st.session_state.df_users["USERNAME"]==selected_username]["USERID"]
        selected_usercode = servant.get_code_from_name(st.session_state.df_users, df_selected_usercode, "CODE")
        wo_woid = st.session_state.df_woassignedto[st.session_state.df_woassignedto['USERNAME'] == selected_username]['WOID']
        unique_woid = wo_woid.unique()
        sorted_woid = sorted(unique_woid)
        wo_woid_options = list(sorted_woid)
        disable_search_button = False
    else:
        wo_woid_options = []
        disable_search_button = True


    # Calcola la data di oggi meno 7 giorni
    previus_7days = datetime.datetime.now() - datetime.timedelta(days=7)
    selected_from_date = st.sidebar.date_input(":blue[From date]", value=previus_7days, key="di_datefrom", format="DD/MM/YYYY", disabled=False)
    selected_to_date = st.sidebar.date_input(":blue[To date]", value="today", key="di_dateto", format="DD/MM/YYYY", disabled=False)
    filtered_workitems = st.session_state.df_workitems[st.session_state.df_workitems["USERID"]==selected_usercode]
    search_button = st.sidebar.button("Search", key="search_button", type="primary", use_container_width=True, on_click=None, disabled=disable_search_button)
    if search_button:
        st.dataframe(data=st.session_state.df_workitems, use_container_width=True, hide_index=True)
        #st.dataframe(data=None, width=None, height=None, *, use_container_width=False, hide_index=None, column_order=None, column_config=None, key=None, on_select="ignore", selection_mode="multi-row")

        