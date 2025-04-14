import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_childs,fetch_carga_childs,fetch_padron
from utils.helpers import *
from utils.functions_data import childs_unicos_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def resumen25():
    styles(2)
    st.title("Resuemn Tramo III")
    childs_df = pd.read_parquet('data/resumen/childs_resumen.parquet', engine='pyarrow')
    #print(childs_df.columns)
    #print(childs_df['Estado Visitas'].unique())
    #st.dataframe(childs_df)
    childs_count_df = childs_df.groupby(["Mes"])[["Tipo Documento"]].count().reset_index()
    childs_count_df.columns = ["Mes","Niños Programados"]
    childs_programvd_df = childs_df.groupby(["Mes"])[['N° Visitas Completas']].sum().reset_index()
    childs_programvd_df.columns = ["Mes","Visitas Programadas"]
    table_dff = pd.merge(childs_count_df,childs_programvd_df , left_on='Mes', right_on='Mes', how='left')
    #ONLY ENCONTRADOS
    childs_encontrados_df = childs_df[childs_df["Estado Visitas"].isin(["Visitas Completas"])]
    childs_encont_df = childs_encontrados_df.groupby(["Mes"])[['Total de VD presencial Válidas MOVIL']].count().reset_index()
    childs_encont_df.columns = ["Mes","Niños Encontados"]
    table_dff = pd.merge(table_dff,childs_encont_df , left_on='Mes', right_on='Mes', how='left')
    childs_vd_df = childs_encontrados_df.groupby(["Mes"])[['Total de VD presencial Válidas MOVIL']].sum().reset_index()
    childs_vd_df.columns = ["Mes","Visitas Geo Realizadas"]
    table_dff = pd.merge(table_dff,childs_vd_df , left_on='Mes', right_on='Mes', how='left')
    table_dff["% Georreferencia"] = round((table_dff["Visitas Geo Realizadas"]/table_dff["Visitas Programadas"])*100,1)
    table_dff["% Indicador"] = round((table_dff["Niños Encontados"]/table_dff["Niños Programados"])*100,1)
    table_dff['Mes'] = table_dff['Mes'].replace({1: 'Enero',2: 'Febrero',3:"Marzo"})
    st.dataframe(table_dff)
    gestantes_df = pd.read_parquet('data/resumen/gestantes_resumen.parquet', engine='pyarrow')
    print(gestantes_df.columns)
    #st.dataframe(gestantes_df)
    gest_count_df = gestantes_df.groupby(["Mes"])[["Tipo de Documento"]].count().reset_index()
    gest_count_df.columns = ["Mes","Gestantes Programadas"]
    gest_programvd_df = gestantes_df.groupby(["Mes"])[['Total de visitas completas para la edad']].sum().reset_index()
    gest_programvd_df.columns = ["Mes","Visitas Programadas"]
    table_ges_df = pd.merge(gest_count_df,gest_programvd_df , left_on='Mes', right_on='Mes', how='left')
    #st.dataframe(table_ges_df)
    #
    ##ONLY
    gest_etapa_df = gestantes_df[gestantes_df["Etapa"].isin(["Visita Domiciliaria (Adolescente)","Visita Domiciliaria (Adulta)"])]
    gest_encont_df = gest_etapa_df.groupby(["Mes"])[['Total de VD presencial Válidas MOVIL']].count().reset_index()
    gest_encont_df.columns = ["Mes","Gestantes Efectivas"]
    table_ges_df = pd.merge(table_ges_df,gest_encont_df , left_on='Mes', right_on='Mes', how='left')
    
    ###
    gest_etapa_nega_df = gestantes_df[(gestantes_df["Etapa"].isin(["No Encontrado"]))&(gestantes_df["ESTADO_NACIMIENTO"]=="PUERPERA")]
    gest_des_df = gest_etapa_nega_df.groupby(["Mes"])[['Total de VD presencial Válidas MOVIL']].count().reset_index()
    gest_des_df.columns = ["Mes","Puerperas Efectivas"]
    nueva_fila = {'Mes': 1, 'Puerperas Efectivas': 97}
    gest_des_df = pd.concat([gest_des_df, pd.DataFrame([nueva_fila])], ignore_index=True)
    table_ges_df = pd.merge(table_ges_df,gest_des_df , left_on='Mes', right_on='Mes', how='left')
    
    #TODAS LAS GEORREFERENCIAS
    geo_gest_df = gestantes_df.groupby(["Mes"])[['Total de VD presencial Válidas MOVIL']].sum().reset_index()
    geo_gest_df.columns = ["Mes","Visitas Geo Realizadas"]
    
    
    table_ges_df = pd.merge(table_ges_df,geo_gest_df , left_on='Mes', right_on='Mes', how='left')
    table_ges_df["% Georreferencia"] = round((table_ges_df["Visitas Geo Realizadas"]/table_ges_df["Visitas Programadas"])*100,1)
    table_ges_df["% Indicador"] = round((table_ges_df["Gestantes Efectivas"]/table_ges_df["Gestantes Programadas"])*100,1)
    table_ges_df['Mes'] = table_ges_df['Mes'].replace({1: 'Enero',2: 'Febrero',3:"Marzo"})
    st.dataframe(table_ges_df)
    st.download_button(
                label="Descargar Datos Niño",
                data=convert_excel_df(table_dff),
                file_name=f"Tabla_resumen_niños.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    st.download_button(
                label="Descargar Datos Gestante",
                data=convert_excel_df(table_ges_df),
                file_name=f"Tabla_resumen_gestante.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )