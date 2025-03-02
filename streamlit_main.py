# Python built-in libraries
import datetime
import os
import io
import time
import json
import re
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List
import numpy as np

# 3th party packages
import streamlit as st
import pandas as pd
import sqlitecloud
import pytz 
import hmac
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode
import numpy as np


# Global constants
APPNAME = "TORP" #IPH Technical Office Request POC (Proof Of Concept)
APPCODE = "TORP"
APPVERSION = "0.2"
ACTIVE_STATUS = "ACTIVE"
DISABLED_STATUS = "DISABLED"
DEFAULT_DEPT_CODE = "DTD"
REQ_STATUS_OPTIONS = ['NEW', 'PENDING', 'ASSIGNED', 'WIP', 'COMPLETED', 'DELETED']

#######################################################################################################
def open_sqlitecloud_db():
    db_link = ""
    db_apikey = ""
    db_name = ""
    # Get database information
    try:
        #Search DB credentials using ST.SECRETS
        db_link = st.secrets["db_credentials"]["SQLITECLOUD_DBLINK"]
        db_apikey = st.secrets["db_credentials"]["SQLITECLOUD_APIKEY"]
        db_name = st.secrets["db_credentials"]["SQLITECLOUD_DBNAME"]
    except Exception as errMsg:
        st.error(f"**ERROR: DB credentials NOT FOUND: \n{errMsg}", icon="🚨")
        rc = 1
        
    conn_string = "".join([db_link, db_apikey])
    global conn
    # Connect to SQLite Cloud platform
    try:
        conn = sqlitecloud.connect(conn_string)
        # st.success(f"Connected to {db_name} database!")
    except Exception as errMsg:
        st.error(f"**ERROR connecting to database: \n{errMsg}", icon="🚨")
    
    # Open SQLite database
    conn.execute(f"USE DATABASE {db_name}")
    global cursor
    cursor = conn.cursor()

#######################################################################################################
def close_sqlitecloud_db():
    with st.container(border=True):
        try:
            if cursor:
                cursor.close()    
            if conn:
                conn.close() 
        except Exception as errMsg:
            st.error(f"**ERROR closing database connection: \n{errMsg}", icon="🚨")
        else:
            st.success(f"Database closed successfully!")   
            
#######################################################################################################
def display_app_info() -> None:
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
    
#######################################################################################################
def load_initial_data() -> None:
    """Load initial data from database"""
    global df_depts
    global df_users
    global df_pline
    global df_pfamily
    global df_type
    global df_category
    global df_detail
    global df_lk_category_detail
    global df_lk_pline_tdtl
    global df_taskl1


    df_depts = pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME, 
            A.mngrcode AS MNGR_CODE, 
            A.rprofcode AS REQPROF_CODE 
        FROM TORP_DEPARTMENTS AS A
        ORDER by name
        """, conn)

    df_users = pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME, 
            A.deptcode AS DEPTCODE, 
            B.name AS DEPTNAME
        FROM TORP_USERS A
        INNER JOIN TORP_DEPARTMENTS B ON B.code = A.deptcode
        ORDER by A.name
        """, conn)

    df_pline = pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME
        FROM TORP_PLINE A
        ORDER by A.name
        """, conn)

    df_pfamily = pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME, 
            A.pcode AS PLINE_CODE
        FROM TORP_PFAMILY A
        ORDER by A.name
        """, conn)

    df_type = pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME
        FROM TORP_TYPE A
        ORDER by A.name
        """, conn)

    df_category = pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME
        FROM TORP_CATEGORY A
        ORDER by A.name
        """, conn)

    df_detail = pd.read_sql_query("""
        SELECT 
            A.code AS CODE,                                    
            A.name AS NAME
        FROM TORP_DETAIL A
        ORDER by A.name
        """, conn)

    df_lk_type_category = pd.read_sql_query("""
        SELECT 
            A.typecode AS TYPE_CODE, 
            A.categorycode AS CATEGORY_CODE
        FROM TORP_LINK_TYPE_CATEGORY A
        ORDER by A.typecode 
        """, conn)

    df_lk_category_detail = pd.read_sql_query("""
        SELECT 
            A.categorycode AS CATEGORY_CODE, 
            A.detailcode AS DETAIL_CODE
        FROM TORP_LINK_CATEGORY_DETAIL A
        ORDER by A.categorycode 
        """, conn)

    df_lk_pline_tdtl = pd.read_sql_query("""
        SELECT 
            A.plinecode AS PLINE_CODE, 
            A.usercode AS USER_CODE,
            B.name AS USER_NAME
        FROM TORP_LINK_PLINE_TDTL A
        INNER JOIN TORP_USERS B ON B.code = A.usercode
        ORDER by A.plinecode 
        """, conn)


#######################################################################################################
def load_requests_data():
    """ Load requests from database to df """
    
    global df_requests
    global df_reqassignedto
    
    df_requests = pd.read_sql_query("""
    SELECT 
        A.reqid AS REQID, 
        A.status AS STATUS, 
        A.insdate AS INSDATE, 
        A.dept AS DEPT, 
        A.requester AS REQUESTER, 
        A.user AS USER, 
        A.priority AS PRIORITY, 
        A.pline AS PR_LINE, 
        A.pfamily AS PR_FAMILY, 
        A.type AS TYPE, 
        A.category AS CATEGORY, 
        A.detail AS DETAIL, 
        A.title AS TITLE, 
        A.description AS DESCRIPTION, 
        A.note_td AS NOTE_TD, 
        A.woid AS WOID  
    FROM TORP_REQUESTS A
    ORDER by REQID desc
    """, conn)

    df_reqassignedto = pd.read_sql_query("""
    SELECT 
        A.userid AS USERID, 
        A.reqid AS REQID,
        A.status AS STATUS,
        B.name AS USERNAME 
    FROM TORP_REQASSIGNEDTO A
    INNER JOIN TORP_USERS B ON B.code = A.userid
    WHERE A.status = 'ACTIVE'
    ORDER BY USERID desc
    """, conn)


#######################################################################################################
def load_workorders_data():
    """ Load TORP_WORKORDERS records into df """
    
    # global df_workorders
    
    df_workorders = pd.read_sql_query("""
    SELECT 
        A.woid AS WOID,
        A.tdtlid AS TDTLID, 
        A.type AS TYPE, 
        A.status AS STATUS,        
        A.title AS TITLE,
        A.description AS DESCRIPTION,
        A.time_qty AS TIME_QTY,
        A.time_um AS TIME_UM,                                                                
        A.startdate AS STARTDATE, 
        A.enddate AS ENDDATE,                                       
        A.reqid AS REQID
    FROM TORP_WORKORDERS A
    ORDER BY REQID
    """, conn)
    
    return df_workorders

def load_woassignedto_data():
    """ Load TORP_WOASSIGNEDTO records into df """
    
#    global df_woassignedto
    
    df_woassignedto = pd.read_sql_query("""
    SELECT 
        A.userid AS USERID, 
        A.woid AS WOID, 
        A.status AS STATUS, 
        B.name AS USERNAME 
    FROM TORP_WOASSIGNEDTO A
    INNER JOIN TORP_USERS B ON B.code = A.userid    
    WHERE A.status = 'ACTIVE'
    ORDER BY WOID
    """, conn)    

    return df_woassignedto

def load_tskgrl1_data():
    
    df_tskgrl1 = pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME
        FROM TORP_TASKGRP_L1 AS A
        ORDER by name
        """, conn)
    
    return df_tskgrl1

def load_tskgrl2_data():
    
    df_tskgrl2 = pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME,
            A.pcode AS PCODE
        FROM TORP_TASKGRP_L2 AS A
        ORDER by name
        """, conn)

    return df_tskgrl2

# def load_workorders_data():
#     """ Load work orders from database to df """
    
#     global df_workorders
#     global df_woassignedto
    
#     df_workorders = pd.read_sql_query("""
#     SELECT 
#         A.woid AS WOID,
#         A.tdtlid AS TDTLID, 
#         A.type AS TYPE, 
#         A.status AS STATUS,        
#         A.title AS TITLE,
#         A.description AS DESCRIPTION,
#         A.time_qty AS TIME_QTY,
#         A.time_um AS TIME_UM,                                                                
#         A.startdate AS STARTDATE, 
#         A.enddate AS ENDDATE,                                       
#         A.reqid AS REQID
#     FROM TORP_WORKORDERS A
#     ORDER BY REQID
#     """, conn)

#     df_woassignedto = pd.read_sql_query("""
#     SELECT 
#         A.userid AS USERID, 
#         A.woid AS WOID, 
#         A.status AS STATUS, 
#         B.name AS USERNAME 
#     FROM TORP_WOASSIGNEDTO A
#     INNER JOIN TORP_USERS B ON B.code = A.userid    
#     WHERE A.status = 'ACTIVE'
#     ORDER BY WOID
#     """, conn)

#######################################################################################################
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


