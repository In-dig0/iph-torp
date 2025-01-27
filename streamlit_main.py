# Python built-in libraries
import datetime
import os
import io
import time
import json
import re
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List

# 3th party packages
import mytest
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

    df_category= pd.read_sql_query("""
        SELECT 
            A.code AS CODE, 
            A.name AS NAME
        FROM TORP_CATEGORY A
        ORDER by A.name
        """, conn)

    df_detail= pd.read_sql_query("""
        SELECT 
            A.code AS CODE,                                    
            A.name AS NAME
        FROM TORP_DETAIL A
        ORDER by A.name
        """, conn)

    df_lk_type_category= pd.read_sql_query("""
        SELECT 
            A.typecode AS TYPE_CODE, 
            A.categorycode AS CATEGORY_CODE
        FROM TORP_LINK_TYPE_CATEGORY A
        ORDER by A.typecode 
        """, conn)

    df_lk_category_detail= pd.read_sql_query("""
        SELECT 
            A.categorycode AS CATEGORY_CODE, 
            A.detailcode AS DETAIL_CODE
        FROM TORP_LINK_CATEGORY_DETAIL A
        ORDER by A.categorycode 
        """, conn)

    df_lk_pline_tdtl= pd.read_sql_query("""
        SELECT 
            A.plinecode AS PLINE_CODE, 
            A.usercode AS USER_CODE
        FROM TORP_LINK_PLINE_TDTL A
        ORDER by A.plinecode 
        """, conn)

#######################################################################################################
def load_requests_data():
    """ Load requests from database to df """
    global df_requests
    global df_reqassignedto
    
    df_requests = pd.read_sql_query("""
    SELECT 
        A.reqid as REQID, 
        A.status as STATUS, 
        A.insdate as INSDATE, 
        A.dept as DEPT, 
        A.requester as REQUESTER, 
        A.user as USER, 
        A.priority as PRIORITY, 
        A.pline as PR_LINE, 
        A.pfamily as PR_FAMILY, 
        A.type as TYPE, 
        A.category as CATEGORY, 
        A.detail AS DETAIL, 
        A.title as TITLE, 
        A.description as DESCRIPTION, 
        A.note_td as NOTE_TD, 
        A.woid as WOID  
    FROM TORP_REQUESTS A
    ORDER by REQID desc
    """, conn)

    df_reqassignedto = pd.read_sql_query("""
    SELECT 
        A.userid as USERID, 
        A.reqid as REQID,
        A.status as STATUS 
    FROM TORP_REQASSIGNEDTO A
    ORDER by USERID desc
    """, conn)


#######################################################################################################
def load_workorders_data():
    """ """
    global df_workorders
    global df_woassignedto

    df_workorders = pd.read_sql_query ("""
    SELECT 
        A.woid as WOID, 
        A.type as TYPE, 
        A.title as TITLE,
        A.description as DESCRIPTION,
        A.time_qty AS TIME_QTY,
        A.time_um AS TIME_UM,                                                                
        A.status as STATUS,
        A.startdate as STARTDATE, 
        A.enddate as ENDDATE,                                       
        A.reqid as REQID
    FROM TORP_WORKORDERS A
    ORDER BY REQID
    """, conn)


    df_woassignedto = pd.read_sql_query("""
    SELECT 
        A.userid as USERID, 
        A.woid as WOID, 
        A.status as STATUS, 
        B.name as USERNAME 
    FROM TORP_WOASSIGNEDTO A
    INNER JOIN TORP_USERS B ON B.code = A.userid
    ORDER BY WOID
    """, conn)


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
                    request.tdtl[0], next_reqid, "ACTIVE"

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
               
            st.text_input(label=":blue[Requester]", value=request["Req_requester"], disabled=True)
            st.text_input(label=":blue[Request title]", value=request["Req_title"], disabled=True)
            st.text_area(label=":blue[Request description]", value=request["Req_description"], disabled=True)
            
            req_status_options = ['NEW', 'PENDING', 'ASSIGNED', 'WIP', 'COMPLETED', 'DELETED']
            idx_status = req_status_options.index(request["Req_status"])
            st.selectbox(label=":blue[Request status]", options=req_status_options, disabled=True, index=idx_status)

            df = request_manager.df_users
            # La lista di codici che vuoi convertire in descrizioni.
            tdtl_codes = request["Req_tdtl"]
            # Richiama la funzione per ogni codice nella lista.
            tdtl_descriptions = [get_description_from_code(df_users, code, "NAME") for code in tdtl_codes]
            st.multiselect(label=":blue[TD Team Leader]", options=tdtl_descriptions, default=tdtl_descriptions, key="sb_tdtl", disabled=True)

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

    #df_requests_grid['REQUESTERNAME'] = df_requests['REQUESTER'].apply(lambda requester_code: get_description_from_code(df_users, requester_code, "NAME"))


    if st.session_state.grid_refresh:
        st.session_state.grid_data = df_requests_grid.copy()
        st.session_state.grid_refresh = False    
        #df_requests_grid["INSDATE"] = pd.to_datetime(df_requests_grid["INSDATE"], format="%Y-%m-%d")

    cellStyle = JsCode("""
        function(params) {
            if (params.column.colId === 'REQID') {
                       return {
                        'backgroundColor': '#CCE9E4',
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
        st.session_state.grid_data = df_requests_grid.loc[df_requests_grid["REQUESTERNAME"] == requestername_filter].copy()
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

        tdtl_code = df_reqassignedto[df_reqassignedto["REQID"] == reqid]["USERID"].values[0]
        tdtl_name = get_description_from_code(df_users, tdtl_code, "NAME")

        # Dati aggiornati
        data_out = {
            "Column name": [
                "Request Id", "Insert date", "Status", "Department", "Requester", 
                "Product line", "Product family", "Type", "Category", "Detail", 
                "Title", "Description", "Tech Department Note", "Tech Department Team Leader"],
            "Column value": [
                reqid, insdate, status, dept_name, requester_name, pline_name, 
                family_name, type_name, category_name, detail_name, title, 
                description, note_td, tdtl_name]
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
                    background-color: lightblue;
                }
                #styled-table tr:nth-child(odd) {
                    background-color: #f9f9f9;
                }
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
    # Constants
    ACTIVE_STATUS = "ACTIVE"
    DISABLED_STATUS = "DISABLED"
    DEFAULT_DEPT_CODE = "DTD"
    REQ_STATUS_OPTIONS = ['NEW', 'PENDING', 'ASSIGNED', 'WIP', 'COMPLETED', 'DELETED']
    
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
        popup_title = f'Request {selected_row["IDROW"][0]}'
        
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

            # Extract request ID
            req_idrow = int(selected_row["IDROW"][0][1:])
            wo_idrow = int(selected_row["WOIDROW"][0])
            # Display request details
            st.text_input(label="Product family", value=selected_row['PR_FAMILY'][0], disabled=True)
            st.text_input(label="Category", value=selected_row['CATEGORY'][0], disabled=True)
            st.text_input(label="Title", value=selected_row['TITLE'][0], disabled=True)
            st.text_input(label="Detail", value=selected_row['DETAIL'][0], disabled=True)            
            st.text_area(label="Description", value=selected_row['DESCRIPTION'][0], disabled=True)
            st.divider()         
            idx_status = req_status_options.index(selected_row['STATUS'][0])
            req_status = st.selectbox(label="Status", options=req_status_options, disabled=False, index=idx_status)
            req_notes = st.text_area(label="Notes", value=selected_row['NOTES'][0], disabled=False)
            if wo_idrow > 0:
                wo_nr = "W" + str(selected_row['WOIDROW'][0]).zfill(4)
            else:
                wo_nr = ""
            req_woassigned = st.text_input(label="Work Order", value=wo_nr, disabled=True)

            if (selected_row['NOTES'][0] == req_notes) and (selected_row['STATUS'][0] == req_status):
                disable_save_button = True
            else:
                disable_save_button = False    
            # Handle save action
            if st.button("Save", type="primary", disabled=disable_save_button, key="req_save_button"):
                success = update_request_fn(req_idrow, req_status, req_notes)               
                if success:
                    st.session_state.grid_refresh = True
                    st.session_state.grid_response = None
                    st.success("Update completed successfully!")
                    
                    st.session_state.need_refresh = True
                    time.sleep(3)
                    reset_application_state()
                    st.rerun()


            return False

        return dialog_content()

#######################################
    def show_workorder_dialog(selected_row, df_workorders, df_woassegnedto, df_users, active_status, default_dept_code, req_status_options, save_workorder_fn, save_woassignments_fn):
        """
        Display and handle the request modification dialog.
        
        Args:
            selected_row: The currently selected grid row
            df_woassegnedto: DataFrame of request assignments
            df_users: DataFrame of users
            req_status_options: List of available status options
            default_dept_code: Default department code
            update_request_fn: Function to update request status and notes
            update_assignments_fn: Function to update request assignments
        """
        popup_title = f'Work Order related to request {selected_row["IDROW"][0]}'
        
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
            reqidrow = int(selected_row["IDROW"][0][1:])
            woidrow = int(selected_row["WOIDROW"][0])
            # Display request details
#            st.text_input(label="Product family", value=selected_row['PR_FAMILY'][0], disabled=True)
#            st.text_input(label="Category", value=selected_row['CATEGORY'][0], disabled=True)
            st.text_input(label="Title", value=selected_row['TITLE'][0], disabled=True)
            st.text_area(label="Detail", value=selected_row['DETAIL'][0], disabled=True)
            # if selected_rows['NOTES'][0]:
            #     st.text_area(label="Notes", value=selected_row['NOTES'][0], disabled=True)
            #st.divider()
            wo_type_options=["Standard", "APQP Project"]  #APQP -> ADVANCED PRODUCT QUALITY PLANNING"  
            if woidrow > 0:
                wo_nr = "W" + str(woidrow).zfill(4)
                wo_type_default = list(df_workorders[df_workorders["IDROW"] == woidrow]["TYPE"])[0]
                wo_type_index = wo_type_options.index(wo_type_default)
                wo_startdate_default = list(df_workorders[df_workorders["IDROW"] == woidrow]["STARTDATE"])[0]
                wo_enddate_default = list(df_workorders[df_workorders["IDROW"] == woidrow]["ENDDATE"])[0]
                wo_notes_default = list(df_workorders[df_workorders["IDROW"] == woidrow]["NOTES"])[0]                
            else:
                wo_nr = ""
                wo_type_index = 0
                wo_startdate_default = None
                wo_enddate_default = None
                wo_notes_default = None                    
            
            wo_idrow = st.text_input(label="Work Order", value=wo_nr, disabled=True)        
            wo_type = st.selectbox(label="Type(:red[*])", options=wo_type_options, index=wo_type_index, disabled=False)            
            wo_startdate = st.date_input(label="Start date(:red[*])", format="DD/MM/YYYY", value=wo_startdate_default, disabled=False)
            wo_enddate = st.date_input(label="End date(:red[*])", format="DD/MM/YYYY", value=wo_enddate_default, disabled=False)
            wo_notes = st.text_area(label="TechDept notes", value=wo_notes_default, disabled=False)
            # Tech Dept (TD) user assignment selection
            filtered_woassignedto = df_woassegnedto[
                (df_woassegnedto["WOIDROW"] == woidrow) & 
                (df_woassegnedto["STATUS"] == active_status)
            ]

            wo_assignedto_default = list(filtered_woassignedto["USERNAME"])
            df_tdusers = df_users[df_users["DEPTCODE"] == default_dept_code]
            wo_assignedto_option = list(df_tdusers["NAME"])
            wo_assignedto_title = "Assigned to (:red[*]):"
            wo_assignedto = st.multiselect(
                label=wo_assignedto_title, 
                options=wo_assignedto_option, 
                default=wo_assignedto_default, 
                max_selections=3,
                disabled=False
            )


            if woidrow > 0:
                if (wo_type == wo_type_default and wo_startdate == wo_startdate_default and wo_enddate == wo_enddate_default and wo_assignedto == wo_assignedto_default):
                    disable_save_button = True
                else:
                    disable_save_button = False    
            else:
                if not (wo_type and wo_startdate and wo_enddate and wo_assignedto):
                    disable_save_button = True
                else:
                    disable_save_button = False    
            # Handle save action
            if st.button("Save", type="primary", disabled=disable_save_button, key="wo_save_button"):
                wo = {"idrow":0, "type": wo_type, "startdate": wo_startdate, "endate": wo_enddate, "title": selected_row["TITLE"][0], "notes": wo_notes, "status": ACTIVE_STATUS, "reqidrow": reqidrow}
                wo_idrow, success = save_workorder(wo)
                if success:
#                    st.success(f"Work order W{str(wo_idrow).zfill(4)} created successfully!")
                    success = save_workorder_assignments(wo_idrow, wo_assignedto, df_users, df_woassegnedto)
                    success = update_request(reqidrow, "ASSIGNED", selected_row['NOTES'][0], wo_idrow)
                    if success:
                        st.session_state.grid_refresh = True
                        st.session_state.grid_response = None
                        st.success(f"Work order W{str(wo_idrow).zfill(4)} assigned successfully!")
                    
                    st.session_state.need_refresh = True
                    time.sleep(3)
                    reset_application_state()
                    st.rerun()

            return False

        return dialog_content()
#######################################

    # # Database queries
    # def fetch_requests():
    #     query = """
    #     SELECT 
    #         idrow as IDROW, 
    #         status as STATUS,
    #         insdate as DATE, 
    #         deptcode as DEPTCODE, 
    #         requestername as REQUESTERNAME,
    #         priority as PRIORITY, 
    #         pline as PR_LINE, 
    #         pfamily as PR_FAMILY,
    #         type as TYPE, 
    #         category as CATEGORY, 
    #         title as TITLE,
    #         description as DESCRIPTION,
    #         notes as NOTES,
    #         woidrow as WOIDROW
    #         detail as DETAIL,
    #     FROM TORP_REQUESTS
    #     ORDER BY IDROW DESC
    #     """
    #     df = pd.read_sql_query(query, conn)
    #     df["DATE"] = pd.to_datetime(df["DATE"], format="%Y-%m-%d")
    #     df["IDROW"] = 'R' + df["IDROW"].astype(str).str.zfill(4)
    #     return df

    # def fetch_users():
    #     query = """
    #     SELECT 
    #         A.code AS CODE, 
    #         A.name AS NAME, 
    #         A.deptcode AS DEPTCODE, 
    #         B.name AS DEPTNAME
    #     FROM TORP_USERS A
    #     INNER JOIN TORP_DEPARTMENTS B ON B.code = A.deptcode
    #     ORDER BY A.name
    #     """
    #     return pd.read_sql_query(query, conn)
    

    # Database update functions
    def update_request(idrow_nr, new_status, new_notes, new_woidrow=0):
        try:
            cursor.execute(
                "UPDATE TORP_REQUESTS SET status = ?, notes = ?, woidrow = ? WHERE idrow = ?",
                (new_status, new_notes, new_woidrow, idrow_nr)
            )
            return True
        except Exception as e:
            st.error(f"Error updating request status: {str(e)}", icon="🚨")
            return False

    def save_workorder(wo: dict):
        # Get next available row ID
        try:
            cursor.execute('SELECT MAX(idrow) FROM TORP_WORKORDERS')
            max_idrow = cursor.fetchone()[0]
            if max_idrow is not None:
                next_rownr = max_idrow + 1
            else:
                next_rownr = 1    
                
            sql = """
                    INSERT INTO TORP_WORKORDERS (
                        idrow, type, startdate, enddate, 
                        title, notes, status, reqidrow
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
            values = (
                    next_rownr, wo["type"], wo["startdate"],wo["endate"],
                    wo["title"], wo["notes"], wo["status"], wo["reqidrow"]
                )
                
            cursor.execute(sql, values)
            conn.commit()
            return next_rownr, True
                
        except Exception as e:
            st.error(f"**ERROR inserting request in TORP_WORKORDERS: \n{e}", icon="🚨")
            return 0, False

        
    def save_workorder_assignments(wo_idrow, assigned_users, df_users, df_woassegnedto):
        try:
            # Disable existing assignments
            cursor.execute(
                "UPDATE TORP_WOASSIGNEDTO SET status = ? WHERE woidrow = ?",
                (DISABLED_STATUS, wo_idrow)
            )
            
            # Add new assignments
            for user_name in assigned_users:
                user_code = df_users[df_users["NAME"] == user_name]["CODE"].iloc[0]
                existing_assignment = df_woassegnedto[
                    (df_woassegnedto['WOIDROW'] == wo_idrow) & 
                    (df_woassegnedto['USERCODE'] == user_code)
                ]
                
                if existing_assignment.empty:
                    cursor.execute(
                        "INSERT INTO TORP_WOASSIGNEDTO (usercode, woidrow, status) VALUES (?, ?, ?)",
                        (user_code, wo_idrow, ACTIVE_STATUS)
                    )
                else:
                    cursor.execute(
                        "UPDATE TORP_WOASSIGNEDTO SET status = ? WHERE woidrow = ? AND usercode = ?",
                        (ACTIVE_STATUS, wo_idrow, user_code)
                    )
            
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Error updating workorder assignments: {str(e)}", icon="🚨")
            conn.rollback()
            return False



    # Grid configuration
    def configure_grid(df_requests):
        cell_style = JsCode("""
            function(params) {
                if (params.column.colId === 'IDROW') {
                    return {
                        'backgroundColor': '#ECEBBD',
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
        builder.configure_column("IDROW", cellStyle=cell_style)
        builder.configure_selection(selection_mode='single', use_checkbox=True, header_checkbox=True)
        
        return builder.build()


    # Main execution
    # df_users = fetch_users()    
    # df_requests = fetch_requests()
    # df_workorders = fetch_workorders()    
    # df_woassegnedto = fetch_assigned_wo()

    load_initial_data()
    load_requests_data()
    load_workorders_data()
    # Initialize session state
    if "grid_data" not in st.session_state:
        st.session_state.grid_data = df_requests.copy()
    if "grid_response" not in st.session_state:
        st.session_state.grid_response = None
    if "grid_refresh_key" not in st.session_state: 
        st.session_state.grid_refresh_key = "initial"    

    # Sidebar filters
    st.sidebar.header("Filters")
    req_status_options = df_requests['STATUS'].drop_duplicates().sort_values()
    status_filter = st.sidebar.selectbox(
        "Select a Status value:", 
        req_status_options, 
        index=None,
        key='Status_value'
    )
    req_pline_options = df_requests['PR_LINE'].drop_duplicates().sort_values()
    pline_filter = st.sidebar.selectbox(
        "Select a Product Line value:", 
        req_pline_options, 
        index=None,
        key='Pline_value'
    )

# Apply filters 
    filtered_data = df_requests.copy() 
    if status_filter: 
        filtered_data = filtered_data[filtered_data["STATUS"] == status_filter] 
    if pline_filter: 
        filtered_data = filtered_data[filtered_data["PR_LINE"] == pline_filter] 
    st.session_state.grid_data = filtered_data
##################
    
    # Display grid
    st.subheader("Request list:")
    grid_options = configure_grid(st.session_state.grid_data)
    
    st.session_state.grid_response = AgGrid(
        st.session_state.grid_data,
        gridOptions=grid_options,
        allow_unsafe_jscode=True,
        theme="balham",
        fit_columns_on_grid_load=False,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.AS_INPUT,
        #key="main_grid"
        key=f"main_grid_{st.session_state.grid_refresh_key}"
    )
    # Add refresh button in a container below the grid
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Refresh", type="tertiary"):
                reset_application_state()
        with col2:
            if st.button("✏️ Modify", type="secondary"):
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
            if st.button("💎 Work Order", type="secondary"):
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
                            df_woassegnedto, 
                            df_users,
                            ACTIVE_STATUS, 
                            DEFAULT_DEPT_CODE,
                            REQ_STATUS_OPTIONS,
                            save_workorder,
                            save_workorder_assignments
                        )



#######################################################################################################
def manage_wo():
    pass

#######################################################################################################
def manage_wi():
# Sidebar per selezionare il work-order
    def fetch_users():
        query = """
        SELECT 
            A.code AS CODE, 
            A.name AS NAME, 
            A.deptcode AS DEPTCODE, 
            B.name AS DEPTNAME
        FROM TORP_USERS A
        INNER JOIN TORP_DEPARTMENTS B ON B.code = A.deptcode
        ORDER BY A.name
        """
        return pd.read_sql_query(query, conn)
    
    def fetch_workorders():
        query = """
        SELECT 
            A.idrow as IDROW, 
            A.type as TYPE, 
            A.startdate as STARTDATE, 
            A.enddate as ENDDATE,
            A.title as TITLE,
            A.notes as NOTES,
            A.status as STATUS,
            A.reqidrow as REQIDROW
        FROM TORP_WORKORDERS A
        ORDER BY REQIDROW
        """
        return pd.read_sql_query(query, conn)
    
    def fetch_assigned_wo():
        query = """
        SELECT 
            A.usercode as USERCODE, 
            A.woidrow as WOIDROW, 
            A.status as STATUS, 
            B.name as USERNAME 
        FROM TORP_WOASSIGNEDTO A
        INNER JOIN TORP_USERS B ON B.code = A.usercode
        ORDER BY WOIDROW
        """
        return pd.read_sql_query(query, conn)

    def convert_woidrow_to_str(value: int)-> str:
        return "W" + str(value).zfill(4)
    def convert_woidrow_to_int(value: str)-> int:
        return int(value[1:])
    def convert_reqidrow_to_str(value: int)-> str:
        return "R" + str(value).zfill(4)
    def convert_reqidrow_to_int(value: str)-> int:
        return int(value[1:])

    def save_work_item(witem: dict) -> Tuple[str, bool]:
        """Save request to database and return request number and status"""
        try:
        # # Get next available row ID
            cursor.execute('SELECT MAX(idrow) FROM TORP_WORKITEMS')
            max_idrow = cursor.fetchone()[0]
            if max_idrow is not None:
                next_idrow = max_idrow + 1
            else:
                next_idrow = 1  
                          
            sql = """
                INSERT INTO TORP_WORKITEMS (
                    idrow, ucode, tskgroup, tskdate, qty, um, 
                    description, notes, status, woidrow
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                next_idrow, witem["wi_ucode"], witem["wi_tskgroup"], witem["wi_tskdate"], witem["wi_qty"], witem["wi_um"],
                witem["wi_desc"], witem["wi_notes"], witem["wi_status"], witem["wi_woidrow"]
            )
            
            cursor.execute(sql, values)
            conn.commit()
            return next_idrow, True
        
        except Exception as e:
            st.error(f"**ERROR inserting data in table TORP_WORKITEM: \n{e}", icon="🚨")
            return "", False

        
    df_users = fetch_users()    
    df_workorders = fetch_workorders()    
    df_woassegnedto = fetch_assigned_wo()

    # Inzialize sessione state
    if 'selected_username' not in st.session_state:
        st.session_state.selected_username = False
    if 'selected_wo' not in st.session_state:
        st.session_state.selected_wo = False

    # Aggiungi un divisore nella sidebar
    st.sidebar.divider()
    st.sidebar.header("Work order filters")
    
    unique_usernames = df_woassegnedto['USERNAME'].unique()
    sorted_usernames = sorted(unique_usernames)
    wo_username_options = list(sorted_usernames)
    
    selected_username = st.sidebar.selectbox(label="TD user:", options=wo_username_options, index=None)
    
    df_wi_usercode = df_woassegnedto[df_woassegnedto['USERNAME'] == selected_username]["USERCODE"].unique()
    wi_usercode = list(df_wi_usercode)

    if selected_username:
        st.session_state.selected_username = True


    wo_idrow = df_woassegnedto[df_woassegnedto['USERNAME'] == selected_username]['WOIDROW'].apply(convert_woidrow_to_str)
    unique_wo_idrow = wo_idrow.unique()
    sorted_wo_idrow = sorted(wo_idrow)
    wo_idrow_options = list(sorted_wo_idrow)
  
    selected_wo = st.sidebar.selectbox(label="Work-Order:", options=wo_idrow_options, index=None)
    if selected_wo:
        st.session_state.selected_wo = True

    # Input per inserire i dettagli del task svolto
    if st.session_state.selected_wo:
        st.header(f"Work Order {selected_wo}")
        with st.expander("WO details"):
            df_wo_out = pd.DataFrame()
            df_wo = df_workorders[df_workorders["IDROW"].apply(convert_woidrow_to_str) == selected_wo]
            df_wo_out['IDROW'] = df_wo['IDROW'].apply(convert_woidrow_to_str)
            df_wo_out['TYPE'] = df_wo['TYPE']
            df_wo_out['STARTDATE'] = df_wo['STARTDATE']
            df_wo_out['ENDDATE'] = df_wo['ENDDATE']
            df_wo_out['TITLE'] = df_wo['TITLE']
            df_wo_out['NOTES'] = df_wo['NOTES']  
            df_wo_out['REQIDROW'] = df_wo['REQIDROW'].apply(convert_reqidrow_to_str)
            st.dataframe(df_wo_out, use_container_width=True, hide_index=True)
        
        st.subheader(f"Insert a Work Item")
        wi_description = st.text_input(label="Work item description:", value="")
        wi_duration = st.number_input(label="Time spent (in hours):", min_value=0.0, step=0.5)
        wi_date = st.date_input("Date of execution", format="DD/MM/YYYY", disabled=False)
        wi_notes = st.text_area("Notes")
        wo_nr = convert_woidrow_to_int(selected_wo)
        work_item = {"wi_ucode": wi_usercode[0], "wi_tskgroup": "standard", "wi_tskdate": wi_date,"wi_qty": wi_duration, "wi_um": "H", "wi_desc": wi_description, "wi_notes": wi_notes, "wi_status": "ACTIVE", "wi_woidrow": wo_nr}
        # Bottone per aggiungere il task
        if st.button("Save Work Item", type="primary"):
            if wi_description and wi_duration > 0:
                wi_nr, rc = save_work_item(work_item)
                #st.success(f"Task '{wi_description}' di durata {wi_duration} ore aggiunto per {selected_wo} il {wi_date}.")
                if rc == True:
                    st.success(f"Task {wi_nr} saved successfully!")

            else:
                st.error("Per favore, inserisci una descrizione valida e una durata maggiore di zero.")
    else:
        st.header(f"Please select a work order first!")

        # Visualizzazione dei task (per esempio, da salvare in un dataframe)
        # Qui potresti implementare la logica per memorizzare e mostrare i task inseriti

#######################################################################################################
# def my_test():
#     pass

#######################################################################################################
def main():
#   if not check_password():
#     st.stop()
  open_sqlitecloud_db()
  load_initial_data()
  st.set_page_config(layout="wide")  
  page_names_to_funcs = {
    " ℹ️  App Info": display_app_info,
    "📄 Insert Request": insert_request,
    "🔍 View Request ": view_request,
    "🗂️ Manage Request": manage_request,
    "📌 Manage Work Orders": manage_wo,
    "🛠️ Manage Work Items": manage_wi,
    "🔐 Close db": close_sqlitecloud_db,
    "MYTEST": my_test()
}    
  # Aggiungi l'immagine alla sidebar 
  st.sidebar.image("https://iph.it/wp-content/uploads/2020/02/logo-scritta.png", width=150)
  demo_name = st.sidebar.selectbox("Choose a function", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()


if __name__ == "__main__":
    main()
