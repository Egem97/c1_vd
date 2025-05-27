import asyncio
import streamlit as st
import pandas as pd 

@st.cache_data(ttl=3000)
def fetch_vd_childs():
    
    return pd.read_parquet('https://storage.googleapis.com/data-c1-vd-25/actividad_nino.parquet', engine='pyarrow')

@st.cache_data(ttl=3000)
def fetch_carga_childs():
    
    return pd.read_parquet('https://storage.googleapis.com/data-c1-vd-25/carga_nino.parquet', engine='pyarrow')

@st.cache_data(ttl=3000)
def fetch_vd_gestantes():
    return pd.read_parquet('https://storage.googleapis.com/data-c1-vd-25/actividad_gestante.parquet', engine='pyarrow')

@st.cache_data(ttl=3000)
def fetch_carga_gestantes():
    return pd.read_parquet('https://storage.googleapis.com/data-c1-vd-25/carga_gestantes.parquet', engine='pyarrow')

@st.cache_data(ttl=3000)
def fetch_padron():
    return pd.read_parquet('https://storage.googleapis.com/data-c1-vd-25/padron.parquet', engine='pyarrow')