#######################################################################################################
def get_next_object_id(obj_class: str, obj_year: str, obj_pline="") -> str:
    """Get next available row ID"""

    ZERO_PADDING_NR = 4
    SEP_CHAR = '-'

    try:
        cursor.execute('SELECT prefix AS PREFIX, prog AS PROG FROM TORP_OBJNUMERATOR WHERE obj_class=? and obj_year=? and obj_pline=?', (obj_class, obj_year, obj_pline))
        results = cursor.fetchone()
        if results:
            prefix = results[0]
            next_prog = int(results[1]) + 1
            next_rowid = prefix + obj_year[2:4] + SEP_CHAR + str(next_prog).zfill(ZERO_PADDING_NR)
            cursor.execute(
                "UPDATE TORP_OBJNUMERATOR SET prog = ? WHERE obj_class=? and obj_year=? and obj_pline=?",
                (next_prog, obj_class, obj_year, obj_pline)
            )               
        else:        
            prefix = obj_class[0]
            next_prog = 1
            next_rowid = prefix + obj_year[2:4] + SEP_CHAR + str(next_prog).zfill(ZERO_PADDING_NR)
            cursor.execute(
                "INSERT INTO TORP_OBJNUMERATOR (obj_class, obj_year, obj_pline, prefix, prog) VALUES (?, ?, ?, ?, ?)",
                (obj_class, obj_year, obj_pline, prefix, next_prog)
            )

        conn.commit()                        
    except Exception as errMsg:
        st.error(f"**ERROR impossbile to get the next rowid from table TORP_OBJNUMERATOR: {errMsg}")
        conn.rollback()
        return ""
    return next_rowid

#######################################################################################################
def get_code_from_name(df, name, code_column):
    result = df[df["NAME"] == name][code_column]
    return list(result)[0] if not result.empty else ""

def get_description_from_code(df, code, description_column):
    result = df[df["CODE"] == code][description_column]
    return list(result)[0] if not result.empty else ""

#######################################################################################################
def insert_request() -> None:
    """Main function to handle request insertion"""
    @dataclass
    class RequestData:
        """Class to store request data with type hints"""
        insdate: str
        user: str
        status: str
        dept: str
        requester: str
        priority: str
        pline: str
        pfamily: str
        type: str
        category: str
        detail: str
        title: str
        description: str
        tdtl: list[str]

    class RequestManager:
        """Class to handle request management operations"""
    
        def __init__(self, conn, cursor):
            self.conn = conn
            self.cursor = cursor
            self.load_initial_data()

        def load_initial_data(self) -> None:
            """Load initial data from database"""
            self.df_depts = pd.read_sql_query(
                "SELECT code AS CODE, name AS NAME, mngrcode AS MNGR_CODE, rprofcode AS REQPROF_CODE FROM TORP_DEPARTMENTS ORDER by name", 
                self.conn
            )
            self.df_depts["DEPT_KEY"] = self.df_depts["NAME"]

            self.df_users = pd.read_sql_query("""
                SELECT A.code AS CODE, A.name AS NAME, A.deptcode AS DEPTCODE, B.name AS DEPTNAME
                FROM TORP_USERS A
                INNER JOIN TORP_DEPARTMENTS B ON B.code = A.deptcode
                ORDER by A.name
            """, self.conn)

            self.df_pline = pd.read_sql_query("""
                SELECT A.code AS CODE, A.name AS NAME
                FROM TORP_PLINE A
                ORDER by A.name
            """, self.conn)

            self.df_pfamily = pd.read_sql_query("""
                SELECT A.code AS CODE, A.name AS NAME, A.pcode AS PLINE_CODE
                FROM TORP_PFAMILY A
                ORDER by A.name
            """, self.conn)

            self.df_type = pd.read_sql_query("""
                SELECT A.code AS CODE, A.name AS NAME
                FROM TORP_TYPE A
                ORDER by A.name
            """, self.conn)

            self.df_category= pd.read_sql_query("""
                SELECT A.code AS CODE, A.name AS NAME
                FROM TORP_CATEGORY A
                ORDER by A.name
            """, self.conn)

            self.df_detail= pd.read_sql_query("""
                SELECT A.code AS CODE, A.name AS NAME
                FROM TORP_DETAIL A
                ORDER by A.name
            """, self.conn)

            self.df_lk_type_category= pd.read_sql_query("""
                SELECT A.typecode AS TYPE_CODE, A.categorycode AS CATEGORY_CODE
                FROM TORP_LINK_TYPE_CATEGORY A
                ORDER by A.typecode 
            """, self.conn)

            self.df_lk_category_detail= pd.read_sql_query("""
                SELECT A.categorycode AS CATEGORY_CODE, A.detailcode AS DETAIL_CODE
                FROM TORP_LINK_CATEGORY_DETAIL A
                ORDER by A.categorycode 
            """, self.conn)

            self.df_lk_pline_tdtl= pd.read_sql_query("""
                SELECT A.plinecode AS PLINE_CODE, A.usercode AS USER_CODE
                FROM TORP_LINK_PLINE_TDTL A
                ORDER by A.plinecode 
            """, self.conn)

        def save_request(self, request: RequestData) -> Tuple[str, int]:
            """Save request to database and return request number and status"""

            try:

                #next_rownr = self._get_next_row_id()
                next_reqid = get_next_object_id("REQ", request.insdate[0:4])
                sql = """
                    INSERT INTO TORP_REQUESTS (
                        reqid, status, insdate, dept, requester, user, 
                        priority, pline, pfamily, type, category, detail,
                        title, description, note_td, woid
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    next_reqid, request.status, request.insdate, request.dept,
                    request.requester, request.user, request.priority, 
                    request.pline, request.pfamily, request.type, request.category,
                    request.detail, request.title, request.description, None, 0 
                )
                
                self.cursor.execute(sql, values)
                self.conn.commit()
                
            except Exception as e:
                st.error(f"**ERROR inserting request in TORP_REQUESTS: \n{e}", icon="🚨")
                return "", False

            try:               
                sql = """
                    INSERT INTO TORP_REQASSIGNEDTO (
                        userid, reqid, status
                    ) VALUES (?, ?, ?)
                """
                values = (
                    request.tdtl[0], next_reqid, ACTIVE_STATUS

                )
                
                self.cursor.execute(sql, values)
                self.conn.commit()
                          
            except Exception as e:
                st.error(f"**ERROR inserting request in TORP_REQASSIGNEDTO: \n{e}", icon="🚨")
                return "", False

            #return f"R{str(next_rownr).zfill(4)}", 0
            return next_reqid, True 

        def _get_next_row_id(self) -> int:
            """Get next available row ID"""
            self.cursor.execute('SELECT MAX(idrow) FROM TORP_REQUESTS')
            max_idrow = self.cursor.fetchone()[0]
            return (max_idrow + 1) if max_idrow is not None else 1
        
   
        
    # Inizializzazione delle chiavi di stato per i widget
    FORM_KEYS = [
        'sb_dept', 'sb_requester', 'sb_pline', 'sb_pfamily',
        'sb_type', 'sb_category', 'sb_detail',
        'ti_title', 'ti_description'
    ]
    
    # Inizializzazione dello stato del form
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    
    if 'reset_form' not in st.session_state:
        st.session_state.reset_form = False
        
    # Inizializzazione delle chiavi del form se non esistono
    for key in FORM_KEYS:
        if key not in st.session_state:
            st.session_state[key] = None if key.startswith('sb_') else ""

    request_manager = RequestManager(conn, cursor)  # conn e cursor devono essere definiti globalmente
    

    def display_request_popup(req_nr: str, request: dict) -> None:
        """Display confirmation popup after request submission"""
        
        @st.dialog(title=f"Request {req_nr} submitted!")  
        def create_pop_form():
            """Form with widgets to collect user information"""
            st.markdown(
                """
                <style>
                div[data-testid="stTextInput"] > div > div > input:not([disabled]) {
                    color: #28a745;
                    border: 2px solid #28a745;
                    -webkit-text-fill-color: #28a745 !important;
                    font-weight: bold;
                }
                div[data-testid="stTextInput"] > div > div > input[disabled] {
                    color: #6c757d !important;
                    opacity: 1 !important;
                    -webkit-text-fill-color: #6c757d !important;
                    background-color: #e9ecef !important;
                    border: 1px solid #ced4da !important;
                    font-style: italic;
                }
                .stSelectbox > div > div > div > div {
                    color: #28a745;
                }
                .stMultiSelect > div > div > div > div {
                    color: #28a745 !important;
                }
                .stMultiSelect div[role="option"] {
                    color: #28a745 !important;
                }
                .stMultiSelect div[role="option"] > div > div {
                    color: #28a745 !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )          
               
            requester_code = request["Req_requester"]
            requester_name = get_description_from_code(df_users, requester_code, "NAME")
            st.text_input(label=":blue[Requester]", value=requester_name, disabled=True)
            st.text_input(label=":blue[Request title]", value=request["Req_title"], disabled=True)
            st.text_area(label=":blue[Request description]", value=request["Req_description"], disabled=True)
            
            req_status_options = ['NEW', 'PENDING', 'ASSIGNED', 'WIP', 'COMPLETED', 'DELETED']
            idx_status = req_status_options.index(request["Req_status"])
            st.selectbox(label=":blue[Request status]", options=req_status_options, disabled=True, index=idx_status)

            #df = request_manager.df_users
            # La lista di codici che vuoi convertire in descrizioni.
            tdtl_codes = request["Req_tdtl"]
            # Richiama la funzione per ogni codice nella lista.
            tdtl_descriptions = [get_description_from_code(df_users, code, "NAME") for code in tdtl_codes]
            st.multiselect(label=":blue[Tech Department Team Leader]", options=tdtl_descriptions, default=tdtl_descriptions, key="sb_tdtl", disabled=True)

            if st.button("Close"):
                st.session_state.reset_form = True
                time.sleep(0.1)  # Piccola pausa per assicurare il corretto aggiornamento dello stato
                st.rerun()

        return create_pop_form()

    def reset_form_state():
        """Reset all form fields to their initial state"""
        for key in FORM_KEYS:
            if key.startswith('sb_'):
                st.session_state[key] = None
            else:
                st.session_state[key] = ""

    def create_selectbox(label, options, key, default_index=None):
        return st.selectbox(label, options, index=default_index, key=key)

    def get_code_from_name(df, name, code_column):
        result = df[df["NAME"] == name][code_column]
        return list(result)[0] if not result.empty else ""

    def get_description_from_code(df, code, description_column):
        result = df[df["CODE"] == code][description_column]
        return list(result)[0] if not result.empty else ""

    def create_form() -> RequestData:
        """Create and handle the request form"""
 
        # REQUESTER INFO SECTION
        st.header(":orange[Requester informations]")
        
        # 'Department' selection
        department = None
        department = create_selectbox(":blue[Department(:red[*])]", request_manager.df_depts['NAME'].tolist(), "sb_dept")
        dept_code = get_code_from_name(request_manager.df_depts, department, "CODE")
 
        # 'Requester' selection
        requester = None
        if department:
            filtered_users = request_manager.df_users[request_manager.df_users["DEPTNAME"] == department]
        else:
            filtered_users = request_manager.df_users
        requester_option = filtered_users["NAME"].tolist()
        requester = create_selectbox(":blue[Requester(:red[*])]", requester_option, "sb_requester")
        requester_code = get_code_from_name(request_manager.df_users, requester, "CODE")
        
        st.header(":orange[Product group informations]")
        
        # 'Product line' selection
        pline = None
        pline = create_selectbox(":blue[Product line(:red[*])]", request_manager.df_pline['NAME'].tolist(), "sb_pline")
        pline_code = get_code_from_name(request_manager.df_pline, pline, "CODE")

        # 'Product family' selection
        pfamily = None
        if pline:
            filtered_pfamily = request_manager.df_pfamily[request_manager.df_pfamily["PLINE_CODE"] == pline_code]
        else:
            filtered_pfamily = request_manager.df_pfamily
        pfamily_option = filtered_pfamily["NAME"].tolist()
        pfamily = create_selectbox(":blue[Product family(:red[*])]", pfamily_option, "sb_pfamily")
        pfamily_code = get_code_from_name(request_manager.df_pfamily, pfamily, "CODE")

        # REQUEST INFO SECTION
        st.header(":orange[Request informations]")
        
        # 'Priority' selection
        priority = create_selectbox(":blue[Request priorty(:red[*])]", ["High", "Medium", "Low"], "sb_priority", 1)    

        # 'Type' selection
        reqtype = None
        reqtype = create_selectbox(":blue[Request type(:red[*])]", request_manager.df_type['NAME'].tolist(), "sb_type")
        reqtype_code = get_code_from_name(request_manager.df_type, reqtype, "CODE")

        # 'Category' selection
        reqcategory = None       
        # Filtro sul DataFrame delle categorie ammesse
        category_filter = request_manager.df_lk_type_category[request_manager.df_lk_type_category["TYPE_CODE"] == reqtype_code]
        # Applicazione del filtro basato sui codici di categoria
        filtered_reqcategory = request_manager.df_category[request_manager.df_category["CODE"].isin(category_filter["CATEGORY_CODE"])]
        # Creazione della lista di opzioni per le categorie
        reqcategory_option = filtered_reqcategory["NAME"].tolist()
        reqcategory = create_selectbox(":blue[Request category(:red[*])]", reqcategory_option, "sb_category")
        reqcategory_code = get_code_from_name(request_manager.df_category, reqcategory, "CODE")

        # 'Detail' selection
        detail = None    
        # Filtro sul DataFrame delle categorie ammesse
        detail_filter = request_manager.df_lk_category_detail[request_manager.df_lk_category_detail["CATEGORY_CODE"] == reqcategory_code]
        # Applicazione del filtro basato sui codici di categoria
        filtered_detail = request_manager.df_detail[request_manager.df_detail["CODE"].isin(detail_filter["DETAIL_CODE"])]
        # Creazione della lista di opzioni per le categorie
        detail_option = filtered_detail["NAME"].tolist()
        detail = create_selectbox(":blue[Request detail(:red[*])]", detail_option, "sb_detail")
        detail_code = get_code_from_name(request_manager.df_detail, detail, "CODE")

        # 'Title' selection
        title = None
        title = st.text_input(":blue[Request title(:red[*])]", key="ti_title")

        # 'Description' selection        
        description = None
        description = st.text_area(":blue[Request description]", key="ti_description")

        # 'TD Team Leader' selection (hidden)
        tdtl = None       
        # Filtro sul DataFrame delle linee ammesse
        tdtl_filter = request_manager.df_lk_pline_tdtl[request_manager.df_lk_pline_tdtl["PLINE_CODE"] == pline_code]
        # Applicazione del filtro basato sui codici di utenti
        tdtl_option = request_manager.df_users[request_manager.df_users["CODE"].isin(tdtl_filter["USER_CODE"])]
        # Creazione della lista di opzioni per il multiselect
        tdtl_code_list = tdtl_option["CODE"].tolist()        
        tdtl_name_list = tdtl_option["NAME"].tolist()
        #st.multiselect(label=":blue[TD Team Leader]", options=tdtl_name_list, default=tdtl_name_list, key="sb_tdtl2", disabled=True)
       
        return RequestData(
            insdate=datetime.datetime.now().strftime("%Y-%m-%d"),
            user="RB",
            status="NEW",
            dept=dept_code,
            requester=requester_code,
            priority=priority,
            pline=pline_code,
            pfamily=pfamily_code,
            type=reqtype_code,
            category=reqcategory_code,
            detail=detail_code,            
            title=title,
            description=description,
            tdtl=tdtl_code_list

        )

    # Reset del form se necessario
    if st.session_state.reset_form:
        reset_form_state()
        st.session_state.reset_form = False
        st.rerun()

    # Main form handling
    request_data = create_form()
    st.divider()
    

    save_botton_disabled = not all([
        request_data.dept, request_data.requester, request_data.pline,
        request_data.pfamily, request_data.type, request_data.category,
        request_data.detail, request_data.title
    ])
    
    if st.button("Submit", type="primary", disabled=save_botton_disabled):
        req_nr, rc = request_manager.save_request(request_data)
        if rc == True:
            st.session_state.form_submitted = True
            display_request_popup(req_nr, {
                "Req_requester": request_data.requester,
                "Req_title": request_data.title,
                "Req_description": request_data.description,
                "Req_status": request_data.status,
                "Req_tdtl": request_data.tdtl
            })


#######################################################################################################
def view_request():
    # Inzialise variables
    rc = 0
    req_nr = ""

    # Aggiungere all'inizio della funzione assign_request(), dopo le altre inizializzazioni
    if "grid_refresh" not in st.session_state:
        st.session_state.grid_refresh = False
    
    load_requests_data()
    df_requests_grid = pd.DataFrame()
    df_requests_grid['REQID'] = df_requests['REQID']
    df_requests_grid['STATUS'] = df_requests['STATUS']
    df_requests_grid['INSDATE'] = df_requests['INSDATE']
#    df_requests_grid['DEPTNAME'] = df_requests['DEPT'].apply(lambda dept_code: get_description_from_code(df_depts, dept_code, "NAME"))
    df_requests_grid['PRIORITY'] = df_requests['PRIORITY']
    df_requests_grid['PRLINE_NAME'] = df_requests['PR_LINE'].apply(lambda pline_code: get_description_from_code(df_pline, pline_code, "NAME"))
    df_requests_grid['TITLE'] = df_requests['TITLE']
    df_requests_grid['REQUESTER_NAME'] = df_requests['REQUESTER'].apply(lambda requester_code: get_description_from_code(df_users, requester_code, "NAME"))

    if st.session_state.grid_refresh:
        st.session_state.grid_data = df_requests_grid.copy()
        st.session_state.grid_refresh = False    

    cellStyle = JsCode("""
        function(params) {
            if (params.column.colId === 'REQID') {
                       return {
                        'backgroundColor': '#8ebfde',
                        'color': '#111810',
                        'fontWeight': 'bold'
                    };
            }
            return null;
        }
        """)

    grid_builder = GridOptionsBuilder.from_dataframe(df_requests_grid)
    # makes columns resizable, sortable and filterable by default
    grid_builder.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
        enableRowGroup=False
    )
    # Enalble pagination
    grid_builder.configure_pagination(paginationAutoPageSize=False, paginationPageSize=12)
