# Python built-in libraries
import datetime
import os
import io
import time
import re
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List

# Local modules
import servant
import app_info
import app_signin
import sqlite_db
import insert_request
import view_request
import view_workitem
import insert_workitem
import manage_request
import manage_workorder
import dashboard
import test_calendar
import test_tile

# 3th party packages
import streamlit as st
import pandas as pd
import sqlitecloud
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode

# Global constants
APPNAME = "TORP" #IPH Technical Office Request POC (Proof Of Concept)
APPCODE = "TORP"
APPVERSION = "0.2"


def main():   

  st.set_page_config(layout="wide")
  # Login procedure
  login_procedure = False
  if login_procedure == True:
    if not app_signin.check_password():
      st.stop()
  else:
    # Open connection to SQLITE db
    conn = sqlite_db.open_sqlitecloud_db()
    if conn:
      # Load initial data
      with st.spinner(text="Loading data..."):
        sqlite_db.initialize_session_state(conn)
    else:
      st.error("Database connection failed!") 
      st.stop() 

 
  if "username" in st.session_state:
    current_username = st.session_state.df_users[st.session_state.df_users["EMAIL"] == st.session_state.username]["NAME"]
    st.title(f"Welcome :orange[{current_username.iloc[0]}]!")

  # Simulate a user login with R01 role (Requester)
  st.session_state["USER_ROLE"] = "R01"
  st.write(st.session_state["USER_ROLE"])
  
  # Add IPH logo to sidebar 
  st.sidebar.image("https://iph.it/wp-content/uploads/2020/02/logo-scritta.png", width=150)    
  
  # Functional menù
  sidebar_title = st.sidebar.header(f":blue[Function menù]")
  page_names_to_funcs = {
    "ℹ️ App Info": lambda: app_info.display_app_info(APPNAME, APPVERSION),
    "📄 Create Request": lambda: insert_request.insert_request(conn),    
    "🔍 View Request ": lambda: view_request.view_requests(conn),       
    "🗂️ Manage Request": lambda: manage_request.manage_request(conn),
    "📌 Manage Work Orders": lambda: manage_workorder.manage_workorder(conn),
    "🎯 Insert Workitem": lambda: insert_workitem.create_workitem(conn),
    "📅 View Workitem": lambda: view_workitem.view_workitems(conn),
    "📉 Dashboard": lambda: dashboard.dashboard(conn),
    "TEST Calendar": lambda: test_calendar.show_calendar(conn),
    "TEST Tile": lambda: test_tile.show_tile(conn)
    # "🔐 Close db": close_sqlitecloud_db,
}    
  demo_name = st.sidebar.selectbox(":orange[Choose a function]", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()
  st.sidebar.divider()
  
  if st.sidebar.button("Logout", type="primary", use_container_width=False):
    sqlite_db.close_sqlitecloud_db
    st.success(f"Logout successfully!")
    st.stop()
    return True

           
if __name__ == "__main__":
    main()