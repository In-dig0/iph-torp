import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
from streamlit_calendar import calendar
import calendar as std_cal
from datetime import datetime, timedelta

# Internal app module
import servant

def create_workitem(conn)-> None:
    def show_calendar():
        # Titolo
        #st.title("Esempio di Calendario Streamlit")

        # Ottieni la data corrente
        now = datetime.now()
        # Ottieni l'ultimo giorno del mese corrente
        ultimo_giorno = std_cal.monthrange(now.year, now.month)[1]
        # Crea la data completa per l'ultimo giorno del mese corrente
        last_day_current_month = datetime(now.year, now.month, ultimo_giorno)
    
        # Calcola il primo giorno del mese corrente
        first_day_current_month = datetime(now.year, now.month, 1)   
        # Calcola l'ultimo giorno del mese precedente
        last_day_previous_month = first_day_current_month - timedelta(days=1)   
        # Calcola il primo giorno del mese precedente
        first_day_previous_month = datetime(last_day_previous_month.year, last_day_previous_month.month, 1)
        
        calendar_options = {
            "editable": True,
            "navLinks": True,
            "selectable": True,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek"
            },
            "validRange": {
                "start": f"{first_day_previous_month}",
                "end": f"{last_day_current_month}"
            },
            "hiddenDays": [0, 6],  # Nasconde le domeniche (0) e i sabati (6)
            "locale": {
                "code": "it",
                "week": {
                "dow": 1,  # Inizia la settimana da lunedì
                "doy": 4
                }
            },
            "timeZone": "Europe/Rome",  # Forza il fuso orario a UTC+1
            "buttonText": {
                "today": "Oggi",
                "month": "Mese",
                "week": "Settimana"
            },
            'views': {
            'dayGridMonth': {
                'buttonText': 'Mese',
                'dayHeaderFormat': {
                    'weekday': 'short'  # Solo abbreviazione giorno per vista mensile
                }
            },
            'timeGridWeek': {
                'buttonText': 'Settimana',
                'dayHeaderFormat': {
                    'weekday': 'short',
                    'day': '2-digit',
                    'month': '2-digit',
                }
            }
            }
        }
        custom_css = """
            .fc-event-past {
                opacity: 0.8;
            }
            .fc-event-time {
                font-style: italic;
            }
            .fc-event-title {
                font-weight: 700;
            }
            .fc-toolbar-title {
                font-size: 2rem;
            }
            .fc-daygrid-day.fc-day-other {
                display: none;
            }
            .fc-daygrid-day.fc-day-other {
                display: none;
            }
            .fc-event-title {
                white-space: pre-wrap; /* Forza il testo a capo */
            }
            .fc-col-header-cell {
            background-color: #fad7a0 !important; /* Colore di sfondo per le intestazioni dei giorni della settimana */
            color: #000000; /* Colore del testo per le intestazioni dei giorni della settimana */
            }
        """
        time_wo1 = "2H"
        time_wo2 = "4H"
        calendar_events = [
            {
            "id":'W25-0012',
            "title": f'[W25-0012] Update Scania project-> {time_wo1}',
            "start": '2025-02-12',
            "backgroundColor": '#FF4B4B',
            "borderColor": '#FF6C6C'
            },
            {
            "id": 'W25-0017',
            "title": f'[W25-0017] Update Volvo project-> {time_wo2}',
            "start": '2025-02-12',
            "backgroundColor": '#FF4B4B',
            "borderColor": '#FF6C6C'       
            }
        ]
        
    # Configurazione del calendario con stile personalizzato
        try:
            calendar_output = calendar(
                events=calendar_events, 
                options=calendar_options, 
                custom_css=custom_css,
                key='calendar' # Assign a widget key to prevent state loss
                #style=custom_style
            )
            #st.write(calendar_output)  # Only write if successful
        except Exception as e:
            st.error(f"Error displaying calendar: {e}")  # Display error in Streamlit
            st.write("Check your event data and calendar options.") # Provide user-friendly feedback
            import traceback
            st.write(traceback.format_exc()) # Print the full traceback for debugging
        
        return calendar_output

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

    previus_xdays = datetime.now() - timedelta(days=10)
    previus_xdays = previus_xdays.date()

    if "df_out" not in st.session_state:
        # Esegui il filtro
        st.session_state.df_out = st.session_state.df_workitems[
            st.session_state.df_workitems["REFDATE"].dt.date > previus_xdays
        ].copy()  # .copy() is important

    # Reload workitems if needed
    if 'reload_needed' in st.session_state and st.session_state.reload_needed:
        st.session_state.df_workitems = sqlite_db.load_workitems_data(conn)
        st.session_state.df_out = st.session_state.df_workitems[st.session_state.df_workitems["REFDATE"].dt.date > previus_xdays].copy()
        del st.session_state.reload_needed

    tdsp_woassignedto_names_df = st.session_state.df_users[st.session_state.df_users["DEPTCODE"]=="DTD"]["NAME"]
    tdsp_woassignedto_names_list = list(tdsp_woassignedto_names_df)
    tdsp_woassignedto_names = sorted(tdsp_woassignedto_names_list)


    selected_tdsp_name = st.sidebar.selectbox(
        label=":blue[Tech Dept Specialist]",
        options=tdsp_woassignedto_names,
        index=None,
        key="tdsp_sidebar"
    )

    # Store selected_tdsp_code in session state for consistency
    if selected_tdsp_name:
        selected_tdsp_code = st.session_state.df_users[st.session_state.df_users["NAME"] == selected_tdsp_name]["CODE"].iloc[0]
        st.session_state.selected_tdsp_code = selected_tdsp_code  # Store in session state
    else:
        st.session_state.selected_tdsp_code = None


    # Filter workitems based on the stored code in session state
    if st.session_state.selected_tdsp_code:
        filtered_workitems = st.session_state.df_workitems[
            st.session_state.df_workitems["TDSPID"] == st.session_state.selected_tdsp_code
        ].copy()  # .copy() is crucial here as well
    else:
        filtered_workitems = st.session_state.df_workitems.copy() #.copy() is crucial here as well

    st.session_state.df_out = pd.DataFrame(filtered_workitems)  # No need to drop columns here

    # Reset form fields if needed
    if 'form_reset' in st.session_state and st.session_state.form_reset:
        st.session_state.tdsp_form = st.session_state.tdsp_sidebar
        st.session_state.sb_wo = None
        st.session_state.sb_tskgrl1 = None
        st.session_state.sb_tskgrl2 = None
        st.session_state.in_time_qty = 0.0
        st.session_state.ti_description = ""
        st.session_state.ta_note = ""
        del st.session_state.form_reset

    with st.container(border=True):
        st.header("🎯Last Workitems")
        with st.container():
            # Format the REFDATE column for display
            st.session_state.df_out['REFDATE'] = st.session_state.df_out['REFDATE'].dt.date  # Convert to date objects            
            
            # Apply the function to get descriptions
            st.session_state.df_out['TSKGRL1_DESC'] = st.session_state.df_out['TSKGRL1'].apply(
                lambda code: servant.get_description_from_code(st.session_state.df_tskgrl1, code, "NAME")
            )

            st.session_state.df_out['TSKGRL2_DESC'] = st.session_state.df_out['TSKGRL2'].apply(
                lambda code: servant.get_description_from_code(st.session_state.df_tskgrl2, code, "NAME")
            )

            st.session_state.df_out['TDSP_DESC'] = st.session_state.df_out['TDSPID'].apply(
                lambda code: servant.get_description_from_code(st.session_state.df_users, code, "NAME")
            )            

            # Format the REFDATE column for display
