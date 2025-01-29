import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_gestantes,fetch_padron,fetch_carga_gestantes
from utils.helpers import *
from datetime import datetime
from utils.functions_data import gestantes_unicas_visitados

def gestantes_status_vd():
    styles(2)
    fecha_actual = datetime.now()
    vd_df = fetch_vd_gestantes()
    vd_df["Año"] = vd_df["Año"].astype(str)
    carga_df = fetch_carga_gestantes()
    carga_df["Mes"] = carga_df["Mes"].astype(int)
    padron_df = fetch_padron()
    gestantes = pd.read_parquet('datos_gestantes.parquet', engine='pyarrow')

    eess = list(carga_df["Establecimiento de Salud"].unique())


    columns_row1 = st.columns([3,2,2,4])
    columns_row1[0].title("Visitas a Gestantes")
    with columns_row1[1]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with columns_row1[2]:
        select_mes  = st.selectbox("Mes:", ["Ene"], key="select2")
    with columns_row1[3]:
        select_eess  = st.multiselect("Establecimiento de Salud:", eess, key="select3",placeholder="Seleccione EESS")
        
        if len(select_eess)> 0:    
            select_eess_recorted = [s[11:] for s in select_eess]
            
            carga_df = carga_df[carga_df["Establecimiento de Salud"].isin(select_eess)]
            vd_df = vd_df[vd_df["Establecimiento de Salud"].isin(select_eess_recorted)]
    if select_mes == "Ene":
        select_year_verifi = str(int(select_year) - 1)
        select_mes_verifi = mes_short(12)
    else:
        select_year_verifi = select_year
        select_mes_verifi = select_mes

    carga_filt_df = carga_df[(carga_df['Año']==str(select_year))&(carga_df['Mes']==mestext_short(select_mes))]
    actvd_filt_df_last = vd_df[(vd_df['Año']==str(select_year))&(vd_df['Mes']==select_mes)]  
    actvd_filt_df = vd_df[(vd_df['Año']==str(select_year_verifi))&(vd_df['Mes']==select_mes_verifi)]  
    #totales
    num_carga = carga_filt_df.shape[0]
    num_visitas = carga_filt_df["Total de Intervenciones"].sum()
    num_visitas_validas = carga_filt_df["Total de VD presenciales Válidas"].sum()
    gestantes_unicas_vd = gestantes_unicas_visitados(actvd_filt_df_last,'Número de Documento',"ALL GESTANTE W DUPLICADOS")
    num_gestantes_vd = gestantes_unicas_vd.shape[0]
    num_vd_movil = carga_filt_df["Total de VD presencial Válidas MOVIL"].sum()
    num_vd_web = carga_filt_df["Total de VD presencial Válidas WEB"].sum()
    
    porcentaje_gestante_visita = f"{round((num_gestantes_vd/num_carga)*100,2)}%"
    
    #metricas cards
    metric_col = st.columns(7)
    metric_col[0].metric("Gestantes Cargadas",num_carga,f"Con Visita {num_gestantes_vd}({porcentaje_gestante_visita})",border=True)
    metric_col[1].metric("Total de Visitas",num_visitas,f"Visitas Válidas: {num_visitas_validas}",border=True)
    metric_col[2].metric("Visitas Movil",num_vd_movil,"-",border=True)#,f"Visitas Válidas: {num_visitas_validas}"
    gestantes_unicas_vd.columns = ["Doc_Ultimo_Mes","Actor Social Ultimo Mes","Estado_Visita_Ult","count"]
    gestantes_unicas_vd = gestantes_unicas_vd[["Doc_Ultimo_Mes","Actor Social Ultimo Mes","Estado_Visita_Ult"]]
    dataframe_pn = padron_df[[
        'Tipo_file', 'Documento', 'Tipo de Documento','DATOS NIÑO PADRON','CELULAR2_PADRON','SEXO',
        'FECHA DE NACIMIENTO', 'EJE VIAL', 'DIRECCION PADRON','REFERENCIA DE DIRECCION','MENOR VISITADO',
        'EESS NACIMIENTO','EESS', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN','TIPO DE DOCUMENTO DE LA MADRE',
        'NUMERO DE DOCUMENTO  DE LA MADRE','DATOS MADRE PADRON','TIPO DE DOCUMENTO DEL JEFE DE FAMILIA',
        'NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA','DATOS JEFE PADRON','ENTIDAD','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA','NUMERO DE CELULAR', 'CELULAR_CORREO',
    ]]
    #oin_df = pd.merge(carga_filt_df, dataframe_pn, left_on='Número de Documento', right_on='Documento', how='left')
    st.dataframe(carga_filt_df)













def geo_gestantes():
    styles(2)
    df = fetch_vd_gestantes()
    dff = df[df["Dispositivo Intervención"]=="MOVIL"]
    eess = list(dff["Establecimiento de Salud"].unique())
    year = list(dff["Año"].unique())
    month = list(dff["Mes"].unique())
    latitud_name = "Latitud Intervención"
    longitud_name = "Longitud Intervención"
    col_filt = st.columns([3,6,1,1])
    with col_filt[0]:
        st.title("Georef a Gestantes")
    with col_filt[1]:
        eess_selected = st.multiselect("Establecimientos de Salud",eess,placeholder="Escoja un Establecimiento de Salud")
        if len(eess_selected) > 0:
            dff = dff[dff["Establecimiento de Salud"].isin(eess_selected)]
    with col_filt[2]:
        year_selected = st.selectbox("Año",year)
        dff = dff[dff["Año"]==year_selected]
    with col_filt[3]:
        month_selected = st.selectbox("Mes",month)
        dff = dff[dff["Mes"]==month_selected]
    
    
    tab1,tab2,=st.tabs(['Mapa','Datos'])
    with tab1:    
        #
        col_filt_map = st.columns([3,3,3,3])
        with col_filt_map[0]:
            as_selected = st.selectbox('Actor Social',options=sorted(list(dff["Actores Sociales"].unique())),placeholder="Escoja un actor social",index=None) 
            if as_selected != None:
                dff = dff[dff["Actores Sociales"] == as_selected]
        
        with col_filt_map[1]:
            doc_input = st.text_input("Buscar por Doc Gestante")
            if len(doc_input) == 8 :
                dff = dff[dff["Número de Documento"] == doc_input]
        with col_filt_map[2]:  
            parMapa = st.selectbox('Tipo Mapa',options=["open-street-map", "carto-positron","carto-darkmatter"])          
            
        with col_filt_map[3]:
            
            st.metric("N° de Georreferencias",dff.shape[0])
        
        fig = px.scatter_mapbox(
            dff,lat=latitud_name,lon=longitud_name, 
            color="Establecimiento de Salud", hover_name="Actores Sociales",
            hover_data=["Número de Documento","Fecha Intervención"],
            zoom=14,
            height=600,
            #color_continuous_scale=px.colors.cyclical.IceFire
        )
        
        fig.update_layout(mapbox_style=parMapa)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        fig.update_layout(legend=dict(
            orientation="h",
            #entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        map_ = st.plotly_chart(fig, on_select="rerun")
        try:
            st.dataframe(dff[dff["Número de Documento"]==map_["selection"]["points"][0]["customdata"][0]])
        except:
            st.warning("Seleccione Gestante Georreferenciado")
        
    with tab2:
        
        st.dataframe(dff,use_container_width=True,hide_index=True)