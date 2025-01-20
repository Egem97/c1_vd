import streamlit as st
import pandas as pd
from styles import styles
from utils.cache_handler import fetch_carga_childs,fetch_vd_childs
from utils.helpers import *

def indicadores_childs():
    styles(2)

    carga_df = fetch_carga_childs()
    vd_df = fetch_vd_childs()
    columns_row1 = st.columns([3,4,4])
    columns_row1[0].title("Indicadores 1.2")
    with columns_row1[1]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with columns_row1[2]:
        select_mes  = st.selectbox("Mes:", ["Ene"], key="select2")
    vd_df = vd_df[(vd_df["Año"]==select_year)&(vd_df["Mes"]==select_mes)]#=
    carga_df = carga_df[(carga_df["Año"]==int(select_year))&(carga_df["Mes"]==mestext_short(select_mes))]
    num_carga = carga_df.shape[0]
    num_total_vd = carga_df["Total de visitas completas para la edad"].sum()
    num_vd_actu = carga_df["Total de VD presenciales Válidas"].sum()
    num_vd_movil = carga_df["Total de VD presencial Válidas MOVIL"].sum()
    metric_col = st.columns(6)
    metric_col[0].metric("N° Cargados",num_carga,border=True)
    metric_col[1].metric("N° Total Visitas Completas",num_total_vd,border=True)
    metric_col[2].metric("N° Visitas Realizadas Válidas",num_vd_actu,border=True)
    metric_col[3].metric("N° Visitas Realizadas MOVIL",num_vd_movil,border=True)
    st.write(vd_df)
    st.write(carga_df)