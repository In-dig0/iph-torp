import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
# Internal app module
import servant

def insert_workitems(conn):

    def reset_form():
        st.session_state.reset_pending = True
        st.rerun()

    if 'reset_pending' not in st.session_state:
        st.session_state.reset_pending = False 
    
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
        'df_tskgrl1': sqlite_db.load_tskgrl1_data, 
        'df_tskgrl2': sqlite_db.load_tskgrl2_data,
    }

    for key, loader in session_data.items():
        if key not in st.session_state:
            st.session_state[key] = loader(conn)

    st.write(f"Sessione state stamp:")
    st.write(st.session_state)

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
    selected_usercode = servant.get_code_from_name(st.session_state.df_users, selected_username, "CODE")
    

    if selected_username:
        st.session_state.selected_username = True
        disable_search_button = False
    else:
        disable_search_button = True


    # Calcola la data di oggi meno 7 giorni
    previus_7days = datetime.datetime.now() - datetime.timedelta(days=7)
    selected_from_date = st.sidebar.date_input(":blue[From date]", value=previus_7days, key="di_datefrom", format="DD/MM/YYYY", disabled=False)
    selected_to_date = st.sidebar.date_input(":blue[To date]", value="today", key="di_dateto", format="DD/MM/YYYY", disabled=False)

    search_button = st.sidebar.button("Search", key="search_button", type="primary", use_container_width=True, on_click=None, disabled=disable_search_button)
    if search_button:
        filtered_workitems = st.session_state.df_workitems[
            (st.session_state.df_workitems["USERID"] == selected_usercode) & 
            (st.session_state.df_workitems["DATE"] >= selected_from_date) & 
            (st.session_state.df_workitems["DATE"] <= selected_to_date)]

        st.subheader(f":orange[List of Work items]")
        with st.container(border=True, key="Workitem grid"):
            st.dataframe(data=filtered_workitems, use_container_width=True, hide_index=False)
        #st.dataframe(data=None, width=None, height=None, *, use_container_width=False, hide_index=None, column_order=None, column_config=None, key=None, on_select="ignore", selection_mode="multi-row")
        st.divider()
        st.subheader(f":orange[New Task]")
        with st.container(border=True, key="Insert Task"):
            
            #taskl1_options = st.session_state.df_tskgrl1["NAME"].tolist().sort()
            taskl1_options = st.session_state.df_tskgrl1["NAME"]

            st.write(taskl1_options)
            wi_task_l1 = st.selectbox(
                label=":blue[Task Group L1]", 
                options=taskl1_options, 
                index= None,
                key="sb_wi_taskl1"
             )
            if wi_task_l1:
                wi_task_l1_code = servant.get_code_from_name(st.session_state.df_tskgrl1, wi_task_l1, "CODE")
            else:
                wi_task_l1_code = None
            # st.write(wi_task_l1_code)            

            # # # Per Task Group L1
            # initial_task_l1 = None if st.session_state.reset_pending else st.session_state.get('sb_wi_taskl1')
            # wi_task_l1 = st.selectbox(
            #     label=":blue[Task Group L1]", 
            #     options=taskl1_options, 
            #     index=None if initial_task_l1 is None else taskl1_options.index(initial_task_l1) if initial_task_l1 in taskl1_options else None, 
            #     key="sb_wi_taskl1"
            # )
            # wi_task_l1_code = st.session_state.df_tskgrl1[st.session_state.df_tskgrl1["NAME"]==wi_task_l1]["CODE"].tolist() if wi_task_l1 else []
            # st.write(wi_task_l1_code)
            
            # # Per Task Group L2
            # taskl2_options = st.session_state.df_tskgrl2["NAME"].tolist()
            # initial_task_l2 = None if st.session_state.reset_pending else st.session_state.get('sb_wi_taskl2')
            # wi_task_l2 = st.selectbox(
            #     label=":blue[Task Group L2]", 
            #     options=taskl2_options, 
            #     index=None if initial_task_l2 is None else taskl2_options.index(initial_task_l2) if initial_task_l2 in taskl2_options else None, 
            #     key="sb_wi_taskl2"
            # )
            # wi_task_l2_code = st.session_state.df_tskgrl2[st.session_state.df_tskgrl2["NAME"]==wi_task_l2]["CODE"].tolist() if wi_task_l2 else []


        