import streamlit as st
import sqlitecloud
import datetime
import pytz 
import io
import hmac

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


def display_user_section() -> dict:
    """ Show a section to declare the user informations """
    req_department = ""
    req_user = ""
    with st.container():
        st.header(":orange[User informations]")
        req_dept_values_00 = ["DMN-ACCOUNTING", "DTD-DESIGN TECHNICAL DEPARTMENT", "COMMERCIALE AFTER MARKET"]
        req_department = st.selectbox(":blue[Requester Department(:red[*])]", req_dept_values_00, index=None)
        if req_department == "DMN-ACCOUNTING":
            req_user_values_01 = ["COMELLINI GIORGIO", "ROMANI CORRADO", "ROSSI PAOLA"]
            req_user = st.selectbox(":blue[Requester User(:red[*])]", req_user_values_01, index=None)
        elif req_department == "DTD-DESIGN TECHNICAL DEPARTMENT":
            req_user_values_02 = ["CARLINI MICHELE", "FENARA GABRIELE", "PALMA NICOLA"]
            req_user = st.selectbox(":blue[Requester User(:red[*])]", req_user_values_02, index=None)
        elif req_department == "COMMERCIALE AFTER MARKET":
            req_user_values_03 = ["GIORGI IVAN", "ANGOTTI FRANCESCO", "BALDINI ROBERTO"]
            req_user = st.selectbox(":blue[Requester User(:red[*])]", req_user_values_03, index=None)
    st.divider()    
    rec_out =    {
                     "Req_dept": req_department,
                     "Req_user": req_user
                 }
           
    return rec_out        


def display_productgroup_section() -> dict:
    """ Show a section to declare the product group informations """
    
    product_line = ""
    product_family = ""
    with st.container():
        st.header(":orange[Product group informations]")
        product_line_values_00 = ["POWER TAKE OFFs", "HYDRAULICS", "CYLINDERS", "ALL"]
        product_line = st.selectbox(":blue[Product line(:red[*])]", product_line_values_00, index=None)
        if product_line == "POWER TAKE OFFs":
            product_line_values_01 = ["GEARBOX PTO", "ENGINE PTO", "SPLIT SHAFT PTO", "PARALLEL GEARBOXES"]
            product_family = st.selectbox(":blue[Product family(:red[*])]", product_line_values_01, index=None)
        elif product_line == "HYDRAULICS":
            product_line_values_02 = ["PUMPS", "MOTORS", "VALVES", "WET KITS"]
            product_family = st.selectbox(":blue[Product family(:red[*])]", product_line_values_02, index=None)
        elif product_line == "CYLINDERS":
            product_line_values_03 = ["FRONT-END CYLINDERS", "UNDERBODY CYLINDERS", "DOUBLE ACTING CYLINDERS", "BRACKETS FOR CYLINDERS"]
            product_family = st.selectbox(":blue[Product family(:red[*])]", product_line_values_03, index=None)
    st.divider()       
    rec_out =    {
                     "Prd_line": product_line,
                     "Prd_family": product_family
                 }
    return rec_out 


def display_request_section() -> dict:
    """ Show a section to declare the request informations """
    req_type = ""
    req_category = ""
    st.header(":orange[Add a request]")
    with st.container():
        priority_values_00 = ["High", "Medium", "Low"]
        req_priority = st.selectbox(":blue[Priority]", priority_values_00, index=1)
        type_values_00 = ["DOCUMENTATION", "PRODUCT", "SERVICE"]
        req_type = st.selectbox(":blue[Request type (:red[*])]", type_values_00, index=None)
        if req_type == "PRODUCT":
            category_01 = ["NEW PRODUCT", "PRODUCT CHANG", "OBSOLETE PRODUCT", "PRODUCT VALIDATION"]
            req_category = st.selectbox(":blue[Request category(:red[*])]", category_01, index=None)
        elif req_type == "DOCUMENTATION":
            category_02 = ["WEBPTO", "DRAWING", "IMDS (INTERNATIONAL MATERIAL DATA SYSTEM)", "CATALOGUE"]
            req_category = st.selectbox(":blue[Request category(:red[*])]", category_02, index=None)
        elif req_type == "SERVICE":
            category_03 = ["VISITING CUSTOMER PLANT", "VISITING SUPPLIER PLANT"]
            req_category = st.selectbox(":blue[Request category(:red[*])]", category_03, index=None)
        req_title = st.text_input(":blue[Request title(:red[*])]")
        req_detail = st.text_area(":blue[Request details(:red[*])]", key="req_det")
    st.divider()   
    rec_out =    {
                    "Req_priority": req_priority, 
                    "Req_type": req_type,
                    "Req_category": req_category,                    
                    "Req_title": req_title,
                    "Req_detail": req_detail
                }
    return rec_out 

