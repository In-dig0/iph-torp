# Python built-in libraries
import datetime
import os
import io
import time
import json
import urllib.parse

# 3th party packages
import streamlit as st
import pandas as pd
import sqlitecloud
import pytz 
import hmac
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode
import numpy as np
#from streamlit_modal import Modal
#import extra_streamlit_components as stx



# Global constants
APPNAME = "TORP" #IPH Technical Office Request POC (Proof Of Concept)
APPCODE = "TORP"
APPVERSION = "0.1"

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
    
    import streamlit as st

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
def insert_request()-> None:
    """ Function to insert a new request """    
    
    @st.dialog("Request submitted!", width="large")
    def display_request_popup(req_nr: str, request: dict)-> None:
        """ Function to get request information from user """
        st.markdown(f"Request :green-background[**{req_nr}**] submitted! Here are the details:")
        df_request = pd.DataFrame([request])
        st.dataframe(df_request, use_container_width=True, hide_index=True)
        time.sleep(10)

#######################################################################################################
    def save_request_to_sqlitecloud(row:dict):
        """ Save new request into SQLite Cloud Database """
        # Inzialise variables
        rc = 0
        req_nr = ""
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
        # Connect to SQLite Cloud platform
        try:
            conn = sqlitecloud.connect(conn_string)
        except Exception as errMsg:
            st.error(f"**ERROR connecting to database: \n{errMsg}", icon="🚨")
        
        # Open SQLite database
        conn.execute(f"USE DATABASE {db_name}")
        cursor = conn.cursor()

        # Calculate the next rowid
        cursor.execute('SELECT MAX(r_id) FROM TORP_REQUESTS')
        max_rowid = cursor.fetchone()[0]
        next_rownr = (max_rowid + 1) if max_rowid is not None else 1

        # Setup sqlcode for inserting applog as a new row
        sqlcode = """INSERT INTO TORP_REQUESTS (r_id, r_user, r_status, r_dept, r_requester, r_priority, r_pline, r_pfamily, r_type, r_category, r_title, r_detail, r_insdate) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """    
        
        # Setup row values
        values = (next_rownr, row["Req_user"], row["Req_status"], row["Req_dept"], row["Req_requester"], row["Req_priority"], row["Req_pline"], row["Req_pfamily"], row["Req_type"], row["Req_category"], row["Req_title"], row["Req_detail"], row["Req_insdate"])
        try:
            cursor.execute(sqlcode, values)
        #    cursor.lastrowid
        except Exception as errMsg:
            st.error(f"**ERROR inserting request in tab TORP_REQUESTS: \n{errMsg}", icon="🚨")
            rc = 1
        else:
            conn.commit()
            req_nr = f"R-{str(next_rownr).zfill(4)}"
            rc = 0
       
        cursor.close()    
        if conn:
            conn.close()

        return req_nr, rc


    sb_dept_key = "sb_dept"
    reset_sb_dept_key = "reset_sb_dept"
    req_dept_option = ["DMN-ACCOUNTING", "DTD-DESIGN TECHNICAL DEPARTMENT", "COMMERCIALE AFTER MARKET"]
    
    sb_requester_key = "sb_requester"
    reset_sb_requester_key = "reset_sb_requester"
    req_requester_option_01 = ["COMELLINI GIORGIO", "ROMANI CORRADO", "ROSSI PAOLA"]
    req_requester_option_02 = ["CARLINI MICHELE", "FENARA GABRIELE", "PALMA NICOLA"]
    req_requester_option_03 = ["GIORGI IVAN", "ANGOTTI FRANCESCO", "BALDINI ROBERTO"]

    sb_pline_key = "sb_pline"
    reset_sb_pline_key = "reset_sb_pline"
    req_pline_option = ["POWER TAKE OFFs", "HYDRAULICS", "CYLINDERS", "ALL"]

    sb_pfamily_key = "sb_pfamily"
    reset_sb_pfamily_key = "reset_sb_pfamily"
    req_pfamily_option_01 = ["GEARBOX PTO", "ENGINE PTO", "SPLIT SHAFT PTO", "PARALLEL GEARBOXES"]
    req_pfamily_option_02 = ["PUMPS", "MOTORS", "VALVES", "WET KITS"]
    req_pfamily_option_03 = ["FRONT-END CYLINDERS", "UNDERBODY CYLINDERS", "DOUBLE ACTING CYLINDERS", "BRACKETS FOR CYLINDERS"]

    sb_priority_key = "sb_priority"
    reset_sb_priority_key = "reset_sb_priority"
    req_priority_option = ["High", "Medium", "Low"]

    sb_type_key = "sb_type"
    reset_sb_type_key = "reset_sb_type"
    req_type_option = ["DOCUMENTATION", "PRODUCT", "SERVICE"]

    sb_category_key = "sb_category"
    reset_sb_category_key = "reset_sb_category"
    req_category_option_01 = ["NEW PRODUCT", "PRODUCT CHANG", "OBSOLETE PRODUCT", "PRODUCT VALIDATION"] 
    req_category_option_02 = ["WEBPTO", "DRAWING", "IMDS (INTERNATIONAL MATERIAL DATA SYSTEM)", "CATALOGUE"]
    req_category_option_03 = ["VISITING CUSTOMER PLANT", "VISITING SUPPLIER PLANT"]

    ti_title_key = "ti_title"
    reset_ti_title_key = "reset_ti_detail"
    ti_detail_key = "ti_detail"
    reset_ti_detail_key = "reset_ti_detail"

    # Gestione reset selectbox
    if reset_sb_dept_key not in st.session_state:
        st.session_state[reset_sb_dept_key] = False
    if reset_sb_requester_key not in st.session_state:
        st.session_state[reset_sb_requester_key] = False
    if reset_sb_pline_key not in st.session_state:
        st.session_state[reset_sb_pline_key] = False 
    if reset_sb_pfamily_key not in st.session_state:
        st.session_state[reset_sb_pfamily_key] = False
    if reset_sb_type_key not in st.session_state:
        st.session_state[reset_sb_type_key] = False 
    if reset_sb_category_key not in st.session_state:
        st.session_state[reset_sb_category_key] = False                                        

    if st.session_state[reset_sb_dept_key]:
        st.session_state[sb_dept_key] = None
        st.session_state[reset_sb_dept_key] = False
        st.session_state[sb_requester_key] = None
        st.session_state[reset_sb_requester_key] = False
        st.session_state[sb_pline_key] = None
        st.session_state[reset_sb_pline_key] = False   
        st.session_state[sb_pfamily_key] = None
        st.session_state[reset_sb_pfamily_key] = False  
        st.session_state[sb_type_key] = None
        st.session_state[reset_sb_type_key] = False  
        st.session_state[sb_category_key] = None
        st.session_state[reset_sb_category_key] = False                                         
        st.rerun()

    # Gestione reset text input
    if reset_ti_title_key not in st.session_state:
        st.session_state[reset_ti_title_key] = False
    if reset_ti_detail_key not in st.session_state:
        st.session_state[reset_ti_detail_key] = False    
    if st.session_state[reset_ti_title_key]:
        st.session_state[ti_title_key] = ""
        st.session_state[reset_ti_title_key] = False
        st.session_state[ti_detail_key] = ""
        st.session_state[reset_ti_detail_key] = False
        st.rerun()

    #Inizializzazione
    if sb_dept_key not in st.session_state:
        st.session_state[sb_dept_key] = None
    if sb_requester_key not in st.session_state:
        st.session_state[sb_requester_key] = None
    if sb_pline_key not in st.session_state:
        st.session_state[sb_pline_key] = None
    if sb_pfamily_key not in st.session_state:
        st.session_state[sb_pfamily_key] = None
    if sb_type_key not in st.session_state:
        st.session_state[sb_type_key] = None
    if sb_category_key not in st.session_state:
        st.session_state[sb_category_key] = None  

    if ti_title_key not in st.session_state:
        st.session_state[ti_title_key] = ""
    if ti_detail_key not in st.session_state:
        st.session_state[ti_detail_key] = ""

    #Inzialize variables
    req_department = ""
    req_requester = ""
    req_pline = ""
    req_pfamily = ""
    req_type = ""
    req_category = ""
    req_title = ""
    req_detail = ""          
    
    st.header(":orange[Requester informations]")
    req_department = st.selectbox("Department", req_dept_option, key=sb_dept_key)
    if req_department == "DMN-ACCOUNTING":
        req_requester = st.selectbox("Requester", req_requester_option_01, key=sb_requester_key)
    elif req_department == "DTD-DESIGN TECHNICAL DEPARTMENT":
        req_requester = st.selectbox("Requester", req_requester_option_02, key=sb_requester_key)            
    elif req_department == "COMMERCIALE AFTER MARKET":
        req_requester = st.selectbox("Requester", req_requester_option_03, key=sb_requester_key)
    st.divider()

    st.header(":orange[Product group informations]")
    req_pline = st.selectbox("Product line", req_pline_option, key=sb_pline_key)
    if req_pline == "POWER TAKE OFFs":
        req_pfamily = st.selectbox(":blue[Product family(:red[*])]", req_pfamily_option_01, index=None, key="sb_pfamily")
    elif req_pline == "HYDRAULICS":
        req_pfamily = st.selectbox(":blue[Product family(:red[*])]", req_pfamily_option_02, index=None, key="sb_pfamily")
    elif req_pline == "CYLINDERS":
        req_pfamily = st.selectbox(":blue[Product family(:red[*])]", req_pfamily_option_03, index=None, key="sb_pfamily")
    st.divider()

    st.header(":orange[Request informations]")
    req_priority = st.selectbox(":blue[Priority]", req_priority_option, index=1)
    req_type = st.selectbox(":blue[Request type (:red[*])]", req_type_option, index=None, key="sb_type")
    if req_type == "PRODUCT":
        req_category = st.selectbox(":blue[Request category(:red[*])]", req_category_option_01, index=None, key="sb_category")  
    elif req_type == "DOCUMENTATION":
        req_category = st.selectbox(":blue[Request category(:red[*])]", req_category_option_02, index=None, key="sb_category")  
    elif req_type == "SERVICE":
        req_category = st.selectbox(":blue[Request category(:red[*])]", req_category_option_03, index=None, key="sb_category")  
    
    req_title = st.text_input(":blue[Request title(:red[*])]", key=ti_title_key)
    req_detail = st.text_area(":blue[Request detail(:red[*])]", key=ti_detail_key)

    req_insdate = datetime.datetime.now().strftime("%Y-%m-%d")
    req_user = "RB"
    req_status = "NEW"
    request_record =    {
            "Req_insdate": req_insdate,
            "Req_user": req_user,
            "Req_status": req_status,
            "Req_dept": req_department,
            "Req_requester": req_requester,
            "Req_priority": req_priority,
            "Req_pline": req_pline,
            "Req_pfamily": req_pfamily,
            "Req_type": req_type,
            "Req_category": req_category,
            "Req_title": req_title,
            "Req_detail": req_detail
        }
    st.divider()
    if req_department and req_requester and req_pline and req_pfamily and req_priority and req_type and req_category and req_detail:
        if st.button("Submit", type="primary", disabled=False):
            req_nr = ""
            req_nr, rc = save_request_to_sqlitecloud(request_record)
            display_request_popup(req_nr, request_record)
            st.session_state[reset_sb_dept_key] = True
            st.session_state[reset_sb_requester_key] = True
            st.session_state[reset_sb_pline_key] = True
            st.session_state[reset_sb_pfamily_key] = True
            st.session_state[reset_sb_type_key] = True
            st.session_state[reset_sb_category_key] = True                                       
            st.session_state[reset_ti_title_key] = True
            st.session_state[reset_ti_detail_key] = True            
            st.rerun()
    else:
        st.button("Submit", type="primary", disabled=True)