#            st.session_state.df_out['REFDATE'] = st.session_state.df_out['REFDATE'].dt.date
            df_to_display = st.session_state.df_out.drop(columns=["TSKGRL1", "TSKGRL2", "STATUS", "DESC", "NOTE"])
            
                    # Add radio button for view selection
            view_option = st.sidebar.radio(
                ":blue[View Options]", 
                ["Detail View", "Grouped by Work Order"]
            )
            if view_option == "Detail View":
                st.write(f"Number of workitems: `{len(df_to_display)}`")
            
                st.dataframe(df_to_display, 
                            use_container_width=True, 
                            hide_index=True,
                            column_order=["REFDATE", "WOID", "TDSP_DESC", "TSKGRL1_DESC","TIME_QTY", "TIME_UM"]
                            )
            else:
                # Group by WOID and sum TIME_QTY
                grouped_workitems = df_to_display.groupby(["WOID", "TDSP_DESC", "TIME_UM"])["TIME_QTY"].sum().reset_index()
                grouped_workitems = grouped_workitems[["WOID", "TDSP_DESC","TIME_QTY", "TIME_UM"]]
                st.dataframe(data=grouped_workitems, use_container_width=True, hide_index=True)
    calendar_output = show_calendar()
    
    st.write(selected_tdsp_name)
    st.write(calendar_output)#.get["dateClick"])
    st.write(calendar_output.keys())#.get["dateClick"])
    
    if selected_tdsp_name:
        with st.expander(label=":orange[New Workitem]", expanded=False):
            if selected_tdsp_name:
                tdsp_index = tdsp_woassignedto_names.index(selected_tdsp_name)
                selected_td_specialist_form = st.selectbox(
                    label=":blue[TD Specialist](:red[*])",
                    options=tdsp_woassignedto_names,
                    index=tdsp_index if selected_tdsp_name else None,  # Use index or None
                    key="tdsp_form"
                )

            if selected_tdsp_name:
                selected_tdsp_code = servant.get_code_from_name(st.session_state.df_users, selected_tdsp_name, "CODE")

                # Correctly filter and extract Work Order IDs
                filtered_workorder_df = st.session_state.df_woassignedto[
                    st.session_state.df_woassignedto["TDSPID"] == selected_tdsp_code
                ]

                if not filtered_workorder_df.empty:  # Check if the DataFrame is not empty
                    filtered_workorder_list = sorted(filtered_workorder_df["WOID"].tolist())  # Extract WOIDs and convert to a sorted list
                else:
                    filtered_workorder_list = []  # Handle the case where no work orders are found

            else:
                filtered_workorder_list = []
                selected_tdsp_code = ""

            selected_workorder = st.selectbox(
                label=":blue[Work Order]",
                options=filtered_workorder_list,
                index=None,
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
            execution_date = st.date_input(label=":blue[Execution Date]", value=datetime.now(), format="DD/MM/YYYY")

            # Quantity
            quantity = st.number_input(label=":blue[Time]", min_value=0.0, step=0.5, value=0.0, key="in_time_qty")

            # Description
            desc = st.text_input(label=":blue[Description]", key="ti_description")

            # Note
            note = st.text_area(label=":blue[Notes]", key="ta_note")

            save_button_disabled = not all([  # Use all() for cleaner logic
                execution_date,
                selected_tdsp_code,
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



            