def display_attachment_section() -> dict:
    """ Show a section to upload attachments """
    rec_out = dict()
    st.header(":orange[Add an attachment (only PDF file)]")
    with st.container():
        uploaded_file = upload_pdf_file()
    if uploaded_file is not None:
        # To read file as bytes:
        #bytes_data = uploaded_file.getvalue()
        bytes_data = uploaded_file.read()
        rec_out =    {
                    "Atch_name": uploaded_file.name,
                    "Atch_type": "GENERIC",
                    "Atch_link": " ",                    
                    "Atch_data": bytes_data,
                }
    st.divider()              
    return rec_out       

def upload_pdf_file():
    """ Widget used to upload an xml file """
    uploaded_file = st.file_uploader("Choose a PDF file:", type=["pdf","jpg"], accept_multiple_files=False)
    return uploaded_file


def check_request_fields(record: dict) -> bool:
    res = all(record.values())
    return res


def click_submit_button():
    st.session_state.submit_clicked = True


def clear_text(t_txt):
    st.session_state[t_txt] = ""


def save_applog_to_sqlitecloud(log_values:dict) -> None:
    """ Save applog into SQLite Cloud Database """

    db_link = ""
    db_apikey = ""
    db_name = ""
    # Get database information
    try:
        #Search DB credentials using OS.GETENV
        db_link = os.getenv("SQLITECLOUD_DBLINK")
        db_apikey = os.getenv("SQLITECLOUD_APIKEY")
        db_name = os.getenv("SQLITECLOUD_DBNAME")
    except st.StreamlitAPIException as errMsg:
        try:
            #Search DB credentials using ST.SECRETS
            db_link = st.secrets["SQLITE_DBLINK"]
            db_apikey = st.secrets["SQLITE_APIKEY"]
            db_name = st.secrets["SQLITE_DBNAME"]
        except st.StreamlitAPIException as errMsg:
            st.error(f"**ERROR: DB credentials NOT FOUND: \n{errMsg}", icon="🚨")
    
    conn_string = "".join([db_link, db_apikey])
    # Connect to SQLite Cloud platform
    try:
        conn = sqlitecloud.connect(conn_string)
    except Exception as errMsg:
        st.error(f"**ERROR connecting to database: \n{errMsg}", icon="🚨")
    
    # Open SQLite database
    conn.execute(f"USE DATABASE {db_name}")
    cursor = conn.cursor()
    
    # Setup sqlcode for inserting applog as a new row
    sqlcode = """INSERT INTO applog (appname, applink, appcode, apparam, appstatus, appmsg, cpudate) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """
        
    rome_tz = pytz.timezone('Europe/Rome')
    rome_datetime = rome_tz.localize(datetime.datetime.now()) 
    cpudate = rome_datetime.strftime("%Y-%m-%d %H:%M:%S")
    values = (log_values["appname"], log_values["applink"], log_values["appcode"], log_values["apparam"], log_values["appstatus"], log_values["appmsg"], cpudate)
    try:
        cursor.execute(sqlcode, values)
    except Exception as errMsg:
        st.error(f"**ERROR inserting new applog row: \n{errMsg}", icon="🚨")
    else:
        conn.commit()
    finally:
        cursor.close()

