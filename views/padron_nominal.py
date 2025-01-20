import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from styles import styles
from utils.cache_handler import fetch_padron
from utils.helpers import convert_excel_df

def dash_padron():
    styles(2)
    df = fetch_padron()
    df["Documento"]= df["Documento"].astype(str)
    df['EESS'] = df['EESS'].fillna("NO ESPECIFICADO")
    #df['FECHA DE MODIFICACIÓN DEL REGISTRO'] = df['FECHA DE MODIFICACIÓN DEL REGISTRO'].dt.date
    
    
    tipo_doc_list = df["Tipo de Documento"].unique()
    entidad_act_list = df["ENTIDAD"].unique()
    eess_list = df['EESS'].unique()
    col_filt = st.columns([3,2,2,5])
    with col_filt[0]:
        st.title("Padron Nominal")
    with col_filt[1]:
        select_tipo_doc  = st.selectbox("Tipo de Documento:", tipo_doc_list, key="select1",index=None, placeholder="Seleccione Tipo Doc")
        if select_tipo_doc != None:
            df = df[df["Tipo de Documento"] == select_tipo_doc]
    with col_filt[2]:
        select_entidad  = st.selectbox("Entidad que Actualiza:", entidad_act_list, key="select2",index=None, placeholder="Seleccione Entidad")
        if select_entidad != None:
            df = df[df["ENTIDAD"] == select_entidad]
    with col_filt[3]:
        select_entidad  = st.multiselect("Establecimiento de Salud Atención:", eess_list, key="select3", placeholder="Seleccione EESS")
        if select_entidad != None and len(select_entidad) > 0:
            df = df[df["EESS"].isin(select_entidad)]
    #FECHA DE MODIFICACIÓN DEL REGISTRO
    #dff = df[(df["FECHA DE MODIFICACIÓN DEL REGISTRO"]>=fecha_inicio)&(df["FECHA DE MODIFICACIÓN DEL REGISTRO"]<=fecha_fin)]
    duplicados_df = df[df.duplicated(subset=["Documento"], keep=False)]
    rows_dup = duplicados_df.shape[0]
    num_rows_ = df.shape[0]
    sin_ejevial_df = df[df['EJE VIAL'] == " "]
    sin_ref_df = df[df['REFERENCIA DE DIRECCION'].isnull()]
    #count_entidad_muni = (df["ENTIDAD"] == "MUNICIPIO").sum()
    count_entidad_muni = df[(df["ENTIDAD"] == "MUNICIPIO") & (df["EJE VIAL"] != " ") & (df["REFERENCIA DE DIRECCION"].notna())]
    
    col_metric = st.columns([2,2,2,2,2])    
    col_metric[0].metric("N° Registros",num_rows_,border=True)
    col_metric[1].metric("N° Duplicados",rows_dup,border=True)
    col_metric[2].metric("N° SIN EJE VIAL",sin_ejevial_df.shape[0],border=True)
    col_metric[3].metric("N° SIN REFERENCIA",sin_ref_df.shape[0],border=True)
    col_metric[4].metric("Porcentaje de Actualizaciones",f"{(round((count_entidad_muni.shape[0]/num_rows_)*100,1))}%",border=True)

    bar_d = df.groupby(["ENTIDAD"])[["CÓDIGO DE PADRON"]].count().reset_index()
    bar_d = bar_d.rename(columns = {"CÓDIGO DE PADRON":"Registros"})
    tipo_doc_ = df.groupby(["Tipo de Documento"])[['CÓDIGO DE PADRON']].count().sort_values('CÓDIGO DE PADRON').reset_index()
    tipo_doc_ = tipo_doc_.rename(columns = {"CÓDIGO DE PADRON":"Registros"})
    eess_df = df.groupby(["EESS"])[["CÓDIGO DE PADRON"]].count().sort_values('CÓDIGO DE PADRON').reset_index().tail(25)
    eess_df = eess_df.rename(columns=  {"CÓDIGO DE PADRON":"Registros"})
    
    crea_reg_df = df.groupby(["FECHA CREACION DE REGISTRO"])[["CÓDIGO DE PADRON"]].count().sort_values('FECHA CREACION DE REGISTRO').reset_index()
    crea_reg_df = crea_reg_df.rename(columns=  {"CÓDIGO DE PADRON":"Registros"})
    crea_reg_df["Año"] = crea_reg_df['FECHA CREACION DE REGISTRO'].dt.year
    crea_reg_df["Mes"] = crea_reg_df['FECHA CREACION DE REGISTRO'].dt.month
    crea_reg_df = crea_reg_df.groupby(["Año"])[["Registros"]].sum().reset_index()

    crea_mod_df = df.groupby(["FECHA DE MODIFICACIÓN DEL REGISTRO"])[["CÓDIGO DE PADRON"]].count().sort_values('FECHA DE MODIFICACIÓN DEL REGISTRO').reset_index()
    crea_mod_df = crea_mod_df.rename(columns=  {"CÓDIGO DE PADRON":"Registros"})
    crea_mod_df["Año"] = crea_mod_df['FECHA DE MODIFICACIÓN DEL REGISTRO'].dt.year
    crea_mod_df["Mes"] = crea_mod_df['FECHA DE MODIFICACIÓN DEL REGISTRO'].dt.month
    crea_mod_df = crea_mod_df.groupby(["Año"])[["Registros"]].sum().reset_index()


    fig_doc = px.pie(tipo_doc_, values='Registros', names='Tipo de Documento',
                        title='N° de Registros por Tipo Documento', width=700)
    fig_doc.update_traces(textposition='inside', textinfo='percent+label')
    fig_doc.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        
    )
    fig_entiedad = px.pie(bar_d, values='Registros', names='ENTIDAD',
                        title='N° de Registros por Entidad que Actualiza', width=700)
    fig_entiedad.update_traces(textposition='inside', textinfo='percent+label')
    fig_entiedad.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    fig_eess = px.bar(eess_df, x='Registros', y='EESS',text='Registros',title="Top 25 Esblecimientos de Salud de Atención", width=700)
    fig_eess.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess.update_layout(yaxis=dict(title=dict(text="Número de Registros")),font=dict(size=16))
    fig_eess.update_layout(margin=dict(l=20, r=20, t=40, b=20))

    fig_crea_reg = px.line(crea_reg_df, x="Año", y="Registros", title='Creación de Registros')
    fig_mod_reg = px.line(crea_mod_df, x="Año", y="Registros", title='Actualización de Registros')

    columnas = st.columns([3,2,2])
    columnas[2].plotly_chart(fig_doc)
    columnas[1].plotly_chart(fig_entiedad)
    columnas[0].plotly_chart(fig_eess,use_container_width=False)

    columnas_2 = st.columns(2)
    columnas_2[0].plotly_chart(fig_crea_reg)
    columnas_2[1].plotly_chart(fig_mod_reg)
    


    with st.expander("Descargas"):
        st.download_button(
                label="Descargar Duplicados",
                data=convert_excel_df(duplicados_df),
                file_name=f"padron_duplicados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar SIN EJEVIAL",
                data=convert_excel_df(sin_ejevial_df),
                file_name=f"padron_sinejevial.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar REFERENCIA",
                data=convert_excel_df(sin_ref_df),
                file_name=f"padron_referencia_direccion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar Actualizados Muni",
                data=convert_excel_df(count_entidad_muni),
                file_name=f"padron_actualizados_municipio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )