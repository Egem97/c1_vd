import streamlit as st
from datetime import datetime
from utils.cache_handler import (
    fetch_carga_childs, fetch_vd_childs, fetch_padron,
    fetch_vd_gestantes, fetch_carga_gestantes
)
from styles import styles

def index():
    styles(1)
    st.title("Panel de Control Municipal")
    st.markdown("Bienvenido al sistema de seguimiento y gestión de indicadores municipales.")

    fecha_actual = datetime.now()
    carga_df = fetch_carga_childs()
    vd_df = fetch_vd_childs()
    padron_df = fetch_padron()
    gestantes_vd_df = fetch_vd_gestantes()
    gestantes_carga_df = fetch_carga_gestantes()
    st.dataframe(gestantes_vd_df)
    st.dataframe(gestantes_carga_df)
    # Filtrar datos actuales
    carga_df = carga_df[(carga_df["Año"] == fecha_actual.year) & (carga_df["Mes"] == fecha_actual.month)]
    gestantes_carga_df["Mes"] = gestantes_carga_df["Mes"].astype(int)
    gestantes_carga_df = gestantes_carga_df[
        (gestantes_carga_df["Año"] == str(fecha_actual.year)) & (gestantes_carga_df["Mes"] == fecha_actual.month)
    ]

    # Layout Principal
    col_c1, col_pn = st.columns(2, gap="medium")

    # Sección Compromiso 1
    with col_c1:
        with st.container():
            st.subheader("🩸 Compromiso 1")
            st.markdown(
                """
                **Mejora del estado nutricional y de salud.**
                
                Seguimiento de visitas domiciliarias a niños y gestantes para prevenir la anemia y asegurar el desarrollo infantil temprano.
                """
            )
            st.markdown("---")
            
            # Métricas Compromiso 1
            c1_m1, c1_m2 = st.columns(2)
            with c1_m1:
                st.metric(
                    label="Visitas Niños", 
                    value=int(carga_df["Total de Intervenciones"].sum()),
                    help="Total de intervenciones realizadas a niños en el periodo actual"
                )
                st.caption(f"Última: {str(vd_df['Fecha Intervención'].max())[:10]}")
            
            with c1_m2:
                st.metric(
                    label="Visitas Gestantes", 
                    value=int(gestantes_carga_df["Total de Intervenciones"].sum()),
                    help="Total de intervenciones realizadas a gestantes"
                )
                st.caption(f"Última: {str(gestantes_vd_df['Fecha Intervención'].max())[:10]}")

    # Sección Padrón Nominal
    with col_pn:
        with st.container():
            st.subheader("📋 Padrón Nominal")
            st.markdown(
                """
                **Registro de niños y niñas menores de 6 años.**
                
                Herramienta para la actualización y homólogos de información, garantizando el acceso a servicios de salud e identidad.
                """
            )
            st.markdown("---")

            # Métricas Padrón Nominal
            st.metric(
                label="Última Actualización del Padrón", 
                value=str(padron_df["FECHA CREACION DE REGISTRO"].max())[:10],
                delta="Fecha Registro Central",
                delta_color="off"
            )
            st.info("💡 Mantener el padrón actualizado es clave para el cumplimiento de metas.")
  
    