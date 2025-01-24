import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from styles import styles
from utils.cache_handler import fetch_padron
from utils.helpers import convert_excel_df


def dash_padron_modreg():
    styles(2)
    df = fetch_padron()
    df["Documento"]= df["Documento"].astype(str)
    df['EESS'] = df['EESS'].fillna("NO ESPECIFICADO")
    df["NUMERO DE CELULAR"] = df["NUMERO DE CELULAR"].str.strip()
    df["FECHA DE MODIFICACIÓN DEL REGISTRO"] = pd.to_datetime(df["FECHA DE MODIFICACIÓN DEL REGISTRO"])
    #df["FECHA DE MODIFICACIÓN DEL REGISTRO"] = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].dt.strftime("%Y-%m-%d")
    fecha_maxima = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].max().strftime("%Y-%m-%d")
    fecha_minima = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].min().strftime("%Y-%m-%d")
    print(df.info())
    
    #tipo_doc_list = df["Tipo de Documento"].unique()
    
    #eess_list = df['EESS'].unique()
    col_filt = st.columns([3,2,2,2,3])
    with col_filt[0]:
        st.title("Padron Nominal")
    with col_filt[1]:
        datepicker_inicio = st.date_input("Fecha Inicio", fecha_minima)
    with col_filt[2]:
        datepicker_fin = st.date_input("Fecha Fin", fecha_maxima)
    df = df[
        (df["FECHA DE MODIFICACIÓN DEL REGISTRO"] >= pd.to_datetime(datepicker_inicio)) &
        (df["FECHA DE MODIFICACIÓN DEL REGISTRO"] <= pd.to_datetime(datepicker_fin))
    ]
    entidad_act_list = df["ENTIDAD"].unique()
    with col_filt[3]:
        select_entidad  = st.selectbox("Entidad que Actualiza:", entidad_act_list, key="select2",index=None, placeholder="Seleccione Entidad")
        if select_entidad != None:
            df = df[df["ENTIDAD"] == select_entidad]
    usuario_act_list = df["USUARIO QUE MODIFICA"].unique()
    with col_filt[4]:
        select_usuario  = st.multiselect("Usuario que Actualiza:", usuario_act_list, key="select3", placeholder="Seleccione Usuario")
        if len(select_usuario) > 0:
            df = df[df["USUARIO QUE MODIFICA"].isin(select_usuario)]
    num_rows = df.shape[0]
    st.write(num_rows)
    st.dataframe(df)
    st.download_button(
                label="Descargar Padron Nominal",
                data=convert_excel_df(df),
                file_name=f"padron_registros_actualizados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )