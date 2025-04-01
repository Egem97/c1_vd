import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_childs,fetch_carga_childs,fetch_padron
from utils.helpers import *
from utils.functions_data import childs_unicos_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def periodo_excluyentes():
    styles(2)
    carga_df = fetch_carga_childs()
    padron_df = fetch_padron()
    datos_ninos_df = pd.read_parquet('datos_niños.parquet', engine='pyarrow')
    eess = list(carga_df["Establecimiento de Salud"].unique())
    eess.remove(None)
    MESES = ["Ene","Feb","Mar","Abr"]
    columns_row1 = st.columns([3,2,2,])
    columns_row1[0].title("Niños no cargados 2025")
    with columns_row1[1]:
        select_mes_primero  = st.selectbox("Periodo Principal:",MESES , key="select1",index=len(MESES) - 2)
        
    with columns_row1[2]:
        select_mes_segundo  = st.selectbox("Periodo Nuevo:",MESES , key="select2",index=len(MESES) - 1)

    datos_ninos_1_df = datos_ninos_df[datos_ninos_df["Periodo"]==f"2025 - {select_mes_primero}"]
    datos_ninos_2_df = datos_ninos_df[datos_ninos_df["Periodo"]==f"2025 - {select_mes_segundo}"]
    carga_mes_1_df = carga_df[(carga_df['Año']==int(2025))&(carga_df['Mes']==int(mestext_short(select_mes_primero)))]
    carga_mes_2_df = carga_df[(carga_df['Año']==int(2025))&(carga_df['Mes']==int(mestext_short(select_mes_segundo)))]
    st.dataframe(carga_mes_1_df)
    st.dataframe(carga_mes_2_df)
    dataframe_pn = padron_df[[
        'Tipo_file', 'Documento', 'Tipo de Documento','DATOS NIÑO PADRON','CELULAR2_PADRON','SEXO',
        'FECHA DE NACIMIENTO', 'EJE VIAL', 'DIRECCION PADRON','REFERENCIA DE DIRECCION','MENOR VISITADO',
        'EESS NACIMIENTO','EESS', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN','TIPO DE DOCUMENTO DE LA MADRE',
        'NUMERO DE DOCUMENTO  DE LA MADRE','DATOS MADRE PADRON','TIPO DE DOCUMENTO DEL JEFE DE FAMILIA',
        'NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA','DATOS JEFE PADRON','ENTIDAD','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA','NUMERO DE CELULAR', 'CELULAR_CORREO',
        'TIPO DE SEGURO'
    ]]