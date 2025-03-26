import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_childs,fetch_carga_childs,fetch_padron
from utils.helpers import *
from utils.functions_data import childs_unicos_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def status24_nominal():
    styles(2)
    padron_df = fetch_padron()
    actvd_df = fetch_vd_childs()
    actvd_df["Año"] = actvd_df["Año"].astype(str)
    carga_df = fetch_carga_childs()
    
    carga_df["Año"] = carga_df["Año"].astype(str)
    carga_df = carga_df[(carga_df["Año"]=="2024")&(carga_df["Mes"].isin([8,9,10,11,12]))]
    actvd_df = actvd_df[(actvd_df["Año"]=="2024")&(actvd_df["Mes"].isin(["Ago","Set","Oct","Nov","Dic"]))]
    carga_df["Número de Documento del niño"] = carga_df["Número de Documento del niño"].astype(str)
    columnas_head = st.columns([6,3,3])
    with columnas_head[0]:
        st.title("REVISION NIÑOS 1.2 (2024)")
    with columnas_head[1]:
        st.subheader(f"Tramo II", divider=True)
    childs_unique_df = actvd_df.groupby(['Mes','Número de Documento de Niño','Etapa'])[['Año']].count().reset_index()
    
    etapa_vd_df_dup =childs_unique_df.groupby(['Mes','Número de Documento de Niño'])["Año"].count().reset_index()
    etapa_vd_df_dup = etapa_vd_df_dup.rename(columns=  {"Año":"Verificacion"})
    etapa_vd_df_dup['Verificacion'] = etapa_vd_df_dup['Verificacion'].replace({
            1: 'Registro Regular',
            2: 'Registro Irregular'
    })
    
    #unicos duplicados drop
    etapa_vd_unique_df = childs_unique_df.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
    etapa_vd_unique_df = etapa_vd_unique_df.drop_duplicates(subset=["Mes",'Número de Documento de Niño'], keep='first')
    etapa_vd_unique_df.columns = ["Mes","Doc_Ultimo_Mes","Estado_Visita_Ult","count"]
   

    etapa_vd_join_df = pd.merge(etapa_vd_unique_df,etapa_vd_df_dup , left_on=['Mes','Doc_Ultimo_Mes'], right_on=['Mes','Número de Documento de Niño'], how='left')
    etapa_vd_join_df = etapa_vd_join_df[["Mes","Número de Documento de Niño","Estado_Visita_Ult","Verificacion"]]
    etapa_vd_join_df.columns = ["Mes","Número de Documento de Niño","ETAPA","Verificacion"]
    
    """FECHA DE VISITAS PIVOT"""
    #st.dataframe()
    #cols_vd_df =  actvd_df.groupby(['Mes','Número de Documento de Niño','Fecha Intervención'])[['Año']].count().reset_index()
    #result = cols_vd_df.pivot(index='Número de Documento de Niño', columns='Año', values='Fecha Intervención')
    #st.write(result.shape)
    actvd_df['Fecha Intervención'] = pd.to_datetime(actvd_df['Fecha Intervención'])
    df_grouped = actvd_df.groupby(['Mes', 'Número de Documento de Niño']) \
                .agg({
                    'Fecha Intervención': list  # Agruparemos las fechas en una lista
                }).reset_index()
    df_grouped[['VISITA1', 'VISITA2', 'VISITA3','VISITA4','VISITA5']] = pd.DataFrame(df_grouped['Fecha Intervención'].tolist(), index=df_grouped.index)
    df_grouped = df_grouped.drop(columns=['Fecha Intervención'])
    print(carga_df.columns)
    #st.write(etapa_vd_join_df.shape)
    #st.write(etapa_vd_join_df)
    carga_df = carga_df[['Establecimiento de Salud','Nombres del Actor Social','Mes','Número de Documento del niño', 'Fecha de Nacimiento',
       'Total de visitas completas para la edad', 'Total de Intervenciones',
       'Total de VD presenciales Realizadas',
       'Total de VD presenciales Válidas',
       'Total de VD presencial Válidas WEB',
       'Total de VD presencial Válidas MOVIL','DNI de la madre']
    ]
    carga_df= carga_df.sort_values("Mes")
    carga_df["Mes_"] = carga_df["Mes"]
    carga_df["Mes"] = carga_df.apply(lambda x: mes_short(x['Mes']),axis=1)
    
    dff = pd.merge(carga_df,etapa_vd_join_df , left_on=["Mes","Número de Documento del niño"], right_on=["Mes","Número de Documento de Niño"], how='left')
    dff['Estado Visitas'] =  dff.apply(lambda x: estado_visitas_completas(x['Total de visitas completas para la edad'], x['Total de VD presenciales Válidas'],x['ETAPA']),axis=1)
    
    dff = pd.merge(dff,df_grouped , left_on=["Mes","Número de Documento del niño"], right_on=["Mes","Número de Documento de Niño"], how='left')
    dff = dff.rename(columns = {"Número de Documento de Niño_x":"Número de Documento del Niño"})
    dff = dff.drop(["Número de Documento de Niño_y"], axis=1)
    
    dataframe_pn = padron_df[[
        'Tipo_file', 'Documento', 'Tipo de Documento','DATOS NIÑO PADRON','SEXO',
        'FECHA DE NACIMIENTO', 'DIRECCION PADRON','REFERENCIA DE DIRECCION','MENOR VISITADO',
        'EESS','ENTIDAD','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA','NUMERO DE CELULAR', 'CELULAR_CORREO',
        'TIPO DE SEGURO'
    ]]
    reemplazo = {
        "0": "NINGUNO",
        "1": "SIS",
        "2": "ESSALUD",
        "3": "SANIDAD",
        "4": "PRIVADO"
    }
    dataframe_pn["TIPO DE SEGURO"] = dataframe_pn["TIPO DE SEGURO"].fillna("SIN DATOS").apply(
        lambda x: "SIN DATOS" if x == "SIN DATOS" else 
              ", ".join([reemplazo.get(num.strip(), num.strip()) 
                         for num in x.split(",") if num.strip()])
    )
    dataframe_pn["Documento"] = dataframe_pn["Documento"].astype(str)
   
    ##ADD RESULTADOS 2024
    result_childs_24_df = pd.read_parquet('result_2024_1.2.parquet', engine='pyarrow')
    
    result_childs_24_df["DOCUMENTO_NUMERO"] = result_childs_24_df["DOCUMENTO_NUMERO"].astype(str)
    result_childs_24_df["Periodo"] = result_childs_24_df["Periodo"].str[:3]
    #print()
    dfff = pd.merge(result_childs_24_df,dff , left_on=["Periodo","DOCUMENTO_NUMERO"], right_on=["Mes","Número de Documento del niño"], how='left')
    
    
    st.write(dfff.shape)

    #st.dataframe(dfff)
    dfff = pd.merge(dfff,dataframe_pn , left_on=["DOCUMENTO_NUMERO"], right_on=["Documento"], how='left')
    dfff["Tipo_file"] = dfff["Tipo_file"].fillna("En otro Padron")
    dfff = dfff.rename(columns = {"Tipo_file":"Estado Padrón"})
    dfff = dfff[
        ['Periodo','Establecimiento de Salud','Nombres del Actor Social', 'DOCUMENTO_NUMERO', 'Tipo Documento',
        'FECHA DE NACIMIENTO DEL NIÑO PREVIO', 'TIPO DE SEGURO_x',
        'NIÑO NO ENCONTRADO', 'NIÑO CON CAMBIO DE UBIGEO',
        'TRANSEUNTE O MIGRANTE', 'N° DE VISITAS PROGRAMADAS',
        'N° DE VISITAS REALIZADAS', 'FECHA DE VISITA 1', 'FECHA DE VISITA 2',
        'FECHA DE VISITA 3', 'CON VISITA CONSECUTIVA', 'CON VISITA OPORTUNA',
        'N° DE VISITAS  GEORREFERENCIADAS', 'CUMPLE CON FOTOGRAFIA VALIDA',
        'NIÑO CON VERIFICACION NEGATIVA INEI', 'NO ENCONTRADO REUBICADO',
         'Mes','DNI de la madre', 'Número de Documento del niño',
        'Total de visitas completas para la edad',
        'Total de Intervenciones', 'Total de VD presenciales Realizadas',
        'Total de VD presenciales Válidas',
        'Total de VD presencial Válidas WEB',
        'Total de VD presencial Válidas MOVIL',  'Mes_',
        'Número de Documento del Niño', 'ETAPA', 'Verificacion',
        'Estado Visitas', 'VISITA1', 'VISITA2', 'VISITA3',
        'Estado Padrón', 'Documento', 'Tipo de Documento', 'DATOS NIÑO PADRON',
        'FECHA DE NACIMIENTO', 'DIRECCION PADRON',
        'REFERENCIA DE DIRECCION', 'MENOR VISITADO', 'EESS', 'ENTIDAD',
        'FECHA DE MODIFICACIÓN DEL REGISTRO', 'USUARIO QUE MODIFICA',
        'TIPO DE SEGURO_y'
        ]
    ]
    
    dup_df = dfff.groupby(["Periodo","DOCUMENTO_NUMERO"])[["TIPO DE SEGURO_x"]].count().reset_index()
    dup_df.columns = ["Periodo","DOCUMENTO_NUMERO","ESTADO REGISTRO PADRON"]
    dup_df['ESTADO REGISTRO PADRON'] = dup_df['ESTADO REGISTRO PADRON'].replace({
            1: 'No Duplicado durante el Mes',
            2: 'Duplicado durante el Mes',
            3: 'Triplicado durante el Mes',
    })
    dfff = pd.merge(dfff,dup_df , left_on=["Periodo","DOCUMENTO_NUMERO"], right_on=["Periodo","DOCUMENTO_NUMERO"], how='left')
    st.write(dfff.shape)
    last_df = dfff.copy()
    prioridad = {'DNI': 1, 'CUI': 2, 'CNV': 3}
    last_df['Prioridad'] = last_df['Tipo de Documento'].map(prioridad)
    last_df = last_df.sort_values(by=['Periodo','Número de Documento del niño', 'Prioridad'])
    last_df = last_df.drop_duplicates(subset=['Periodo','Número de Documento del niño'], keep='first')
    last_df = last_df.drop(columns=['Prioridad'])
    st.write(last_df.shape)
    st.dataframe(last_df)
    def eliminar_periodos_duplicados(texto):
        periodos = texto.split(" - ")
        periodos_unicos = sorted(set(periodos), key=periodos.index)
        return " - ".join(periodos_unicos)
    def addColPeriodosVisitados(dataframe = pd.DataFrame()):
        dataframe["Periodos"] = dataframe["Periodo"]+" - "
        childs_buscados_periodos_df = dataframe.groupby(["DOCUMENTO_NUMERO",])[["Periodos"]].sum().reset_index()
        childs_buscados_periodos_df["Periodos"] = childs_buscados_periodos_df.apply(lambda x: eliminar_periodos_duplicados(x['Periodos']),axis=1)
        childs_buscados_periodos_df.columns = ["DOCUMENTO_NUMERO","Periodos"]
        return childs_buscados_periodos_df
    duplicates_per_df = addColPeriodosVisitados(last_df)

    last_df = pd.merge(last_df,duplicates_per_df , left_on=["DOCUMENTO_NUMERO"], right_on=["DOCUMENTO_NUMERO"], how='left')
    last_df = last_df.drop(columns=['Periodos_x'])
    last_df = last_df.rename(columns=  {"Periodos_y":"Periodos"})
    st.write(last_df.shape)
    st.dataframe(last_df)

    doc_eess_df = last_df.groupby(["DOCUMENTO_NUMERO","Establecimiento de Salud"])[['N° DE VISITAS REALIZADAS']].sum().reset_index()
    doc_eess_df["Establecimiento de Salud"] = doc_eess_df["Establecimiento de Salud"]+ " - "
    
    doc_eess_df = doc_eess_df.groupby(["DOCUMENTO_NUMERO"])[["Establecimiento de Salud"]].sum().reset_index()
    
    doc_eess_df["Establecimiento de Salud"] = doc_eess_df.apply(lambda x: eliminar_periodos_duplicados(x['Establecimiento de Salud']),axis=1)
    doc_eess_df["Establecimiento de Salud"] = doc_eess_df["Establecimiento de Salud"].str[:-2]
    doc_eess_df = doc_eess_df[["Establecimiento de Salud","DOCUMENTO_NUMERO"]]
    st.write(doc_eess_df.shape)
    st.dataframe(doc_eess_df)
    
    with st.expander("Descargas"):
        st.download_button(
                label="Descargar Reporte sin Duplicados",
                data=convert_excel_df(last_df),
                file_name=f"REVISION_GENERAL_VD_NIÑOS_2024.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar Reporte con Duplicados",
                data=convert_excel_df(dfff),
                file_name=f"REVISION_GENERAL_VD_NIÑOS_2024.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar DNI UNICOS",
                data=convert_excel_df(doc_eess_df),
                file_name=f"REVISION_GENERAL_VD_UNICOSCHILDS_2024.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )