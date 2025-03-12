import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_childs,fetch_carga_childs,fetch_padron
from utils.helpers import *
from utils.functions_data import childs_unicos_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def status24():
    styles(2)
    actvd_df = fetch_vd_childs()
    actvd_df["Año"] = actvd_df["Año"].astype(str)
    carga_df = fetch_carga_childs()
    carga_df["Año"] = carga_df["Año"].astype(str)
    carga_df = carga_df[(carga_df["Año"]=="2024")&(carga_df["Mes"].isin([8,9,10,11,12]))]
    actvd_df = actvd_df[(actvd_df["Año"]=="2024")&(actvd_df["Mes"].isin(["Ago","Set","Oct","Nov","Dic"]))]
    carga_df["Número de Documento del niño"] = carga_df["Número de Documento del niño"].astype(str)
    columnas_head = st.columns([6,3,3])
    with columnas_head[0]:
        st.title("COMPROMISO 1 2024")
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
    
    #st.write(etapa_vd_join_df.shape)
    #st.write(etapa_vd_join_df)
    carga_df = carga_df[['Mes','Número de Documento del niño', 'Fecha de Nacimiento',
       'Total de visitas completas para la edad', 'Total de Intervenciones',
       'Total de VD presenciales Realizadas',
       'Total de VD presenciales Válidas',
       'Total de VD presencial Válidas WEB',
       'Total de VD presencial Válidas MOVIL']
    ]
    carga_df= carga_df.sort_values("Mes")
    carga_df["Mes_"] = carga_df["Mes"]
    carga_df["Mes"] = carga_df.apply(lambda x: mes_short(x['Mes']),axis=1)
    
    dff = pd.merge(carga_df,etapa_vd_join_df , left_on=["Mes","Número de Documento del niño"], right_on=["Mes","Número de Documento de Niño"], how='left')
    dff['Estado Visitas'] =  dff.apply(lambda x: estado_visitas_completas(x['Total de visitas completas para la edad'], x['Total de VD presenciales Válidas'],x['ETAPA']),axis=1)
    
    #st.write(dff.shape)
    
    vd_programadas_df = dff.groupby(["Mes"])[["Total de visitas completas para la edad"]].sum().reset_index()
    
    child_programados_df = dff.groupby(["Mes_","Mes"])[["Total de visitas completas para la edad"]].count().reset_index()
    child_programados_df = child_programados_df.rename(columns=  {"Total de visitas completas para la edad":"Niños Programados"})
    proyectado_dff = pd.merge(child_programados_df,vd_programadas_df , left_on='Mes', right_on='Mes', how='left')
    #ONLY REG CORRECTOS VD COMPLETA
    dataframe_efec = dff[
        (dff["ETAPA"].isin(["Visita Domiciliaria (6 a 12 Meses)","Visita Domiciliaria (1 a 5 meses)"])) &
        (dff["Verificacion"] == "Registro Regular") &
        (dff["Estado Visitas"] == "Visitas Completas")
    ]
    vd_movil_df = dataframe_efec.groupby(["Mes"])[["Total de VD presencial Válidas MOVIL"]].sum().reset_index()
    childs_encontrados_df = dataframe_efec.groupby(["Mes"])[["ETAPA"]].count().reset_index()
    childs_encontrados_df = childs_encontrados_df.rename(columns=  {"ETAPA":"Niños Encontrados"})
    proyectado_dff = pd.merge(proyectado_dff, childs_encontrados_df, left_on='Mes', right_on='Mes', how='left')
    proyectado_dff = pd.merge(proyectado_dff, vd_movil_df, left_on='Mes', right_on='Mes', how='left')
    
    proyectado_dff = proyectado_dff.drop(columns=['Mes_'])
    proyectado_dff = proyectado_dff.rename(columns={
        "Total de visitas completas para la edad": "Visitas Programadas",
        "Total de VD presencial Válidas MOVIL":"Visitas Georreferenciadas"
    })
    total_row = pd.DataFrame({
        "Mes": ["TOTAL"],  # Nombre de la fila
        "Niños Programados":proyectado_dff["Niños Programados"].sum(),
        "Visitas Programadas":proyectado_dff["Visitas Programadas"].sum(),
        "Niños Encontrados":proyectado_dff["Niños Encontrados"].sum(),
        "Visitas Georreferenciadas":proyectado_dff["Visitas Georreferenciadas"].sum(),
        

    })
    proyectado_dff = pd.concat([proyectado_dff, total_row], ignore_index=True)
    proyectado_dff["% GEO"] = round((proyectado_dff["Visitas Georreferenciadas"] / proyectado_dff["Visitas Programadas"])*100,1)
    proyectado_dff["% Cumplimiento"] = round((proyectado_dff["Niños Encontrados"] / proyectado_dff["Niños Programados"])*100,1)
    
    gb = GridOptionsBuilder.from_dataframe(proyectado_dff)
    gb.configure_default_column(cellStyle={'fontSize': '20px'}) 
    grid_options = gb.build()
    
    
    grid_response = AgGrid(proyectado_dff, # Dataframe a mostrar
                            gridOptions=grid_options,
                            height = 250,
                            enable_enterprise_modules=False,
                            #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                            update_mode='MODEL_CHANGED',
                            fit_columns_on_grid_load=True,
                            
                        
    )
    dff["ETAPA"] = dff["ETAPA"].fillna("Sin Visita")
    dff["Verificacion"] = dff["Verificacion"].fillna("Sin Registro")
    #NEGATIVOS
    negatido_dff =dff[dff["ETAPA"].isin(["No Encontrado","Rechazado","Sin Visita"])]
    etapa_nega_df = negatido_dff.groupby(["Mes_","Mes","ETAPA"])[["Número de Documento del niño"]].count().reset_index()
    etapa_nega_df.columns = ["Mes_","Mes","ETAPA","Niños Negativos"]
    fig_neg= px.bar(etapa_nega_df, x="Mes",color="ETAPA", y="Niños Negativos",text="Niños Negativos", title='Niños Negativos',barmode="group")
    fig_neg.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)


    #INCOMPLETOS
    incon_dff =dff[dff["Estado Visitas"].isin(["Visitas Incompletas(faltantes:1)","Visitas Incompletas(faltantes:2)","Visitas Incompletas(faltantes:3)"])]
    incon_dff = incon_dff.groupby(["Mes_","Mes","Estado Visitas"])[["Número de Documento del niño"]].count().reset_index()
    incon_dff.columns = ["Mes_","Mes","Estado Visitas","Niños VD Incompletas"]
    fig_incon= px.bar(incon_dff, x="Mes",color="Estado Visitas", y="Niños VD Incompletas",text="Niños VD Incompletas", title='Niños con VD Incompletas',barmode="group")
    fig_incon.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)

    columnas_add = st.columns(2)

    with columnas_add[0]:
        st.plotly_chart(fig_neg)
    with columnas_add[1]:
        st.plotly_chart(fig_incon)
    
    with st.expander("Descargas"):
        st.download_button(
                label="Descargar data 2024",
                data=convert_excel_df(dff),
                file_name=f"EstadoVisitas2024.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    
