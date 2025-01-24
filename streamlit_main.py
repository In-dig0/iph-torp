# Python built-in libraries
import datetime
import os
import io
import time
import json
#import urllib.parse
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List

# 3th party packages
import streamlit as st
import pandas as pd
import sqlitecloud
import pytz 
import hmac
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode
import numpy as np
#from streamlit_extras.app_logo import add_logo
#from streamlit_modal import Modal
#import extra_streamlit_components as stx


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
# def get_next_rowid(obj_class: str, obj_year: str, obj_pline=None) -> str:
#     """Get next available row ID"""

#     try:
#         self.cursor.execute('SELECT prefix AS PREFIX, prog AS PROG FROM TORP_OBJ_NUMERATOR WHERE obj_class=? and obj_year=? and obj_pline=?', (obj_class, obj_year, obj_pline))
#         results = self.cursor.fetchone()[0]
#         prefix = results['PREFIX']
#         prog = results['PROG']
#         rowid = prefix + prog.zfill(3)
#     except Exception as errMsg:
#         prefix = obj_class[1]
#         prog = 1
#         rowid = prefix + prog.zfill(3)
   
#     return rowid
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

    class RequestManager:
        """Class to handle request management operations"""
    
        PRODUCT_FAMILIES = {
            "POWER TAKE OFFs": ["GEARBOX PTO", "ENGINE PTO", "SPLIT SHAFT PTO", "PARALLEL GEARBOXES"],
            "HYDRAULICS": ["PUMPS", "MOTORS", "VALVES", "WET KITS"],
            "CYLINDERS": ["FRONT-END CYLINDERS", "UNDERBODY CYLINDERS", "DOUBLE ACTING CYLINDERS", "BRACKETS FOR CYLINDERS"],
            "ALL": ["--"]
        }
        
        REQUEST_CATEGORIES = {
            "PRODUCT": ["NEW PRODUCT", "PRODUCT CHANGE", "OBSOLETE PRODUCT", "PRODUCT VALIDATION"],
            "DOCUMENTATION": ["WEBPTO", "DRAWING", "IMDS (INTERNATIONAL MATERIAL DATA SYSTEM)", "CATALOGUE"],
            "SERVICE": ["VISITING CUSTOMER PLANT", "VISITING SUPPLIER PLANT"]
        }

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

            self.df_detail["DETAIL_KEY"] = self.df_detail["NAME"]

        def save_request(self, request: RequestData) -> Tuple[str, int]:
            """Save request to database and return request number and status"""
            try:
                next_rownr = self._get_next_row_id()
                
                sql = """
                    INSERT INTO TORP_REQUESTS (
                        idrow, usercode, status, deptcode, requestername, 
                        priority, pline, pfamily, type, category, 
                        title, description, insdate, notes, woidrow, detail
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    next_rownr, request.user, request.status, request.dept,
                    request.requester, request.priority, request.pline,
                    request.pfamily, request.type, request.category,
                    request.title, request.description, request.insdate, 
                    None, 0, request.detail
                )
                
                self.cursor.execute(sql, values)
                self.conn.commit()
                return f"R{str(next_rownr).zfill(4)}", 0
                
            except Exception as e:
                st.error(f"**ERROR inserting request in TORP_REQUESTS: \n{e}", icon="🚨")
                return "", 1

        def _get_next_row_id(self) -> int:
            """Get next available row ID"""
            self.cursor.execute('SELECT MAX(idrow) FROM TORP_REQUESTS')
            max_idrow = self.cursor.fetchone()[0]
            return (max_idrow + 1) if max_idrow is not None else 1
        
    # Inizializzazione delle chiavi di stato per i widget
    FORM_KEYS = [
        'sb_dept', 'sb_requester', 'sb_pline', 'sb_pfamily',
        'sb_type', 'sb_category', 'sb_detail', #'sb_priority',
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
            
#                st.text_input("Request Nr", value=req_nr, disabled=True)
            st.text_input("Requester", value=request["Req_requester"], disabled=True)
            st.text_input("Request title", value=request["Req_title"], disabled=True)
            st.text_area("Request description", value=request["Req_description"], disabled=True)
            
            req_status_options = ['NEW', 'PENDING', 'ASSIGNED', 'WIP', 'COMPLETED', 'DELETED']
            idx_status = req_status_options.index(request["Req_status"])
            st.selectbox("Request status", req_status_options, disabled=True, index=idx_status)
            
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

    def create_form() -> RequestData:
        """Create and handle the request form"""
        st.header(":orange[Requester informations]")
        
        # Department and requester selection
        department = st.selectbox(
            ":blue[Department(:red[*])]", 
            request_manager.df_depts['DEPT_KEY'].tolist(),
            index=None,
            key="sb_dept"
        )
        
        requester = None
        if department:
            filtered_users = request_manager.df_users[
                request_manager.df_users["DEPTNAME"] == department
            ]
            requester = st.selectbox(
                ":blue[Requester(:red[*])]", 
                filtered_users["NAME"].tolist(),
                index=None,
                key="sb_requester"
            )

        st.header(":orange[Product group informations]")
        
        # Product line and family selection
        pline = st.selectbox(
            ":blue[Product line(:red[*])]",
            ["POWER TAKE OFFs", "HYDRAULICS", "CYLINDERS", "ALL"],
            index=None,
            key="sb_pline"
        )
        
        pfamily = None
        if pline in RequestManager.PRODUCT_FAMILIES:
            pfamily = st.selectbox(
                ":blue[Product family(:red[*])]",
                RequestManager.PRODUCT_FAMILIES[pline],
                index=None,
                key="sb_pfamily"
            )

        st.header(":orange[Request informations]")
        
        # Request details
        priority = st.selectbox(
            ":blue[Request Priority(:red[*])]",
            ["High", "Medium", "Low"],
            index=1,
            key="sb_priority"
        )
        
        req_type = st.selectbox(
            ":blue[Request type (:red[*])]",
            ["PRODUCT","COMPONENT", "DOCUMENTATION",  "SERVICE"],
            index=None,
            key="sb_type"
        )
        
        category = None
        if req_type in RequestManager.REQUEST_CATEGORIES:
            category = st.selectbox(
                ":blue[Request category(:red[*])]",
                RequestManager.REQUEST_CATEGORIES[req_type],
                index=None,
                key="sb_category"
            )

        detail = None
        detail = st.selectbox(
            ":blue[Request detail(:red[*])]",
            request_manager.df_detail["DETAIL_KEY"].tolist(),
            index=None,
            key="sb_detail"
        )

        df_detail = request_manager.df_detail[request_manager.df_detail["NAME"] == detail]["CODE"]
        # Verifica se df_detail non è vuoto
        if not df_detail.empty:
            detail_code = list(df_detail)[0]
            st.write(detail_code)
        else:
            detail_code = ""
            
        title = None
        title = st.text_input(":blue[Request title(:red[*])]", key="ti_title")
        description = None
        description = st.text_area(":blue[Request description]", key="ti_description")

        return RequestData(
            insdate=datetime.datetime.now().strftime("%Y-%m-%d"),
            user="RB",
            status="NEW",
            dept=department,
            requester=requester,
            priority=priority,
            pline=pline,
            pfamily=pfamily,
            type=req_type,
            category=category,
            detail=detail_code,            
            title=title,
            description=description 

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
    
    #save_botton_disabled = False
    
    # st.write(f"Dept:{request_data.dept}\n-Requester:{request_data.requester}\n-Pline:{request_data.pline}\n")
    # st.write(f"Pfamily:{request_data.pfamily}\n-Type:{request_data.type}\n-Category:{request_data.category}\n")
    # st.write(f"Detail:{request_data.detail}-\nTitle:{request_data.title}-\nDescription:{request_data.description}")

    if st.button("Submit", type="primary", disabled=save_botton_disabled):
        req_nr, rc = request_manager.save_request(request_data)
        if rc == 0:
            st.session_state.form_submitted = True
            display_request_popup(req_nr, {
                "Req_requester": request_data.requester,
                "Req_title": request_data.title,
                "Req_description": request_data.description,
                "Req_status": request_data.status
            })


#######################################################################################################
def view_request():
    # Inzialise variables
    rc = 0
    req_nr = ""

    # Aggiungere all'inizio della funzione assign_request(), dopo le altre inizializzazioni
    if "grid_refresh" not in st.session_state:
        st.session_state.grid_refresh = False
    
    df_requests = pd.read_sql_query("""
    SELECT idrow as IDROW, usercode as USERCODE, status as STATUS, 
        insdate as DATE, deptcode as DEPTCODE, requestername as REQUESTERNAME, 
        priority as PRIORITY, pline as PR_LINE, pfamily as PR_FAMILY, 
        type as TYPE, category as CATEGORY, title as TITLE, 
        description as DESCRIPTION, notes as NOTES, woidrow as WOIDROW, detail AS DETAIL 
    FROM TORP_REQUESTS
    ORDER by IDROW desc
    """, conn)

    # Aggiungi questo dopo il caricamento dei dati
    if st.session_state.grid_refresh:
        st.session_state.grid_data = df_requests.copy()
        st.session_state.grid_refresh = False    
        df_requests["DATE"] = pd.to_datetime(df_requests["DATE"], format="%Y-%m-%d")

    df_requests["IDROW"] = 'R' + df_requests["IDROW"].astype(str).str.zfill(4)
    cellStyle = JsCode("""
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

    grid_builder = GridOptionsBuilder.from_dataframe(df_requests)
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
    grid_builder.configure_column(
    field="DATE",
    header_name="INSERT DATE",
    valueFormatter="value != undefined ? new Date(value).toLocaleString('it-IT', {dateStyle:'short'}): ''",
    )
    grid_builder.configure_column("IDROW", cellStyle=cellStyle)   
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
        st.session_state.grid_data = df_requests.copy()  # Copia per evitare modifiche al DataFrame originale
    if "grid_response" not in st.session_state:
        st.session_state.grid_response = None

    # Sidebar controls - Filters
    st.sidebar.header("Filters")
    ct_requester = df_requests['REQUESTERNAME'].drop_duplicates()
    df_ct_requester = pd.DataFrame({"REQUESTERNAME": ct_requester}).sort_values(by="REQUESTERNAME")

    # Get an optional value requester filter
    requester_filter = st.sidebar.selectbox("Select a Requester:", df_ct_requester, index=None)

    # Filtro e AGGIORNAMENTO DEI DATI (utilizzando la sessione)
    if requester_filter:
        st.session_state.grid_data = df_requests.loc[df_requests["REQUESTERNAME"] == requester_filter].copy()
    else:
        st.session_state.grid_data = df_requests.copy() # Mostra tutti i dati se il filtro è None

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
#        selected_row = selected_row[0] 
        data_out = {
            'Column name': ["Request Number", "Insert date", "User", "Status", "Department", "Requester", "Priority", "Product Line", "Product Family", "Type", "Category", "Detail", "Title", "Description"],
            'Column value': [selected_row['IDROW'][0], selected_row['DATE'][0], selected_row['USERCODE'][0], selected_row['STATUS'][0], selected_row['DEPTCODE'][0], selected_row['REQUESTERNAME'][0], selected_row['PRIORITY'][0], selected_row['PR_LINE'][0], selected_row['PR_FAMILY'][0], selected_row['TYPE'][0], selected_row['CATEGORY'][0], selected_row['DETAIL'][0], selected_row['TITLE'][0], selected_row['DESCRIPTION'][0]]
        }
        df_out = pd.DataFrame(data_out)
        st.subheader("Request details:")         
        st.dataframe(df_out, use_container_width=True, height=500, hide_index=True)


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

    # Database queries
    def fetch_requests():
        query = """
        SELECT 
            idrow as IDROW, 
            status as STATUS,
            insdate as DATE, 
            deptcode as DEPTCODE, 
            requestername as REQUESTERNAME,
            priority as PRIORITY, 
            pline as PR_LINE, 
            pfamily as PR_FAMILY,
            type as TYPE, 
            category as CATEGORY, 
            title as TITLE,
            description as DESCRIPTION,
            notes as NOTES,
            woidrow as WOIDROW
            detail as DETAIL,
        FROM TORP_REQUESTS
        ORDER BY IDROW DESC
        """
        df = pd.read_sql_query(query, conn)
        df["DATE"] = pd.to_datetime(df["DATE"], format="%Y-%m-%d")
        df["IDROW"] = 'R' + df["IDROW"].astype(str).str.zfill(4)
        return df

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
    df_users = fetch_users()    
    df_requests = fetch_requests()
    df_workorders = fetch_workorders()    
    df_woassegnedto = fetch_assigned_wo()

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
def my_test():
    pass

#######################################################################################################
def main():
#   if not check_password():
#     st.stop()
  open_sqlitecloud_db()
  #load_data_from_db()
  st.set_page_config(layout="wide")  
  page_names_to_funcs = {
    " ℹ️  App Info": display_app_info,
    "📄 Insert Request": insert_request,
    "🔍 View Request ": view_request,
    "🗂️ Manage Request": manage_request,
    "📌 Manage Work Orders": manage_wo,
    "🛠️ Manage Work Items": manage_wi,
    "🔐 Close db": close_sqlitecloud_db,
    "MYTEST": my_test
}    
  # Aggiungi l'immagine alla sidebar 
  st.sidebar.image("https://iph.it/wp-content/uploads/2020/02/logo-scritta.png", width=150)
  demo_name = st.sidebar.selectbox("Choose a function", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()


if __name__ == "__main__":
    main()
