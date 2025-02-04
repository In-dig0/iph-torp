import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
# Internal app module
import servant

def create_workitem(conn)-> None:
   
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

    # st.subheader(":orange[Last Workitem]")
    # with st.container():
    # Calculate date 7 days ago
    previus_7days = datetime.datetime.now() - datetime.timedelta(days=7)
    today = datetime.datetime.now()

    # Convert DATE column to datetime objects (if it's not already)
    if st.session_state.df_workitems['DATE'].dtype != 'datetime64[ns]':  # Check the data type
        st.session_state.df_workitems['DATE'] = pd.to_datetime(st.session_state.df_workitems['DATE'])        
      
    # Filter workitems dynamically
    filtered_workitems = st.session_state.df_workitems
    [
#            (st.session_state.df_workitems["TDSPID"] == selected_usercode) &
        (st.session_state.df_workitems["DATE"] >= previus_7days) &
        (st.session_state.df_workitems["DATE"] <= today)
    ]

    df = pd.DataFrame(filtered_workitems)
    st.session_state.df = df
        #st.dataframe(df, use_container_width=True, hide_index=True)
    
    
#    st.subheader()

    with st.container(border=True):
        with st.expander(label=":orange[New Workitem]", expanded=False):
            # TD Specialist dropdown
            td_specialists = st.session_state.df_woassignedto['USERNAME'].unique()
            sorted_td_specialist = sorted(td_specialists)
            td_specialist_options = list(sorted_td_specialist)
            selected_td_specialist = st.selectbox(label=":blue[TD Specialist]", options=td_specialist_options, index=None, key="sb_tds")
            selected_td_specialist_code = servant.get_code_from_name(st.session_state.df_users, selected_td_specialist, "CODE")

            # Work Order Number dropdown 
            workorders = st.session_state.df_woassignedto['WOID'].unique()
            sorted_workorders = sorted(workorders)
            workorders_option = list(sorted_workorders)
            selected_workorder = st.selectbox(label=":blue[Work Order]", options=workorders_option, index=None, key="sb_wo")

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

            # Save button
            if st.button("Save"):
                # Code to save the new work item goes here
                st.success("New workitem created!")

                today = datetime.datetime.now().strftime("%Y-%m-%d")
                df_new = pd.DataFrame(
                    [
                        {
                            "DATE": execution_date,
                            "WOID": selected_workorder,
                            "TDSPID": selected_td_specialist_code,
                            "STATUS": "ACTIVE",
                            "TSKGRL1": selected_tskgrl1_code,
                            "TSKGR21": selected_tskgrl2_code,
                            "DESC": desc,
                            "NOTE": note,
                            "TIME_QTY": quantity,
                            "TIME_UM": "H"
                        }
                    ]
                )
                st.dataframe(df_new, use_container_width=True, hide_index=True)
                st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

    st.header("Last Workitems")
    with st.container():
        st.write(f"Number of workitems: `{len(st.session_state.df)}`")

# st.info(
#     "You can edit the tickets by double clicking on a cell. Note how the plots below "
#     "update automatically! You can also sort the table by clicking on the column headers.",
#     icon="✍️",
# )

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
        edited_df = st.data_editor(
            st.session_state.df,
            use_container_width=True,
            hide_index=True,
            # column_config={
            #     "Status": st.column_config.SelectboxColumn(
            #         "Status",
            #         help="Ticket status",
            #         options=["Open", "In Progress", "Closed"],
            #         required=True,
            #     ),
            #     "Priority": st.column_config.SelectboxColumn(
            #         "Priority",
            #         help="Priority",
            #         options=["High", "Medium", "Low"],
            #         required=True,
            #     ),
            #},
            # Disable editing the ID and Date Submitted columns.
            disabled=["WOID"],
        )
