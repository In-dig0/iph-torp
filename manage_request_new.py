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

# ... (Caricamento dei dati nello stato della sessione come prima)

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
    st.rerun()

def show_request_dialog(selected_row_dict, req_status_options, update_request_fn):  # Passa un dizionario
    """Visualizza e gestisci la finestra di dialogo di modifica della richiesta."""

    popup_title = f'Richiesta {selected_row_dict["REQID"]}'  # Accedi a REQID direttamente

    @st.dialog(popup_title, width="large")
    def dialog_content():
        # ... (Il tuo codice di stile)

        reqid = selected_row_dict["REQID"] # Usa direttamente il dizionario

        # ... (Altre visualizzazioni di input, usando selected_row_dict)

        description = st.session_state.df_requests.loc[st.session_state.df_requests["REQID"] == reqid, "DESCRIPTION"].values[0]
        st.text_area(label="Descrizione", value=description, disabled=True)

        # ... (Resto del contenuto del dialogo)

        if st.button("Salva", type="primary", disabled=disable_save_button, key="req_save_button"):
            success = update_request_fn(reqid, req_status, req_note_td, 0, req_tdtl_code, conn)
            # ... (Resto della tua logica di salvataggio)

    return dialog_content()

def show_workorder_dialog(selected_row_dict,  # Passa un dizionario
                         df_workorders, df_woassignedto, df_users, active_status, 
                         default_dept_code, req_status_options, save_workorder_fn, 
                         save_woassignments_fn):
    """Visualizza e gestisci la finestra di dialogo dell'ordine di lavoro."""

    popup_title = f'Richiesta {selected_row_dict["REQID"]}' # Accedi a REQID direttamente

    @st.dialog(popup_title, width="large")
    def dialog_content():
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


        reqid = selected_row_dict["REQID"]  # Usa direttamente il dizionario
        woid = "W" + selected_row_dict["REQID"][1:]

        # ... (Resto del contenuto del dialogo, usando selected_row_dict)
        # Display request details
        st.text_input(label="Product Line", value=selected_row['PRLINE_NAME'][0], disabled=True)
        st.text_input(label="Request title", value=selected_row['TITLE'][0], disabled=True)

        req_description = st.session_state.df_requests.loc[st.session_state.df_requests["REQID"] == reqid, "DESCRIPTION"]
        if not req_description.empty:
            req_description_default = req_description.values[0]
        else:
            req_description_default = ""
        st.text_input(label="Descrizione della richiesta", value=req_description_default, disabled=True)

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


        if st.button("Salva", type="primary", disabled=disable_save_button, key="wo_save_button"):
            # ... (Resto della tua logica di salvataggio)

            wo = {"woid":woid, "tdtlid": req_tdtl_code, "type": wo_type, "title": selected_row["TITLE"][0], "description": req_description_default, "time_qty": wo_time_qty, "time_um": wo_time_um, "status": ACTIVE_STATUS, "startdate": wo_startdate, "enddate": wo_enddate, "reqid": reqid}
            wo_idrow, success = sqlite_db.save_workorder(wo, conn)
            if success:
                st.write(f"{woid} - {req_tdtl_code} - {wo_assignedto}- {st.session_state.df_user} - {st.session_state.df_woassignedt}")
                time.sleep(5)
                success = sqlite_db.save_workorder_assignments(woid, req_tdtl_code, wo_assignedto, st.session_state.df_users, st.session_state.df_woassignedto, conn)
                success = sqlite_db.update_request(reqid, "ASSIGNED", req_note_td, "", [], conn)
                if success:
                    st.session_state.grid_refresh = True
                    st.session_state.grid_response = None
                    st.success(f"Work order {woid} created successfully!")
                
                st.session_state.need_refresh = True
                time.sleep(10)
                reset_application_state()
                st.rerun()

    return dialog_content()


def manage_request(conn):

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


    selected_rows = st.session_state.grid_response['selected_rows']

    # ... (Pulsanti e chiamate di dialogo)

    with col2:
        if st.button("✏️ Modifica", type="secondary", disabled=modify_request_button_disable):
            if selected_rows:  # Controlla se selected_rows non è vuoto
                selected_row_dict = selected_rows[0]  # Ottieni la riga selezionata come dizionario
                show_request_dialog(selected_row_dict, REQ_STATUS_OPTIONS, sqlite_db.update_request)

    with col3:
        if st.button(" Ordine di Lavoro", type="secondary", disabled=workorder_button_disable):
            if selected_rows:  # Controlla se selected_rows non è vuoto
                selected_row_dict = selected_rows[0]  # Ottieni la riga selezionata come dizionario
                show_workorder_dialog(selected_row_dict, st.session_state.df_workorders, st.session_state.df_woassignedto, st.session_state.df_users, ACTIVE_STATUS, DEFAULT_DEPT_CODE, REQ_STATUS_OPTIONS, sqlite_db.save_workorder, sqlite_db.save_workorder_assignments)

# ... (Resto del tuo codice)