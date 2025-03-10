import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_childs,fetch_carga_childs,fetch_padron
from utils.helpers import *
from utils.functions_data import childs_unicos_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def geo_vd_childs():
    styles(2)
    actvd_df = fetch_vd_childs()
    carga_df = fetch_carga_childs()
    carga_df["Número de Documento del niño"] = carga_df["Número de Documento del niño"].astype(str)
    fecha_maxima = actvd_df["Fecha Intervención"].max().strftime("%Y-%m-%d")
    eess = list(carga_df["Establecimiento de Salud"].unique())
    eess.remove(None)
    MESES = ["Ene","Feb","Mar"]
    column_head = st.columns([4,3,3,3])
    with column_head[0]:
        st.title("Proyección Geo")
    with column_head[1]:
        st.subheader(f"Actualizado: {fecha_maxima}", divider=True)#fecha_maxima
    with column_head[2]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with column_head[3]:
        select_mes  = st.selectbox("Mes:",MESES , key="select2",index=len(MESES) - 1)
    
    carga_df = carga_df[(carga_df['Año']==int(select_year))&(carga_df['Mes']==int(mestext_short(select_mes)))]
    actvd_df = actvd_df[(actvd_df['Año']==select_year)&(actvd_df['Mes']==select_mes)]
    st.write(carga_df.shape)
    st.write(actvd_df.shape)
  
    childs_unique_df = actvd_df.groupby(['Número de Documento de Niño','Etapa'])[['Año']].count().reset_index()

    etapa_vd_df_dup =childs_unique_df.groupby(['Número de Documento de Niño'])["Año"].count().reset_index()
    etapa_vd_df_dup = etapa_vd_df_dup.rename(columns=  {"Año":"Verificacion"})
    etapa_vd_df_dup['Verificacion'] = etapa_vd_df_dup['Verificacion'].replace({
            1: 'Registro Regular',
            2: 'Registro Irregular'
    })
    #unicos duplicados drop
    etapa_vd_unique_df = childs_unique_df.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
    etapa_vd_unique_df = etapa_vd_unique_df.drop_duplicates(subset='Número de Documento de Niño', keep='first')
    etapa_vd_unique_df.columns = ["Doc_Ultimo_Mes","Estado_Visita_Ult","count"]
    
    
    etapa_vd_join_df = pd.merge(etapa_vd_unique_df,etapa_vd_df_dup , left_on='Doc_Ultimo_Mes', right_on='Número de Documento de Niño', how='left')
    etapa_vd_join_df = etapa_vd_join_df[["Número de Documento de Niño","Estado_Visita_Ult","Verificacion"]]
    etapa_vd_join_df.columns = ["Número de Documento de Niño","ETAPA","Verificacion"]

    print(carga_df.columns)
    
   
    carga_df = carga_df[['Establecimiento de Salud','Número de Documento del niño', 'Fecha de Nacimiento',
       'Total de visitas completas para la edad', 'Total de Intervenciones',
       'Total de VD presenciales Realizadas',
       'Total de VD presenciales Válidas',
       'Total de VD presencial Válidas WEB',
       'Total de VD presencial Válidas MOVIL']]
    dff = pd.merge(carga_df,etapa_vd_join_df , left_on='Número de Documento del niño', right_on='Número de Documento de Niño', how='left')
    dataframe_efec = dff[dff["ETAPA"].isin(["Visita Domiciliaria (6 a 12 Meses)","Visita Domiciliaria (1 a 5 meses)"])]
    vd_programadas_df = dff.groupby(["Establecimiento de Salud"])[["Total de visitas completas para la edad"]].sum().sort_values("Total de visitas completas para la edad",ascending=False).reset_index()#,"Total de VD presencial Válidas WEB",
    child_programados_df = dff.groupby(["Establecimiento de Salud"])[["Total de visitas completas para la edad"]].count().sort_values("Total de visitas completas para la edad",ascending=False).reset_index()
    child_programados_df = child_programados_df.rename(columns=  {"N° Visitas Completas":"Niños Programados"})
    #st.write(dff.shape)
    #st.dataframe(dataframe_efec)
    
    vd_movil_df = dataframe_efec.groupby(["Establecimiento de Salud"])[["Total de VD presencial Válidas MOVIL"]].sum().reset_index()
    childs_encontrados_df = dataframe_efec.groupby(["Establecimiento de Salud"])[["ETAPA"]].count().reset_index()
    childs_encontrados_df = childs_encontrados_df.rename(columns=  {"ETAPA":"Niños Encontrados"})
    proyectado_dff = pd.merge(child_programados_df,vd_programadas_df , left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')
    proyectado_dff = pd.merge(proyectado_dff, childs_encontrados_df, left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')
    proyectado_dff = pd.merge(proyectado_dff, vd_movil_df, left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')
    st.write(proyectado_dff.shape)
    st.dataframe(proyectado_dff)