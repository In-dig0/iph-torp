import streamlit as st
from streamlit_calendar import calendar


def show_calendar(conn):
    # Titolo
    st.title("Esempio di Calendario Streamlit")

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
        "initialDate": "2025-02-01",
        "validRange": {
            "start": "2025-02-01",
            "end": "2025-02-14"
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
    """

    calendar_events = [
        {
        "id":'W25-0012',
        "title": '[W25-0012] Update Scania project -> 2H',
        "start": '2025-02-12',
        "backgroundColor": '#FF6C6C',
        "borderColor": '#FF6C6C'
        },
        {
        "id": 'W25-0017',
        "title": '[W25-0017] Update Volvo project -> 4H',
        "start": '2025-02-12',
        "backgroundColor": '#FF6C6C',
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