# Python built-in libraries
import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode
# Internal app module
import servant
import sqlite_db

# Global constants
ACTIVE_STATUS = "ACTIVE"
DISABLED_STATUS = "DISABLED"
DEFAULT_DEPT_CODE = "DTD"
REQ_STATUS_OPTIONS = ['NEW', 'PENDING', 'ASSIGNED', 'WIP', 'COMPLETED', 'DELETED']

def manage_request(conn):
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
            selected_pline_code = st.session_state.df_pline[st.session_state.df_pline["NAME"] == selected_pline_name]["CODE"].values[0]
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
            description = st.session_state.df_requests[st.session_state.df_requests["REQID"] == reqid]["DESCRIPTION"].values[0]
            st.text_area(label="Description", value=description, disabled=True)

            st.divider()
            tdtl_usercode = st.session_state.df_lk_pline_tdtl["USER_CODE"].drop_duplicates().sort_values().tolist() #conversione in lista
            tdtl_username_list = st.session_state.df_users[st.session_state.df_users["CODE"].isin(tdtl_usercode)]["NAME"].tolist()

            tdtl_default_codes = st.session_state.df_reqassignedto[st.session_state.df_reqassignedto["REQID"] == reqid]["TDTLID"].tolist()

            if tdtl_default_codes:
                tdtl_option = st.session_state.df_users[st.session_state.df_users["CODE"].isin(tdtl_default_codes)]
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
                req_tdtl_code = st.session_state.df_users[st.session_state.df_users["NAME"].isin(req_tdtl_name)]["CODE"].tolist()
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
            default_note_td = str(st.session_state.df_requests[st.session_state.df_requests["REQID"] == reqid]["NOTE_TD"].values[0])
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
            
            req_description = st.session_state.df_requests[st.session_state.df_requests["REQID"]==reqid]["DESCRIPTION"]
            if not req_description.empty:
                req_description_default = req_description.values[0]
            else:
                req_description_default = ""
            st.text_input(label="Request description", value=req_description_default, disabled=True)

            req_note_td = st.session_state.df_requests[st.session_state.df_requests["REQID"]==reqid]["NOTE_TD"]
            if not req_note_td.empty:
                req_note_td_default = req_note_td.values[0]
            else:
                req_note_td_default = ""

            st.divider()
            st.subheader(f"Work Order {woid}")

            wo_nr = st.session_state.df_workorders[st.session_state.df_workorders["REQID"] == reqid]["WOID"]

            wo_type_options=["Standard", "APQP Project"]  #APQP -> ADVANCED PRODUCT QUALITY PLANNING"  
            wo_type_filtered = st.session_state.df_workorders[st.session_state.df_workorders["WOID"] == woid]["TYPE"]
            if not wo_type_filtered.empty:
                wo_type_default = wo_type_filtered.values[0]
                wo_type_index = wo_type_options.index(wo_type_default)
            else:
                wo_type_index = 0  

            wo_startdate_filtered = st.session_state.df_workorders[st.session_state.df_workorders["WOID"] == woid]["STARTDATE"]
            if not wo_startdate_filtered.empty:
                wo_startdate_default = wo_startdate_filtered.values[0]
            else:
                wo_startdate_default = None  # O un valore di default appropriato

            wo_enddate_filtered = st.session_state.df_workorders[st.session_state.df_workorders["WOID"] == woid]["ENDDATE"]
            if not wo_enddate_filtered.empty:
                wo_enddate_default = wo_enddate_filtered.values[0]
            else:
                wo_enddate_default = None  # O un valore di default appropriato

            wo_timeqty_filtered = st.session_state.df_workorders[st.session_state.df_workorders["WOID"] == woid]["TIME_QTY"]
            if not wo_timeqty_filtered.empty:
                wo_timeqty_default = float(wo_timeqty_filtered.iloc[0])  # Converti a float!
                min_value = 0.0 # Valore minimo predefinito come float
            else:
                wo_timeqty_default = 0.0  # Valore di default come float
                min_value = 0.0 # Valore minimo predefinito come float             
                 
            df_tdusers = df_users[df_users["DEPTCODE"] == default_dept_code]
            
            # Lista dei possibili nomi dei Team Leader
            tdtl_usercode = st.session_state.df_lk_pline_tdtl["USER_CODE"].drop_duplicates().sort_values().tolist() #conversione in lista
            tdtl_username_list = st.session_state.df_users[st.session_state.df_users["CODE"].isin(tdtl_usercode)]["NAME"].tolist()

            tdtl_default_codes = st.session_state.df_reqassignedto[st.session_state.df_reqassignedto["REQID"] == reqid]["TDTLID"].tolist()

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
                    success = sqlite_db.update_request(reqid, "ASSIGNED", req_note_td, "", [], conn)
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
    # Load data only once and store in session state
    session_data = {
        'df_depts': sqlite_db.load_dept_data,
        'df_users': sqlite_db.load_users_data,
        'df_pline': sqlite_db.load_pline_data,
        'df_pfamily': sqlite_db.load_pfamily_data,
        'df_category': sqlite_db.load_category_data,
        'df_type': sqlite_db.load_type_data,
        'df_lk_type_category': sqlite_db.load_lk_type_category_data,
        'df_lk_category_detail': sqlite_db.load_lk_category_detail_data,
        'df_lk_pline_tdtl': sqlite_db.load_lk_pline_tdtl_data,
        'df_detail': sqlite_db.load_detail_data,
        'df_requests': sqlite_db.load_requests_data,
        'df_reqassignedto': sqlite_db.load_reqassignedto_data,
        'df_attachments': sqlite_db.load_attachments_data,
        'df_workorders': sqlite_db.load_workorders_data,
        'df_woassignedto': sqlite_db.load_woassignedto_data,
        'df_workitems': sqlite_db.load_workitems_data,
        'df_tskgrl1': sqlite_db.load_tskgrl1_data,
        'df_tskgrl2': sqlite_db.load_tskgrl2_data,
    }

    for key, loader in session_data.items():
        if key not in st.session_state:
            st.session_state[key] = loader(conn)

    # Initialize session state
    if "grid_data" not in st.session_state:
        st.session_state.grid_data = st.session_state.df_requests.copy()
    if "grid_response" not in st.session_state:
        st.session_state.grid_response = None
    if "grid_refresh_key" not in st.session_state: 
        st.session_state.grid_refresh_key = "initial"    


    df_requests_grid = pd.DataFrame()
    df_requests_grid['REQID'] = st.session_state.df_requests['REQID']
    df_requests_grid['STATUS'] = st.session_state.df_requests['STATUS']
    df_requests_grid['INSDATE'] = st.session_state.df_requests['INSDATE']
#    df_requests_grid['DEPTNAME'] = df_requests['DEPT'].apply(lambda dept_code: get_description_from_code(df_depts, dept_code, "NAME"))
    df_requests_grid['PRIORITY'] = st.session_state.df_requests['PRIORITY']
    df_requests_grid['PRLINE_NAME'] = st.session_state.df_requests['PR_LINE'].apply(lambda pline_code: servant.get_description_from_code(st.session_state.df_pline, pline_code, "NAME"))
    df_requests_grid['TITLE'] = st.session_state.df_requests['TITLE']
    df_requests_grid['REQUESTER_NAME'] = st.session_state.df_requests['REQUESTER'].apply(lambda requester_code: servant.get_description_from_code(st.session_state.df_users, requester_code, "NAME"))

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
                            sqlite_db.update_request
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
                            st.session_state.df_workorders, 
                            st.session_state.df_woassignedto, 
                            st.session_state.df_users,
                            ACTIVE_STATUS, 
                            DEFAULT_DEPT_CODE,
                            REQ_STATUS_OPTIONS,
                            save_workorder,
                            save_workorder_assignments
                        )


