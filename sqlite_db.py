import sqlitecloud
import streamlit as st
import pandas as pd
from typing import Optional, Tuple, Dict, List
import base64
from datetime import datetime, date

def open_sqlitecloud_db():
    """ Open a connection to SQLITE database"""
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
        rc = False
        
    conn_string = "".join([db_link, db_apikey])

    if 'conn' not in st.session_state:
        try:
            # Connect to SQLite Cloud platform
            conn = sqlitecloud.connect(conn_string)
            cursor = conn.cursor()

            # Open SQLite database
            conn.execute(f"USE DATABASE {db_name}")  

            # Get Sqlite Cloud database version
            cursor.execute("SELECT sqlite_version();")
            #st.success(f"Connect to SQLITE CLOUD version {cursor.fetchone()}")
            sqlite_version = cursor.fetchone()
            #st.write(f"{type(sqlite_version)} - {sqlite_version}" )

            if conn:
                st.session_state.conn = conn
            if sqlite_version:    
                st.session_state.sqlite_version = sqlite_version[0]
            if db_name:
                st.session_state.dbname = db_name

        except Exception as errMsg:
            st.error(f"**ERROR connecting to database: \n{errMsg}", icon="🚨")
            return None
        
        finally: cursor.close()  
        
        return conn
    else:
        return st.session_state["conn"]

