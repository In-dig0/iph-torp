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
import sqlite_db
import insert_request
import view_request
import view_workitem
import insert_workitem
import manage_request
import manage_workorder

# 3th party packages
import streamlit as st
import pandas as pd
import sqlitecloud
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode

# Global constants
APPNAME = "TORP" #IPH Technical Office Request POC (Proof Of Concept)
APPCODE = "TORP"
APPVERSION = "0.2"



#def main():
  # def display_welcome_popup(username:str)-> None:
    
  #   @st.dialog(title=f"Welcome {username}!")  
  #   def display_welcome_message():
  #     with st.spinner(text="Loading data..."):      
  #       if conn:
  #         sqlite_db.initialize_session_state(conn) #passo la connessione
  #         st.markdown(f"Ready to start? 🌞")
  #         return True
  #       #time.spleep(4)
  #   #st.write(f"Profile: Standard User")  
  #   return display_welcome_message()
  
  # st.set_page_config(layout="wide")  
  # if not servant.check_password():
  #   st.stop()
  # else:
  #   conn = sqlite_db.open_sqlitecloud_db()
  #   display_welcome_popup(st.session_state.username)

# def main():
#   # Define the dialog function *outside* any other function
#   @st.dialog(title=f"Welcome {st.session_state.get('username', 'User')}!")  # Use .get() to handle missing username
#   def display_welcome_message():
#       with st.spinner(text="Loading data..."):
#         sqlite_db.initialize_session_state(conn)
#         st.markdown(f"Ready to start? 🌞")
#       return True


#   st.set_page_config(layout="wide")
#   if not servant.check_password():
#       st.stop()
#   else:
#       conn = sqlite_db.open_sqlitecloud_db()  # Open connection *inside* the dialog
#       # No need to open the connection here anymore. It's handled in the dialog.
#       if conn:
#         if 'welcome_displayed' not in st.session_state or not st.session_state.welcome_displayed:  # Check if the dialog has been shown
#             if display_welcome_message():  # Call the dialog function directly
#                 st.session_state.welcome_displayed = True
#       else:
#         st.error("Database connection failed!") 
#         st.stop()       


# Define the dialog function *outside* any other function



# def main():
#   @st.dialog(title=f"Welcome {st.session_state.get('username', 'User')}!")
#   def display_welcome_message():
#       with st.spinner(text="Loading data..."):
#           try:  # Add a try-except block for better error handling
#               conn = sqlite_db.open_sqlitecloud_db()  # Open connection *inside* the dialog
#               if conn:
#                   sqlite_db.initialize_session_state(conn)
#                   st.markdown(f"Ready to start? 🌞")
#                   return True
#               else:
#                   st.error("Database connection failed!")
#                   return False
#           except Exception as e:  # Catch any potential errors during connection or initialization
#               st.exception(e)  # Display the full error details
#               return False

#   st.set_page_config(layout="wide")

#   if not servant.check_password():
#       st.stop()
#   else:
#       # Check BEFORE opening the connection if the dialog has already been shown
#       if 'welcome_displayed' not in st.session_state or not st.session_state.welcome_displayed:
#           if display_welcome_message():  # Call the dialog function directly
#               st.session_state.welcome_displayed = True
#               st.rerun()  # Force a rerun after the dialog is closed to avoid issues
#       else:  # Connection is only opened if the dialog has already been shown
#           conn = sqlite_db.open_sqlitecloud_db()
#           if not conn:  # Handle the case where the connection fails AFTER the welcome dialog
#               st.error("Database connection failed!")
#               st.stop()


def main():   

  st.set_page_config(layout="wide")
  conn = sqlite_db.open_sqlitecloud_db()
  if conn:
    with st.spinner(text="Loading data..."):
      sqlite_db.initialize_session_state(conn)
  else:
    st.error("Database connection failed!") 
    st.stop() 
  
  # Aggiungi l'immagine alla sidebar 
  st.sidebar.image("https://iph.it/wp-content/uploads/2020/02/logo-scritta.png", width=150)    
  
  page_names_to_funcs = {
    "ℹ️ App Info": lambda: app_info.display_app_info(APPNAME, APPVERSION),
    "📄 Create Request": lambda: insert_request.insert_request(conn),    
    "🔍 View Request ": lambda: view_request.view_requests(conn),       
    "🗂️ Manage Request": lambda: manage_request.manage_request(conn),
    "📌 Manage Work Orders": lambda: manage_workorder.manage_workorder(conn),
    "🎯 Insert Workitem": lambda: insert_workitem.create_workitem(conn),
    "📅 View Workitem": lambda: view_workitem.view_workitems(conn)
    # "🔐 Close db": close_sqlitecloud_db,
}    
  st.sidebar.divider()
  sidebar_title = st.sidebar.header(f":blue[Function menù]")
  demo_name = st.sidebar.selectbox(":orange[Choose a function]", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()

           
if __name__ == "__main__":
    main()