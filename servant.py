import streamlit as st
import pandas as pd
import sqlite_db
import datetime
import time
from typing import Optional, Tuple, Dict, List
import io
import re
import os
import pandas as pd
import hmac
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def get_code_from_name(df, name, code_column):
    result = df[df["NAME"] == name][code_column]
    return list(result)[0] if not result.empty else ""


def get_description_from_code(df, code, description_column):
    result = df[df["CODE"] == code][description_column]
    return list(result)[0] if not result.empty else ""


def convert_df(df):
    df_clean = df.copy()
    df_clean["Column value"] = df_clean["Column value"].apply(remove_html_tags)
    return df_clean.to_csv(index=False, sep=';').encode('utf-8')


def clean_html_tags(text):
    """Rimuove i tag HTML dal testo"""
    if isinstance(text, str):
        # Rimuove i tag <b> e </b>
        text = re.sub(r'</?b>', '', text)
        # Rimuove i tag span con stile
        text = re.sub(r'<span[^>]*>', '', text)
        text = re.sub(r'</span>', '', text)
    return text


def create_pdf_buffer(df):
    """
    Crea un buffer PDF contenente la tabella formattata
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Pulisci i dati dai tag HTML per il PDF
    df_clean = df.copy()
    df_clean['Column value'] = df_clean['Column value'].apply(clean_html_tags)
    
    # Converti DataFrame in lista di liste per la tabella
    data = [df_clean.columns.tolist()] + df_clean.values.tolist()
    
    # Crea e stila la tabella
    table = Table(data)
    table.setStyle(TableStyle([
        # Stile header
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        # Stile celle
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Stile speciale per Request Id (bold)
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        # Stile speciale per Status (verde)
        ('TEXTCOLOR', (1, 3), (1, 3), colors.green),
    ]))
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.title("📝 :blue[TORP App Login]")
            st.divider()
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            #del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