def load_dept_data(conn):
    """ Load TORP_DEPARTMENTS records into df """ 

    try:
        df_depts = pd.read_sql_query("""
            SELECT 
                A.code AS CODE, 
                A.name AS NAME, 
                A.mngrcode AS MNGR_CODE, 
                A.rprofcode AS REQPROF_CODE 
            FROM TORP_DEPARTMENTS AS A
            ORDER by name
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_DEPARTMENTS: \n{errMsg}", icon="🚨")
        return None
    
    return df_depts

def load_users_data(conn):
    """ Load TORP_USERS records into df """ 

    try:
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
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_USERS: \n{errMsg}", icon="🚨")
        return None
    
    return df_users

def load_pline_data(conn):
    """ Load TORP_PLINE records into df """ 
    
    try:
        df_pline = pd.read_sql_query("""
            SELECT 
                A.code AS CODE, 
                A.name AS NAME
            FROM TORP_PLINE A
            ORDER by A.name
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_PLINE: \n{errMsg}", icon="🚨")
        return None
    
    return df_pline

def load_pfamily_data(conn):
    """ Load TORP_PFAMILY records into df """ 

    try:
        df_pfamily = pd.read_sql_query("""
            SELECT 
                A.code AS CODE, 
                A.name AS NAME, 
                A.pcode AS PLINE_CODE
            FROM TORP_PFAMILY A
            ORDER by A.name
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_PFAMILY: \n{errMsg}", icon="🚨")
        return None
    
    return df_pfamily

def load_type_data(conn):
    """ Load TORP_TYPE records into df """ 

    try:
        df_type = pd.read_sql_query("""
            SELECT 
                A.code AS CODE, 
                A.name AS NAME
            FROM TORP_TYPE A
            ORDER by A.name
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_TYPE: \n{errMsg}", icon="🚨")
        return None
    
    return df_type

def load_category_data(conn):
    """ Load TORP_CATEGORY records into df """ 

    try:
        df_category= pd.read_sql_query("""
            SELECT 
                A.code AS CODE, 
                A.name AS NAME
            FROM TORP_CATEGORY A
            ORDER by A.name
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_CATEGORY: \n{errMsg}", icon="🚨")
        return None
    
    return df_category

def load_detail_data(conn):
    """ Load TORP_DETAIL records into df """ 

    try:
        df_detail= pd.read_sql_query("""
            SELECT 
                A.code AS CODE,                                    
                A.name AS NAME
            FROM TORP_DETAIL A
            ORDER by A.name
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_DETAIL: \n{errMsg}", icon="🚨")
        return None
    
    return df_detail


def load_lk_type_category_data(conn):
    """ Load TORP_LINK_TYPE_CATEGORY records into df """ 

    try:
        df_lk_type_category= pd.read_sql_query("""
            SELECT 
                A.typecode AS TYPE_CODE, 
                A.categorycode AS CATEGORY_CODE
            FROM TORP_LINK_TYPE_CATEGORY A
            ORDER by A.typecode 
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_LINK_TYPE_CATEGORY: \n{errMsg}", icon="🚨")
        return None
    
    return df_lk_type_category

def load_lk_category_detail_data(conn):
    """ Load TORP_LINK_CATEGORY_DETAIL records into df """ 

    try: 
        df_lk_category_detail= pd.read_sql_query("""
            SELECT 
                A.categorycode AS CATEGORY_CODE, 
                A.detailcode AS DETAIL_CODE
            FROM TORP_LINK_CATEGORY_DETAIL A
            ORDER by A.categorycode 
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_LINK_CATEGORY_DETAIL: \n{errMsg}", icon="🚨")
        return None
    
    return df_lk_category_detail

def load_lk_pline_tdtl_data(conn):
    """ Load TORP_LINK_PLINE_TDTL records into df """ 

    try:
        df_lk_pline_tdtl= pd.read_sql_query("""
            SELECT 
                A.plinecode AS PLINE_CODE, 
                A.usercode AS USER_CODE
            FROM TORP_LINK_PLINE_TDTL A
            ORDER by A.plinecode 
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR loading data from TORP_LINK_PLINE_TDTL: \n{errMsg}", icon="🚨")
        return None
    
    return df_lk_pline_tdtl


def load_tskgrl1_data(conn):
    """ Load TORP_TASKGRP_L1 records into df """ 
    
    try: 
        df_tskgrl1 = pd.read_sql_query("""
            SELECT 
                A.code AS CODE, 
                A.name AS NAME
            FROM TORP_TASKGRP_L1 AS A
            ORDER by name
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR load data from TORP_TASKGRP_L1: \n{errMsg}", icon="🚨")
        return None
    
    return df_tskgrl1

def load_tskgrl2_data(conn):
    """ Load TORP_TASKGRP_L2 records into df """    
    
    try:
        df_tskgrl2 = pd.read_sql_query("""
            SELECT 
                A.code AS CODE, 
                A.name AS NAME,
                A.pcode AS PCODE
            FROM TORP_TASKGRP_L2 AS A
            ORDER by name
            """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR load data from TORP_TASKGRP_L2: \n{errMsg}", icon="🚨")
        return None
    
    return df_tskgrl2

def load_requests_data(conn):
    """ Load TORP_REQUESTS records into df """    

    try:
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
    except Exception as errMsg:
        st.error(f"**ERROR load data from TORP_REQUESTS: \n{errMsg}", icon="🚨")
        return None
    
    return df_requests

def load_reqassignedto_data(conn):
    """ Load TORP_REQASSIGNEDTO records into df """    

    try:
        df_reqassignedto = pd.read_sql_query("""
        SELECT 
            A.reqid AS REQID,
            A.tdtlid AS TDTLID, 
            A.status AS STATUS,
            B.name AS USERNAME 
        FROM TORP_REQASSIGNEDTO A
        INNER JOIN TORP_USERS B ON B.code = A.userid
        WHERE A.status = 'ACTIVE'
        ORDER BY USERID desc
        """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR load data from TORP_REQASSIGNEDTO: \n{errMsg}", icon="🚨")
        return None
    
    return df_reqassignedto


def load_attachments_data(conn):
    """ Load TORP_ATTACHMENTS records into df """    

    try:
        df_attachments = pd.read_sql_query("""
        SELECT 
            A.class AS CLASS,
            A.title AS TITLE,                                  
            A.reqid AS REQID
        FROM TORP_ATTACHMENTS A
        ORDER BY A.title
        """, conn)
    except Exception as errMsg:
        st.error(f"**ERROR load data from TORP_ATTACHMENTS: \n{errMsg}", icon="🚨")
        return None
    
    return df_attachments


def load_workorders_data(conn):
    """ Load TORP_WORKORDERS records into df """

    try:
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
    except Exception as errMsg:
        st.error(f"**ERROR load data from TORP_WORKORDERS: \n{errMsg}", icon="🚨")
        return None
    return df_workorders

def load_woassignedto_data(conn):
    """ Load TORP_WOASSIGNEDTO records into df """
       
    try:
        df_woassignedto = pd.read_sql_query("""
        SELECT 
            A.woid AS WOID, 
            A.tdtlid AS TDTLID, 
            A.tdspid AS TDSPID,
            A.status AS STATUS, 
            B.name AS USERNAME 
        FROM TORP_WOASSIGNEDTO A
        INNER JOIN TORP_USERS B ON B.code = A.userid    
        WHERE A.status = 'ACTIVE'
        ORDER BY WOID
        """, conn)    
    except Exception as errMsg:
        st.error(f"**ERROR load data from TORP_WOASSIGNEDTO: \n{errMsg}", icon="🚨")
        return None
    return df_woassignedto


def load_workitems_data(conn):
    """ Load TORP_TORP_WORKITEMS records into df """
       
    try:
        df_workitem = pd.read_sql_query("""
        SELECT 
            A.date AS DATE, 
            A.woid AS WOID, 
            A.tdspid AS TDSPID,
            A.status AS STATUS, 
            A.tskgrl1 AS TSKGRL1,
            A.tskgrl2 AS TSKGRL2,
            A.description AS DESC,
            A.note AS NOTE,
            A.time_qty AS TIME_QTY,
            A.time_um AS TIME_UM
        FROM TORP_WORKITEMS A  
        WHERE A.status = 'ACTIVE'
        ORDER BY WOID
        """, conn, parse_dates=["DATE"])
        df_workitem['DATE'] = df_workitem['DATE'].dt.date

    except Exception as errMsg:
        st.error(f"**ERROR load data from TORP_WORKITEMS: \n{errMsg}", icon="🚨")
        return None
    return df_workitem


def get_next_object_id(obj_class, obj_year, obj_pline, obj_parent, conn) -> str:
    """Get next available row ID"""

    ZERO_PADDING_NR = 4
    SEP_CHAR = '-'
    WO_PREFIX = "W"
    next_rowid = ""

    # Work Order numeration-> Prefix + numeration of Request
    if obj_class == "WOR": 
        next_rowid = WO_PREFIX + obj_parent[1:]
    
    # Request numeration
    if obj_class == "REQ":    
        try:
            cursor = conn.cursor()
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
            st.error(f"**ERROR impossible to get the next rowid from table TORP_OBJNUMERATOR: {errMsg}")
            conn.rollback()
            return ""
        finally:
            if cursor:
                cursor.close() # Close the cursor in a finally block
    
    else:
        st.error(f"**ERROR impossible to get the next rowid for object {obj_class}-{obj_year}-{obj_pline}")
        return ""
    
    return next_rowid


def save_request(request: dict, conn) -> Tuple[str, int]:
    """Save request to database and return request number and status"""

    try:
        cursor = conn.cursor()
        req_year = request["insdate"][0:4]
        next_reqid = get_next_object_id("REQ", req_year, "", "", conn)
        sql = """
            INSERT INTO TORP_REQUESTS (
                reqid, status, insdate, dept, requester, user, 
                priority, pline, pfamily, type, category, detail,
                title, description, note_td, woid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            next_reqid, request["status"], request["insdate"], request["dept"],
            request["requester"], request["user"], request["priority"], 
            request["pline"], request["pfamily"], request["type"], request["category"],
            request["detail"], request["title"], request["description"], "", "" 
        )
        
        cursor.execute(sql, values)
        conn.commit()
        
    except Exception as e:
        st.error(f"**ERROR inserting request in TORP_REQUESTS: \n{e}", icon="🚨")
        return "", False

    try:               
        for tdtl in request["tdtl_list"]: 
            sql = """
                INSERT INTO TORP_REQASSIGNEDTO (
                    reqid, tdtlid, status
                ) VALUES (?, ?, ?)
            """
            values = (
                next_reqid, tdtl, "ACTIVE"

            )
        
        cursor.execute(sql, values)
        conn.commit()
                    
    except Exception as e:
        conn.rollback()
        st.error(f"**ERROR inserting request in TORP_REQASSIGNEDTO: \n{e}", icon="🚨")
        return "", False
    
    finally:
        if cursor:
            cursor.close()  
    
    return next_reqid, True 


def load_attachments_from_db(reqid: str, conn):
    """Visualizza gli allegati PDF."""

    try:
        cursor = conn.cursor()

        sql = """
            SELECT title, data 
            FROM TORP_ATTACHMENTS 
            WHERE reqid = :1 
        """
        cursor.execute(sql, [reqid])
        attachments = cursor.fetchall()

        if not attachments:
            st.info(f"Nessun allegato trovato per la richiesta {reqid}")
            return

        for title, pdf_data in attachments:
            if pdf_data:
                #st.subheader(title)
                with st.expander(title):  # Expander per ogni allegato
                    st.download_button(
                        label=f" Download PDF - {title}",
                        data=pdf_data,
                        file_name=f"{title}.pdf",
                        mime="application/pdf"
                    )
                    # Visualizzazione PDF (con controllo visibilità)
                    if st.checkbox("Mostra anteprima", key=f"preview_{title}"): # Checkbox univoco per ogni anteprima
                        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Errore nel caricamento degli allegati: {e}")
        import traceback
        st.error(traceback.format_exc())
    finally:
        if cursor:
            cursor.close() # Close the cursor in a finally block
    return True


def save_attachments(req_id: str, attachments_list: list, conn) -> bool:
    """ Salva i file allegati di una richiesta nella tabella TORP_ATTACHMENTS """
    try:
        cursor = conn.cursor()
        for attachments in attachments_list:
            sql = """
                INSERT INTO TORP_ATTACHMENTS (class, title, link, data, reqid)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (attachments["class_type"], attachments["title"], attachments["link"], attachments["file_content"], req_id))
            conn.commit()  # Commit AFTER saving
    
    except Exception as e:
        st.error(f"Error saving attachment: {e}")
        conn.rollback() # Rollback on error
        return False
    
    finally:
        cursor.close()
    return True        

def view_attachments(reqid: str, conn)-> None:
    """Visualizza gli allegati PDF."""

    try:
        with conn:  # Use a context manager for the connection
            cursor = conn.cursor()

            sql = """
                SELECT title, data 
                FROM TORP_ATTACHMENTS 
                WHERE reqid = :1 
            """
            cursor.execute(sql, [reqid])
            attachments = cursor.fetchall()

            if not attachments:
                st.info(f"Nessun allegato trovato per la richiesta {reqid}")
                return

            for title, pdf_data in attachments:
                if pdf_data:
                    #st.subheader(title)
                    file_name = f"{reqid}_details.pdf"
                    with st.expander(title):  # Expander per ogni allegato
                        st.download_button(
                            label=f" Download PDF",
                            data=pdf_data,
                            file_name=file_name,
                            mime="application/pdf",
                            icon="📥"
                        )
                        # Visualizzazione PDF (con controllo visibilità)
                        if st.checkbox("Mostra anteprima", key=f"preview_{title}"): # Checkbox univoco per ogni anteprima
                            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000"></iframe>'
                            st.markdown(pdf_display, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Errore nel caricamento degli allegati: {e}")
        import traceback
        st.error(traceback.format_exc())
    finally:
        cursor.close() # Close the cursor in a finally block
