import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
# Internal app module
import servant

def view_workitems(conn) -> None :
    # Initialize session state if not already set
    if 'reset_pending' not in st.session_state:
        st.session_state.reset_pending = False

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

    st.sidebar.divider()
    
    st.sidebar.header(f":orange[Filters]")
    if st.session_state.df_woassignedto is None or st.session_state.df_woassignedto.empty:
        st.warning("No work order assignment data available. Please check your data source")
        st.stop()  # Stop execution of the script
    else:
        unique_tdtl_names = st.session_state.df_woassignedto['USERNAME'].unique()
        sorted_tdtl_names = sorted(unique_tdtl_names)
        tdtl_name_options = list(sorted_tdtl_names)

    # Select Team Leader Name with dynamic filtering
    selected_tdtl_name = st.sidebar.selectbox(
        label=":blue[Tech Dept Team Leader]", 
        options=tdtl_name_options, 
        index=None,
        key="tdtlname_selectbox"
    )
    if selected_tdtl_name: #se è stato selezionato un TL
        selected_tdtl_code = st.session_state.df_users[st.session_state.df_users["NAME"] == selected_tdtl_name]["CODE"].iloc[0] #Recupero il codice del TL
    else:
        selected_tdtl_code = None # o un valore di default che preferisci   


    filtered_tdsp_woassignedto = st.session_state.df_woassignedto[
        (st.session_state.df_woassignedto['TDTLID'] == selected_tdtl_code)
    ]  # Usa isin()            
    
    #st.write(filtered_tdsp_woassignedto)
    
    tdsp_woassignedto_names = []  # Lista per i nomi predefiniti
    for code in filtered_tdsp_woassignedto["TDSPID"]: # Itero sui codici
        name = servant.get_description_from_code(st.session_state.df_users, code, "NAME")
        if name not in tdsp_woassignedto_names:
            tdsp_woassignedto_names.append(name)
        sorted(tdsp_woassignedto_names)    

    #st.write(tdsp_woassignedto_names)
    # Select TD Specialist Name with dynamic filtering
    selected_tdsp_name = st.sidebar.selectbox(
        label=":blue[Tech Dept Specialist]", 
        options=tdsp_woassignedto_names, 
        index=None,
        key="tdspname_selectbox"
    )

    if selected_tdsp_name: #se è stato selezionato un TD Specialist
        selected_tdsp_code = st.session_state.df_users[st.session_state.df_users["NAME"] == selected_tdsp_name]["CODE"].iloc[0] #Recupero il codice del TL
    else:
        selected_tdsp_code = None # o un valore di default che preferisci   

    # Calculate date 10 days ago
    previus_7days = datetime.datetime.now() - datetime.timedelta(days=10)
    previus_7days_date = previus_7days.date()

    selected_from_date = st.sidebar.date_input(
        ":blue[From date]", 
        value=previus_7days_date, 
        key="di_datefrom", 
        format="DD/MM/YYYY"
    )
    selected_to_date = st.sidebar.date_input(
        ":blue[To date]", 
        value="today", 
        key="di_dateto", 
        format="DD/MM/YYYY"
    )

    # Check if a username is selected
    if selected_tdsp_name:       
        # Filter workitems dynamically
        filtered_workitems = st.session_state.df_workitems[
            (st.session_state.df_workitems["TDSPID"] == selected_tdsp_name) &
            (st.session_state.df_workitems["REFDATE"].dt.date >= selected_from_date) &
            (st.session_state.df_workitems["REFDATE"].dt.date <= selected_to_date)
        ]
    else:
        # Filter workitems dynamically
        filtered_workitems = st.session_state.df_workitems[
            (st.session_state.df_workitems["REFDATE"].dt.date >= selected_from_date) &
            (st.session_state.df_workitems["REFDATE"].dt.date <= selected_to_date)
        ]    



        df_out = filtered_workitems
        # Format the REFDATE column for display
        df_out['REFDATE'] = filtered_workitems['REFDATE'].dt.date  # Convert to date objects            
        
        # Apply the function to get descriptions
        df_out['TSKGRL1_DESC'] = filtered_workitems['TSKGRL1'].apply(
            lambda code: servant.get_description_from_code(st.session_state.df_tskgrl1, code, "NAME")
        )

        df_out['TSKGRL2_DESC'] = filtered_workitems['TSKGRL2'].apply(
            lambda code: servant.get_description_from_code(st.session_state.df_tskgrl2, code, "NAME")
        )

        df_out['TDSP_DESC'] = filtered_workitems['TDSPID'].apply(
            lambda code: servant.get_description_from_code(st.session_state.df_users, code, "NAME")
        )            

        df_to_display = df_out.drop(columns=["TSKGRL1", 
                                             "TSKGRL1_DESC", 
                                             "TSKGRL2", 
                                             "STATUS", 
                                             "DESC", 
                                             "NOTE"])



        st.subheader(f":orange[List of Work Items]")
        # Add radio button for view selection
        view_option = st.sidebar.radio(
            ":blue[View Options]", 
            ["Detail View", "Grouped by Work Order"]
        )
        with st.container(border=True, key="Workitem grid"):
            if view_option == "Detail View":
                st.write(f"Number of workitems: `{len(df_to_display)}`")
                st.dataframe(df_to_display, 
                            use_container_width=True, 
                            hide_index=True,
                            column_order=["REFDATE", 
                                          "WOID", 
                                          "TDSP_DESC", 
                                          #"TSKGRL1_DESC", 
                                          "TSKGRL2_DESC", 
                                          "TIME_QTY", 
                                          "TIME_UM"]
                            )

            else:
                # Group by WOID and sum TIME_QTY
                grouped_workitems = df_to_display.groupby(["WOID", "TDSP_DESC", "TIME_UM"])["TIME_QTY"].sum().reset_index()
                grouped_workitems = grouped_workitems[["WOID", "TDSP_DESC","TIME_QTY", "TIME_UM"]]
                st.dataframe(data=grouped_workitems, use_container_width=True, hide_index=True)
    
    
    
    # else:
    #     # If no username is selected, show an empty or default state
    #     st.info("Please select a Tech Department Specialist to view work items")