#######################################################################################################
def view_request():
    # Inzialise variables
    rc = 0
    req_nr = ""
    db_link = ""
    db_apikey = ""
    db_name = ""

    # Aggiungere all'inizio della funzione assign_request(), dopo le altre inizializzazioni
    if "grid_refresh" not in st.session_state:
        st.session_state.grid_refresh = False
    
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
    # Connect to SQLite Cloud platform
    try:
        conn = sqlitecloud.connect(conn_string)
    except Exception as errMsg:
        st.error(f"**ERROR connecting to database: \n{errMsg}", icon="🚨")
    
    # Open SQLite database
    conn.execute(f"USE DATABASE {db_name}")
    cursor = conn.cursor()

    # Modifica la query per includere anche il campo r_assignedto
    df_requests = pd.read_sql_query("""
        SELECT r_id as ROWID, r_user as USER, r_status as STATUS, 
            r_insdate as DATE, r_dept as DEPARTMENT, r_requester as REQUESTER, 
            r_priority as PRIORITY, r_pline as PR_LINE, r_pfamily as PR_FAMILY, 
            r_type as TYPE, r_category as CATEGORY, r_title as TITLE, 
            r_detail as DETAIL 
        FROM TORP_REQUESTS
        ORDER by ROWID desc
    """, conn)

    # Aggiungi questo dopo il caricamento dei dati
    if st.session_state.grid_refresh:
        st.session_state.grid_data = df_requests.copy()
        st.session_state.grid_refresh = False    
        df_requests["DATE"] = pd.to_datetime(df_requests["DATE"], format="%Y-%m-%d")

    df_requests["ROWID"] = 'R' + df_requests["ROWID"].astype(str).str.zfill(4)
    # Custom cell styling based on stock levels
    cellStyle = JsCode("""
        function(params) {
            if (params.column.colId === 'ROWID') {
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
    grid_builder.configure_column("ROWID", cellStyle=cellStyle)   
    grid_builder.configure_selection(
    selection_mode='single',     # Enable multiple row selection
    use_checkbox=False             # Show checkboxes for selection
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
    ct_requester = df_requests['REQUESTER'].drop_duplicates()
    df_ct_requester = pd.DataFrame({"REQUESTER": ct_requester}).sort_values(by="REQUESTER")

    # Get an optional value requester filter
    requester_filter = st.sidebar.selectbox("Select a Requester:", df_ct_requester, index=None)

    # Filtro e AGGIORNAMENTO DEI DATI (utilizzando la sessione)
    if requester_filter:
        st.session_state.grid_data = df_requests.loc[df_requests["REQUESTER"] == requester_filter].copy()
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
            'Column name': ["Request Number", "Insert date", "User", "Status", "Department", "Requester", "Priority", "Product Line", "Product Family", "Type", "Category", "Title", "Detail"],
            'Column value': [selected_row['ROWID'][0], selected_row['DATE'][0], selected_row['USER'][0], selected_row['STATUS'][0], selected_row['DEPARTMENT'][0], selected_row['REQUESTER'][0], selected_row['PRIORITY'][0], selected_row['PR_LINE'][0], selected_row['PR_FAMILY'][0], selected_row['TYPE'][0], selected_row['CATEGORY'][0], selected_row['TITLE'][0], selected_row['DETAIL'][0]]
        }
        df_out = pd.DataFrame(data_out)
        st.subheader("Request details:")         
        st.dataframe(df_out, use_container_width=True, height=500, hide_index=True)

#######################################################################################################
def assign_request():

    # Inzialize variables
    rc = 0
    req_nr = ""
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
    # Connect to SQLite Cloud platform
    try:
        conn = sqlitecloud.connect(conn_string)
    except Exception as errMsg:
        st.error(f"**ERROR connecting to database: \n{errMsg}", icon="🚨")
    
    # Open SQLite database
    conn.execute(f"USE DATABASE {db_name}")
    cursor = conn.cursor()
   
    df_requests = pd.read_sql_query("""
    SELECT r_id as ROWID, r_user as USER, r_status as STATUS, 
        r_insdate as DATE, r_dept as DEPARTMENT, r_requester as REQUESTER, 
        r_priority as PRIORITY, r_pline as PR_LINE, r_pfamily as PR_FAMILY, 
        r_type as TYPE, r_category as CATEGORY, r_title as TITLE, 
        r_detail as DETAIL 
    FROM TORP_REQUESTS
    ORDER by ROWID desc
    """, conn)
    
    df_requests["DATE"] = pd.to_datetime(df_requests["DATE"], format="%Y-%m-%d")

#    df_requests["ROWID"] = "R"+df_requests["ROWID"]
    df_requests["ROWID"] = 'R' + df_requests["ROWID"].astype(str).str.zfill(4)

    # Custom cell styling based on stock levels
    cellStyle = JsCode("""
        function(params) {
            if (params.column.colId === 'ROWID') {
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
    #gb = GridOptionsBuilder()
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
    grid_builder.configure_column("ROWID", cellStyle=cellStyle)   
    grid_builder.configure_selection(
    selection_mode='single',     # Enable multiple row selection
    use_checkbox=False             # Show checkboxes for selection
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
    ct_status = df_requests['STATUS'].drop_duplicates()
    df_ct_status = pd.DataFrame({"STATUS": ct_status}).sort_values(by="STATUS")

    # Get an optional value requester filter
    status_filter = st.sidebar.selectbox("Select a Status value:", df_ct_status, index=None)

    # Filtro e AGGIORNAMENTO DEI DATI (utilizzando la sessione)
    if status_filter:
        st.session_state.grid_data = df_requests.loc[df_requests["STATUS"] == status_filter].copy()
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
    
        
    def show_request_dialog(selected_row):
        popup_title = f'Request {selected_row["ROWID"][0]} detail'
    
        @st.dialog(popup_title, width="small")
        def dialog_content():
            rc = 0
            req_status = ""
            req_assignedto = ""
        # Stili personalizzati per gli input
            st.markdown(
                """
                <style>
                /* Stile per text_input abilitato */
                div[data-testid="stTextInput"] > div > div > input:not([disabled]) {
                    color: #28a745; /* Verde scuro */
                    border: 2px solid #28a745;
                    -webkit-text-fill-color: #28a745 !important;
                    font-weight: bold;
                }

                /* Stile per text_input disabilitato */
                div[data-testid="stTextInput"] > div > div input[disabled] {
                    color: #6c757d !important; /* Grigio più chiaro */
                    opacity: 1 !important;
                    -webkit-text-fill-color: #6c757d !important;
                    background-color: #e9ecef !important; /* Grigio ancora più chiaro */
                    border: 1px solid #ced4da !important;
                    font-style: italic;
                }

                /* Stile per selectbox abilitato */
                .stSelectbox > div > div > div > div {
                    color: #007bff; /* Blu per il testo */
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.text_input(label="Product family", value=selected_row['PR_FAMILY'][0], disabled=True)
            st.text_input(label="Category", value=selected_row['CATEGORY'][0], disabled=True)                
            st.text_input(label="Title", value=selected_row['TITLE'][0], disabled=True)
            st.text_area(label="Details", value=selected_row['DETAIL'][0], disabled=True)
            status_option = ['NEW', 'ASSIGNED', 'WIP', 'COMPLETED', 'DELETED']
            idx_status = status_option.index(selected_row['STATUS'][0])
            req_status = st.selectbox("Status", status_option, disabled=False, index=idx_status)
            assignedto_option = ["TOP_01", "TOP_02", "TOP_03", "TOP_04"]
            if req_status == "ASSIGNED":
                req_assignedto = st.multiselect("Assigned to:", assignedto_option)

            # Aggiungi funzioni per pulsante "Save"
            if req_status != selected_row['STATUS'][0]:
                if st.button("Save", type="primary", disabled=False, key="save_button"):                       
                    # Aggiorna il database
                    try:
                        cursor.execute("""
                            UPDATE TORP_REQUESTS 
                            SET r_status = ? 
                            WHERE r_id = ?
                        """, (req_status, selected_row["ROWID"][0][1:]))
                        conn.commit()
                        cursor.close()  
                        if conn:
                            conn.close()

                        st.session_state.grid_refresh = True
                        st.session_state.grid_response = None
                        st.success("Aggiornamento eseguito con successo!")
                        
                        # Imposta una flag per indicare che dobbiamo refreshare
                        st.session_state.need_refresh = True
                        time.sleep(3)  # Piccola pausa per mostrare il messaggio di successo
                        st.rerun()

                    except Exception as errMsg:
                        st.error(f"**ERROR updating request in tab TORP_REQUESTS: \n{errMsg}", icon="🚨")
                        return False

            return False             
        return dialog_content()
    
    # Nel codice principale:
    if selected_row is not None and len(selected_row) > 0:
        if 'dialog_shown' not in st.session_state:
            st.session_state.dialog_shown = False
            
        if 'need_refresh' not in st.session_state:
            st.session_state.need_refresh = False
            
        if st.session_state.need_refresh:
            st.session_state.need_refresh = False
            st.session_state.dialog_shown = False
        else:
            if not st.session_state.dialog_shown:
                if show_request_dialog(selected_row):
                    st.session_state.dialog_shown = True
                    st.rerun()
   


#######################################################################################################
def mytest():
    pass
    

#######################################################################################################
def main():
#  if not check_password():
#      st.stop()
  st.set_page_config(layout="wide")
  page_names_to_funcs = {
    "ℹ️ App Info": display_app_info,
    "🪄 Insert Request": insert_request,
    "🔍 View Request ": view_request,
    "📝 Assign Request": assign_request,
    "MYTEST": mytest
}    
  demo_name = st.sidebar.selectbox("Choose a function", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()


if __name__ == "__main__":
    main()
