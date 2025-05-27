import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from styles import styles
from utils.cache_handler import *
from utils.helpers import *
from datetime import datetime
from utils.functions_data import gestantes_unicas_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

PADRON_COLUMNS = [
            'Tipo_file','Tipo de Documento','Documento','DATOS NIÑO PADRON',
            'FECHA DE NACIMIENTO', 'EJE VIAL', 'DIRECCION PADRON',
       'REFERENCIA DE DIRECCION', 'MENOR VISITADO', '¿MENOR ENCONTRADO?', 'FECHA DE VISITA',
       'FUENTE DE DATOS', 'FECHA DE FUENTE DE DATOS', 'EESS NACIMIENTO',
       'EESS', 'FRECUENCIA DE ATENCION', 'TIPO DE SEGURO',
       'PROGRAMAS SOCIALES', 'TIPO DE DOCUMENTO DE LA MADRE',
       'NUMERO DE DOCUMENTO  DE LA MADRE','DATOS MADRE PADRON',
       
       'NUMERO DE CELULAR', 'CELULAR_CORREO', 'GRADO DE LA MADRE',
       'LENGUA DE LA MADRE', 
       'FECHA CREACION DE REGISTRO', 'USUARIO QUE CREA',
       'FECHA DE MODIFICACIÓN DEL REGISTRO', 'USUARIO QUE MODIFICA', 'ENTIDAD',
       'TIPO REGISTRO', 
        ]
ORDER_COLS= [
            'RESPONSABLE','Tipo_file', 'Tipo de Documento', 'Documento', 'DATOS NIÑO PADRON','FECHA DE NACIMIENTO', 
            'EJE VIAL', 'DIRECCION PADRON','DIRECCION','DIRECCION DIFF',
            'REFERENCIA DE DIRECCION', 'MENOR VISITADO', '¿MENOR ENCONTRADO?',
            'FECHA DE VISITA', 'FUENTE DE DATOS', 'FECHA DE FUENTE DE DATOS',
            'EESS', 'NOMBRE DEL EESS', 'EESS ATENCION DIFF',
            'FRECUENCIA DE ATENCION',
            'TIPO DE SEGURO','TIPO DE DOCUMENTO DE LA MADRE',
            'NUMERO DE DOCUMENTO  DE LA MADRE', 'DATOS MADRE PADRON','NUMERO DE CELULAR','CELULAR DE LA MADRE', 'CELULAR DIFF',
            'CELULAR_CORREO', 'GRADO DE LA MADRE','LENGUA DE LA MADRE', 
            'FECHA CREACION DE REGISTRO', 'USUARIO QUE CREA','FECHA DE MODIFICACIÓN DEL REGISTRO', 'USUARIO QUE MODIFICA', 
            'ENTIDAD', 
            
        ]
reemplazo = {
            "0": "NINGUNO",
            "1": "SIS",
            "2": "ESSALUD",
            "3": "SANIDAD",
            "4": "PRIVADO"
        }

def eliminar_periodos_duplicados(texto):
    periodos = texto.split(" - ")
    periodos_unicos = sorted(set(periodos), key=periodos.index)
    return " - ".join(periodos_unicos)

def excel_pn_clean(dataframe = pd.DataFrame()):
        drop_cols = [
            "N°","EDAD DEL NIÑO","GRADO DE\nINSTRUCCIÓN DE LA\nMADRE(DEL MENOR DE EDAD)",
            "DIRECCION DE CORREO ELECTRONICO DE LA MADRE",
            "NOMBRES DE LA \nMADRE(DEL MENOR DE \nEDAD)","APELLIDO PATERNO DE LA MADRE (DEL MENOR DE EDAD)",
            "APELLIDO MATERNO DE LA MADRE (DEL MENOR DE EDAD)",
            "NUMERO DE DOCUMENTO DE LA MADRE(DEL MENOR\nDE EDAD)"
        ]
        dataframe= dataframe.drop(drop_cols, axis=1)
        
        
        dataframe.columns = ['Codigo de Padron','CNV','CUI','DNI','APELLIDO PATERNO', 'APELLIDO MATERNO',
       'NOMBRES DEL NIÑO', 'FECHA DE NACIMIENTO','DIRECCION', 'RESPONSABLE','NOMBRE DEL EESS', 'CELULAR DE LA MADRE']
        dataframe['FECHA DE NACIMIENTO']=dataframe['FECHA DE NACIMIENTO'].astype(str)
        dataframe['FECHA DE NACIMIENTO'] = pd.to_datetime(dataframe['FECHA DE NACIMIENTO'].str.strip(), format='%d/%m/%Y', errors='coerce')
        dataframe[['CNV', 'CUI', 'DNI']]=dataframe[['CNV', 'CUI', 'DNI']].fillna(0)
        dataframe[['CNV', 'CUI', 'DNI']]=dataframe[['CNV', 'CUI', 'DNI']].astype('int')
        for columnas in ['APELLIDO PATERNO', 'APELLIDO MATERNO', 'NOMBRES DEL NIÑO']:
            dataframe[columnas]=dataframe[columnas].fillna('')
        dataframe['DATOS NIÑO PADRON'] = dataframe.apply(lambda x: concatenar_datos(x['APELLIDO PATERNO'], x['APELLIDO MATERNO'],x['NOMBRES DEL NIÑO']),axis=1)
        
        dataframe['Documento']= dataframe.apply(lambda x: documento_unique(x['CNV'], x['CUI'],x['DNI'],x['Codigo de Padron'],'DOC'),axis=1)
        dataframe['Tipo de Documento'] = dataframe.apply(lambda x: documento_unique(x['CNV'], x['CUI'],x['DNI'],x['Codigo de Padron'],'TIPO'),axis=1)
        

        cols_orden = ['Codigo de Padron','Tipo de Documento','Documento','DATOS NIÑO PADRON','FECHA DE NACIMIENTO',
                        'DIRECCION',  'NOMBRE DEL EESS', 'CELULAR DE LA MADRE','RESPONSABLE']
        dataframe = dataframe[cols_orden]
        dataframe["Año Nacimiento"] = dataframe["FECHA DE NACIMIENTO"].dt.year
        dataframe["Mes Nacimiento"] = dataframe["FECHA DE NACIMIENTO"].dt.month
        
        return dataframe