#    gb.configure_selection('single', use_checkbox=True)
    grid_builder.configure_grid_options(domLayout='normal')
#    grid_builder.configure_pagination(enabled=True, paginationPageSize=5, paginationAutoPageSize=True)
#    grid_builder.configure_selection(selection_mode="multiple", use_checkbox=True)
#    grid_builder.configure_side_bar(filters_panel=True)# defaultToolPanel='filters')    
    
    # grid_builder.configure_column(
    # field="INSDATE",
    # header_name="INSERT DATE",
    # valueFormatter="value != undefined ? new Date(value).toLocaleString('it-IT', {dateStyle:'short'}): ''",
    # )
    grid_builder.configure_column("REQID", cellStyle=cellStyle)   
    grid_builder.configure_selection(
    selection_mode='single',     # Enable multiple row selection
    use_checkbox=True,             # Show checkboxes for selection
    header_checkbox=True
    )
    grid_options = grid_builder.build()
    # List of available themes
    available_themes = ["streamlit", "alpine", "balham", "material"]
    
    # Inizializzazione della sessione
    if "grid_data" not in st.session_state:
        st.session_state.grid_data = df_requests_grid.copy()  # Copia per evitare modifiche al DataFrame originale
    if "grid_response" not in st.session_state:
        st.session_state.grid_response = None

    # Sidebar controls - Filters
    st.sidebar.header("Filters")
    # Creation of a filter REQUESTERNAME
    ct_requester = df_requests_grid['REQUESTER_NAME'].drop_duplicates().sort_values()
    df_requestername = df_users[df_users["CODE"].isin(ct_requester)]
    option_requestername = df_requestername['NAME'].sort_values()
    
    
    option_requestername_list = ct_requester.tolist()

    # Get an optional value requester filter
    requestername_filter = st.sidebar.selectbox("Select a Requester Name:", option_requestername_list, index=None)
    #requester_filter_code = get_code_from_name(df_users, requester_filter, "CODE")
    

    # Filtro e AGGIORNAMENTO DEI DATI (utilizzando la sessione)
    if requestername_filter:
        st.session_state.grid_data = df_requests_grid.loc[df_requests_grid["REQUESTER_NAME"] == requestername_filter].copy()
    else:
        st.session_state.grid_data = df_requests_grid.copy() # Mostra tutti i dati se il filtro è None

    st.subheader("Request list:") 
    # Creazione/Aggiornamento della griglia (UNA SOLA VOLTA per ciclo di esecuzione)
    if st.session_state.grid_response is None:
        st.session_state.grid_response = AgGrid(
            st.session_state.grid_data,
            gridOptions=grid_options,
            allow_unsafe_jscode=True,
            theme=available_themes[2],
            fit_columns_on_grid_load=False,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            data_return_mode=DataReturnMode.AS_INPUT,
            key="main_grid"
        )
    else:
        st.session_state.grid_response = AgGrid( # Aggiorna la griglia esistente
            st.session_state.grid_data,
            gridOptions=grid_options,
            allow_unsafe_jscode=True,
            theme=available_themes[2],
            fit_columns_on_grid_load=False,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            data_return_mode=DataReturnMode.AS_INPUT,
            key="main_grid"
        )

    selected_row = st.session_state.grid_response['selected_rows']

    if selected_row is not None and len(selected_row) > 0:
        reqid = selected_row['REQID'][0]
        insdate = selected_row['INSDATE'][0]
        status = selected_row['STATUS'][0]
        requester_name = selected_row['REQUESTER_NAME'][0]
        pline_name = selected_row['PRLINE_NAME'][0]

        dept_code = df_requests[df_requests["REQID"] == reqid]["DEPT"].values[0]
        dept_name = get_description_from_code(df_depts, dept_code, "NAME")

        family_code = df_requests[df_requests["REQID"] == reqid]["PR_FAMILY"].values[0]
        family_name = get_description_from_code(df_pfamily, family_code, "NAME")

        type_code = df_requests[df_requests["REQID"] == reqid]["TYPE"].values[0]
        type_name = get_description_from_code(df_type, type_code, "NAME")
        
        category_code = df_requests[df_requests["REQID"] == reqid]["CATEGORY"].values[0]
        category_name = get_description_from_code(df_category, category_code, "NAME")

        detail_code = df_requests[df_requests["REQID"] == reqid]["DETAIL"].values[0]
        detail_name = get_description_from_code(df_detail, detail_code, "NAME")

        title = selected_row['TITLE'][0]
        description = df_requests[df_requests["REQID"] == reqid]["DESCRIPTION"].values[0]
        note_td = df_requests[df_requests["REQID"] == reqid]["NOTE_TD"].values[0]

        tdtl_code_list = df_reqassignedto[df_reqassignedto["REQID"] == reqid]["USERID"]
        #tdtl_name_list = get_description_from_code(df_users, tdtl_code_list, "NAME")
        tdtl_name_list = [get_description_from_code(df_users, code, "NAME") for code in tdtl_code_list]
        tdtl_name_string = "-".join(tdtl_name_list)

        # Dati aggiornati
        data_out = {
            "Column name": [
                "Request Id", "Insert date", "Status", "Department", "Requester", 
                "Product line", "Product family", "Type", "Category", "Detail", 
                "Title", "Description", "Tech Department Note", "Tech Department Team Leader"],
            "Column value": [
                reqid, insdate, status, dept_name, requester_name, pline_name, 
                family_name, type_name, category_name, detail_name, title, 
                description, note_td, tdtl_name_string]
        }
        df_out = pd.DataFrame(data_out)

        # Formattazione Request Id in grassetto
        df_out.loc[df_out["Column name"] == "Request Id", "Column value"] = df_out.loc[
            df_out["Column name"] == "Request Id", "Column value"].apply(lambda x: f"<b>{x}</b>")

        # Formattazione Status in verde
        df_out.loc[df_out["Column name"] == "Status", "Column value"] = df_out.loc[
            df_out["Column name"] == "Status", "Column value"].apply(lambda x: f"<span style='color: green;'>{x}</span>")

        # Convertiamo il DataFrame in HTML con testo allineato a sinistra e senza id riga
        html_table = df_out.to_html(escape=False, index=False, classes='mystyle')
        table_width = 900  # Adjust this width value as needed
        # Convertiamo il DataFrame in HTML con testo allineato a sinistra e senza id riga
        html_table = df_out.to_html(escape=False, index=False, table_id='styled-table')

        # # CSS per lo stile della tabella
        # st.markdown("""
        #     <style>
        #         #styled-table {
        #             width: 100%;
        #             text-align: left;
        #             border-collapse: collapse;
        #         }
        #         #styled-table th {
        #             width: 20%;
        #         }
        #         #styled-table td {
        #             width: 80%;
        #         }
        #         #styled-table th, #styled-table td {
        #             text-align: left;
        #             padding: 8px;
        #             border: 1px solid #ddd;
        #         }
        #         #styled-table thead tr {
        #             background-color: lightblue;
        #         }
        #     </style>
        #     """, unsafe_allow_html=True)

        # CSS per lo stile della tabella e adattamento delle larghezze delle colonne
        st.markdown("""
            <style>
                #styled-table {
                    width: 100%;
                    text-align: left;
                    border-collapse: collapse;
                }
                #styled-table th:nth-child(1), #styled-table td:nth-child(1) {
                    text-align: left;
                    width: 30%;
                    padding: 12px;
                }
                #styled-table th:nth-child(2), #styled-table td:nth-child(2) {
                    text-align: left;
                    width: 70%;
                    padding: 12px;
                }
                #styled-table th, #styled-table td {
                    padding: 8px;
                }
                #styled-table th, #styled-table thead tr {
                    background-color: #8ebfde;
                }
                # #styled-table tr:nth-child(odd) {
                #     background-color: #f9f9f9;
                # }
            </style>
            """, unsafe_allow_html=True)

        st.subheader("Request details:")
        st.write(html_table, unsafe_allow_html=True)
         # Aggiunta del pulsante di esportazione
        def remove_html_tags(text):
            """Rimuove i tag HTML da una stringa, ignorando eventuali valori None."""
            if text is None:
                return ""
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)

        def convert_df(df):
            df_clean = df.copy()
            df_clean["Column value"] = df_clean["Column value"].apply(remove_html_tags)
            return df_clean.to_csv(index=False, sep=';').encode('utf-8')

        csv = convert_df(df_out)

        st.download_button(
            label="Export data",
            data=csv,
            file_name='request_details.csv',
            mime='text/csv',
            type="primary"
        )        


