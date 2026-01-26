import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from styles import styles
from dateutil.relativedelta import relativedelta
from utils.cache_handler import *
from utils.helpers import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def edades_padron():
    styles(2)
    df = fetch_padron()
    df = df[(df["FECHA DE MODIFICACIÓN DEL REGISTRO"].notna())&(df["ENTIDAD"]=="MUNICIPIO")]
    df["Documento"]= df["Documento"].astype(str)
    df['EESS'] = df['EESS'].fillna("NO ESPECIFICADO")
    df["NUMERO DE CELULAR"] = df["NUMERO DE CELULAR"].str.strip()
    
    df['FECHA DE MODIFICACIÓN DEL REGISTRO'] =pd.to_datetime(df['FECHA DE MODIFICACIÓN DEL REGISTRO'], format="%Y-%m-%d")#.dt.strftime('%Y-%m-%d')
    df['Año'] = df['FECHA DE MODIFICACIÓN DEL REGISTRO'].dt.year
    #df["Año"] = df["Año"].astype(str)
    years = sorted(df["Año"].unique())
    #years.remove(None)
    
    fecha_maxima = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].max().strftime("%Y-%m-%d")
    #fecha_minima = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].min().strftime("%Y-%m-%d")
    columnas_head = st.columns([5,3,2,3])
    with columnas_head[0]:
        st.title(":blue[Municipio Avances] :child:")
    with columnas_head[1]:
        st.subheader(f"Actualizado: {fecha_maxima}", divider=True)
    with columnas_head[2]:
        select_year  = st.selectbox("Año Actualizaciones", years,index=len(years)-1)
        df = df[df["Año"]==select_year]
    with columnas_head[3]:
        usuario_act_list = df["USUARIO QUE MODIFICA"].unique()
        select_usuario  = st.multiselect("Usuario que Actualiza:", usuario_act_list, key="select3", placeholder="Seleccione Usuario")
        if len(select_usuario) > 0:
            df = df[df["USUARIO QUE MODIFICA"].isin(select_usuario)]

    df['Edad'] = df['FECHA DE NACIMIENTO'].apply(calcular_edad_anios)
    edad_count_df = df.groupby(["Edad"])[["Documento"]].count().reset_index()
    edad_count_df.columns = ["Edad","Niños"]

    fig_edad_count = px.bar(edad_count_df, x="Edad", y="Niños",text="Niños", title=f'Edad por Actualizaciones ({df.shape[0]})')
    fig_edad_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_edad_count.update_layout(xaxis=dict(title=dict(text="Edad")),yaxis=dict(title=dict(text="Niños")),font=dict(size=16))
    fig_edad_count.update_xaxes(type='category')
    ##############################
    eess_count_df = df.groupby(["EESS"])[["Documento"]].count().sort_values("Documento").reset_index()
    eess_count_df.columns = ["Establecimiento de salud","Niños"]
    eess_count_df = eess_count_df[eess_count_df["Niños"]>2]
    fig_eess_top = px.bar(eess_count_df, x="Niños", y="Establecimiento de salud", title='Establecimientos de Salud con Actualizaciones')
    ##############
    tipo_doc_df = df.groupby(["Tipo de Documento"])[["Documento"]].count().reset_index()
    tipo_doc_df.columns = ["Tipo de Documento","Niños"]
    fig_doc = px.pie(tipo_doc_df, values='Niños', names='Tipo de Documento',
                        title='Niños Actualizados por Tipo Documento')
    fig_doc.update_traces(textposition='inside', textinfo='percent+label+value',insidetextfont=dict(size=18))
    fig_doc.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        
    )
    tipo_seguro_df = df.groupby(["TIPO DE SEGURO"])[["Documento"]].count().reset_index()
    tipo_seguro_df.columns = ["Tipo de Seguro","Niños"]
    fig_tipo_seguro = px.pie(tipo_seguro_df, values='Niños', names='Tipo de Seguro',
                        title='Niños Actualizados por Tipo de Seguro')
    fig_tipo_seguro.update_traces(textposition='inside', textinfo='percent+label+value',insidetextfont=dict(size=18))
    fig_tipo_seguro.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        
    )
    #########
    tipo_visita_df = df.groupby(["MENOR VISITADO"])[["Documento"]].count().reset_index()
    tipo_visita_df.columns = ["Menor Visitado","Niños"]
    fig_tipo_visita = px.pie(tipo_visita_df, values='Niños', names='Menor Visitado',
                        title='Niños Actualizados por Tipo Actualización')
    fig_tipo_visita.update_traces(textposition='inside', textinfo='percent+label+value',insidetextfont=dict(size=18))
    fig_tipo_visita.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        
    )
    #############
   
    columnas_add = st.columns(2)
    with columnas_add[0]:
        st.plotly_chart(fig_edad_count)
    with columnas_add[1]:
        st.plotly_chart(fig_eess_top)
    
    columnas_two = st.columns(3)
    with columnas_two[0]:
        st.plotly_chart(fig_doc)
    with columnas_two[1]:
        st.plotly_chart(fig_tipo_seguro)
    with columnas_two[2]:
        st.plotly_chart(fig_tipo_visita)

    st.download_button(
                    label="Descargar Padron Actualización",
                    data=convert_excel_df(df),
                    file_name=f"padron_muni_actualizacion_{fecha_maxima}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )