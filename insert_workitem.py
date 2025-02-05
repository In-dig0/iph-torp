import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
# Internal app module
import servant

# def create_workitem(conn)-> None:
   
#     # Load data only once and store in session state
#     session_data = {
#         'df_depts': sqlite_db.load_dept_data,
#         'df_users': sqlite_db.load_users_data,
#         'df_pline': sqlite_db.load_pline_data,
#         'df_pfamily': sqlite_db.load_pfamily_data,
#         'df_category': sqlite_db.load_category_data,
#         'df_type': sqlite_db.load_type_data,
#         'df_lk_type_category': sqlite_db.load_lk_type_category_data,
#         'df_lk_category_detail': sqlite_db.load_lk_category_detail_data,
#         'df_lk_pline_tdtl': sqlite_db.load_lk_pline_tdtl_data,
#         'df_detail': sqlite_db.load_detail_data,
#         'df_requests': sqlite_db.load_requests_data,
#         'df_reqassignedto': sqlite_db.load_reqassignedto_data,
#         'df_attachments': sqlite_db.load_attachments_data,
#         'df_workorders': sqlite_db.load_workorders_data,
#         'df_woassignedto': sqlite_db.load_woassignedto_data,
#         'df_workitems': sqlite_db.load_workitems_data,
#         'df_tskgrl1': sqlite_db.load_tskgrl1_data,
#         'df_tskgrl2': sqlite_db.load_tskgrl2_data,
#     }

#     for key, loader in session_data.items():
#         if key not in st.session_state:
#             st.session_state[key] = loader(conn)
    
#     previus_10days = datetime.datetime.now() - datetime.timedelta(days=10)

#     if "df_out" not in st.session_state:
#         st.session_state.df_out = st.session_state.df_workitems[st.session_state.df_workitems["REFDATE"] > previus_10days]
    
#     tdsp_woassignedto_names_df = st.session_state.df_users[st.session_state.df_users["DEPTCODE"]=="DTD"]["NAME"]
#     tdsp_woassignedto_names_list = list(tdsp_woassignedto_names_df)
#     tdsp_woassignedto_names = sorted(tdsp_woassignedto_names_list)
#     #st.write(tdsp_woassignedto_names)
    
#     selected_tdsp_name = st.sidebar.selectbox(
#         label=":blue[Tech Dept Specialist]", 
#         options=tdsp_woassignedto_names, 
#         index=None,
#         key="tdsp_sidebar"
#     )
#     if selected_tdsp_name: #se è stato selezionato un TD Specialist
#         selected_tdsp_code = st.session_state.df_users[st.session_state.df_users["NAME"] == selected_tdsp_name]["CODE"].iloc[0] #Recupero il codice del TL
#     else:
#         selected_tdsp_code = None # o un valore di default che preferisci 

#     st.session_state["selected_tdsp_name"] = selected_tdsp_name
    
#     # Check if a username is selected
#     if  st.session_state.selected_tdsp_name:       
#         # Filter workitems dynamically
#         filtered_workitems = st.session_state.df_workitems[
#             (st.session_state.df_workitems["TDSPID"] == selected_tdsp_code) #&
#             #(st.session_state.df_workitems["REFDATE"] >= selected_from_date) &
#             #(st.session_state.df_workitems["REFDATE"] <= selected_to_date)
#         ]
#     else:
#         # Filter workitems dynamically
#         filtered_workitems = st.session_state.df_workitems#[
#             #(st.session_state.df_workitems["REFDATE"] >= selected_from_date) &
#             #(st.session_state.df_workitems["REFDATE"] <= selected_to_date)
#         #]


#     df_out = pd.DataFrame(filtered_workitems)
#     #df_out.drop('colonna3', axis=1, inplace=True)

#     st.session_state.df_out = df_out
#         #st.dataframe(df, use_container_width=True, hide_index=True)
    
    
# #    st.subheader()

#     with st.container(border=True):
#         with st.expander(label=":orange[New Workitem]", expanded=False):
#             #st.write(tdsp_woassignedto_names)
#             #st.write(st.session_state["selected_tdsp_name"])
#             # if st.session_state["selected_tdsp_name"]:
#             #     st.write(tdsp_woassignedto_names.index(st.session_state["selected_tdsp_name"]))
#             # TD Specialist Dropdown (Form) - Use the VALUE directly
#             if selected_tdsp_name:
#                 selected_td_specialist_form = st.selectbox(
#                     label=":blue[TD Specialist](:red[*])",
#                     options=tdsp_woassignedto_names,
#                     index=tdsp_woassignedto_names.index(st.session_state["selected_tdsp_name"]),
#                     key="tdsp_form"
#                 )
#             else:
#                 selected_td_specialist_form = st.selectbox(
#                     label=":blue[TD Specialist](:red[*])",
#                     options=tdsp_woassignedto_names,
#                     index=None,
#                     key="tdsp_form"
#                 )


#             if selected_td_specialist_form:
#                 selected_td_specialist_form_code = servant.get_code_from_name(st.session_state.df_users, selected_td_specialist_form, "CODE")
#                 # Correctly filter and extract Work Order IDs
#                 filtered_workorder_df = st.session_state.df_woassignedto[
#                     st.session_state.df_woassignedto["TDSPID"] == selected_td_specialist_form_code
#                 ]
                
#                 if not filtered_workorder_df.empty:  # Check if the DataFrame is not empty
#                     filtered_workorder_list = sorted(filtered_workorder_df["WOID"].tolist())  # Extract WOIDs and convert to a sorted list
#                 else:
#                     filtered_workorder_list = []  # Handle the case where no work orders are found

