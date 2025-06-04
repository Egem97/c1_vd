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

def bar_graph(datafrane : pd.DataFrame, x : str, y : str, title : str,color : str,orientation : str):
    if orientation == "v":
        fig = px.bar(datafrane, x= x, y=y,text=y, orientation=orientation,title =title,color=color)
    else:
        fig = px.bar(datafrane, x= x, y=y,text=x, orientation=orientation,title =title,color=color)
        
    fig.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis=dict(title=dict(text="")),font=dict(size=16))
    fig.update_layout(legend=dict(
            orientation="h",
            #entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
    return fig
        
def pie_graph(datafrane : pd.DataFrame, name : str, values : str, title : str):
    fig = px.pie(datafrane, values=values, names=name,title=title)
    fig.update_traces(textposition='inside', textinfo='percent+label+value',insidetextfont=dict(size=15))
    fig.update_layout(showlegend=False)
    return fig


def rn_month_insert():
    styles(2)
    padron_df = fetch_padron()
    carga_childs_df = fetch_carga_childs()
    vd_childs_df = fetch_vd_childs()
    vd_gestantes_df = fetch_vd_gestantes()
    padron_df = padron_df[PADRON_COLUMNS]
    padron_df["Año Nacimiento"] = padron_df["FECHA DE NACIMIENTO"].dt.year
    padron_df["Mes Nacimiento"] = padron_df["FECHA DE NACIMIENTO"].dt.month
    
    padron_df = padron_df.sort_values(by="Mes Nacimiento",ascending=True)
    padron_df["Mes"] = padron_df["Mes Nacimiento"].map(mes_compname)
    
    print(padron_df.info())
    head_col_1,head_col_2,head_col_3 = st.columns([4,2,6])
    with head_col_1:
        st.title("Revisión RN")
    with head_col_2:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        if select_year == "2025":
            padron_df = padron_df[padron_df["Año Nacimiento"]==2025]
    lista_mes = padron_df["Mes"].unique()
    with head_col_3:
        select_mes  = st.multiselect("Mes:",options=lista_mes,key="select2",default=lista_mes)
        if len(select_mes) > 0:
            padron_df = padron_df[padron_df["Mes"].isin(select_mes)]
    
    
    #############################################################################################################
    carga_childs_df["Año"] = carga_childs_df["Año"].astype(str)
    carga_childs_df = carga_childs_df[carga_childs_df["Año"]=="2025"]
    carga_childs_df["Mes_"] = carga_childs_df["Mes"].map(mes_compname)
    carga_childs_df["Periodo"] = carga_childs_df["Año"]+" - "+carga_childs_df["Mes_"]+" - "
    carga_childs_df = carga_childs_df.groupby(["Número de Documento del niño"])[["Periodo"]].sum().reset_index()
    carga_childs_df["Periodo"] = carga_childs_df.apply(lambda x: eliminar_periodos_duplicados(x['Periodo']),axis=1)
    carga_childs_df.columns = ["Documento","Periodo Carga C1"]
    carga_childs_df["Periodo Carga C1"] = carga_childs_df["Periodo Carga C1"].str[:-2]
    carga_childs_df = carga_childs_df.drop_duplicates(subset=['Documento'], keep='first')
    #st.write(carga_childs_df.shape)
    #st.dataframe(carga_childs_df)
    
    #############################################################################################################
    #########################
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
    vd_childs_df = vd_childs_df.drop_duplicates(subset=['Documento'], keep='first')
    #########################        
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
    #############################
    padron_df["TIPO DE SEGURO"] = padron_df["TIPO DE SEGURO"].fillna("SIN DATOS").apply(
            lambda x: "SIN DATOS" if x == "SIN DATOS" else 
                ", ".join([reemplazo.get(num.strip(), num.strip()) 
                            for num in x.split(",") if num.strip()])
        )        
    padron_df['Edad'] = padron_df['FECHA DE NACIMIENTO'].apply(calcular_edad_dias)
    dff = pd.merge(padron_df, vd_childs_df, left_on='Documento', right_on='Documento', how='left') 
    dff = pd.merge(dff, vd_gestantes_df, left_on='NUMERO DE DOCUMENTO  DE LA MADRE', right_on='NUMERO DE DOCUMENTO  DE LA MADRE', how='left')
    dff = pd.merge(dff, carga_childs_df, left_on='Documento', right_on='Documento', how='left')
    dff["ACTUALIZADO"] = np.where(
            (dff["ENTIDAD"] == "MUNICIPIO") &
            (dff["USUARIO QUE MODIFICA"].isin(["18215881", "SERVICIO DNI ESTADO"])) &
            (dff["EJE VIAL"] != " ") &
            (dff["REFERENCIA DE DIRECCION"].notna()),
            "ACTUALIZADO",
            "NO ACTUALIZADO"
    )
    total_childs = dff.shape[0]
    act_mes_df = dff.groupby(["Mes Nacimiento","Mes","ACTUALIZADO"])[["Documento"]].count().sort_values(by="Mes Nacimiento",ascending=True).reset_index()
    act_mes_df.columns = ["Mes Nacimiento","Mes","Actualizado","Niños"]
    tipo_seguro_df = dff.groupby(["TIPO DE SEGURO"])[["ACTUALIZADO"]].count().sort_values("ACTUALIZADO",ascending=False).reset_index()
    tipo_seguro_df.columns = ["Tipo de Seguro","Niños"]
    actualizado_df = dff.groupby(["ACTUALIZADO"])[["Documento"]].count().sort_values("Documento",ascending=False).reset_index()
    actualizado_df.columns = ["Actualizado","Niños"]
    
    col_1,col_2 = st.columns([1,1])
    with col_1:
        st.plotly_chart(bar_graph(act_mes_df,x="Mes",y="Niños",title=f"Niños Actualizados por Mes ({total_childs})",color="Actualizado",orientation="v"))
    with col_2:
        st.plotly_chart(bar_graph(tipo_seguro_df,x="Tipo de Seguro",y="Niños",title="Niños Actualizados por Tipo de Seguro",color=None,orientation="v"))
    col_1_1,col_1_2 = st.columns(2)
    with col_1_1:
        st.plotly_chart(pie_graph(actualizado_df, "Actualizado", "Niños", "Niños por Tipo de Documento"))
    with col_1_2:
        st.download_button(
                label="Descargar Reporte RN",
                data=convert_excel_df(dff),
                file_name=f"AvancesRN_meses.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    #st.write(dff.shape)
    #st.write(dff)