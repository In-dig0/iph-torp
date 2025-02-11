import streamlit as st
from streamlit_calendar import calendar

# def show_calendar(conn):
#     calendar_options = {
#         "editable": True,
#         "selectable": True,
#         "headerToolbar": {
#             "left": "today prev,next",
#             "center": "title",
#             "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
#         },
#         # "slotMinTime": "08:00:00",
#         # "slotMaxTime": "18:00:00",
#         "initialView": "resourceTimelineDay",
#         #"resourceGroupField": "building",
#         # "resources": [
#         #     {"id": "a", "building": "Building A", "title": "Building A"},
#         #     {"id": "b", "building": "Building A", "title": "Building B"},
#         #     {"id": "c", "building": "Building B", "title": "Building C"},
#         #     {"id": "d", "building": "Building B", "title": "Building D"},
#         #     {"id": "e", "building": "Building C", "title": "Building E"},
#         #     {"id": "f", "building": "Building C", "title": "Building F"},
#         # ],
#     }
#     calendar_events = [
#         {
#             "title": "Event 1",
#             "start": "2025-02-11T08:30:00",
#             "end": "2025-02-11T10:30:00",
#             "resourceId": "a",
#         },
#         {
#             "title": "Event 2",
#             "start": "2025-02-10T07:30:00",
#             "end": "2025-02-10T10:30:00",
#             "resourceId": "b",
#         },
#         {
#             "title": "Event 3",
#             "start": "2025-02-09T10:40:00",
#             "end": "2025-02-09T12:30:00",
#             "resourceId": "a",
#         }
#     ]
#     custom_css="""
#         .fc-event-past {
#             opacity: 0.8;
#         }
#         .fc-event-time {
#             font-style: italic;
#         }
#         .fc-event-title {
#             font-weight: 700;
#         }
#         .fc-toolbar-title {
#             font-size: 2rem;
#         }
#     """

#     try:
#         calendar_output = calendar(
#             events=calendar_events, 
#             options=calendar_options, 
#             custom_css=custom_css
#         )
#         st.write(calendar_output)  # Only write if successful
#     except Exception as e:
#         st.error(f"Error displaying calendar: {e}")  # Display error in Streamlit
#         st.write("Check your event data and calendar options.") # Provide user-friendly feedback
#         import traceback
#         st.write(traceback.format_exc()) # Print the full traceback for debugging

def show_calendar(conn):
    # Titolo
    st.title("Esempio di Calendario Streamlit")

    # calendar_options = {
    # "editable": True,
    # "navLinks": True,
    # "selectable": True,
    # "headerToolbar": {
    #     "left": "today prev,next",
    #     "center": "title",
    #     "right": "",
    #     },
    # "initialDate": "2025-02-01",
    # }
    calendar_options = {
        "editable": True,
        "navLinks": True,
        "selectable": True,
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        },
        "initialDate": "2025-02-01",
        # Aggiungi la configurazione delle viste
        'views': {
            'dayGridMonth': {'buttonText': 'month'},
            'timeGridWeek': {'buttonText': 'week'}
        }
    }
    
    custom_css="""
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
    """

    try:
        calendar_output = calendar(
#            events=calendar_events, 
            options=calendar_options, 
            custom_css=custom_css
        )
        st.write(calendar_output)  # Only write if successful
    except Exception as e:
        st.error(f"Error displaying calendar: {e}")  # Display error in Streamlit
        st.write("Check your event data and calendar options.") # Provide user-friendly feedback
        import traceback
        st.write(traceback.format_exc()) # Print the full traceback for debugging