#             else:
#                 filtered_workorder_list = []
#                 selected_td_specialist_form_code = ""

#             selected_workorder = st.selectbox(
#                 label=":blue[Work Order]", 
#                 options=filtered_workorder_list, 
#                 index=None, 
#                 key="sb_wo"
#             )


#             # Task Group Level 1 dropdown
#             tskgrl1_options = st.session_state.df_tskgrl1["NAME"].tolist()
#             selected_tskgrl1 = st.selectbox(label=":blue[TaskGroup L1]", options=tskgrl1_options, index=None, key="sb_tskgrl1")
#             selected_tskgrl1_code = servant.get_code_from_name(st.session_state.df_tskgrl1, selected_tskgrl1, "CODE")

#             # Task Group Level 2 dropdown (dependent on Level 1)
#             tskgrl2_options = st.session_state.df_tskgrl2[st.session_state.df_tskgrl2['PCODE'] == selected_tskgrl1_code]['NAME'].unique()
#             selected_tskgrl2 = st.selectbox(label=":blue[TaskGroup L2]", options=tskgrl2_options, index=None, key="sb_tskgrl2")
#             selected_tskgrl2_code = servant.get_code_from_name(st.session_state.df_tskgrl2, selected_tskgrl2, "CODE")

#             # Execution Date
#             execution_date = st.date_input(label=":blue[Execution Date]", value=datetime.datetime.now(), format="DD/MM/YYYY")

#             # Quantity
#             quantity = st.number_input(label=":blue[Time]", min_value=0.0, step=0.5, value=0.0, key="in_time_qty")

#             # Description
#             desc = st.text_input(label=":blue[Description]", key="ti_description")

#             # Note
#             note = st.text_area(label=":blue[Notes]", key="ta_note")

#             save_button_disabled = not [
#                 execution_date and 
#                 selected_td_specialist_form_code and 
#                 selected_workorder and 
#                 selected_tskgrl1_code and 
#                 selected_tskgrl2_code and 
#                 quantity
#                 ]
#             # Save button
#             if st.button("Save Work Item", disabled=save_button_disabled):
#                 # Code to save the new work item goes here

#                 witem = {
#                             "wi_refdate": execution_date,
#                             "wo_woid": selected_workorder,
#                             "wi_tdspid": selected_td_specialist_form_code,
#                             "wi_status": "ACTIVE",
#                             "wi_tskgrl1": selected_tskgrl1_code,
#                             "wi_tskgrl2": selected_tskgrl2_code,
#                             "wi_desc": desc,
#                             "wi_note": note,
#                             "wi_time_qty": quantity,
#                             "wi_time_um": "H"
#                         }

#                 columns_name = ["REFDATE","WOID","TDSPID","STATUS","TSKGRL1","TSKGRL2","DESC","NOTE","TIME_QTY", "TIME_UM"]
#                 df_new = pd.DataFrame(
#                     [witem],
#                     columns=columns_name
#                 )
#                 st.session_state.df_out = pd.concat([df_new, st.session_state.df_out], axis=0)        
#                 success = sqlite_db.save_workitem(witem, conn)        
#                 if success:
#                     st.success("New workitem created!")

#     st.header("🎯Last Workitems")
#     with st.container():
#         st.write(f"Number of workitems: `{len(df_out)}`")
#         st.dataframe(df_out, use_container_width=True, hide_index=True)


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

    previus_10days = datetime.datetime.now() - datetime.timedelta(days=10)

    if "df_out" not in st.session_state:
        st.session_state.df_out = st.session_state.df_workitems[st.session_state.df_workitems["REFDATE"] > previus_10days].copy() # .copy() is important

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

    with st.container(border=True):
        with st.expander(label=":orange[New Workitem]", expanded=False):
            if selected_tdsp_name:
                tdsp_index = tdsp_woassignedto_names.index(selected_tdsp_name)  # Get the index
                selected_td_specialist_form = st.selectbox(
                    label=":blue[TD Specialist](:red[*])",
                    options=tdsp_woassignedto_names,
                    index=tdsp_index,  # Use index to set the default selection
                    key="tdsp_form"
                )
            else:
                selected_td_specialist_form = st.selectbox(
                    label=":blue[TD Specialist](:red[*])",
                    options=tdsp_woassignedto_names,
                    index=None,
                    key="tdsp_form"
                )

            if selected_td_specialist_form:
                selected_td_specialist_form_code = servant.get_code_from_name(st.session_state.df_users, selected_td_specialist_form, "CODE")

                # Correctly filter and extract Work Order IDs
                filtered_workorder_df = st.session_state.df_woassignedto[
                    st.session_state.df_woassignedto["TDSPID"] == selected_td_specialist_form_code
                ]
                
                if not filtered_workorder_df.empty:  # Check if the DataFrame is not empty
                    filtered_workorder_list = sorted(filtered_workorder_df["WOID"].tolist())  # Extract WOIDs and convert to a sorted list
                else:
                    filtered_workorder_list = []  # Handle the case where no work orders are found

            else:
                filtered_workorder_list = []
                selected_td_specialist_form_code = ""

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

                    df_new = pd.DataFrame([witem])  # No need to specify columns if the dictionary keys match
                    st.session_state.df_out = pd.concat([df_new, st.session_state.df_out], axis=0, ignore_index=True) # Add ignore_index=True
                    success = sqlite_db.save_workitem(witem, conn)
                    if success:
                        st.success("New workitem created!")

    st.header("🎯Last Workitems")
    with st.container():
        st.write(f"Number of workitems: `{len(st.session_state.df_out)}`")
        st.dataframe(st.session_state.df_out, use_container_width=True, hide_index=True) # Access df_out from session state