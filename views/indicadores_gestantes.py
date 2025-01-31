import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from styles import styles
from utils.cache_handler import *
from utils.helpers import *

def indicadores_gestantes():
    styles(2)
    fecha_actual = datetime.now()
    carga_df = fetch_carga_gestantes()
    carga_df["Mes"] = carga_df["Mes"].astype(int)
    vd_df = fetch_vd_gestantes()
    vd_df["Año"] = vd_df["Año"].astype(str)
    padron_df = fetch_padron()
    gestantes = pd.read_parquet('datos_gestantes.parquet', engine='pyarrow')
    columns_row1 = st.columns([3,4,4])
    columns_row1[0].title("Gestantes")
    with columns_row1[1]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with columns_row1[2]:
        select_mes  = st.selectbox("Mes:", ["Ene"], key="select2")
    
    if select_mes == "Ene":
        select_year_verifi = str(int(select_year) - 1)
        select_mes_verifi = mes_short(12)
    else:
        select_year_verifi = select_year
        select_mes_verifi = select_mes

    
    #st.write(select_year_verifi)
    #st.write(select_mes_verifi)
    
    carga_filt_df = carga_df[(carga_df['Año']==str(select_year))&(carga_df['Mes']==mestext_short(select_mes))]
    actvd_filt_df_last = vd_df[(vd_df['Año']==str(select_year))&(vd_df['Mes']==select_mes)]     
    actvd_filt_df = vd_df[(vd_df['Año']==select_year_verifi)&(vd_df['Mes']==select_mes_verifi)]
    
    carga_filt_df['Establecimiento de Salud'] = carga_filt_df['Establecimiento de Salud'].fillna("Sin Asignar")
    num_carga_ges = carga_filt_df.shape[0]
    num_visitas_ges = carga_filt_df["Total de VD presenciales Válidas"].sum()
    col_metric = st.columns(4)
    col_metric[0].metric(f"Gestantes Cargadas", num_carga_ges)
    col_metric[1].metric(f"N° Visitas Realizadas Válidas", num_visitas_ges)
    
    vd_ref = actvd_filt_df.groupby(["Número de Documento","Actores Sociales","Etapa"])[["Año"]].count().reset_index()
    vd_ref_2 = vd_ref.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
    vd_ref_2 = vd_ref_2.drop_duplicates(subset='Número de Documento', keep='first')
    vd_ref_2.columns = ["Documento","Actores Sociales","Etapa","count"]
    vd_ref_2["Documento"] = vd_ref_2["Documento"].str.strip()

    
    vd_ref_act = actvd_filt_df_last.groupby(["Número de Documento","Etapa"])[["Año"]].count().reset_index()
    vd_ref_act = vd_ref_act.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
    vd_ref_act = vd_ref_act.drop_duplicates(subset='Número de Documento', keep='first')
    vd_ref_act.columns = ["Documento_","Etapa","count"]
    vd_ref_act["Documento_"] = vd_ref_act["Documento_"].str.strip()
            #JOIN 1
         
    vd_add_df = pd.merge(carga_filt_df, gestantes, left_on='Número de Documento', right_on='Documento', how='left')
            
    vd_add_df["DOC"] = vd_add_df["Número de Documento"].str.lstrip('0')
    
    
            #JOIN 2
    vd_fin_df = pd.merge(vd_add_df, vd_ref_2, left_on='DOC', right_on='Documento', how='left')
            #SELECCIONAR COLUMNAS
    dataframe_gestante = vd_fin_df[['Nombres del Actor Social', 'Rango de Edad','Tipo de Documento', 'Número de Documento', 'Fecha de Nacimiento',
        'Dirección',  'Celular de la Madre', 'Zona', 'Manzana', 'Sector','Establecimiento de Salud', 
            'Total de visitas completas para la edad', 'Periodo', 'Gestante', 'EESS_C1', 'Actores Sociales','Etapa']]
    
    cols = ['Actor Social', 'Rango de Edad','Tipo de Documento', 'Número de Documento', 'Fecha de Nacimiento',
                'Dirección',  'Celular de la Madre', 'Zona', 'Manzana', 'Sector','Establecimiento de Salud', 
                'Número de Visitas Completas', 'Periodo', 'Nombre Gestante', 'EESS ULTIMA ATENCIÓN', 'Actores Social MES ANTERIOR','Etapa']
    dataframe_gestante.columns = cols
    cols_order = ['Periodo','Actores Social MES ANTERIOR','Actor Social','Establecimiento de Salud','Rango de Edad',
            'Tipo de Documento', 'Número de Documento','Nombre Gestante', 'Fecha de Nacimiento',
            'Dirección',  'Celular de la Madre','Número de Visitas Completas', 'Zona', 'Manzana', 'Sector', 
            'EESS ULTIMA ATENCIÓN', 'Etapa']
    dataframe_gestante = dataframe_gestante[cols_order]
    dataframe_gestante['Celular de la Madre'] = dataframe_gestante['Celular de la Madre'].fillna(0)
    dataframe_gestante['Celular de la Madre'] = dataframe_gestante['Celular de la Madre'].astype(int)
            
    dataframe_gestante['Etapa'] = dataframe_gestante.apply(lambda x: estado_gestante(x['Etapa'], x['Establecimiento de Salud']),axis=1)
    #new dataframe puerperas
    dataframe_gestante = dataframe_gestante[["Periodo","Actor Social","Establecimiento de Salud","Rango de Edad","Tipo de Documento","Número de Documento",
    "Nombre Gestante","Dirección","EESS ULTIMA ATENCIÓN","Etapa"
    ]]
    prioridad = {'DNI': 1, 'CUI': 2, 'CNV': 3}
    padron_df['Prioridad'] = padron_df['Tipo de Documento'].map(prioridad)
    padron_df = padron_df.sort_values(by=['Documento', 'Prioridad'])
    padron_df = padron_df.drop_duplicates(subset='Documento', keep='first')
    padron_df = padron_df.drop(columns=['Prioridad'])
    padron_df["EDAD_MESES"] = padron_df["FECHA DE NACIMIENTO"].apply(lambda x: (fecha_actual.year - x.year) * 12 + (fecha_actual.month - x.month))
    padron_df = padron_df[[
    'NUMERO DE DOCUMENTO  DE LA MADRE',"Documento","DATOS NIÑO PADRON","DATOS MADRE PADRON","ENTIDAD","Tipo_file","FECHA DE NACIMIENTO","DIRECCION PADRON","EESS","EDAD_MESES"
    ]]
    test_df = pd.merge(dataframe_gestante, padron_df, left_on='Número de Documento', right_on='NUMERO DE DOCUMENTO  DE LA MADRE', how='right')
    dff = test_df[test_df['Periodo'].notna()]
    dff = dff[dff["EDAD_MESES"]<= 12]
    trash_df = pd.merge(dff, vd_ref_act, left_on='Número de Documento', right_on='Documento_', how='left')
    trash_df= trash_df.drop(["Documento_","count"], axis=1)
    trash_df = trash_df.rename(columns = {"Etapa_y":f"Estado Actual ({select_mes})","Etapa_x":"Etapa MES ANTERIOR","Tipo_file":"Estado PADRON"})
    trash_df[f"Estado Actual ({select_mes})"] = trash_df[f"Estado Actual ({select_mes})"].fillna("SIN VISITA")
    
    #st.dataframe(trash_df,hide_index=True)
    #st.write(trash_df.shape[0])
    carga_childs = fetch_carga_childs()
    carga_childs = carga_childs[(carga_childs["Año"]==int(select_year))&(carga_childs["Mes"]==mestext_short(select_mes))]
    carga_childs["Número de Documento del niño"] = carga_childs["Número de Documento del niño"].astype(str)
    
    #carga_childs['Número de Documento del niño'] = carga_childs['Número de Documento del niño'].astype(str)
    vd_childs = fetch_vd_childs()
    vd_childs = vd_childs[(vd_childs["Año"]==str(select_year))&(vd_childs["Mes"]==select_mes)]
    vd_childs = vd_childs.groupby(['Número de Documento de Niño','Actores Sociales','Etapa'])[['Año']].count().reset_index()
    vd_childs = vd_childs.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
    vd_childs = vd_childs.drop_duplicates(subset='Número de Documento de Niño', keep='first')
    vd_childs.columns = ["Doc_Ultimo_Mes","Actor Social Ultimo Mes","Estado_Visita_Ult","count"]
    vd_childs = vd_childs[["Doc_Ultimo_Mes","Actor Social Ultimo Mes","Estado_Visita_Ult"]]
    #vd_childs["Doc_Ultimo_Mes"] = vd_childs["Doc_Ultimo_Mes"].astype(str)
    
    carga_childs = pd.merge(carga_childs, vd_childs, left_on='Número de Documento del niño', right_on='Doc_Ultimo_Mes', how='left')
    #st.dataframe(carga_childs)
    #st.write(carga_childs.shape[0])
    last_Df = pd.merge(carga_childs, dataframe_gestante, left_on='DNI de la madre', right_on='Número de Documento', how='left')
    last_Df = last_Df[last_Df['Periodo'].notna()]
    #
    last_Df = pd.merge(last_Df, vd_ref_act, left_on='Número de Documento', right_on='Documento_', how='left')
    columns_d = ['Nombres del Actor Social','Celular de la madre',
       'Rango de Edad_x', 'Tipo de Documento del niño',
       'Número de Documento del niño', 'Fecha de Nacimiento', 'Dirección_x',
       'Establecimiento de Salud_x','Mes', 'Año', 'Estado_Visita_Ult', 'Periodo',
       'Actor Social', 'Establecimiento de Salud_y', 'Rango de Edad_y',
       'Tipo de Documento', 'Número de Documento', 'Nombre Gestante',
       'Dirección_y', 'Etapa_y']
    last_Df = last_Df[columns_d]
    cols_order = [ 'Año','Mes','Periodo','Tipo de Documento del niño', 'Número de Documento del niño', 
      'Rango de Edad_x','Rango de Edad_y', 'Celular de la madre', 'Fecha de Nacimiento','Dirección_x','Dirección_y','Establecimiento de Salud_x','Establecimiento de Salud_y',
       'Nombres del Actor Social','Actor Social','Estado_Visita_Ult', 'Etapa_y',  'Tipo de Documento',
       'Número de Documento', 'Nombre Gestante']
    
    last_Df = last_Df[cols_order]
    cols_order = [ 'Año','Mes','Periodo','Tipo de Documento del niño', 'Número de Documento del niño', 
      'Rango de Edad NIÑO','Rango de Edad GESTANTE', 'Celular de la madre', 'Fecha de Nacimiento','Dirección_NIÑO','Dirección_GESTANTE','Establecimiento de Salud_NIÑO','Establecimiento de Salud_GESTANTE',
       'Actor Social - NIÑO','Actor Social - GESTANTE','ESTA DE VISITA ACTUAL NIÑO', 'ESTA DE VISITA ACTUAL GESTANTE',  'Tipo de Documento GESTANTE',
       'Número de Documento GESTANTE', 'Nombre Gestante']
    last_Df.columns = cols_order
   
    #pd.merge(last_Df, dataframe_gestante, left_on='Número de Documento', right_on='Número de Documento', how='left')
    
    eess_top_cargados = carga_filt_df.groupby(['Establecimiento de Salud'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
    eess_top_cargados = eess_top_cargados.rename(columns=  {"Número de Documento":"Registros"})
    fig_eess_count = px.bar(eess_top_cargados, x="Registros", y="Establecimiento de Salud",
                                    text="Registros", orientation='h',title = "Gestantes Asignadas por Establecimiento de Salud")
    fig_eess_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_count.update_layout(xaxis=dict(title=dict(text="Número de Gestantes")),font=dict(size=16))
    
    eess_top_visitas = actvd_filt_df_last.groupby(['Establecimiento de Salud','Dispositivo Intervención'])[['Número de Documento']].count().sort_values(["Número de Documento","Dispositivo Intervención"]).reset_index()
    eess_top_visitas = eess_top_visitas.rename(columns=  {"Número de Documento":"Registros"})
    fig_eess_top_visitas = px.bar(eess_top_visitas, x="Registros", y="Establecimiento de Salud",color = "Dispositivo Intervención",
                                    text="Registros", orientation='h',title = "Gestantes Visitados por Establecimiento de Salud")
    fig_eess_top_visitas.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_top_visitas.update_layout(xaxis=dict(title=dict(text="Número de Gestantes Visitadas")),font=dict(size=16))
    num_gest_visitadas_df = vd_ref_act.groupby(["Etapa"])[["count"]].count().reset_index()
    num_gest_visitadas_df = num_gest_visitadas_df.rename(columns=  {"count":"Registros"})

    fig_etapa_visitas = px.pie(num_gest_visitadas_df, values='Registros', names='Etapa',
                        title='N° de Registros por Etapa')
    fig_etapa_visitas.update_traces(textposition='inside', textinfo='percent+label+value')
    fig_etapa_visitas.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        
    )
    ssdf = carga_filt_df.groupby(["Establecimiento de Salud","Nombres del Actor Social"])[["Número de Documento"]].count().reset_index()
    dss = ssdf.groupby(["Establecimiento de Salud"])[["Nombres del Actor Social"]].count().sort_values("Nombres del Actor Social").reset_index()
    fig_eess_count_as = px.bar(dss, x="Nombres del Actor Social", y="Establecimiento de Salud",
                                    text="Nombres del Actor Social", orientation='h',title = "Actores Sociales por Establecimiento de Salud")
    fig_eess_count_as.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_count_as.update_layout(xaxis=dict(title=dict(text="Número de Actores Sociales")),font=dict(size=16))

    columnas_fig = st.columns(2)
    columnas_fig[0].plotly_chart(fig_eess_count)
    columnas_fig[1].plotly_chart(fig_eess_top_visitas)
    columnas_fig_2 = st.columns(2)
    columnas_fig_2[0].plotly_chart(fig_etapa_visitas)
    columnas_fig_2[1].plotly_chart(fig_eess_count_as)

    with st.expander("Descargas"):
        st.download_button(
                label="Descargar PUERPERAS",
                data=convert_excel_df(trash_df),
                file_name=f"puerperas_{select_mes}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar GESTANTES - NIÑOS",
                data=convert_excel_df(last_Df), 
                file_name=f"gestantes_niños_{select_mes}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    #st.write(dataframe_gestante.shape[0])
    #st.dataframe(dataframe_gestante)
    