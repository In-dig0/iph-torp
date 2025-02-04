# Python built-in libraries
import datetime
import os
import io
import time
import re
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List

# Local modules
import app_info
import sqlite_db
import insert_request
import view_request
import view_workitem
import insert_workitem
import manage_request

# 3th party packages
import streamlit as st
import pandas as pd
import sqlitecloud
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode

# Global constants
APPNAME = "TORP" #IPH Technical Office Request POC (Proof Of Concept)
APPCODE = "TORP"
APPVERSION = "0.1"

def main():

  st.set_page_config(layout="wide")  
  conn = sqlite_db.open_sqlitecloud_db()

  # Aggiungi l'immagine alla sidebar 
  st.sidebar.image("https://iph.it/wp-content/uploads/2020/02/logo-scritta.png", width=150)    
  


  page_names_to_funcs = {
    "ℹ️ App Info": lambda: app_info.display_app_info(APPNAME, APPVERSION),
    #"Connect Database": lambda: sqlite_db.open_sqlitecloud_db()
    "📄 Create Request": lambda: insert_request.insert_request(conn),    
    "🔍 View Request ": lambda: view_request.view_requests(conn),       
    "🗂️ Manage Request": lambda: manage_request.manage_request(conn),
    # "📌 Manage Work Orders": manage_wo,
    "🎯 Insert Workitem": lambda: insert_workitem.create_workitem(conn),
    "📅 View Workitem": lambda: view_workitem.view_workitems(conn)
    # "🔐 Close db": close_sqlitecloud_db,
    # "--> TEST": my_test
}    
  st.sidebar.divider()
  sidebar_title = st.sidebar.header(f":blue[Function menù]")
  demo_name = st.sidebar.selectbox("Choose a function", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()

           
if __name__ == "__main__":
    main()