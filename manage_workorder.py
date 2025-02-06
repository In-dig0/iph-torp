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
STATUS_NEW = "NEW"
STATUS_WIP = "WIP"
REQ_STATUS_OPTIONS = ['NEW', 'PENDING', 'ASSIGNED', 'WIP', 'COMPLETED', 'DELETED']



def reset_application_state():
    """Reset all session state variables and cached data"""
    # Lista delle chiavi di sessione da eliminare
    keys_to_clear = [
        'wo_grid_data',
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

##########################################
def create_workitem(wo):
    with st.container(border=True):
        
        tdsp_woassignedto_names_df = st.session_state.df_users[st.session_state.df_users["DEPTCODE"]=="DTD"]["NAME"]
        tdsp_woassignedto_names_list = list(tdsp_woassignedto_names_df)
        tdsp_woassignedto_names = sorted(tdsp_woassignedto_names_list)
        selected_tdsp = st.selectbox(
            label=":blue[TD Specialist](:red[*])",
            options=tdsp_woassignedto_names,
            index=None, 
            key="sb_tdsp"
        )

        if selected_tdsp:
            selected_tdsp_code = servant.get_code_from_name(st.session_state.df_users, selected_tdsp, "CODE")

        filtered_workorder_list = sorted(list(wo["WOID"]["1"]))  
        selected_workorder = st.selectbox(
            label=":blue[Work Order]",
            options=filtered_workorder_list,
            index=0,
            key="sb_wo"
            )

        # Task Group Level 1 dropdown
        tskgrl1_options = st.session_state.df_tskgrl1["NAME"].tolist()
        selected_tskgrl1 = st.selectbox(label=":blue[TaskGroup L1]", options=tskgrl1_options, index=None, key="sb_tskgrl1")
        selected_tskgrl1_code = servant.get_code_from_name(st.session_state.df_tskgrl1, selected_tskgrl1, "CODE")

        # Task Group Level 2 dropdown (dependent on Level 1)
        tskgrl2_options = st.session_state.df_tskgrl2[st.session_state.df_tskgrl2['PCODE'] == selected_tskgrl1_code]['NAME'].unique()
        selected_tskgrl2 = st.selectbox(label=":blue[TaskGroup L2]", options=tskgrl2_options, index=None, key="sb_tskgrl2")
        selected_tskgrl2_code = servant.get_code_from_name(st.session_state.df_tskgrl2, selected_tskgrl2, "CODE")

        # Execution Date
        execution_date = st.date_input(label=":blue[Execution Date]", value=datetime.datetime.now(), format="DD/MM/YYYY")

        # Quantity
        quantity = st.number_input(label=":blue[Time]", min_value=0.0, step=0.5, value=0.0, key="in_time_qty")

        # Description
        desc = st.text_input(label=":blue[Description]", key="ti_description")

        # Note
        note = st.text_area(label=":blue[Notes]", key="ta_note")

        save_button_disabled = not all([  # Use all() for cleaner logic
            execution_date,
            selected_td_specialist_form_code,
            selected_workorder,
            selected_tskgrl1_code,
            selected_tskgrl2_code,
            quantity
        ])

        if st.button("Save Work Item", disabled=save_button_disabled):
            witem = {
                "wi_refdate": execution_date,
                "wo_woid": selected_workorder,
                "wi_tdspid": selected_td_specialist_form_code,
                "wi_status": "ACTIVE",
                "wi_tskgrl1": selected_tskgrl1_code,
                "wi_tskgrl2": selected_tskgrl2_code,
                "wi_desc": desc,
                "wi_note": note,
                "wi_time_qty": quantity,
                "wi_time_um": "H"
            }

            success = sqlite_db.save_workitem(witem, conn)
            if success:
                st.success("New workitem created!")
                # Set a flag in session state to indicate that a reload is needed
                st.session_state.reload_needed = True
                # Set default values for the form fields
                st.session_state.form_reset = True
                time.sleep(1)
                st.rerun()
                return True
            else:
                st.error("**ERROR saving WorkItem!")
                return False        


##########################################

def manage_workorder(conn):
    # Initialize session state
    sqlite_db.initialize_session_state(conn)
    #st.write("P00")
    #st.write(st.session_state.df_workorders)
    
    # Load data only once when needed
    if "df_workorders" not in st.session_state:
        st.session_state.df_workorders = sqlite_db.df_workorders(conn)
    if "wo_grid_data" not in st.session_state:
        st.session_state.wo_grid_data = st.session_state.df_workorders.copy()
    
    #st.write("P01")
    #st.write(st.session_state.wo_grid_data)

    # Create display DataFrame
    df_workorder_grid = pd.DataFrame({
        'WOID': st.session_state.df_workorders['WOID'],
        'INSDATE': pd.to_datetime(st.session_state.df_workorders['INSDATE']).dt.strftime('%d/%m/%Y'),
        'TDTLID': st.session_state.df_workorders['TDTLID'],
        'STATUS': st.session_state.df_workorders['STATUS'],
        'SEQUENCE': st.session_state.df_workorders.get('SEQUENCE', None),  # Preserve SEQUENCE values
        'TYPE': st.session_state.df_workorders['TYPE'],
        'REQID': st.session_state.df_workorders['REQID'],
        'TITLE': st.session_state.df_workorders['TITLE']
    })

    # Cell styling
    cellStyle = JsCode("""
        function(params) {
            if (params.column.colId === 'WOID') {
                return {
                    'backgroundColor': '#a2add0',
                    'color': '#111810',
                    'fontWeight': 'bold'
                };
            }
            return null;
        }
    """)

    sequenceCellStyle = JsCode("""
        function(params) {
            if (params.value === 'HIGH' || params.value === 'LOW') {
                return {
                    'color': 'red'
                };
            }
            return null;
        }
    """)

        # Sort function considering SEQUENCE values
    def sort_dataframe(df):
        if 'SEQUENCE' in df.columns:
            # Create a priority map for sorting (HIGH should be first)
            priority_map = {'HIGH': 1, 'LOW': 2}
            
            # Create a temporary column for sorting
            df = df.copy()
            df['sort_priority'] = df['SEQUENCE'].map(lambda x: priority_map.get(x, 3))
            
            # Sort by priority
            df = df.sort_values('sort_priority', ascending=True)
            
            # Remove temporary column
            df = df.drop('sort_priority', axis=1)
            
            return df
        return df

    # Grid configuration
    grid_builder = GridOptionsBuilder.from_dataframe(df_workorder_grid)
    grid_builder.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
        enableRowGroup=False
    )
    grid_builder.configure_pagination(paginationAutoPageSize=False, paginationPageSize=12)
    grid_builder.configure_grid_options(domLayout='normal')
    grid_builder.configure_column("WOID", cellStyle=cellStyle)
    grid_builder.configure_column("SEQUENCE", 
                                editable=True, 
                                cellEditor='agSelectCellEditor', 
                                cellEditorParams={'values': ['HIGH', 'LOW']}, 
                                cellStyle=sequenceCellStyle)
    grid_builder.configure_selection(selection_mode='single', use_checkbox=True)
    grid_options = grid_builder.build()
    # List of available themes
    available_themes = ["streamlit", "alpine", "balham", "material"]
    # Sidebar filters
    st.sidebar.header(":blue[Filters]")
    wo_status_options = list(df_workorder_grid['STATUS'].drop_duplicates().sort_values())
    status_filter = st.sidebar.selectbox(
        ":orange[Status]", 
        wo_status_options, 
        index=None,
        key='Status_value'
    )
    
    wo_tdtl_options = df_workorder_grid['TDTLID'].drop_duplicates().sort_values()
    tdtl_filter = st.sidebar.selectbox(
        ":orange[TDTL Id]", 
        wo_tdtl_options, 
        index=None,
        key='tdtl_value'
    )

    # Apply filters
    filtered_data = df_workorder_grid.copy()
    if status_filter:
        filtered_data = filtered_data[filtered_data["STATUS"] == status_filter]
    if tdtl_filter:
        filtered_data = filtered_data[filtered_data["TDTLID"] == tdtl_filter]

    # Sort and display grid
    st.subheader(":orange[Work Order list]")
    filtered_data = sort_dataframe(filtered_data)
    
    grid_response = AgGrid(
        filtered_data,
        gridOptions=grid_options,
        allow_unsafe_jscode=True,
        theme=available_themes[2],
        fit_columns_on_grid_load=False,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.AS_INPUT,
        key="workorder_grid"
    )

    if grid_response['data'] is not None:
        new_data = pd.DataFrame(grid_response['data'])
        new_data = sort_dataframe(new_data)  # Sort before updating
        st.session_state.wo_grid_data = new_data

    # Handle selected rows - Safe handling of None case
    selected_rows = grid_response.get('selected_rows', [])
    has_selection = selected_rows is not None and len(selected_rows) > 0
    workorder_button_disable = not has_selection
    workitem_button_disable = not has_selection

    # Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh data", type="secondary"):
            st.session_state.df_workorders = sqlite_db.load_workorders_data(conn)
            st.session_state.wo_grid_data = st.session_state.df_workorders.copy()
            st.rerun()
#            reset_application_state()
#             st.session_state.df_workorders = sqlite_db.load_workorder_data(conn)  # Ricarica i dati dal database
    
    with col2:
        if st.button("✏️ Modify Work Order", type="secondary", disabled=workorder_button_disable):
            if has_selection:
                pass
                #selected_row_dict = selected_rows[0]
                # Uncomment when dialog is implemented
                #show_workorder_dialog(selected_row_dict, WO_STATUS_OPTIONS, sqlite_db.update_workorder, conn)

    with col3:
        if st.button("🎯 Create Work Item", type="secondary", disabled=workitem_button_disable):
            if has_selection:
                st.write(selected_rows)
                #selected_row_dict = selected_rows.to_dict()
                workorder_id = selected_rows["WOID"].to_list()
                st.write(workorder_id)
                #success = create_work_item(workorder_id)

