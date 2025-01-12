import streamlit as st
import pandas as pd
from styles import styles
from utils.cache_handler import fetch_vd_childs

def vd_childs():
    styles(1)
    st.title("Visitas a Niños")
    df = fetch_vd_childs()
    st.dataframe(df)