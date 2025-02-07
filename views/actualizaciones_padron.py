import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from styles import styles
from dateutil.relativedelta import relativedelta
from utils.cache_handler import fetch_padron
from utils.helpers import convert_excel_df

def calcular_edad(fecha_nacimiento):
    hoy = pd.to_datetime('today')
    diferencia = relativedelta(hoy, fecha_nacimiento)
    return f"{diferencia.years} año(s), {diferencia.months} mes(es)"

def calcular_edad_anios(fecha_nacimiento):
    hoy = pd.to_datetime('today')
    return relativedelta(hoy, fecha_nacimiento).years

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
    df['EDAD FORMATO'] = df['FECHA DE NACIMIENTO'].apply(calcular_edad)
    print(df.columns)
    Columnas=['CÓDIGO DE PADRON', 'CNV', 'CUI', 'DNI', 'ESTADO DE TRAMITE DE DNI',
       'FECHA DE TRAMITE DE DNI', 'APELLIDO PATERNO DEL NIÑO',
       'APELLIDO MATERNO DEL NIÑO', 'NOMBRES DEL NIÑO','DATOS NIÑO PADRON',  'SEXO',
       'FECHA DE NACIMIENTO','EDAD FORMATO', 'EJE VIAL', 'DIRECCION PADRON',
       'REFERENCIA DE DIRECCION', 'CENTRO POBLADO', 'TIPO CP',
       'MENOR VISITADO', '¿MENOR ENCONTRADO?', 'FECHA DE VISITA',
       'FUENTE DE DATOS', 'FECHA DE FUENTE DE DATOS', 'EESS NACIMIENTO',
       'EESS', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN', 'TIPO DE SEGURO',
       'PROGRAMAS SOCIALES', 'TIPO DE DOCUMENTO DE LA MADRE',
       'NUMERO DE DOCUMENTO  DE LA MADRE', 'APELLIDO PATERNO DE LA MADRE',
       'APELLIDO MATERNO DE LA MADRE', 'NOMBRES DE LA MADRE','DATOS MADRE PADRON',
       'NUMERO DE CELULAR', 'CELULAR_CORREO', 'GRADO DE LA MADRE',
       'LENGUA DE LA MADRE', 'RELACION JEFE DE FAMILIA',
       'TIPO DE DOCUMENTO DEL JEFE DE FAMILIA',
       'NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA','DATOS JEFE PADRON',
       'APELLIDO PATERNO DEL JEFE DE FAMILIA',
       'APELLIDO MATERNO DEL JEFE DE FAMILIA', 'NOMBRES DEL JEFE DE FAMILIA',
       'ESTADO REGISTRO', 'FECHA CREACION DE REGISTRO', 'USUARIO QUE CREA',
       'FECHA DE MODIFICACIÓN DEL REGISTRO', 'USUARIO QUE MODIFICA', 'ENTIDAD',
       'TIPO REGISTRO', 'Tipo_file', 'Documento', 'Tipo de Documento',
        'CELULAR2_PADRON']
    df = df[Columnas]
    st.dataframe(df)
    dff = df[df["Tipo_file"]!="Activos Transito"]
    dff['EDAD_ANIOS'] = dff['FECHA DE NACIMIENTO'].apply(calcular_edad_anios)
    eess_ = ['ARANJUEZ','CLUB DE LEONES','DE ESPECIALIDADES BASICAS LA NORIA','EL BOSQUE','LA UNION','LIBERTAD',
     'LOS GRANADOS "SAGRADO CORAZON"','LOS JARDINES','PESQUEDA II','PESQUEDA III','SAN MARTIN DE PORRES'
    ]
    dff = dff[dff["EESS"].isin(eess_)]
    anios_child_padron_df = dff.groupby(["EESS","EDAD_ANIOS"])[["Tipo_file"]].count().reset_index()
    df_pivot = anios_child_padron_df.pivot_table(index='EESS', columns='EDAD_ANIOS', values='Tipo_file', aggfunc='sum', fill_value=0)

    df_pivot = df_pivot.reset_index()
    
    
    st.dataframe(df_pivot)
    #st.write(.shape[0])
    st.download_button(
                label="Descargar Padron Nominal",
                data=convert_excel_df(df),
                file_name=f"padron_registros_actualizados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button(
                label="Descargar eess microred",
                data=convert_excel_df(dff),
                file_name=f"padron_registros_actualizados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button(
                label="Descargar totales por eess",
                data=convert_excel_df(df_pivot),
                file_name=f"padron_registros_actualizados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )