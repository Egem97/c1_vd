import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_carga_childs, fetch_vd_childs, fetch_carga_gestantes, fetch_vd_gestantes
from utils.helpers import mestext_short
from utils.functions_data import *

def indicadores_avance_c1():
    styles(2)
    st.title("Indicadores de Avance - Compromiso 1")


    # Cargar datos
    carga_childs = fetch_carga_childs()
    vd_childs = fetch_vd_childs()
    carga_ges = fetch_carga_gestantes()
    vd_ges = fetch_vd_gestantes()

    # Tipos
    vd_childs["Año"] = vd_childs["Año"].astype(str)
    vd_ges["Año"] = vd_ges["Año"].astype(str)
    carga_childs["Año"] = carga_childs["Año"].astype(str)
    carga_ges["Año"] = carga_ges["Año"].astype(str)

    
    st.dataframe(vd_childs)