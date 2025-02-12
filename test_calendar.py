import streamlit as st
from streamlit_calendar import calendar


def show_calendar(conn):
    # Titolo
    st.title("Esempio di Calendario Streamlit")

    # Ottieni la data corrente
    now = datetime.now()
    # Ottieni l'ultimo giorno del mese corrente
    ultimo_giorno = calendar.monthrange(now.year, now.month)[1]
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
        #"initialDate": "2025-02-01",
        #"initialDate": f"2025-02-01",
        "validRange": {
            "start": f"{first_day_previous_month}",
            "end": f"{last_day_current_month}"
        },
        "hiddenDays": [0, 6],  # Nasconde le domeniche (0) e i sabati (6)
        #"locale": "it",  # Imposta la lingua italiana
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
        .fc-daygrid-day[data-date="2025-02-16"],
        .fc-daygrid-day[data-date="2025-02-17"],
        .fc-daygrid-day[data-date="2025-02-18"],
        .fc-daygrid-day[data-date="2025-02-19"],
        .fc-daygrid-day[data-date="2025-02-20"],
        .fc-daygrid-day[data-date="2025-02-21"],
        .fc-daygrid-day[data-date="2025-02-22"],
        .fc-daygrid-day[data-date="2025-02-23"],
        .fc-daygrid-day[data-date="2025-02-24"],
        .fc-daygrid-day[data-date="2025-02-25"],
        .fc-daygrid-day[data-date="2025-02-26"],
        .fc-daygrid-day[data-date="2025-02-27"],
        .fc-daygrid-day[data-date="2025-02-28"] {
            visibility: hidden;
        }
        .fc-event-title {
            white-space: pre-wrap; /* Forza il testo a capo */
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
        st.write(calendar_output)  # Only write if successful
    except Exception as e:
        st.error(f"Error displaying calendar: {e}")  # Display error in Streamlit
        st.write("Check your event data and calendar options.") # Provide user-friendly feedback
        import traceback
        st.write(traceback.format_exc()) # Print the full traceback for debugging