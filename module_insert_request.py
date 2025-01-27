import streamlit as st
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List

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


