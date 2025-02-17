import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from styles import styles
from utils.cache_handler import *
from utils.helpers import * 

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode 


def as_vd():
    styles(1)
    carga_df = fetch_carga_childs()
    carga_df = carga_df[(carga_df['Año']==int(2025))&(carga_df['Mes']==int(mestext_short('Feb')))]
    carga_df = carga_df.groupby(["Nombres del Actor Social"])[["Tipo de Documento del niño"]].count().reset_index()
    vd_df = fetch_vd_childs()
    
    vd_df = vd_df[vd_df["Etapa"].isin(["Rechazado","No Encontrado"])]
    # dataframe_.apply(lambda x: completar_names_col(x['DATOS NIÑO PADRON'], x['Niño']),axis=1)
    vd_df["Mes"] = vd_df.apply(lambda x: mestext_short(x['Mes']),axis=1)
    vd_df["Mes_"] = vd_df["Mes"].astype(str)
    vd_df["Periodo"] =  vd_df["Año"]+"-"+ vd_df["Mes_"]
    st.title("Actores Sociales")
    
    dff = vd_df.groupby(["Establecimiento de Salud","Actores Sociales","Periodo","Año","Mes"])[["Tipo de Registro VD"]].count().sort_values(["Año","Mes"]).reset_index()
    del vd_df
    df_pivot = dff.pivot_table(
        index=["Establecimiento de Salud", "Actores Sociales"], 
        columns="Periodo", 
        values="Tipo de Registro VD", 
        aggfunc="sum", 
        fill_value=0
    ).reset_index()
    columns_text = list(df_pivot.columns[:2])
    columns_periodo = list(df_pivot.columns[2:])
    fechas_2024 = [fecha for fecha in columns_periodo if fecha.startswith("2024-")]
    fechas_2025 = [fecha for fecha in columns_periodo if fecha.startswith("2025-")]
    columns_2024 = sorted(fechas_2024, key=lambda x: int(x.split('-')[1]))
    columns_2025 = sorted(fechas_2025, key=lambda x: int(x.split('-')[1]))
    df_pivot = df_pivot[columns_text+columns_2024+columns_2025]
    dfff = pd.merge(carga_df,df_pivot , left_on='Nombres del Actor Social', right_on='Actores Sociales', how='left')
    dfff = dfff.rename(columns=  {"Tipo de Documento del niño":"Niños Asignados(Feb)"})

    st.dataframe(dfff)

    st.download_button(
                label="Descargar Datos",
                data=convert_excel_df(dfff),
                file_name=f"Actores Sociales.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )