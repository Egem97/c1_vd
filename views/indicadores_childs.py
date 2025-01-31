import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_carga_childs,fetch_vd_childs
from utils.helpers import *

def indicadores_childs():
    styles(2)

    carga_df = fetch_carga_childs()
    vd_df = fetch_vd_childs()
    columns_row1 = st.columns([3,4,4])
    columns_row1[0].title("Niños")
    with columns_row1[1]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with columns_row1[2]:
        select_mes  = st.selectbox("Mes:", ["Ene"], key="select2")
    vd_df = vd_df[(vd_df["Año"]==select_year)&(vd_df["Mes"]==select_mes)]#=
    



    carga_df = carga_df[(carga_df["Año"]==int(select_year))&(carga_df["Mes"]==mestext_short(select_mes))]
    carga_df['Establecimiento de Salud'] = carga_df['Establecimiento de Salud'].fillna("Sin Asignar")

    #VISITAS 
    vd_ref = vd_df.groupby(["Número de Documento de Niño","Etapa"])[["Año"]].count().reset_index()
    vd_ref_2 = vd_ref.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
    vd_ref_2 = vd_ref_2.drop_duplicates(subset='Número de Documento de Niño', keep='first')
    vd_ref.columns = ["Documento","Etapa","count"]
    vd_ref_df = vd_ref.groupby(["Etapa"])[["count"]].count().reset_index()
    vd_ref_df = vd_ref_df.rename(columns=  {"count":"Registros"})
    
    num_childs_visitados = vd_ref.shape[0]
    num_vd_ = (vd_ref['Etapa'].isin(["Visita Domiciliaria (6 a 12 Meses)","Visita Domiciliaria (1 a 5 meses)"])).sum()
    #st.write(num_vd_)
    num_carga = carga_df.shape[0]
    porcentaje_niños_visitados = f"{round((num_childs_visitados/num_carga)*100,2)}% - N° Faltantes {num_carga-num_childs_visitados}"
    num_vd_actu = carga_df["Total de VD presenciales Válidas"].sum()
    visitas_invalidas_sistema = carga_df["Total de VD presenciales Realizadas"].sum() - num_vd_actu
    num_vd_movil = carga_df["Total de VD presencial Válidas MOVIL"].sum()
    df_con_num_cel = (carga_df[carga_df["Celular de la madre"]!=0])#
    df_con_num_cel["Celular de la madre"] = df_con_num_cel["Celular de la madre"].astype(str)
    df_con_num_cel['Celular de la madre2'] = df_con_num_cel.apply(lambda x:validar_primer_digito_cel(x['Celular de la madre']),axis=1)
    cel_mal_reg = (df_con_num_cel['Celular de la madre2']==False).sum()
    con_num_cel = df_con_num_cel["Celular de la madre"].count()
    porcentaje_celular = f"{round(((con_num_cel-cel_mal_reg)/num_carga)*100,2)}%"
    
    metric_col = st.columns(6)
    metric_col[0].metric("N° Cargados",num_carga,"-",border=True)
    metric_col[1].metric("N° Total Niños Visitados",num_childs_visitados,porcentaje_niños_visitados,border=True)
    metric_col[2].metric("N° Visitas Realizadas Válidas",num_vd_actu,f"Visitas observadas {visitas_invalidas_sistema}",border=True)
    metric_col[3].metric("N° Visitas Realizadas MOVIL",num_vd_movil,"-",border=True)
    metric_col[4].metric("% Registros por Movil",f"{round((num_vd_movil/num_vd_actu)*100,2)}%","-",border=True)
    metric_col[5].metric("% Registro Celular",porcentaje_celular,"-",border=True)

    #st.write(vd_df)
    #st.write(carga_df.columns)
    eess_top_cargados = carga_df.groupby(['Establecimiento de Salud'])[['Número de Documento del niño']].count().sort_values("Número de Documento del niño").reset_index()
    eess_top_cargados = eess_top_cargados.rename(columns=  {"Número de Documento del niño":"Registros"})
    fig_eess_count = px.bar(eess_top_cargados, x="Registros", y="Establecimiento de Salud",
                                    text="Registros", orientation='h',title = "Niños Asignados por Establecimiento de Salud")
    fig_eess_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_count.update_layout(xaxis=dict(title=dict(text="Número de Niños Cargados")),font=dict(size=16))
    
    eess_top_visitas = vd_df.groupby(['Establecimiento de Salud','Dispositivo Intervención'])[['Número de Documento de Niño']].count().sort_values(["Número de Documento de Niño","Dispositivo Intervención"]).reset_index()
    eess_top_visitas = eess_top_visitas.rename(columns=  {"Número de Documento de Niño":"Registros"})
    fig_eess_top_visitas = px.bar(eess_top_visitas, x="Registros", y="Establecimiento de Salud",color = "Dispositivo Intervención",
                                    text="Registros", orientation='h',title = "Niños Visitados por Establecimiento de Salud")
    fig_eess_top_visitas.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_top_visitas.update_layout(xaxis=dict(title=dict(text="Número de Niños Visitados")),font=dict(size=16))
    #fig_eess_top_visitas.update_xaxes(categoryorder='category ascending')
    
    
    fig_etapa_visitas = px.pie(vd_ref_df, values='Registros', names='Etapa',
                        title='N° de Registros por Etapa')
    fig_etapa_visitas.update_traces(textposition='inside', textinfo='percent+label+value')
    fig_etapa_visitas.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        
    )
    print(carga_df.info())
    ssdf = carga_df.groupby(["Establecimiento de Salud","Nombres del Actor Social"])[["Número de Documento del niño"]].count().reset_index()
    dss = ssdf.groupby(["Establecimiento de Salud"])[["Nombres del Actor Social"]].count().sort_values("Nombres del Actor Social").reset_index()
    fig_eess_count_as = px.bar(dss, x="Nombres del Actor Social", y="Establecimiento de Salud",
                                    text="Nombres del Actor Social", orientation='h',title = "Actores Sociales por Establecimiento de Salud")
    fig_eess_count_as.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_count_as.update_layout(xaxis=dict(title=dict(text="Número de Actores Sociales")),font=dict(size=16))
    columnas_fig = st.columns(2)
    columnas_fig[0].plotly_chart(fig_eess_count)
    columnas_fig[1].plotly_chart(fig_eess_top_visitas)
    #st.write(vd_df)
    #st.write(vd_df.columns)
    columnas_fig_2 = st.columns(2)
    columnas_fig_2[0].plotly_chart(fig_etapa_visitas)
    columnas_fig_2[1].plotly_chart(fig_eess_count_as)