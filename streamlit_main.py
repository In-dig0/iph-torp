# Python built-in libraries
import datetime
import os
import io
import time

# 3th party packages
import streamlit as st
import pandas as pd
import sqlitecloud
import pytz 
import hmac
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode


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

def display_app_info():
    """ Show app title and description """
    
    import streamlit as st

    st.header(":blue[TORP Web Application]", divider="blue")
    st.subheader(
        """
        TORP - Technical Office Requests POC (Proof Of Concept), is a simple web application to manage request to IPH Technical Office.
        """
    )
    st.markdown(f":grey[Version: {APPVERSION}]")
    st.divider()
    st.markdown("Powered with Streamlit :streamlit:")

def insert_request()-> None:
    """ Function to insert a new request """    
    
############################################################################################    
    @st.dialog("Request submitted!", width="large")
    def display_request_popup(req_nr: str, request: dict)-> None:
        """ Function to get request information from user """
        st.markdown(f"Request :green-background[**{req_nr}**] submitted! Here are the details:")
        df_request = pd.DataFrame([request])
        st.dataframe(df_request, use_container_width=True, hide_index=True)
        time.sleep(10)

############################################################################################    
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
        sqlcode = """INSERT INTO TORP_REQUESTS (r_id, r_dept, r_requester, r_pline, r_pfamily, r_priority, r_type, r_category, r_title, r_detail, r_insdate) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """    
        
        # Setup row values
        values = (next_rownr, row["Req_dept"], row["Req_requester"], row["Req_pline"], row["Req_pfamily"], row["Req_priority"], row["Req_type"], row["Req_category"], row["Req_title"], row["Req_detail"], row["Req_insdate"])
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


############################################################################################    

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
    req_detail = st.text_input(":blue[Request detail(:red[*])]", key=ti_detail_key)

    insdate = datetime.datetime.now().strftime("%Y-%m-%d")
    request_record =    {
            "Req_insdate": insdate,
            "Req_dept": req_department,
            "Req_requester": req_requester,
            "Req_pline": req_pline,
            "Req_pfamily": req_pfamily,
            "Req_priority": req_priority,
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
            # display_request_popup(request_record)
            # st.session_state[reset_sb_dept_key] = True
            # st.session_state[reset_sb_requester_key] = True
            # st.session_state[reset_ti_title_key] = True
            # st.rerun()

def view_request():
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

    df_requests = pd.read_sql_query("SELECT r_id as ROWID, r_insdate as DATE, r_dept as DEPARTMENT, r_requester as REQUESTER, r_pline as PR_LINE, r_pfamily as PR_FAMILY, r_priority as PRIORITY, r_type as TYPE, r_category as CATEGORY, r_title as TITLE, r_detail as DETAIL FROM TORP_REQUESTS", conn)
    df_requests["DATE"] = pd.to_datetime(df_requests["DATE"], format="%Y-%m-%d")
#    df_requests["ROWID"] = "R"+df_requests["ROWID"]
    df_requests["ROWID"] = 'R' + df_requests["ROWID"].astype(str).str.zfill(4)
    #####################
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
    #####################
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
    grid_builder.configure_pagination(enabled=True, paginationPageSize=20)
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
    use_checkbox=True             # Show checkboxes for selection
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

    # # Visualizzazione dei dati (opzionale)
    # if not st.session_state.grid_response['data'].empty:  # Check if data exists
    #     st.write("Dati visualizzati nella griglia:")
    #     st.dataframe(st.session_state.grid_response['data'])

def test_funct():
    try:
        #Search DB credentials using ST.SECRETS
        db_link = st.secrets["db_credentials"]["SQLITECLOUD_DBLINK"]
        db_apikey = st.secrets["db_credentials"]["SQLITECLOUD_APIKEY"]
        db_name = st.secrets["db_credentials"]["SQLITECLOUD_DBNAME"]
    except Exception as errMsg:
        st.error(f"**ERROR: DB credentials NOT FOUND: \n{errMsg}", icon="🚨")
    else:
        st.write(f"DBLINK: {db_link}")
        st.write(f"APIKEY: {db_apikey}")
        st.write(f"DBNAME: {db_name}")

def main():
#  if not check_password():
#      st.stop()
  page_names_to_funcs = {
    "ℹ️ App Info": display_app_info,
    "📝 Insert Request": insert_request,
    "🔍 View Request ": view_request
}    
  demo_name = st.sidebar.selectbox("Choose a function", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()


if __name__ == "__main__":
    main()
