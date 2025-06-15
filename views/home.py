import streamlit as st
from datetime import datetime
from utils.cache_handler import (
    fetch_carga_childs, fetch_vd_childs, fetch_padron,
    fetch_vd_gestantes, fetch_carga_gestantes
)
from styles import styles

def index():
    styles(1)
    st.title("Home")

    fecha_actual = datetime.now()
    carga_df = fetch_carga_childs()
    vd_df = fetch_vd_childs()
    padron_df = fetch_padron()
    gestantes_vd_df = fetch_vd_gestantes()
    gestantes_carga_df = fetch_carga_gestantes()

    # Filtrar datos actuales
    carga_df = carga_df[(carga_df["Año"] == fecha_actual.year) & (carga_df["Mes"] == fecha_actual.month)]
    gestantes_carga_df["Mes"] = gestantes_carga_df["Mes"].astype(int)
    gestantes_carga_df = gestantes_carga_df[
        (gestantes_carga_df["Año"] == str(fecha_actual.year)) & (gestantes_carga_df["Mes"] == fecha_actual.month)
    ]

    # Métricas principales en cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Visitas Niños", int(carga_df["Total de Intervenciones"].sum()))
        st.metric("Última Visita Niño", str(vd_df["Fecha Intervención"].max())[:10])
    with col2:
        st.metric("Total Visitas Gestantes", int(gestantes_carga_df["Total de Intervenciones"].sum()))
        st.metric("Última Visita Gestante", str(gestantes_vd_df["Fecha Intervención"].max())[:10])
    with col3:
        st.metric("Última Actualización Padrón", str(padron_df["FECHA CREACION DE REGISTRO"].max())[:10])

    # Puedes agregar más cards o detalles aquí si lo deseas
    st.markdown("---")
    st.subheader("Resumen General")
    st.write("Aquí puedes agregar gráficos, tablas o información adicional relevante para el usuario.")



  
    