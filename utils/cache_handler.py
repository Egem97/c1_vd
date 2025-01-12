import asyncio
import streamlit as st
import pandas as pd 

@st.cache_data(ttl=1200)
def fetch_vd_childs():
    
    return pd.read_parquet('https://storage.googleapis.com/data-c1-vd-25/actividad_nino.parquet', engine='pyarrow')