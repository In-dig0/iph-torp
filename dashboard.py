import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
import altair as alt
# Internal app module
import servant

status_plot = (
    alt.Chart(st.session_state.df_requests)
    .mark_bar()
    .encode(
        x=alt.X('DATE:O', 
            title='Date',
            axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('count():Q',
            title='Number of Requests'),
        xOffset="STATUS:N",  # Modificato da "Status:N" a "STATUS:N"
        color=alt.Color("STATUS:N", title="Status"),  # Modificato da "Status:N" a "STATUS:N"
        tooltip=['INSDATE', 'STATUS', 'count()']  # Modificato da 'Status' a 'STATUS'
    )
    .configure_legend(
        orient="bottom",
        titleFontSize=14,
        labelFontSize=14,
        titlePadding=5
    )
)