import asyncio
import streamlit as st
import pandas as pd 
from constans import BUCKET_NAME
DEELAY_DATA = 500

@st.cache_data(ttl=DEELAY_DATA)
def fetch_vd_childs():
    
    return pd.read_parquet(f'https://storage.googleapis.com/{BUCKET_NAME}/actividad_nino.parquet', engine='pyarrow')

@st.cache_data(ttl=DEELAY_DATA)
def fetch_carga_childs():
    
    return pd.read_parquet(f'https://storage.googleapis.com/{BUCKET_NAME}/carga_nino.parquet', engine='pyarrow')

@st.cache_data(ttl=DEELAY_DATA)
def fetch_vd_gestantes():
    return pd.read_parquet(f'https://storage.googleapis.com/{BUCKET_NAME}/actividad_gestante.parquet', engine='pyarrow')

@st.cache_data(ttl=DEELAY_DATA)
def fetch_carga_gestantes():
    return pd.read_parquet(f'https://storage.googleapis.com/{BUCKET_NAME}/carga_gestantes.parquet', engine='pyarrow')

@st.cache_data(ttl=DEELAY_DATA)
def fetch_padron():
    return pd.read_parquet(f'https://storage.googleapis.com/{BUCKET_NAME}/padron.parquet', engine='pyarrow')


