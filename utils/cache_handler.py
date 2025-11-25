import asyncio
import streamlit as st
import pandas as pd 
from constans import BUCKET_NAME
DEELAY_DATA = 500

@st.cache_data(ttl=DEELAY_DATA,show_spinner="Cargando datos vd niños...")
def fetch_vd_childs():
    
    #return pd.read_parquet(f'https://storage.googleapis.com/{BUCKET_NAME}/actividad_nino.parquet', engine='pyarrow')
    return pd.read_parquet(f'./data/backups/actividad_nino.parquet', engine='pyarrow')
@st.cache_data(ttl=DEELAY_DATA,show_spinner="Cargando datos carga niños...")
def fetch_carga_childs():
    
    #return pd.read_parquet(f'./data/backups/carga_nino.parquet', engine='pyarrow')
    return pd.read_parquet(f'./data/backups/carga_nino.parquet', engine='pyarrow')

@st.cache_data(ttl=DEELAY_DATA,show_spinner="Cargando datos vd gestantes...")
def fetch_vd_gestantes():
    return pd.read_parquet(f'./data/backups/actividad_gestante.parquet', engine='pyarrow')

@st.cache_data(ttl=DEELAY_DATA,show_spinner="Cargando datos gestantes...")
def fetch_carga_gestantes():
    return pd.read_parquet(f'./data/backups/carga_gestantes.parquet', engine='pyarrow')

@st.cache_data(ttl=DEELAY_DATA,show_spinner="Cargando datos padron...")
def fetch_padron():
    return pd.read_parquet(f'./data/backups/padron.parquet', engine='pyarrow')