#######################################################################################################
def manage_request():
    """
    Handle request assignments and management through a Streamlit interface.
    Includes request filtering, display, and assignment management functionality.
    """
    
    def reset_application_state():
        """Reset all session state variables and cached data"""
        # Lista delle chiavi di sessione da eliminare
        keys_to_clear = [
            'grid_data',
            'grid_response',
            'dialog_shown',
            'need_refresh',
            'main_grid',  # Chiave della griglia AgGrid
#            'Status_value',  # Chiave del filtro status nella sidebar
            'selected_rows' # Chiave della selezione delle righe
        ]
        
        # Rimuovi tutte le chiavi di sessione specificate
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Forza il refresh cambiando la chiave 
        st.session_state.grid_refresh_key = str(time.time())
        # # Reset the grid response to remove any selected rows 
        # st.session_state.grid_response
        # Forza il rerun dell'applicazione        
        st.rerun()

    def show_request_dialog(selected_row, req_status_options, update_request_fn):
        """
        Display and handle the request modification dialog.
        
        Args:
            selected_row: The currently selected grid row
            req_status_options: List of available status options
            update_request_fn: Function to update request status and notes

        """
        popup_title = f'Request {selected_row["REQID"][0]}'
        
        @st.dialog(popup_title, width="large")
        def dialog_content():
            # Custom styles for inputs
            st.markdown(
                """
                <style>
                div[data-testid="stTextInput"] > div > div > input:not([disabled]) {
                    color: #28a745; !important; 
                    border: 2px solid #28a745;
                    -webkit-text-fill-color: #28a745 !important;
                    font-weight: bold;
                }

                div[data-testid="stTextInput"] > div > div input[disabled] {
                    color: #6c757d !important;  
                    opacity: 1 !important;
                    -webkit-text-fill-color: #6c757d !important;
                    background-color: #e9ecef !important;
                    border: 1px solid #ced4da !important;
                    font-style: italic;
                }

                .stSelectbox > div > div > div > div {
                    color: #007bff;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Display Request ID
            reqid = selected_row["REQID"][0]
            # Display Product Line
            selected_pline_name = selected_row['PRLINE_NAME'][0]
            selected_pline_code = df_pline[df_pline["NAME"] == selected_pline_name]["CODE"].values[0]
            st.text_input(label="Product line", value=selected_pline_name, disabled=True)
           
            # Display request details

            # dept_code = df_requests[df_requests["REQID"] == reqid]["DEPT"].values[0]
            # dept_name = get_description_from_code(df_depts, dept_code, "NAME")

            # family_code = df_requests[df_requests["REQID"] == reqid]["PR_FAMILY"].values[0]
            # family_name = get_description_from_code(df_pfamily, family_code, "NAME")

            # type_code = df_requests[df_requests["REQID"] == reqid]["TYPE"].values[0]
            # type_name = get_description_from_code(df_type, type_code, "NAME")
            
            # category_code = df_requests[df_requests["REQID"] == reqid]["CATEGORY"].values[0]
            # category_name = get_description_from_code(df_category, category_code, "NAME")

            # detail_code = df_requests[df_requests["REQID"] == reqid]["DETAIL"].values[0]
            # detail_name = get_description_from_code(df_detail, detail_code, "NAME")

            # title = selected_row['TITLE'][0]
            # description = df_requests[df_requests["REQID"] == reqid]["DESCRIPTION"].values[0]
            # note_td = df_requests[df_requests["REQID"] == reqid]["NOTE_TD"].values[0]

            # tdtl_code = df_reqassignedto[df_reqassignedto["REQID"] == reqid]["USERID"].values[0]
            # tdtl_name = get_description_from_code(df_users, tdtl_code, "NAME")
       
            
            # Display Title
            st.text_input(label="Title", value=selected_row['TITLE'][0], disabled=True)
            # Display Description
            description = df_requests[df_requests["REQID"] == reqid]["DESCRIPTION"].values[0]
            st.text_area(label="Description", value=description, disabled=True)

            st.divider()
            tdtl_usercode = df_lk_pline_tdtl["USER_CODE"].drop_duplicates().sort_values().tolist() #conversione in lista
            tdtl_username_list = df_users[df_users["CODE"].isin(tdtl_usercode)]["NAME"].tolist()

            tdtl_default_codes = df_reqassignedto[df_reqassignedto["REQID"] == reqid]["USERID"].tolist()

            if tdtl_default_codes:
                tdtl_option = df_users[df_users["CODE"].isin(tdtl_default_codes)]
                default_tdtl_name = tdtl_option["NAME"].tolist()
            else:
                default_tdtl_name = []

            req_tdtl_name = st.multiselect(
                label=":blue[Tech Department Team Leader](:red[*])",
                options=tdtl_username_list,
                default=default_tdtl_name,
                key="sb_tdtl_reqmanage",
                disabled=False
            )

            if req_tdtl_name:
                req_tdtl_code = df_users[df_users["NAME"].isin(req_tdtl_name)]["CODE"].tolist()
            else:
                req_tdtl_code = []

            #st.write(f"POINT_A6: {req_tdtl_name}")
            #st.write(f"POINT_A7: {req_tdtl_code}")



            # req_tdtl_name_list = list(req_tdtl_name)
            # st.write(f"POINT_A8: {req_tdtl_name_list}")
            
            # if len(req_tdtl_name_list) == 0:
            #     req_tdtl_name_list = default_tdtl_name

            # st.write(f"POINT_A9: {req_tdtl_name_list}")
            
            # Display Status 
            idx_status = req_status_options.index(selected_row['STATUS'][0])
            req_status = st.selectbox(label=":blue[Status](:red[*])", options=req_status_options, index=idx_status, disabled=False, key="status_selectbox")
            
            # Display Tech Dept Note
            default_note_td = str(df_requests[df_requests["REQID"] == reqid]["NOTE_TD"].values[0])
            req_note_td = st.text_area(label=":blue[Tech Department Notes]", value=default_note_td, disabled=False)


            if (req_note_td == default_note_td) and (selected_row['STATUS'][0] == req_status) and (req_tdtl_name == default_tdtl_name):
                disable_save_button = True
            else:
                disable_save_button = False    
            # Handle save action
            if st.button("Save", type="primary", disabled=disable_save_button, key="req_save_button"):
                #st.write(f"POINT_A10 {req_tdtl_code}")
                success = update_request_fn(reqid, req_status, req_note_td, 0, req_tdtl_code)               
                if success:
                    st.session_state.grid_refresh = True
                    st.session_state.grid_response = None
                    st.success(f"Request {reqid} updated successfully!")
                    
                    st.session_state.need_refresh = True
                    time.sleep(3)
                    reset_application_state()
                    st.rerun()

            return False

        return dialog_content()

#######################################
    def show_workorder_dialog(selected_row, df_workorders, df_woassignedto, df_users, active_status, default_dept_code, req_status_options, save_workorder_fn, save_woassignments_fn):
        """
        Display and handle the request modification dialog.
        
        Args:
            selected_row: The currently selected grid row
            df_woassignedto: DataFrame of request assignments
            df_users: DataFrame of users
            req_status_options: List of available status options
            default_dept_code: Default department code
            update_request_fn: Function to update request status and notes
            update_assignments_fn: Function to update request assignments
        """
        popup_title = f'Request {selected_row["REQID"][0]}'
        
        @st.dialog(popup_title, width="large")
        def dialog_content():
            # Custom styles for inputs
            st.markdown(
                """
                <style>
                div[data-testid="stTextInput"] > div > div > input:not([disabled]) {
                    color: #28a745;
                    border: 2px solid #28a745;
                    -webkit-text-fill-color: #28a745 !important;
                    font-weight: bold;
                }

                div[data-testid="stTextInput"] > div > div input[disabled] {
                    color: #6c757d !important;
                    opacity: 1 !important;
                    -webkit-text-fill-color: #6c757d !important;
                    background-color: #e9ecef !important;
                    border: 1px solid #ced4da !important;
                    font-style: italic;
                }

                .stSelectbox > div > div > div > div {
                    color: #007bff;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Extract request and work order ID
            reqid = selected_row["REQID"][0]
            woid = "W" + selected_row["REQID"][0][1:]

            # Display request details
            st.text_input(label="Product Line", value=selected_row['PRLINE_NAME'][0], disabled=True)
            st.text_input(label="Request title", value=selected_row['TITLE'][0], disabled=True)
            
            req_description = df_requests[df_requests["REQID"]==reqid]["DESCRIPTION"]
            if not req_description.empty:
                req_description_default = req_description.values[0]
            else:
                req_description_default = ""
            st.text_input(label="Request description", value=req_description_default, disabled=True)

            req_note_td = df_requests[df_requests["REQID"]==reqid]["NOTE_TD"]
            if not req_note_td.empty:
                req_note_td_default = req_note_td.values[0]
            else:
                req_note_td_default = ""

            st.divider()
            st.subheader(f"Work Order {woid}")

            wo_nr = df_workorders[df_workorders["REQID"] == reqid]["WOID"]

            wo_type_options=["Standard", "APQP Project"]  #APQP -> ADVANCED PRODUCT QUALITY PLANNING"  
            wo_type_filtered = df_workorders[df_workorders["WOID"] == woid]["TYPE"]
            if not wo_type_filtered.empty:
                wo_type_default = wo_type_filtered.values[0]
                wo_type_index = wo_type_options.index(wo_type_default)
            else:
                wo_type_index = 0  

            wo_startdate_filtered = df_workorders[df_workorders["WOID"] == woid]["STARTDATE"]
            if not wo_startdate_filtered.empty:
                wo_startdate_default = wo_startdate_filtered.values[0]
            else:
                wo_startdate_default = None  # O un valore di default appropriato

            wo_enddate_filtered = df_workorders[df_workorders["WOID"] == woid]["ENDDATE"]
            if not wo_enddate_filtered.empty:
                wo_enddate_default = wo_enddate_filtered.values[0]
            else:
                wo_enddate_default = None  # O un valore di default appropriato

            wo_timeqty_filtered = df_workorders[df_workorders["WOID"] == woid]["TIME_QTY"]
            if not wo_timeqty_filtered.empty:
                wo_timeqty_default = float(wo_timeqty_filtered.iloc[0])  # Converti a float!
                min_value = 0.0 # Valore minimo predefinito come float
            else:
                wo_timeqty_default = 0.0  # Valore di default come float
                min_value = 0.0 # Valore minimo predefinito come float             
                 
            df_tdusers = df_users[df_users["DEPTCODE"] == default_dept_code]
            
            # Lista dei possibili nomi dei Team Leader
            tdtl_usercode = df_lk_pline_tdtl["USER_CODE"].drop_duplicates().sort_values().tolist() #conversione in lista
            tdtl_username_list = df_users[df_users["CODE"].isin(tdtl_usercode)]["NAME"].tolist()

            tdtl_default_codes = df_reqassignedto[df_reqassignedto["REQID"] == reqid]["USERID"].tolist()

            if tdtl_default_codes:
                tdtl_option = df_users[df_users["CODE"].isin(tdtl_default_codes)]
                default_tdtl_name = tdtl_option["NAME"].tolist()
            else:
                default_tdtl_name = []


            if default_tdtl_name:
                # Trova gli indici dei Team Leader predefiniti nella lista di opzioni
                default_indices = []
                for name in default_tdtl_name:
                    try:
                        index = tdtl_username_list.index(name)
                        default_indices.append(index)
                    except ValueError:
                        # Gestisci il caso in cui il nome predefinito non è presente nelle opzioni
                        st.warning(f"Il Team Leader '{name}' non trovato nella lista di opzioni.", icon="⚠️")
                        # Puoi scegliere di ignorare questo nome o di usare un valore di default.
                        # Per esempio, per usare il primo elemento come default in questo caso:
                        # default_indices.append(0) #Aggiungi 0 solo se vuoi che in questo caso prenda il primo elemento della lista.
                # Se default_indices è vuota, vuol dire che nessuno dei nomi di default è presente nella lista.
                # In questo caso, puoi lasciare che Streamlit mostri il primo elemento di default, oppure puoi settare un valore di default esplicito, come fatto nei precedenti esempi.
            else:
                default_indices = []


            req_tdtl_name = st.selectbox(
                label=":blue[Tech Department Team Leader](:red[*])",
                options=tdtl_username_list,
                index=default_indices[0] if default_indices else None,  # Usa il primo indice se presente, altrimenti None
                key="sb_tdtl_reqmanage2",
                disabled=False
            )

            if req_tdtl_name: #se è stato selezionato un TL
                req_tdtl_code = df_users[df_users["NAME"] == req_tdtl_name]["CODE"].iloc[0] #Recupero il codice del TL
                #st.write(f"Team Leader selezionato (nome): {req_tdtl_name}")
                #st.write(f"Team Leader selezionato (codice): {req_tdtl_code}")
            else:
                #st.write("Nessun Team Leader selezionato.")
                req_tdtl_code = None # o un valore di default che preferisci            

            wo_type = st.selectbox(label="Type(:red[*])", options=wo_type_options, index=wo_type_index, disabled=False)
            wo_time_qty = st.number_input(
                label="Time estimated(:red[*]):",
                min_value=min_value, # Usa il valore minimo predefinito
                value=wo_timeqty_default if wo_timeqty_default is not None else 0, # Valore iniziale
                step=0.5
            )  
            wo_time_um = "H" 

            # Tech Dept Specialist assignment selection
            filtered_woassignedto = df_woassignedto[
                (df_woassignedto["WOID"] == woid) & 
                (df_woassignedto["STATUS"] == active_status)
            ]
            wo_assignedto_default = list(filtered_woassignedto["USERNAME"])
            wo_assignedto_option = list(df_tdusers["NAME"])
            wo_assignedto_title = "Tech Department Specialists assigned to (:red[*]):"
            wo_assignedto = st.multiselect(
                label=wo_assignedto_title, 
                options=wo_assignedto_option, 
                default=wo_assignedto_default, 
                max_selections=3,
                disabled=False
            )
            
            wo_startdate = None
            wo_enddate = None
            #wo_startdate = st.date_input(label="Start date", format="DD/MM/YYYY", value=wo_startdate_default, disabled=False)
            #wo_enddate = st.date_input(label="End date", format="DD/MM/YYYY", value=wo_enddate_default, disabled=False)
       

            if not wo_nr.empty:
                if (wo_type == wo_type_default and wo_assignedto == wo_assignedto_default and wo_time_qty == wo_timeqty_default):
                    disable_save_button = True
                else:
                    disable_save_button = False    
            else:
                if not (wo_type and wo_assignedto and wo_time_qty):
                    disable_save_button = True
                else:
                    disable_save_button = False

            # Handle save action
            if st.button("Save", type="primary", disabled=disable_save_button, key="wo_save_button"):
                wo = {"woid":woid, "tdtlid": req_tdtl_code, "type": wo_type, "title": selected_row["TITLE"][0], "description": req_description_default, "time_qty": wo_time_qty, "time_um": wo_time_um, "status": ACTIVE_STATUS, "startdate": wo_startdate, "enddate": wo_enddate, "reqid": reqid}
                wo_idrow, success = save_workorder(wo)
                if success:
#                    st.success(f"Work order W{str(wo_idrow).zfill(4)} created successfully!")
                    success = save_workorder_assignments(woid, wo_assignedto, df_users, df_woassignedto)
                    success = update_request(reqid, "ASSIGNED", req_note_td, "", [])
                    if success:
                        st.session_state.grid_refresh = True
                        st.session_state.grid_response = None
                        st.success(f"Work order {woid} created successfully!")
                    
                    st.session_state.need_refresh = True
                    time.sleep(3)
                    reset_application_state()
                    st.rerun()

            return False

        return dialog_content()
   

    # Database update functions
    def update_request(reqid: str, new_status: str, new_note_td: str, new_woid: str = "", new_tdtl: list=[]):
        
        #st.write(f"POINT_U0: reqid = {reqid} - new_status = {new_status} - new_note_td = {new_note_td} - new_tdtl = {new_tdtl}")

        if isinstance(new_status, pd.Series):  # Check if it's a Series
            new_status = new_status.iloc[0]
        if isinstance(new_note_td, pd.Series):
            new_note_td = new_note_td.iloc[0]
        if isinstance(new_woid, pd.Series):
            new_woid = new_woid.iloc[0]

        # Update TORP_REQUESTS
        try:
            cursor.execute(
                "UPDATE TORP_REQUESTS SET status = ?, note_td = ?, woid = ? WHERE reqid = ?",
                (new_status, new_note_td, new_woid, reqid)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            st.error(f"Error updating TORP_REQUESTS: {str(e)}", icon="🚨")
            return False

        # Update TORP_REQASSIGNEDTO
        try:
            if new_tdtl: # Check if the list is not empty
            # 1. Disable existing assignments (important to do this *before* inserting new ones)
                cursor.execute("UPDATE TORP_REQASSIGNEDTO SET status = ? WHERE reqid = ?", (DISABLED_STATUS, reqid))
                conn.commit()
                # 2. Insert new assignments
                for tdtl in new_tdtl:
                    try:
                        # Check if the record already exists in the table
                        cursor.execute("SELECT 1 FROM TORP_REQASSIGNEDTO WHERE reqid = ? AND userid = ?", (reqid, tdtl))
                        existing_record = cursor.fetchone()
                        if existing_record:
                            # Update the existing record
                            cursor.execute("UPDATE TORP_REQASSIGNEDTO SET status = ? WHERE reqid = ? AND userid = ?", (ACTIVE_STATUS, reqid, tdtl))
                        else:
                            # Insert a new record
                            cursor.execute("INSERT INTO TORP_REQASSIGNEDTO (reqid, userid, status) VALUES (?, ?, ?)", (reqid, tdtl, ACTIVE_STATUS))
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error inserting/updating REQASSIGNEDTO for {tdtl}: {str(e)}", icon="🚨")
                        return False
            # else:
            #     st.warning("Nessun Team Leader fornito per l'aggiornamento di REQASSIGNEDTO", icon="⚠️")

        except Exception as e:
            conn.rollback()
            st.error(f"Error updating REQASSIGNEDTO (disabling): {str(e)}", icon="🚨")
            return False

        return True

    def save_workorder(wo: dict): # Pass connection and cursor
        try:
            # Check if a workorder with the given woid already exists
            cursor.execute("SELECT 1 FROM TORP_WORKORDERS WHERE woid = ? AND tdtlid = ?", (wo["woid"],wo["tdtlid"]))
            existing_workorder = cursor.fetchone()

            if existing_workorder:
                # UPDATE
                sql = """
                    UPDATE TORP_WORKORDERS SET
                        type = ?, title = ?, description = ?,
                        time_qty = ?, time_um = ?, status = ?, startdate = ?,
                        enddate = ?, reqid = ?
                    WHERE woid = ?
                    AND tdtlid = ?
                """
                values = (
                    wo["type"], wo["title"], wo["description"],
                    wo["time_qty"], wo["time_um"], wo["status"], wo["startdate"],
                    wo["enddate"], wo["reqid"], wo["woid"], wo["tdtlid"]  # Include woid in WHERE clause
                )
                cursor.execute(sql, values)
                conn.commit()
                #st.success(f"Workorder {wo['woid']} updated successfully.") # feedback for the user
                return wo["woid"], True

            else:
                # INSERT
                sql = """
                    INSERT INTO TORP_WORKORDERS (
                        woid, tdtlid, type, title, description, time_qty, time_um,
                        status, startdate, enddate, reqid
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = (
                    wo["woid"], wo["tdtlid"], wo["type"], wo["title"], wo["description"],
                    wo["time_qty"], wo["time_um"], wo["status"], wo["startdate"],
                    wo["enddate"], wo["reqid"]
                )
                cursor.execute(sql, values)
                conn.commit()
                #st.success(f"Workorder {wo['woid']} created successfully.") # feedback for the user
                return wo["woid"], True

        except Exception as e:
            conn.rollback() # important to rollback in case of error!
            st.error(f"**ERROR saving workorder: \n{e}", icon="🚨")
            return "", False

    def save_workorder_assignments(woid, assigned_users, df_users, df_woassignedto):
        try:
            # Disable existing assignments
            cursor.execute(
                "UPDATE TORP_WOASSIGNEDTO SET status = ? WHERE woid = ?",
                (DISABLED_STATUS, woid)
            )
            
            # Add new assignments
            for user_name in assigned_users:
                user_code = df_users[df_users["NAME"] == user_name]["CODE"].iloc[0]
                existing_assignment = df_woassignedto[
                    (df_woassignedto['WOID'] == woid) & 
                    (df_woassignedto['USERID'] == user_code)
                ]
                
                if existing_assignment.empty:
                    cursor.execute(
                        "INSERT INTO TORP_WOASSIGNEDTO (userid, woid, status) VALUES (?, ?, ?)",
                        (user_code, woid, ACTIVE_STATUS)
                    )
                else:
                    cursor.execute(
                        "UPDATE TORP_WOASSIGNEDTO SET status = ? WHERE woid = ? AND userid = ?",
                        (ACTIVE_STATUS, woid, user_code)
                    )
            
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Error updating TORP_WOASSIGNEDTO: {str(e)}", icon="🚨")
            conn.rollback()
            return False



    # Grid configuration
    def configure_grid(df_requests):
        cellStyle = JsCode("""
            function(params) {
                if (params.column.colId === 'REQID') {
                        return {
                            'backgroundColor': '#8ebfde',
                            'color': '#111810',
                            'fontWeight': 'bold'
                        };
                }
                return null;
            }
            """)
        
        builder = GridOptionsBuilder.from_dataframe(df_requests)
        builder.configure_default_column(
            resizable=True,
            filterable=True,
            sortable=True,
            editable=False,
            enableRowGroup=False
        )
        builder.configure_pagination(paginationAutoPageSize=False, paginationPageSize=12)
        builder.configure_grid_options(domLayout='normal')
        builder.configure_column(
            field="DATE",
            header_name="INSERT DATE",
            valueFormatter="value != undefined ? new Date(value).toLocaleString('it-IT', {dateStyle:'short'}): ''"
        )
        builder.configure_column("REQID", cellStyle=cell_style)
        builder.configure_selection(selection_mode='single', use_checkbox=True, header_checkbox=True)
        
        return builder.build()

    # Load data from database
    load_initial_data()
    load_requests_data()
    load_workorders_data()
    load_woassignedto_data()

    # Initialize session state
    if "grid_data" not in st.session_state:
        st.session_state.grid_data = df_requests.copy()
    if "grid_response" not in st.session_state:
        st.session_state.grid_response = None
    if "grid_refresh_key" not in st.session_state: 
        st.session_state.grid_refresh_key = "initial"    


    df_requests_grid = pd.DataFrame()
    df_requests_grid['REQID'] = df_requests['REQID']
    df_requests_grid['STATUS'] = df_requests['STATUS']
    df_requests_grid['INSDATE'] = df_requests['INSDATE']
#    df_requests_grid['DEPTNAME'] = df_requests['DEPT'].apply(lambda dept_code: get_description_from_code(df_depts, dept_code, "NAME"))
    df_requests_grid['PRIORITY'] = df_requests['PRIORITY']
    df_requests_grid['PRLINE_NAME'] = df_requests['PR_LINE'].apply(lambda pline_code: get_description_from_code(df_pline, pline_code, "NAME"))
    df_requests_grid['TITLE'] = df_requests['TITLE']
    df_requests_grid['REQUESTER_NAME'] = df_requests['REQUESTER'].apply(lambda requester_code: get_description_from_code(df_users, requester_code, "NAME"))

    cellStyle = JsCode("""
        function(params) {
            if (params.column.colId === 'REQID') {
                       return {
                        'backgroundColor': '#8ebfde',
                        'color': '#111810',
                        'fontWeight': 'bold'
                    };
            }
            return null;
        }
        """)
    grid_builder = GridOptionsBuilder.from_dataframe(df_requests_grid)
    # makes columns resizable, sortable and filterable by default
    grid_builder.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
        enableRowGroup=False
    )
    # Enalble pagination
    grid_builder.configure_pagination(paginationAutoPageSize=False, paginationPageSize=12)
    grid_builder.configure_grid_options(domLayout='normal')
    grid_builder.configure_column("REQID", cellStyle=cellStyle)   
    grid_builder.configure_selection(
    selection_mode='single',     # Enable multiple row selection
    use_checkbox=True,             # Show checkboxes for selection
    header_checkbox=True
    )
    grid_options = grid_builder.build()
    # List of available themes
    available_themes = ["streamlit", "alpine", "balham", "material"]
    
    # Inizializzazione della sessione
    if "grid_data" not in st.session_state:
        st.session_state.grid_data = df_requests_grid.copy()  # Copia per evitare modifiche al DataFrame originale
    if "grid_response" not in st.session_state:
        st.session_state.grid_response = None


    # Sidebar controls - Filters
    st.sidebar.header("Filters")
    req_status_options = list(df_requests_grid['STATUS'].drop_duplicates().sort_values())
    status_filter = st.sidebar.selectbox(
        "Select a Status value:", 
        req_status_options, 
        index=None,
        key='Status_value'
    )
    
    req_pline_options = df_requests_grid['PRLINE_NAME'].drop_duplicates().sort_values()
    pline_filter = st.sidebar.selectbox(
        "Select a Product Line:", 
        req_pline_options, 
        index=None,
        key='Pline_value'
    )

    # req_tdtl_options = df_lk_pline_tdtl['USER_NAME'].drop_duplicates().sort_values()
    # tdtl_filter = st.sidebar.selectbox(
    #     "Select a Tech Dep. Team Leader:", 
    #     req_tdtl_options, 
    #     index=None,
    #     key='Tdtl_value'
    # )

    # Apply filters 
    filtered_data = df_requests_grid.copy() 
    if status_filter: 
        filtered_data = filtered_data[filtered_data["STATUS"] == status_filter] 
    if pline_filter: 
        filtered_data = filtered_data[filtered_data["PRLINE_NAME"] == pline_filter] 
    st.session_state.grid_data = filtered_data

    # Display grid
    st.subheader("Request list:")
    
    # Creazione/Aggiornamento della griglia (UNA SOLA VOLTA per ciclo di esecuzione)
    if st.session_state.grid_response is None:
        st.session_state.grid_response = AgGrid(
            st.session_state.grid_data,
            gridOptions=grid_options,
            allow_unsafe_jscode=True,
            theme=available_themes[2],
            fit_columns_on_grid_load=False,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            data_return_mode=DataReturnMode.AS_INPUT,
            key="main_grid"
        )
    else:
        st.session_state.grid_response = AgGrid( # Aggiorna la griglia esistente
            st.session_state.grid_data,
            gridOptions=grid_options,
            allow_unsafe_jscode=True,
            theme=available_themes[2],
            fit_columns_on_grid_load=False,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            data_return_mode=DataReturnMode.AS_INPUT,
            key="main_grid"
        )

    selected_row = st.session_state.grid_response['selected_rows']
    

    
    
    # Add refresh button in a container below the grid
    with st.container():

        selected_rows = st.session_state.grid_response.get('selected_rows', None)
        modify_request_button_disable = not (selected_rows is not None and isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty)
        workorder_button_disable = not (selected_rows is not None and isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty)

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Refresh", type="tertiary"):
                reset_application_state()
        with col2:
            if st.button("✏️ Modify", type="secondary", disabled=modify_request_button_disable):
                selected_rows = st.session_state.grid_response.get('selected_rows', None)
                if selected_rows is not None and isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
                    if 'dialog_shown' not in st.session_state:
                        st.session_state.dialog_shown = False
                    if 'need_refresh' not in st.session_state:
                        st.session_state.need_refresh = False
                        
                    if st.session_state.need_refresh:
                        st.session_state.need_refresh = False
                        st.session_state.dialog_shown = False
                    elif not st.session_state.dialog_shown:
                        # Modifica anche la funzione show_request_dialog per gestire il DataFrame
                        show_request_dialog(
                            selected_rows, 
                            REQ_STATUS_OPTIONS,
                            update_request
                        )
     
        with col3:
            if st.button("📌 Work Order", type="secondary", disabled=workorder_button_disable):
                selected_rows = st.session_state.grid_response.get('selected_rows', None)
                if selected_rows is not None and isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
                    if 'dialog_shown' not in st.session_state:
                        st.session_state.dialog_shown = False
                    if 'need_refresh' not in st.session_state:
                        st.session_state.need_refresh = False
                        
                    if st.session_state.need_refresh:
                        st.session_state.need_refresh = False
                        st.session_state.dialog_shown = False
                    elif not st.session_state.dialog_shown:
                        # Modifica anche la funzione show_request_dialog per gestire il DataFrame
                        show_workorder_dialog(
                            selected_rows,
                            df_workorders, 
                            df_woassignedto, 
                            df_users,
                            ACTIVE_STATUS, 
                            DEFAULT_DEPT_CODE,
                            REQ_STATUS_OPTIONS,
                            save_workorder,
                            save_workorder_assignments
                        )



#######################################################################################################
def manage_wo():

    def save_work_item(witem: dict) ->  bool:
        """Save request to database and return request number and status"""
        try:

            # Stampa i valori ricevuti per debug
            st.write(f"Saving work item: {witem}")
            st.write(f"Type of time_qty: {type(witem['time_qty'])}")                                    
            sql = """
                INSERT INTO TORP_WORKITEMS (
                    date, woid, userid, status, 
                    tskgrl1, tskgrl2, description, note, 
                    time_qty, time_um
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                witem["wi_date"], witem["wo_id"], witem["wi_userid"], witem["wi_status"],
                witem["wi_tskgrl1"], witem["wi_tskgrl2"], witem["wi_desc"], witem["wi_note"], 
                witem["wi_time_qty"], witem["wi_time_um"]
            )
            cursor.execute(sql, values)
            conn.commit()
            return True
        
        except Exception as e:
            st.error(f"**ERROR inserting data in table TORP_WORKITEM: \n{e}", icon="🚨")
            conn.rollback()
            return False

    def reset_form():
        st.session_state.reset_pending = True
        st.rerun()

        # All'inizio della funzione
    if 'reset_pending' not in st.session_state:
        st.session_state.reset_pending = False 
        
    if 'df_woassignedto' not in st.session_state: # Check if it exists
        st.write(f"Start loading df_woassignedto...")
        st.session_state.df_woassignedto = load_woassignedto_data()  # Load only once

    if 'df_workorders' not in st.session_state: # Check if it exists
        st.write(f"Start loading df_workorders...")
        st.session_state.df_workorders = load_workorders_data()  # Load only once

    if 'df_tskgrl1' not in st.session_state: # Check if it exists
        st.write(f"Start loading df_tskgrl1...")
        st.session_state.df_tskgrl1 = load_tskgrl1_data()  # Load only once

    if 'df_tskgrl2' not in st.session_state: # Check if it exists
        st.write(f"Start loading df_tskgrl2...")
        st.session_state.df_tskgrl2 = load_tskgrl2_data()  # Load only once
  

    # Inizializzazione dello stato del form
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    
    if 'reset_form' not in st.session_state:
        st.session_state.reset_form = False
        
    FORM_KEYS = [
        'sb_wi_taskl1', 'sb_wi_taskl2', 'sb_wi_description',
        'sb_wi_time_qty', 'sb_wi_date', 'sb_wi_note'
    ]

    # Inizializzazione delle chiavi del form se non esistono
    for key in FORM_KEYS:
        if key not in st.session_state:
            st.session_state[key] = None if key.startswith('sb_') else ""
    
    
    # Access from session state
    df_woassignedto = st.session_state.df_woassignedto 
    df_workorders = st.session_state.df_workorders 
    df_tskgrl1 = st.session_state.df_tskgrl1
    df_tskgrl2 = st.session_state.df_tskgrl2


    # Inzialize sessione state
    if 'selected_username' not in st.session_state:
        st.session_state.selected_username = False
    if 'selected_wo' not in st.session_state:
        st.session_state.selected_wo = False

    # Aggiungi un divisore nella sidebar
    st.sidebar.divider()
    st.sidebar.header(f":orange[Work order filters]")
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
  
    selected_wo = st.sidebar.selectbox(label=":blue[Work-Order]", options=wo_woid_options, index=None)
    if selected_wo:
        st.session_state.selected_wo = True

    # Input per inserire i dettagli del task svolto
    if st.session_state.selected_wo:
        st.header(f":orange[Work Order {selected_wo}]")
        with st.expander("WO details"):
            # Get the work order details
            df_wo = df_workorders[df_workorders["WOID"] == selected_wo].copy() # Create a copy to avoid SettingWithCopyWarning
            df_wo = df_wo.drop(['STARTDATE', 'ENDDATE', 'TDTLID'], axis=1)
            # Add the TDSPECIALIST.  This is the KEY change.
            df_wo['TDSPECIALIST'] = selected_username  # Directly modify the df_wo DataFrame
            # Now, you can either display the modified df_wo directly
            # Renaming columns
            df_wo.rename(columns={
                'TDSPECIALIST': 'Tech Specialist', 
                'REQID': 'Request Id', 
                'WOID': 'Workorder Id',
                'TYPE': 'Type',
                'TIME_QTY': 'Estimated effort',
                'TIME_UM': 'Um',
                'TITLE': 'Title',
                'DESCRIPTION': 'Description'
                }, inplace=True)
            
            wo_column_order = ["Request Id", "Tech Specialist", "Workorder Id", "Type'", "Estimated effort", "Um", "Title", "Description" ]
            st.dataframe(df_wo, use_container_width=True, column_order=wo_column_order, hide_index=True)
        
        
        st.subheader(f":orange[Task]")

        #with st.form(key='task_form'):
        taskl1_options = df_tskgrl1["NAME"].tolist()
        
        # Per Task Group L1
        initial_task_l1 = None if st.session_state.reset_pending else st.session_state.get('sb_wi_taskl1')
        wi_task_l1 = st.selectbox(
            label=":blue[Task Group L1]", 
            options=taskl1_options, 
            index=None if initial_task_l1 is None else taskl1_options.index(initial_task_l1) if initial_task_l1 in taskl1_options else None, 
            key="sb_wi_taskl1"
        )
        wi_task_l1_code = df_tskgrl1[df_tskgrl1["NAME"]==wi_task_l1]["CODE"].tolist() if wi_task_l1 else []

        # Per Task Group L2
        taskl2_options = df_tskgrl2["NAME"].tolist()
        initial_task_l2 = None if st.session_state.reset_pending else st.session_state.get('sb_wi_taskl2')
        wi_task_l2 = st.selectbox(
            label=":blue[Task Group L2]", 
            options=taskl2_options, 
            index=None if initial_task_l2 is None else taskl2_options.index(initial_task_l2) if initial_task_l2 in taskl2_options else None, 
            key="sb_wi_taskl2"
        )
        wi_task_l2_code = df_tskgrl2[df_tskgrl2["NAME"]==wi_task_l2]["CODE"].tolist() if wi_task_l2 else []

        # Per Description
        initial_description = "" if st.session_state.reset_pending else st.session_state.get('sb_wi_description', "")
        wi_description = st.text_input(
            label=":blue[Task description]", 
            value=initial_description, 
            key="sb_wi_description"
        )


        # initial_time_qty = 0.0 if st.session_state.reset_pending else st.session_state.get('sb_wi_time_qty', 0.0)
        # wi_time_qty = st.number_input(
        #     label=":blue[Time spent (in hours)(:red[*])]:", 
        #     value=initial_time_qty,
        #     min_value=0.0, 
        #     step=0.5, 
        #     key="sb_wi_time_qty"
        # )

        # # Per Time Quantity
        initial_time_qty = st.session_state.get('sb_wi_time_qty')
        try:
            initial_time_qty = float(initial_time_qty) if initial_time_qty else 0.0
            initial_time_qty = np.float64(initial_time_qty)  # Forza il tipo a float64
            st.write(f"Tipo di dato prima del number_input: {type(initial_time_qty)}")
        except (TypeError, ValueError):
            initial_time_qty = 0.0

        wi_time_qty = st.number_input(
            label=":blue[Time spent (in hours)(:red[*])]:",
            value=initial_time_qty if initial_time_qty is not None else 0, # Valore iniziale
            min_value=0.0,
            step=0.5,
            key="sb_wi_time_qty",
        )

        st.write(f"Valore di wi_time_qty: {wi_time_qty}")  # Stampa il valore dopo l'input
        
        #Per Date
        initial_date = st.session_state.get('sb_wi_date') or datetime.date.today()  # Use session value or today
        wi_date = st.date_input(
            label=":blue[Date of execution(:red[*])]",
            value=initial_date,
            format="DD/MM/YYYY",
            key="sb_wi_date"
        )

        # Per Note
        initial_note = "" if st.session_state.reset_pending else st.session_state.get('sb_wi_note', "")
        wi_note = st.text_area(
            ":blue[Note]", 
            value=initial_note,
            key="sb_wi_note"
        )

        wo_nr = selected_wo
        wi_time_um = "H"
        
        wi_save_botton_disable = False
        submitted = False
        submitted = st.button("Save Work Item", type="primary", icon="🔥", disabled=wi_save_botton_disable)

        if submitted:
            if wi_date:
                wi_date_fmt = wi_date.strftime("%Y-%m-%d")
            else:
                wi_date_fmt = datetime.date.today()    
            if wi_task_l1_code:
               wi_tskgrl1 = wi_task_l1_code[0]
            else: 
               wi_tskgrl1 = ""   
            if wi_task_l2_code:
               wi_tskgrl2 = wi_task_l2_code[0] 
            else:
               wi_tskgrl2 = ""              
            if wo_usercode:
               wi_userid = wo_usercode[0]
            else:
               wi_userid = ""    
            
            if wi_time_qty is None or wi_time_qty == 0:
                st.error("Please enter a valid time quantity")
                st.stop()

            work_item = {
                "wi_date": wi_date_fmt, 
                "wo_id": wo_nr, 
                "wi_userid": wi_userid, 
                "wi_status": ACTIVE_STATUS, 
                "wi_tskgrl1": wi_tskgrl1, 
                "wi_tskgrl2": wi_tskgrl2,  
                "wi_desc": wi_description, 
                "wi_note": wi_note,            
                "wi_time_qty": wi_time_qty, 
                "wi_time_um": wi_time_um
            }
            rc = save_work_item(work_item)
            if rc:
                st.success(f"Task {wo_nr} saved successfully!")
                st.session_state.reset_pending = True
                st.rerun()
    
        # Dopo il form, resettiamo il flag se necessario
        if st.session_state.reset_pending:
            st.session_state.reset_pending = False    
    
    else:
        st.header(f"Please select a work order first!")


#######################################################################################################
def my_test():
     st.write("Local my_test(): --> OK")

#######################################################################################################
def main():
    st.set_page_config(layout="wide")
#   if not check_password():
#     st.stop()
  
    open_sqlitecloud_db()
    load_initial_data()
    # In your main function:
    if 'df_woassignedto' not in st.session_state:
        st.session_state.df_woassignedto = load_woassignedto_data()
    if 'df_workorders' not in st.session_state:
        st.session_state.df_workorders = load_workorders_data()
    if 'df_tskgrl1' not in st.session_state:
        st.session_state.df_tskgrl1 = load_tskgrl1_data()
    if 'df_tskgrl2' not in st.session_state:
        st.session_state.df_tskgrl2 = load_tskgrl2_data()

    page_names_to_funcs = {
        "ℹ️ App Info": display_app_info,
        "📄 Insert Request": insert_request,
        "🔍 View Request ": view_request,
        "🗂️ Manage Request": manage_request,
    #    "📌 Manage Work Orders": manage_wo,
        "📌 Manage Work Orders": manage_wo,
    #    "🔐 Close db": close_sqlitecloud_db,
    #    "--> TEST": my_test
    }    
    # Aggiungi l'immagine alla sidebar 
    st.sidebar.image("https://iph.it/wp-content/uploads/2020/02/logo-scritta.png", width=150)
    
    st.markdown(
            """
        <style>
            /* Stile per st.selectbox */
        div[data-baseweb="select"] > div {
            border: 2px solid !important;
        }
            /* Stile per st.text_input */
        div[data-baseweb="input"] > div {
            border: 2px solid !important;
        }
            /* Stile per st.text_area */
        div[data-baseweb="textarea"] > div {
            border: 2px solid !important;
        }    
        </style>
        """,
        unsafe_allow_html=True
    )

    demo_name = st.sidebar.selectbox("Choose a function", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name]()

if __name__ == "__main__":
    main()
