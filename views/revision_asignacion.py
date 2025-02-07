
import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import *
from utils.helpers import *
from utils.functions_data import childs_unicos_visitados
from utils.cache_handler import * 

def asignacion_mes():
    styles(2)
    
    carga_niño_df = fetch_carga_childs()#fetch_carga_childs()
    
    carga_gestante_df = fetch_carga_gestantes()
    
    carga_gestante_df["Mes"] = carga_gestante_df["Mes"].astype(int)
    eess = list(carga_niño_df["Establecimiento de Salud"].unique())
    eess.remove(None)
    carga_niño_df["Establecimiento de Salud"] = carga_niño_df["Establecimiento de Salud"].fillna("Sin Asignar")
    carga_gestante_df["Establecimiento de Salud"] = carga_gestante_df["Establecimiento de Salud"].fillna("Sin Asignar")
    columns_row1 = st.columns([3,2,2,4])
    columns_row1[0].title("Asignaciones")
    with columns_row1[1]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with columns_row1[2]:
        select_mes  = st.selectbox("Mes:", ["Ene","Feb"], key="select2",index=True)
    with columns_row1[3]:
        select_eess  = st.multiselect("Establecimiento de Salud:", eess, key="select3",placeholder="Seleccione EESS")
        if len(select_eess)> 0:    
            select_eess_recorted = [s[11:] for s in select_eess]
            carga_niño_df = carga_niño_df[carga_niño_df["Establecimiento de Salud"].isin(select_eess)]
            carga_gestante_df = carga_gestante_df[carga_gestante_df["Establecimiento de Salud"].isin(select_eess_recorted)] 
            
    
    

    
    carga_filt_child_df = carga_niño_df[(carga_niño_df['Año']==int(select_year))&(carga_niño_df['Mes']==int(mestext_short(select_mes)))]
    carga_filt_gestante_df = carga_gestante_df[(carga_gestante_df['Año']==select_year)&(carga_gestante_df['Mes']==mestext_short(select_mes))]
    
    

    num_carga_child = carga_filt_child_df.shape[0]
    num_carga_gestante = carga_filt_gestante_df.shape[0]
    metric_col = st.columns(2)
    with metric_col[0]:

        eess_top_cargados = carga_filt_child_df.groupby(['Establecimiento de Salud'])[['Número de Documento del niño']].count().sort_values("Número de Documento del niño").reset_index()
        eess_top_cargados = eess_top_cargados.rename(columns=  {"Número de Documento del niño":"Registros"})
        fig_eess_count = px.bar(eess_top_cargados, x="Registros", y="Establecimiento de Salud",
                                    text="Registros", orientation='h',title = "Niños Asignados por Establecimiento de Salud")
        fig_eess_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_count.update_layout(xaxis=dict(title=dict(text="Número de Niños Cargados")),font=dict(size=16))
        st.metric("Niños Cargados",num_carga_child,border=True)
        st.plotly_chart(fig_eess_count)





    with metric_col[1]:
        eess_top_cargados_ges = carga_filt_gestante_df.groupby(['Establecimiento de Salud'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
        eess_top_cargados_ges = eess_top_cargados_ges.rename(columns=  {"Número de Documento":"Registros"})
        fig_eess_count_ges = px.bar(eess_top_cargados_ges, x="Registros", y="Establecimiento de Salud",
                                        text="Registros", orientation='h',title = "Gestantes Asignadas por Establecimiento de Salud")
        fig_eess_count_ges.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_count_ges.update_layout(xaxis=dict(title=dict(text="Número de Gestantes")),font=dict(size=16))
        
        st.metric("Gestantes Cargadas",num_carga_gestante,border=True)
        st.plotly_chart(fig_eess_count_ges)