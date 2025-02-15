import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
from streamlit_calendar import calendar
import calendar as std_cal
from datetime import datetime, timedelta, date

# Internal app module
import servant

def create_workitem(conn)-> None:
    # #--V0-- Claude
    # def show_calendar():
    #     # Inizializza il flag se non esiste
    #     if 'calendar_needs_update' not in st.session_state:
    #         st.session_state.calendar_needs_update = False

    #     now = datetime.now()
    #     ultimo_giorno = std_cal.monthrange(now.year, now.month)[1]
    #     last_day_current_month = datetime(now.year, now.month, ultimo_giorno)
    #     first_day_current_month = datetime(now.year, now.month, 1)
    #     last_day_previous_month = first_day_current_month - timedelta(days=1)
    #     first_day_previous_month = datetime(last_day_previous_month.year, last_day_previous_month.month, 1)

    #     # Inizializza il dizionario degli eventi se non esiste
    #     if 'event_details' not in st.session_state:
    #         st.session_state.event_details = {}

    #     # Aggiungi un pulsante di refresh
    #     if st.button("🔄 Refresh Calendario"):
    #         st.session_state.calendar_needs_update = True
    #         st.rerun()

    #     cal_col, details_col = st.columns([4, 1])

    #     with cal_col:
    #         # Filtra i workitem in base al TD Specialist selezionato
    #         if st.session_state.selected_tdsp_code:
    #             df_filtered_witems = st.session_state.df_workitems[
    #                 st.session_state.df_workitems["TDSPID"] == st.session_state.selected_tdsp_code
    #             ].copy()
    #         else:
    #             df_filtered_witems = st.session_state.df_workitems.copy()

    #         df_filtered_witems['REFDATE'] = pd.to_datetime(df_filtered_witems['REFDATE']).dt.strftime('%Y-%m-%d')

    #         # Crea gli eventi per il calendario
    #         calendar_events = []
    #         st.session_state.event_details = {}  # Reset dei dettagli degli eventi

    #         for index, row in df_filtered_witems.iterrows():
    #             tdsp_name = servant.get_description_from_code(st.session_state.df_users, row['TDSPID'], "NAME")
    #             tdspid = row['TDSPID']
    #             woid = row['WOID']
    #             date = row['REFDATE']

    #             # Crea una chiave univoca per l'evento
    #             event_key = f"{woid}_{date}_{tdspid}"

    #             # Salva i dettagli dell'evento nella sessione
    #             st.session_state.event_details[event_key] = {
    #                 "woid": woid,
    #                 "tdsp": tdspid,  # Modificato per salvare l'ID invece del nome
    #                 "time_qty": row['TIME_QTY'],
    #                 "time_um": row.get('TIME_UM', 'H'),
    #                 "tskgrl1": row.get('TSKGRL1', ''),  # Salvare il codice invece della descrizione
    #                 "tskgrl2": row.get('TSKGRL2', ''),  # Salvare il codice invece della descrizione
    #                 "description": row.get('DESC', ''),
    #                 "note": row.get('NOTE', ''),
    #                 "date": date,
    #                 "index": index
    #             }

    #             # Crea l'evento per il calendario
    #             event = {
    #                 "id": event_key,
    #                 "title": f"[{woid}] - {row['TIME_QTY']} H - {tdsp_name}",
    #                 "start": date,
    #                 "backgroundColor": '#d4efdf',
    #                 "borderColor": '#a2d9ce',
    #                 "display": "block"
    #             }
    #             calendar_events.append(event)

    #         # [Il resto delle opzioni del calendario rimane invariato]
    #         calendar_options = {
    #             # ... [mantenere le stesse opzioni del calendario]
    #         }

    #         custom_css = """
    #             # ... [mantenere lo stesso CSS]
    #         """

    #         # Mostra il calendario
    #         calendar_output = calendar(
    #             events=calendar_events,
    #             options=calendar_options,
    #             custom_css=custom_css,
    #             key=f'calendar_{st.session_state.selected_tdsp_code or "all"}'
    #         )

    #         # Gestione del click sull'evento
    #         if calendar_output.get("eventClick"):
    #             event_key = calendar_output["eventClick"]["event"]["id"]
    #             st.session_state.selected_event_key = event_key

    #     # Pannello dei dettagli a destra
    #     with details_col:
    #         if hasattr(st.session_state, 'selected_event_key'):
    #             event_key = st.session_state.selected_event_key
    #             if event_key in st.session_state.event_details:
    #                 event_data = st.session_state.event_details[event_key]

    #                 with st.form(key=f"edit_form_{event_key}"):
    #                     st.markdown("### Modifica Workitem")
    #                     st.markdown(f"**Work Order ID:** {event_data['woid']}")
    #                     st.markdown(f"**Specialist:** {servant.get_description_from_code(st.session_state.df_users, event_data['tdsp'], 'NAME')}")
    #                     st.markdown(f"**Data:** {event_data['date']}")

    #                     # Campi modificabili
    #                     new_time_qty = st.number_input(
    #                         ":blue[Time]",
    #                         min_value=0.0,
    #                         max_value=24.0,
    #                         value=float(event_data['time_qty']),
    #                         step=0.5,
    #                         format="%.1f"
    #                     )

    #                     new_description = st.text_area(
    #                         ":blue[Description]",
    #                         value=event_data['description'],
    #                         height=100
    #                     )

    #                     new_note = st.text_area(
    #                         ":blue[Note]",
    #                         value=event_data['note'],
    #                         height=100
    #                     )

    #                     submitted = st.form_submit_button("Save")

    #                     if submitted:
    #                         try:
    #                             # Aggiorna il DataFrame originale
    #                             df_index = event_data['index']
    #                             st.session_state.df_workitems.at[df_index, 'TIME_QTY'] = new_time_qty
    #                             st.session_state.df_workitems.at[df_index, 'DESC'] = new_description
    #                             st.session_state.df_workitems.at[df_index, 'NOTE'] = new_note

    #                             # Prepara il dizionario per l'aggiornamento
    #                             workitem_dict = {
    #                                 "REFDATE": event_data['date'],
    #                                 "WOID": event_data['woid'],
    #                                 "TDSPID": event_data['tdsp'],
    #                                 "TSKGRL1": event_data['tskgrl1'],
    #                                 "TSKGRL2": event_data['tskgrl2'],
    #                                 "TIME_QTY": new_time_qty,
    #                                 "DESC": new_description,
    #                                 "NOTE": new_note
    #                             }

    #                             # Aggiorna il database
    #                             sqlite_db.update_workitem(workitem_dict, conn)  # Modificato l'ordine dei parametri

    #                             # Aggiorna i dettagli dell'evento nella sessione
    #                             st.session_state.event_details[event_key].update({
    #                                 'time_qty': new_time_qty,
    #                                 'description': new_description,
    #                                 'note': new_note
    #                             })

    #                             st.success("Update successfully!")
    #                             st.session_state.calendar_needs_update = True
    #                             time.sleep(1)  # Breve pausa per mostrare il messaggio di successo
    #                             st.rerun()

    #                         except Exception as e:
    #                             st.error(f"ERROR saving workitem data: {str(e)}")

    #     return calendar_output
    def show_calendar():
        # Inizializza il flag se non esiste
        if 'calendar_needs_update' not in st.session_state:
            st.session_state.calendar_needs_update = False

        now = datetime.now()
        ultimo_giorno = std_cal.monthrange(now.year, now.month)[1]
        last_day_current_month = datetime(now.year, now.month, ultimo_giorno)
        first_day_current_month = datetime(now.year, now.month, 1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = datetime(last_day_previous_month.year, last_day_previous_month.month, 1)

        # Inizializza il dizionario degli eventi se non esiste
        if 'event_details' not in st.session_state:
            st.session_state.event_details = {}

        # Aggiungi un pulsante di refresh
        if st.button("🔄 Refresh Calendario"):
            st.session_state.calendar_needs_update = True

        cal_col, details_col = st.columns([4, 1])

        with cal_col:
            # Filtra i workitem in base al TD Specialist selezionato
            if st.session_state.selected_tdsp_code:
                df_filtered_witems = st.session_state.df_workitems[
                    st.session_state.df_workitems["TDSPID"] == st.session_state.selected_tdsp_code
                ].copy()
            else:
                df_filtered_witems = st.session_state.df_workitems.copy()

            df_filtered_witems['REFDATE'] = pd.to_datetime(df_filtered_witems['REFDATE']).dt.strftime('%Y-%m-%d')

            # Crea gli eventi per il calendario
            calendar_events = []
            st.session_state.event_details = {}  # Reset dei dettagli degli eventi

            for index, row in df_filtered_witems.iterrows():
                tdsp_name = servant.get_description_from_code(st.session_state.df_users, row['TDSPID'], "NAME")
                tdspid = row['TDSPID']
                woid = row['WOID']
                date = row['REFDATE']

                # Crea una chiave univoca per l'evento
                event_key = f"{woid}_{date}_{tdspid}"

                # Salva i dettagli dell'evento nella sessione
                st.session_state.event_details[event_key] = {
                    "woid": woid,
                    "tdsp": tdsp_name,
                    "time_qty": row['TIME_QTY'],
                    "time_um": row.get('TIME_UM', 'H'),
                    "tskgrl1": servant.get_description_from_code(st.session_state.df_tskgrl1, row.get('TSKGRL1', ''), "NAME"),
                    "tskgrl2": servant.get_description_from_code(st.session_state.df_tskgrl2, row.get('TSKGRL2', ''), "NAME"),
                    "description": row.get('DESC', ''),
                    "note": row.get('NOTE', ''),
                    "date": date,
                    "index": index
                }

                # Crea l'evento per il calendario
                event = {
                    "id": event_key,
                    "title": f"[{woid}] - {row['TIME_QTY']} H - {tdsp_name}",
                    "start": date,
                    "backgroundColor": '#d4efdf',
                    "borderColor": '#a2d9ce',
                    "display": "block"
                }
                calendar_events.append(event)

            # Opzioni del calendario
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
                "hiddenDays": [0, 6],
                "locale": {
                    "code": "it",
                    "week": {
                        "dow": 1,
                        "doy": 4
                    }
                },
                "timeZone": "Europe/Rome",
                "buttonText": {
                    "today": "Oggi",
                    "month": "Mese",
                    "week": "Settimana"
                },
                'views': {
                    'dayGridMonth': {
                        'buttonText': 'Mese',
                        'dayHeaderFormat': {
                            'weekday': 'short'
                        }
                    },
                    'timeGridWeek': {
                        'buttonText': 'Settimana',
                        'allDaySlot': True,
                        'dayHeaderFormat': {
                            'weekday': 'short',
                            'day': '2-digit',
                            'month': '2-digit',
                        },
                        'slotLabelFormat': {
                            'hour': '',
                            'minute': ''
                        },
                        'height': 300,
                        'slotMinTime': '00:00:00',
                        'slotMaxTime': '00:00:00'
                    }
                }
            }

            # CSS personalizzato
            custom_css = """
                .fc-event-past {
                    opacity: 0.8;
                }
                .fc-event-time {
                    font-style: italic;
                }
                .fc-event-title {
                    font-weight: 700;
                    color: #000000;
                    white-space: pre-wrap;
                    cursor: pointer;
                }            
                .fc-toolbar-title {
                    font-size: 2rem;
                }
                .fc-daygrid-day.fc-day-other {
                    display: none;
                }
                .fc-col-header-cell {
                    background-color: #DAF7A6 !important;
                    color: #000000;
                }
                .fc-timegrid-slot-lane {
                    display: none;
                }
                .fc-timegrid-slot-label {
                    display: none;
                }
            """

            # Mostra il calendario
            if st.session_state.calendar_needs_update:
                with st.spinner("Aggiornamento calendario..."):
                    # Ricarica i dati dal database
                    st.session_state.df_workitems = sqlite_db.load_workitems_data(conn)
                    st.session_state.calendar_needs_update = False  # Reset del flag

                    # Rigenera il calendario
                    calendar_output = calendar(
                        events=calendar_events,
                        options=calendar_options,
                        custom_css=custom_css,
                        key=f'calendar_{st.session_state.selected_tdsp_code or "all"}'
                    )
            else:
                calendar_output = calendar(
                    events=calendar_events,
                    options=calendar_options,
                    custom_css=custom_css,
                    key=f'calendar_{st.session_state.selected_tdsp_code or "all"}'
                )

            # Gestione del click sull'evento
            if calendar_output.get("eventClick"):
                event_key = calendar_output["eventClick"]["event"]["id"]
                st.session_state.selected_event_key = event_key

        # Pannello dei dettagli a destra
        with details_col:
            if hasattr(st.session_state, 'selected_event_key'):
                event_key = st.session_state.selected_event_key
                if event_key in st.session_state.event_details:
                    event_data = st.session_state.event_details[event_key]

                    with st.form(key=f"edit_form_{event_key}"):
                        st.markdown("### Modifica Workitem")
                        st.markdown(f"**Work Order ID:** {event_data['woid']}")
                        st.markdown(f"**Specialist:** {event_data['tdsp']}")
                        st.markdown(f"**Data:** {event_data['date']}")

                        # Campi modificabili
                        new_time_qty = st.number_input(
                            ":blue[Time]",
                            min_value=0.0,
                            max_value=24.0,
                            value=float(event_data['time_qty']),
                            step=0.5,
                            format="%.1f"
                        )

                        new_description = st.text_area(
                            ":blue[Description]",
                            value=event_data['description'],
                            height=100
                        )

                        new_note = st.text_area(
                            ":blue[Note]",
                            value=event_data['note'],
                            height=100
                        )

                        submitted = st.form_submit_button("Save")
                        if submitted:
                            try:
                                # Aggiorna il DataFrame originale
                                df_index = event_data['index']
                                st.session_state.df_workitems.at[df_index, 'TIME_QTY'] = new_time_qty
                                st.session_state.df_workitems.at[df_index, 'DESC'] = new_description
                                st.session_state.df_workitems.at[df_index, 'NOTE'] = new_note

                                # Prepara il dizionario per l'aggiornamento
                                workitem_dict = {
                                    "REFDATE": event_data['date'],
                                    "WOID": event_data['woid'],
                                    "TDSPID": event_data['tdsp'],
                                    "TSKGRL1": event_data['tskgrl1'],
                                    "TSKGRL2": event_data['tskgrl2'],
                                    "TIME_QTY": new_time_qty,
                                    "DESC": new_description,
                                    "NOTE": new_note
                                }

                                # Aggiorna il database
                                sqlite_db.update_workitem(conn, workitem_dict)  # Modificato l'ordine dei parametri

                                # Aggiorna i dettagli dell'evento nella sessione
                                st.session_state.event_details[event_key].update({
                                    'time_qty': new_time_qty,
                                    'description': new_description,
                                    'note': new_note
                                })

                                st.success("Update successfully!")
                                st.session_state.calendar_needs_update = True
                                time.sleep(1)  # Breve pausa per mostrare il messaggio di successo
                                st.rerun()

                            except Exception as e:
                                st.error(f"ERROR saving workitem data: {str(e)}")

                        # if submitted:
                        #     try:
                        #         # Aggiorna il DataFrame originale
                        #         df_index = event_data['index']
                        #         st.session_state.df_workitems.at[df_index, 'TIME_QTY'] = new_time_qty
                        #         st.session_state.df_workitems.at[df_index, 'DESC'] = new_description
                        #         st.session_state.df_workitems.at[df_index, 'NOTE'] = new_note

                        #         # Aggiorna i dettagli dell'evento nella sessione
                        #         st.session_state.event_details[event_key]['time_qty'] = new_time_qty
                        #         st.session_state.event_details[event_key]['description'] = new_description
                        #         st.session_state.event_details[event_key]['note'] = new_note

                        #         # Aggiorna il database
                        #         workitem_dict = {
                        #             "REFDATE": event_data['date'],
                        #             "WOID": event_data['woid'],
                        #             "TDSPID": event_data['tdsp'],
                        #             "TSKGRL1": event_data['tskgrl1'],
                        #             "TSKGRL2": event_data['tskgrl2'],
                        #             "TIME_QTY": new_time_qty,
                        #             "DESC": new_description,
                        #             "NOTE": new_note
                        #         }
                        #         sqlite_db.update_workitem(workitem_dict, conn)

                        #         st.success("Update successfully!")
                        #         st.session_state.calendar_needs_update = True  # Imposta il flag per aggiornare il calendario
                        #         st.rerun()  # Ricarica la pagina

                        #     except Exception as e:
                        #         st.error(f"ERROR saving workitem data: {str(e)}")

        return calendar_output

    # def show_calendar():
    #     if 'calendar_needs_update' not in st.session_state:
    #         st.session_state.calendar_needs_update = False
    #     now = datetime.now()
    #     ultimo_giorno = std_cal.monthrange(now.year, now.month)[1]
    #     last_day_current_month = datetime(now.year, now.month, ultimo_giorno)
    #     first_day_current_month = datetime(now.year, now.month, 1)   
    #     last_day_previous_month = first_day_current_month - timedelta(days=1)   
    #     first_day_previous_month = datetime(last_day_previous_month.year, last_day_previous_month.month, 1)
        
    #     # Inizializza il dizionario degli eventi nella session state se non esiste
    #     if 'event_details' not in st.session_state:
    #         st.session_state.event_details = {}
        
    #     # Crea due colonne: una per il calendario (più larga) e una per i dettagli (più stretta)
    #     cal_col, details_col = st.columns([4, 1])
        
    #     # Container principale per il calendario
    #     with cal_col:
    #         # Filtra i workitem in base al TD Specialist selezionato
    #         if st.session_state.selected_tdsp_code:
    #             df_filtered_witems = st.session_state.df_workitems[
    #                 st.session_state.df_workitems["TDSPID"] == st.session_state.selected_tdsp_code
    #             ].copy()
    #         else:
    #             df_filtered_witems = st.session_state.df_workitems.copy()

    #         # Converti il campo 'REFDATE' in formato YYYY-MM-DD
    #         df_filtered_witems['REFDATE'] = pd.to_datetime(df_filtered_witems['REFDATE']).dt.strftime('%Y-%m-%d')
            
    #         # Crea gli eventi per il calendario e memorizza i dettagli
    #         calendar_events = []
    #         st.session_state.event_details = {}  # Reset dei dettagli degli eventi
            
    #         for index, row in df_filtered_witems.iterrows():
    #             tdsp_name = servant.get_description_from_code(st.session_state.df_users, row['TDSPID'], "NAME")
    #             tdspid = row['TDSPID']
    #             woid = row['WOID']
    #             date = row['REFDATE']
    #             tdspid = row['TDSPID']
                
    #             # Crea una chiave univoca combinando WOID e data
    #             event_key = f"{woid}_{date}_{tdspid}"
                
    #             # Salva i dettagli dell'evento nel dizionario della session state usando la chiave univoca
    #             st.session_state.event_details[event_key] = {
    #                 "woid": woid,
    #                 "tdsp": tdsp_name,
    #                 "time_qty": row['TIME_QTY'],
    #                 "time_um": row.get('TIME_UM', 'H'),
    #                 "tskgrl1": servant.get_description_from_code(st.session_state.df_tskgrl1, row.get('TSKGRL1', ''), "NAME"),
    #                 "tskgrl2": servant.get_description_from_code(st.session_state.df_tskgrl2, row.get('TSKGRL2', ''), "NAME"),
    #                 "description": row.get('DESC', ''),
    #                 "note": row.get('NOTE', ''),
    #                 "date": date,
    #                 "index": index  # Salva l'indice del DataFrame per l'aggiornamento
    #             }

    #             # Crea l'evento per il calendario usando la chiave univoca
    #             event = {
    #                 "id": event_key,
    #                 "title": f"[{woid}] - {row['TIME_QTY']} H - {tdsp_name}",
    #                 "start": date,
    #                 "backgroundColor": '#d4efdf',
    #                 "borderColor": '#a2d9ce',
    #                 "display": "block"
    #             }
    #             calendar_events.append(event)

    #         calendar_options = {
    #             "editable": True,
    #             "navLinks": True,
    #             "selectable": True,
    #             "headerToolbar": {
    #                 "left": "today prev,next",
    #                 "center": "title",
    #                 "right": "dayGridMonth,timeGridWeek"
    #             },
    #             "validRange": {
    #                 "start": f"{first_day_previous_month}",
    #                 "end": f"{last_day_current_month}"
    #             },
    #             "hiddenDays": [0, 6],
    #             "locale": {
    #                 "code": "it",
    #                 "week": {
    #                     "dow": 1,
    #                     "doy": 4
    #                 }
    #             },
    #             "timeZone": "Europe/Rome",
    #             "buttonText": {
    #                 "today": "Oggi",
    #                 "month": "Mese",
    #                 "week": "Settimana"
    #             },
    #             'views': {
    #                 'dayGridMonth': {
    #                     'buttonText': 'Mese',
    #                     'dayHeaderFormat': {
    #                         'weekday': 'short'
    #                     }
    #                 },
    #                 'timeGridWeek': {
    #                     'buttonText': 'Settimana',
    #                     'allDaySlot': True,  # Nasconde lo slot "all-day"
    #                     'dayHeaderFormat': {
    #                         'weekday': 'short',
    #                         'day': '2-digit',
    #                         'month': '2-digit',
    #                     },
    #                     'slotLabelFormat': {  # Nasconde le etichette delle ore
    #                         'hour': '',
    #                         'minute': ''
    #                     },
    #                     # The key change for weekly view height:
    #                     'height': 300,  # or a specific pixel value like 300
    #                     'slotMinTime': '00:00:00',  # Imposta l'ora di inizio della griglia fuori dalla vista
    #                     'slotMaxTime': '00:00:00'   # Imposta l'ora di fine della griglia fuori dalla vista
    #                     }
    #             }
    #         }

    #         custom_css = """
    #             .fc-event-past {
    #                 opacity: 0.8;
    #             }
    #             .fc-event-time {
    #                 font-style: italic;
    #             }
    #             .fc-event-title {
    #                 font-weight: 700;
    #                 color: #000000;
    #                 white-space: pre-wrap;
    #                 cursor: pointer;
    #             }            
    #             .fc-toolbar-title {
    #                 font-size: 2rem;
    #             }
    #             .fc-daygrid-day.fc-day-other {
    #                 display: none;
    #             }
    #             .fc-col-header-cell {
    #                 background-color: #DAF7A6 !important;
    #                 color: #000000;
    #             }
    #             .fc-timegrid-slot-lane {
    #                 display: none;
    #             }
    #             /* Nasconde le etichette degli slot orari */
    #             .fc-timegrid-slot-label {
    #                 display: none;
    #             }
    #         """



    #         if st.session_state.calendar_needs_update:
    #             st.session_state.calendar_needs_update = False  # Reset the flag

    #             # Display a spinner while the calendar updates
    #             with st.spinner("Aggiornamento calendario..."):
    #                 calendar_output = calendar(
    #                     events=calendar_events,
    #                     options=calendar_options,
    #                     custom_css=custom_css,
    #                     key=f'calendar_{st.session_state.selected_tdsp_code or "all"}'
    #                 )
    #         else:
    #             calendar_output = calendar(
    #                 events=calendar_events,
    #                 options=calendar_options,
    #                 custom_css=custom_css,
    #                 key=f'calendar_{st.session_state.selected_tdsp_code or "all"}'
    #             )

    #         # Gestione del click sull'evento
    #         if calendar_output.get("eventClick"):
    #             event_key = calendar_output["eventClick"]["event"]["id"]
    #             st.session_state.selected_event_key = event_key


    # # Pannello dei dettagli a destra
    #     with details_col:
    #         if hasattr(st.session_state, 'selected_event_key'):
    #             event_key = st.session_state.selected_event_key
    #             if event_key in st.session_state.event_details:
    #                 event_data = st.session_state.event_details[event_key]

    #                 # Crea un form per l'editing
    #                 with st.form(key=f"edit_form_{event_key}"):
    #                     st.markdown("### Modifica Workitem")
    #                     st.markdown(f"**Work Order ID:** {event_data['woid']}")
    #                     st.markdown(f"**Specialist:** {event_data['tdsp']}")
    #                     st.markdown(f"**Data:** {event_data['date']}")

    #                     tskgrl1_opt = st.session_state.df_tskgrl1["NAME"].tolist()
    #                     tskgrl1_options = sorted(tskgrl1_opt)
    #                     selected_tskgrl1 = st.selectbox(
    #                         label=":blue[TaskGroup L1]", 
    #                         options=tskgrl1_options, 
    #                         index=tskgrl1_options.index(event_data['tskgrl1']), 
    #                         key="sb_tskgrl1m"
    #                     )
    #                     selected_tskgrl1_code = servant.get_code_from_name(st.session_state.df_tskgrl1, selected_tskgrl1, "CODE")

    #                     # Task Group Level 2 dropdown (dependent on Level 1)
    #                     tskgrl2_opt = st.session_state.df_tskgrl2[st.session_state.df_tskgrl2['PCODE'] == selected_tskgrl1_code]['NAME'].tolist()
    #                     tskgrl2_options = sorted(tskgrl2_opt)
    #                     selected_tskgrl2 = st.selectbox(
    #                         label=":blue[TaskGroup L2]", 
    #                         options=tskgrl2_options, 
    #                         index=tskgrl2_options.index(event_data['tskgrl2']), 
    #                         key="sb_tskgrl2m"
    #                     )
    #                     selected_tskgrl2_code = servant.get_code_from_name(st.session_state.df_tskgrl2, selected_tskgrl2, "CODE")
                       
    #                    # Campo editabile per il tempo
    #                     new_time_qty = st.number_input(
    #                         ":blue[Time]",
    #                         min_value=0.0,
    #                         max_value=24.0,
    #                         value=float(event_data['time_qty']),
    #                         step=0.5,
    #                         format="%.1f"
    #                     )

    #                     # st.markdown(f"**Task Group 1:** {event_data['tskgrl1']}")
    #                     # st.markdown(f"**Task Group 2:** {event_data['tskgrl2']}")

    #                     # Campo editabile per la descrizione
    #                     new_description = st.text_area(
    #                         ":blue[Description]",
    #                         value=event_data['description'],
    #                         height=100
    #                     )

    #                     # Campo editabile per le note
    #                     new_note = st.text_area(
    #                         ":blue[Note]",
    #                         value=event_data['note'],
    #                         height=100
    #                     )

    #                     # Pulsante per salvare le modifiche
    #                     submitted = st.form_submit_button("Save")

    #                     if submitted:
    #                         try:
    #                             # Aggiorna il DataFrame originale
    #                             df_index = event_data['index']
    #                             st.session_state.df_workitems.at[df_index, 'TIME_QTY'] = new_time_qty
    #                             st.session_state.df_workitems.at[df_index, 'DESC'] = new_description
    #                             st.session_state.df_workitems.at[df_index, 'NOTE'] = new_note

    #                             # Aggiorna lo stato della sessione
    #                             st.session_state.event_details[event_key]['time_qty'] = new_time_qty
    #                             st.session_state.event_details[event_key]['description'] = new_description
    #                             st.session_state.event_details[event_key]['note'] = new_note

    #                             tdspid = servant.get_code_from_name(st.session_state.df_users, event_data['tdsp'], "CODE")
    #                             if tdspid:
    #                                 tdspcode = tdspid
                                
    #                             workitem_dict = {
    #                                 "REFDATE": event_data['date'],
    #                                 "WOID": event_data['woid'],
    #                                 "TDSPID": tdspcode,
    #                                 "TSKGRL1": selected_tskgrl1_code,
    #                                 "TSKGRL2": selected_tskgrl2_code,
    #                                 "TIME_QTY": new_time_qty,
    #                                 "DESC": new_description,
    #                                 "NOTE": new_note
    #                                 }
    #                             #st.write(workitem_dict)
    #                             sqlite_db.update_workitem(
    #                                 workitem_dict,
    #                                 conn
    #                             )
                                
    #                             st.success("Update successfully!")
    #                             # Set the flag to trigger calendar update
    #                             st.session_state.calendar_needs_update = True

    #                             # Forza il refresh della pagina per aggiornare il calendario
    #                             st.rerun()  # Use st.rerun()

    #                         except Exception as e:
    #                             st.error(f"ERROR saving workitem data: {str(e)}")
    
    #     return calendar_output


    def show_workitem_dataframe():
        with st.container(border=True):
            st.header("🎯Workitems List")
            with st.expander(label=":orange[Last Workitem]", expanded=False):
                with st.container():
                    # Format the REFDATE column for display
                    st.session_state.df_out['REFDATE'] = st.session_state.df_out['REFDATE']#.dt.strftime('%Y-%m-%d')#.dt.date  # Convert to date objects            
                    
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
    
    filtered_workitems = filtered_workitems.sort_values(['REFDATE','TDSPID','WOID'], ascending=[False, True, True])
    

    st.session_state.df_out = pd.DataFrame(filtered_workitems)  # No need to drop columns here

    # Reset form fields if needed
    if 'form_reset' in st.session_state and st.session_state.form_reset:
        #st.session_state.tdsp_form = st.session_state.tdsp_sidebar
        st.session_state.tdsp_form = st.session_state.selected_tdsp_code
        st.session_state.sb_wo = None
        st.session_state.sb_tskgrl1 = None
        st.session_state.sb_tskgrl2 = None
        st.session_state.in_time_qty = 0.0
        st.session_state.ti_description = ""
        st.session_state.ta_note = ""
        del st.session_state.form_reset
    
    #show_workitem_dataframe()
    calendar_output = show_calendar()
    
    #st.write(selected_tdsp_name)
    #st.write(calendar_output) 
    if calendar_output.get("callback") == "dateClick":
        d = calendar_output.get("dateClick")
        date_iso = d.get("date")
        # 1. Converti la stringa in un oggetto datetime
        data_datetime = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))

        # 2. Formatta l'oggetto datetime nel formato desiderato
        formatted_date = data_datetime.strftime("%Y-%m-%d")
        #st.write(formatted_date)
    else:
        st.write(f"Pick a day from calendar first!")
        formatted_date = datetime.now().strftime("%Y-%m-%d")    
    
    if selected_tdsp_name:
        with st.expander(label=":orange[New Workitem]", expanded=False):
            if selected_tdsp_name:
                # Verifica se selected_tdsp_name è nella lista
                if selected_tdsp_name in tdsp_woassignedto_names:
                    tdsp_index = tdsp_woassignedto_names.index(selected_tdsp_name)
                    selected_tdsp_code = servant.get_code_from_name(st.session_state.df_users, selected_tdsp_name, "CODE")
                else:
                    # Gestisci il caso in cui selected_tdsp_name non è nella lista
                    tdsp_index = 0  # o un altro valore predefinito

                selected_td_specialist_form = st.selectbox(
                    label=":blue[TD Specialist](:red[*])",
                    options=tdsp_woassignedto_names,
                    index=tdsp_index
                )
            else:
                # Gestisci il caso in cui selected_tdsp_name è None o vuoto
                selected_td_specialist_form = st.selectbox(
                    label=":blue[TD Specialist](:red[*])",
                    options=tdsp_woassignedto_names,
                    index=0  # o un altro valore predefinito
                )
                selected_tdsp_code = servant.get_code_from_name(st.session_state.df_users, selected_td_specialist_form, "CODE")


            # Correctly filter and extract Work Order IDs
            filtered_workorder_df = st.session_state.df_woassignedto[
                st.session_state.df_woassignedto["TDSPID"] == selected_tdsp_code
            ]

            if not filtered_workorder_df.empty:  # Check if the DataFrame is not empty
                filtered_workorder_list = sorted(filtered_workorder_df["WOID"].tolist())  # Extract WOIDs and convert to a sorted list
            else:
                filtered_workorder_list = []  # Handle the case where no work orders are found

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
            if formatted_date:
                #st.write(formatted_date)
                default_date_str = formatted_date
                default_date = date.fromisoformat(default_date_str) #Convert to date object
                #st.write(default_date)
        
            execution_date = st.date_input(label=":blue[Execution Date]", value=default_date, format="DD/MM/YYYY")

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
                    "wi_tdspid": selected_tdsp_code,
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



            