def rn_verificacion_insert():
    styles(2)
    padron_df = fetch_padron()
    vd_childs_df = fetch_vd_childs()
    vd_gestantes_df = fetch_vd_gestantes()
    padron_df = padron_df[PADRON_COLUMNS]
    padron_df["Año Nacimiento"] = padron_df["FECHA DE NACIMIENTO"].dt.year
    padron_df["Mes Nacimiento"] = padron_df["FECHA DE NACIMIENTO"].dt.month
    print(padron_df.info())
    head_col_1,head_col_2 = st.columns(2)
    with head_col_1:
        st.title("Revisión Actualizaciones RN")
    with head_col_2:
        
        uploaded_file = st.file_uploader(
            "Ingresa Reporte Recien Nacidos", accept_multiple_files=False
        )
    # VD C1 NIÑOS
    vd_childs_df = vd_childs_df[vd_childs_df["Año"]=="2025"]
    
    vd_childs_df["Etapa"] = vd_childs_df["Etapa"]+" - "
    
    vd_childs_df["Celular de la Madre"] = vd_childs_df["Celular de la Madre"].fillna("0")
    vd_childs_df["Celular de la Madre"] = pd.to_numeric(vd_childs_df["Celular de la Madre"], errors='coerce').fillna(0).astype(int).astype(str)+" - "
    vd_childs_df = vd_childs_df.groupby(["Número de Documento de Niño","Celular de la Madre"])[["Etapa"]].sum().reset_index()
    vd_childs_df = vd_childs_df.groupby(["Número de Documento de Niño","Etapa"])[["Celular de la Madre"]].sum().reset_index()
    vd_childs_df["Etapa"] = vd_childs_df.apply(lambda x: eliminar_periodos_duplicados(x['Etapa']),axis=1)
    vd_childs_df.columns = ["Documento","C1 Niños Visitados","Celular Madre"]
    vd_childs_df["C1 Niños Visitados"] = vd_childs_df["C1 Niños Visitados"].str[:-2]
    vd_childs_df["Documento"] = vd_childs_df["Documento"].astype(int)
    vd_childs_df["Celular Madre"] = vd_childs_df["Celular Madre"].str[:-2]
    #VD C1 GESTANTES
    #st.dataframe(vd_gestantes_df)
    vd_gestantes_df["Etapa"] = vd_gestantes_df["Etapa"]+" - "
    vd_gestantes_df["Celular de la Madre"] = vd_gestantes_df["Celular de la Madre"].fillna("0")
    vd_gestantes_df["Celular de la Madre"] = vd_gestantes_df["Celular de la Madre"].astype(int).astype(str)+" - "
    vd_gestantes_df = vd_gestantes_df.groupby(["Número de Documento","Dirección","Celular de la Madre"])[["Etapa"]].sum().reset_index()#,"Celular de la Madre"
    vd_gestantes_df = vd_gestantes_df.groupby(["Número de Documento","Dirección","Etapa"])[["Celular de la Madre"]].sum().reset_index()
    vd_gestantes_df["Etapa"] = vd_gestantes_df.apply(lambda x: eliminar_periodos_duplicados(x['Etapa']),axis=1)
    vd_gestantes_df["Celular de la Madre"] = vd_gestantes_df.apply(lambda x: eliminar_periodos_duplicados(x['Celular de la Madre']),axis=1)
    vd_gestantes_df.columns = ["NUMERO DE DOCUMENTO  DE LA MADRE","DIRECCION GESTANTE","C1 Gestantes Visitadas","Celular Gestante"]#,"Celular Gestante",
    vd_gestantes_df["C1 Gestantes Visitadas"] = vd_gestantes_df["C1 Gestantes Visitadas"].str[:-2]
    vd_gestantes_df["Celular Gestante"] = vd_gestantes_df["Celular Gestante"].str[:-2]
    vd_gestantes_df = vd_gestantes_df.drop_duplicates(subset=['NUMERO DE DOCUMENTO  DE LA MADRE'], keep='first')
    
    if uploaded_file is not None:
        
        dataframe = pd.read_excel(uploaded_file,skiprows=4,)#dtype={"Número de Documento": "str"}
        dataframe = excel_pn_clean(dataframe = dataframe)
        years = dataframe['Año Nacimiento'].unique()
        months = dataframe['Mes Nacimiento'].unique()
        dataframe = dataframe[["Documento","DIRECCION","NOMBRE DEL EESS","CELULAR DE LA MADRE","RESPONSABLE"]]
        padron_df = padron_df[(padron_df['Año Nacimiento'].isin(years)) & (padron_df['Mes Nacimiento'].isin(months))]
        padron_df = padron_df.reset_index(drop=True)
        dff = pd.merge(padron_df, dataframe, left_on='Documento', right_on='Documento', how='left') 
        dff["RESPONSABLE"] = dff["RESPONSABLE"].fillna("NINGUNO")
        # Remove duplicate rows
        
        dff['DIRECCION DIFF'] = dff.apply(
            lambda x: 'Dirección con cambios' if x['DIRECCION PADRON'] != x['DIRECCION'] 
            else 'Dirección sin cambios', axis=1
        )
        
        dff['CELULAR DIFF'] = dff.apply(
            lambda x: 'Celular con cambios' if x['NUMERO DE CELULAR'] != x['CELULAR DE LA MADRE'] 
            else 'Celular sin cambios', axis=1
        )
        dff['EESS ATENCION DIFF'] = dff.apply(
            lambda x: 'EESS con cambios' if x['EESS'] != x['NOMBRE DEL EESS'] 
            else 'EESS sin cambios', axis=1
        )
        
        dff["TIPO DE SEGURO"] = dff["TIPO DE SEGURO"].fillna("SIN DATOS").apply(
            lambda x: "SIN DATOS" if x == "SIN DATOS" else 
                ", ".join([reemplazo.get(num.strip(), num.strip()) 
                            for num in x.split(",") if num.strip()])
        )
        print(dff.columns)
        
        dff = dff[ORDER_COLS]
        dff = dff.rename(columns={
            'DIRECCION PADRON':'DIRECCION ACTUAL',
            'DIRECCION':'DIRECCION ANTERIOR',
            'NUMERO DE CELULAR':'CELULAR ACTUAL',
            'CELULAR DE LA MADRE':'CELULAR ANTERIOR',
            'EESS':'EESS ACTUAL',
            'NOMBRE DEL EESS':'EESS ANTERIOR',
            'Tipo_file':'Tipo Registro Padron',
        })
        dff['EDAD'] = dff['FECHA DE NACIMIENTO'].apply(calcular_edad_dias)
        dff = pd.merge(dff, vd_childs_df, left_on='Documento', right_on='Documento', how='left') 
        dff = pd.merge(dff, vd_gestantes_df, left_on='NUMERO DE DOCUMENTO  DE LA MADRE', right_on='NUMERO DE DOCUMENTO  DE LA MADRE', how='left')
        dff["ACTUALIZADO"] = np.where(
            (dff["ENTIDAD"] == "MUNICIPIO") &
            (dff["USUARIO QUE MODIFICA"].isin(["18215881", "SERVICIO DNI ESTADO"])) &
            (dff["EJE VIAL"] != " ") &
            (dff["REFERENCIA DE DIRECCION"].notna()),
            "ACTUALIZADO",
            "NO ACTUALIZADO"
        )
        # Remove duplicates only when Celular Gestante is not None
        #dff = dff.sort_values('Celular Gestante', na_position='last')
        #dff = dff.drop_duplicates(subset=['Celular Gestante'], keep='first')
        st.write(dff.shape)
        st.dataframe(dff)
        # Create DIRECCION DIFF column
        st.download_button(
                label="Descargar Reporte RN",
                data=convert_excel_df(dff),
                file_name=f"AvancesRN_{years[0]}_{months[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        
        