def save_request_to_sqlitecloud(row:dict, atch: dict) -> None:
    """ Save applog into SQLite Cloud Database """
    rc = 0
    req_nr = dict()
    db_link = ""
    db_apikey = ""
    db_name = ""
    # Get database information
    try:
        #Search DB credentials using OS.GETENV
        db_link = os.getenv("SQLITECLOUD_DBLINK")
        db_apikey = os.getenv("SQLITECLOUD_APIKEY")
        db_name = os.getenv("SQLITECLOUD_DBNAME")
    except st.StreamlitAPIException as errMsg:
        try:
            #Search DB credentials using ST.SECRETS
            db_link = st.secrets["SQLITE_DBLINK"]
            db_apikey = st.secrets["SQLITE_APIKEY"]
            db_name = st.secrets["SQLITE_DBNAME"]
        except st.StreamlitAPIException as errMsg:
            st.error(f"**ERROR: DB credentials NOT FOUND: \n{errMsg}", icon="🚨")
    
    conn_string = "".join([db_link, db_apikey])
    # Connect to SQLite Cloud platform
    try:
        conn = sqlitecloud.connect(conn_string)
    except Exception as errMsg:
        st.error(f"**ERROR connecting to database: \n{errMsg}", icon="🚨")
    
    # Open SQLite database
    conn.execute(f"USE DATABASE {db_name}")
    cursor = conn.cursor()
    
    # Setup sqlcode for inserting applog as a new row
    sqlcode = """INSERT INTO TORP_REQUESTS (r_id, r_dept, r_requester, r_pline, r_pfamily, r_priority, r_type, r_category, r_title, r_detail, r_insdate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """    
    # Calculate the next rowid
    cursor.execute('SELECT MAX(r_id) FROM TORP_REQUESTS')
    max_rowid = cursor.fetchone()[0]
    next_rowid = (max_rowid + 1) if max_rowid is not None else 1
     
    # Setup row values
    values = (next_rowid, row["Req_dept"], row["Req_user"], row["Prd_line"], row["Prd_family"], row["Req_priority"], row["Req_type"], row["Req_category"], row["Req_title"], row["Req_detail"], row["Req_insdate"])
    try:
        cursor.execute(sqlcode, values)
    #    cursor.lastrowid
    except Exception as errMsg:
        st.error(f"**ERROR inserting row in tab TORP_REQUESTS: \n{errMsg}", icon="🚨")
        rc = 1
    else:
        conn.commit()
        req_nr = f"R-{str(next_rowid).zfill(4)}"
        rc = 0
    if len(atch) > 0:
    # Setup sqlcode for inserting attachments
        sqlcode = """INSERT INTO TORP_ATTACHMENTS (a_type, a_title, a_link, a_data, a_reqid) 
                VALUES (?, ?, ?, ?, ?);
                """  
            # Setup row values
        values = (atch["Atch_name"], atch["Atch_type"], atch["Atch_link"], atch["Atch_data"], next_rowid)
        try:
            cursor.execute(sqlcode, values)
        #    cursor.lastrowid
        except Exception as errMsg:
            st.error(f"**ERROR inserting row in tab TORP_ATTACHMENTS: \n{errMsg}", icon="🚨")
            rc = 1
        else:
            conn.commit()
    
    cursor.close()    
    if conn:
        conn.close()

    return req_nr, rc    


def insert_request():
    rec_user = display_user_section()
    rec_pgroup = display_productgroup_section()
    rec_req = display_request_section()
    rec_attchment = display_attachment_section() 
    rec_request = rec_user | rec_pgroup | rec_req
    insdate = datetime.datetime.now().strftime("%Y-%m-%d")
    rec_request["Req_insdate"] = insdate
    if 'submit_clicked' not in st.session_state:
        st.session_state.submit_clicked = False
    st.button("Submit", type="primary", on_click=click_submit_button)
    if st.session_state.submit_clicked:
      if check_request_fields(rec_request):
          nr_req = ""
          applog = dict()
          nr_req, rc = save_request_to_sqlitecloud(rec_request, rec_attchment)
          if rc == 0:
              # Creare una lista di tuple chiave-valore
              items = list(rec_request.items())
              # Inserire la nuova coppia chiave-valore nella prima posizione
              items.insert(0, ("Req_nr", nr_req))
              # Convertire di nuovo la lista in un dizionario
              rec_request = dict(items)
              st.write(f"Request {nr_req} submitted! Here are the ticket details:")
              df_request = pd.DataFrame([rec_request])
              st.dataframe(df_request, use_container_width=True, hide_index=True)
              applog["appstatus"] = "COMPLETED"
              applog["appmsg"] = " "
          else:
              applog["appstatus"] = "ERROR"
              applog["appmsg"] = "TABLE TORP_REQUESTS: UNIQUE CONSTRAIN ON FIELD r_title"    
          
          applog["appname"] = APPNAME
          applog["applink"] = __file__
          applog["appcode"] = APPCODE
          applog["apparam"] = str(rec_request)
          save_applog_to_sqlitecloud(applog)           
      else:
          st.write(":red-background[**ERROR: please fill all mandatory fields (:red[*])]")


def view_request():
  pass

def main():
  if not check_password():
      st.stop()
  page_names_to_funcs = {
    "ℹ️ App Info": display_app_info,
    "📝 Insert Request": insert_request,
    "🔍 View Request ": view_request
}    
  demo_name = st.sidebar.selectbox("Choose a function", page_names_to_funcs.keys())
  page_names_to_funcs[demo_name]()
if __name__ == "__main__":
    main()
