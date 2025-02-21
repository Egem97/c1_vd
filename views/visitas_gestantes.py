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
    
    
    eess = list(carga_df["Establecimiento de Salud"].unique())


    columns_row1 = st.columns([3,2,2,4])
    columns_row1[0].title("Visitas a Gestantes")
    with columns_row1[1]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with columns_row1[2]:
        select_mes  = st.selectbox("Mes:", ["Ene","Feb"], key="select2",index=True)
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

    #ESTO VALIDA ERRORES DEL EXCEL DE DETALLE GESTANTE
    carga_filt_df["Total de Intervenciones"] = carga_filt_df["Total de VD presencial Válidas WEB"] + carga_filt_df["Total de VD presencial Válidas MOVIL"]
    carga_filt_df["Total de VD presenciales Válidas"] = carga_filt_df["Total de VD presencial Válidas WEB"] + carga_filt_df["Total de VD presencial Válidas MOVIL"]
    #actvd_filt_df = vd_df[(vd_df['Año']==str(select_year_verifi))&(vd_df['Mes']==select_mes_verifi)]  
    #totales
    num_carga = carga_filt_df.shape[0]
    num_visitas_programadas = carga_filt_df["Total de visitas completas para la edad"].sum()
    #st.write(carga_filt_df["Total de visitas completas para la edad"].sum())
    num_visitas = carga_filt_df["Total de Intervenciones"].sum()
    num_visitas_validas = carga_filt_df["Total de VD presenciales Válidas"].sum()
    gestantes_unicas_vd = gestantes_unicas_visitados(actvd_filt_df_last,'Número de Documento',"ALL GESTANTE W DUPLICADOS")
    num_gestantes_vd = gestantes_unicas_vd.shape[0]
    num_vd_movil = carga_filt_df["Total de VD presencial Válidas MOVIL"].sum()
    num_vd_web = carga_filt_df["Total de VD presencial Válidas WEB"].sum()
    
    porcentaje_gestante_visita = f"{round((num_gestantes_vd/num_carga)*100,2)}%"
    
    #metricas cards
    metric_col = st.columns(7)
    metric_col[0].metric("Gestantes Cargadas",num_carga,f"Con Visita {num_gestantes_vd}({num_carga-num_gestantes_vd})",border=True)
    metric_col[1].metric("Total de Visitas",num_visitas,f"VD Programadas: {num_visitas_programadas}",border=True)
    #metric_col[2].metric("Visitas Movil",num_vd_movil,"-",border=True)#,f"Visitas Válidas: {num_visitas_validas}"
    gestantes_unicas_vd.columns = ["Doc_gestante","Actor Social Ultimo Mes","Etapa","Número Visitas"]
    gestantes_unicas_vd = gestantes_unicas_vd[["Doc_gestante","Etapa","Número Visitas"]]
    
    try:
        puerperas_df=pd.read_parquet(f'./data/puerperas/puerperas_verificadas_{select_mes}.parquet', engine='pyarrow')
        puerperas_df = puerperas_df[['Número de Documento','FECHA DE NACIMIENTO','EDAD_MESES']]
        gest_dff = pd.merge(carga_filt_df, puerperas_df, left_on='Número de Documento', right_on='Número de Documento', how='left')
    except:
        prioridad = {'DNI': 1, 'CUI': 2, 'CNV': 3}
        padron_df['Prioridad'] = padron_df['Tipo de Documento'].map(prioridad)
        padron_df = padron_df.sort_values(by=['Documento', 'Prioridad'])
        padron_df = padron_df.drop_duplicates(subset='Documento', keep='first')
        padron_df = padron_df.drop(columns=['Prioridad'])
        padron_df["EDAD_MESES"] = padron_df["FECHA DE NACIMIENTO"].apply(lambda x: (fecha_actual.year - x.year) * 12 + (fecha_actual.month - x.month))
        padron_df = padron_df[[
            'NUMERO DE DOCUMENTO  DE LA MADRE',"Documento","DATOS NIÑO PADRON","FECHA DE NACIMIENTO","DIRECCION PADRON","EESS","EDAD_MESES"
        ]]
        padron_df = padron_df[padron_df["EDAD_MESES"]<= 12]
        gest_dff = pd.merge(carga_filt_df, padron_df, left_on='Número de Documento', right_on='NUMERO DE DOCUMENTO  DE LA MADRE', how='left')
    
    gest_dff["Estado Gestante"] = gest_dff.apply(lambda x:validar_vd_gestante(x['Total de VD presenciales Válidas']),axis=1)
    gest_dff['ESTADO_NACIMIENTO'] = gest_dff['FECHA DE NACIMIENTO'].apply(
        lambda fecha: 'GESTANTE' if pd.isna(fecha) 
        else 'PUERPERA'
    )
    gest_dff = gest_dff.rename(columns={"FECHA DE NACIMIENTO":"Fecha Nacimiento Hijo","EDAD_MESES":"Edad en Meses Hijo"})
    gestantes_join_df = pd.merge(gest_dff, gestantes_unicas_vd, left_on='Número de Documento', right_on='Doc_gestante', how='left')
    gestantes_join_df["Etapa"] = gestantes_join_df["Etapa"].fillna("No Visitadas")
    num_puerperas = (gestantes_join_df["Fecha Nacimiento Hijo"].notna()).sum()
    
    
    vd_completa_gestante_df = gestantes_join_df[gestantes_join_df["Estado Gestante"]=="Visita Completa"]

    con_visita_cel = gestantes_join_df[(gestantes_join_df["Celular de la Madre"].notna())]
    #num_con_visita_cel = con_visita_cel.shape[0]
    percent_reg_tel = round((con_visita_cel.shape[0]/num_carga)*100,2)

    num_ges_result = vd_completa_gestante_df.shape[0]
    total_visitas_validas_movil = vd_completa_gestante_df["Total de VD presencial Válidas MOVIL"].sum()
    percent_vd_completas_movil = round((total_visitas_validas_movil/num_vd_movil)*100,2)
    percent_vd_movil_validate = round((total_visitas_validas_movil/num_visitas_programadas)*100,2)
    total_meta_vd = round(num_visitas_programadas*0.75)
    total_faltante_vd_meta = total_meta_vd-total_visitas_validas_movil

    percent_total_vd_12 = round((num_ges_result/(num_carga))*100,2)


    metric_col[2].metric("Visitas Movil",num_vd_movil,f"VD Completas:{total_visitas_validas_movil}({percent_vd_completas_movil}%)",border=True)
    metric_col[3].metric("Visitas Completas - Movil",total_visitas_validas_movil,f"Meta (75%): {total_meta_vd}",border=True)
    metric_col[4].metric("% VD Georreferenciadas",f"{percent_vd_movil_validate}%",f"VD Faltantes {total_faltante_vd_meta}",border=True)#
    metric_col[5].metric("% Registros Telefonicos",f"{percent_reg_tel}%",f"-",border=True)
    metric_col[6].metric("% Niños Oportunos y Completos",f"{percent_total_vd_12}%",f"Positivos:{num_ges_result}",border=True)#,f"Positivos:{num_ninos_result} Excluidos:{num_excluyen_childs}"
    

    
    #CARGA GESTANTES
    eess_top_cargados = gestantes_join_df.groupby(['Establecimiento de Salud'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
    eess_top_cargados = eess_top_cargados.rename(columns=  {"Número de Documento":"Registros"})
    fig_eess_count = px.bar(eess_top_cargados, x="Registros", y="Establecimiento de Salud",
                                    text="Registros", orientation='h',title = "Gestantes Asignadas por Establecimiento de Salud")
    fig_eess_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_count.update_layout(xaxis=dict(title=dict(text="Número de Gestantes Cargadas")),font=dict(size=16))
    
    #VISITAS GESTANTES
    eess_top_visitas = gestantes_join_df.groupby(['Establecimiento de Salud'])[['Total de VD presenciales Válidas']].sum().sort_values(["Total de VD presenciales Válidas"]).reset_index()
    eess_top_visitas = eess_top_visitas.rename(columns=  {"Total de VD presenciales Válidas":"Visitas"})
    fig_eess_top_visitas = px.bar(eess_top_visitas, x="Visitas", y="Establecimiento de Salud",
                                    text="Visitas", orientation='h',title = "Gestantes Visitadas por Establecimiento de Salud")
    fig_eess_top_visitas.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_top_visitas.update_layout(xaxis=dict(title=dict(text="Número de Visitas")),font=dict(size=16))
    #VISITAS MOVIL
    eess_top_visitas_movil = gestantes_join_df.groupby(['Establecimiento de Salud'])[['Total de VD presencial Válidas MOVIL']].sum().sort_values(["Total de VD presencial Válidas MOVIL"]).reset_index()
    eess_top_visitas_movil = eess_top_visitas_movil.rename(columns=  {"Total de VD presencial Válidas MOVIL":"Visitas"})
    fig_eess_top_visitas_movil = px.bar(eess_top_visitas_movil, x="Visitas", y="Establecimiento de Salud",
                                    text="Visitas", orientation='h',title = "Gestantes con VD MOVIL por Establecimiento de Salud")
    fig_eess_top_visitas_movil.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_top_visitas_movil.update_layout(xaxis=dict(title=dict(text="Número de Visitas")),font=dict(size=16))

    #VISITAS WEB
    eess_top_visitas_web = gestantes_join_df.groupby(['Establecimiento de Salud'])[['Total de VD presencial Válidas WEB']].sum().sort_values(["Total de VD presencial Válidas WEB"]).reset_index()
    eess_top_visitas_web = eess_top_visitas_web.rename(columns=  {"Total de VD presencial Válidas WEB":"Visitas"})
    fig_eess_top_visitas_web = px.bar(eess_top_visitas_web, x="Visitas", y="Establecimiento de Salud",
                                    text="Visitas", orientation='h',title = "Gestantes con VD WEB por Establecimiento de Salud")
    fig_eess_top_visitas_web.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_top_visitas_web.update_layout(xaxis=dict(title=dict(text="Número de Visitas")),font=dict(size=16))
    #DOCUMENTO DE IDENTIDAD
    tipodoc_ges_df = gestantes_join_df.groupby(['Tipo de Documento'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
    tipodoc_ges_df = tipodoc_ges_df.rename(columns=  {"Número de Documento":"Gestantes"})

    fig_tipodoct_ges = px.pie(tipodoc_ges_df, values='Gestantes', names='Tipo de Documento',
                        title='Tipo de Documento de Gestantes')
    fig_tipodoct_ges.update_traces(textposition='inside', textinfo='percent+label+value',insidetextfont=dict(size=18))
    # SI ES PUERPERA
    estado_puerpera_df = gestantes_join_df.groupby(['ESTADO_NACIMIENTO'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
    estado_puerpera_df = estado_puerpera_df.rename(columns=  {"Número de Documento":"Gestantes"})
    fig_puerpera_ges = px.pie(estado_puerpera_df, values='Gestantes', names='ESTADO_NACIMIENTO',
                        title='Estado Puerperas')
    fig_puerpera_ges.update_traces(textposition='inside', textinfo='percent+label+value',insidetextfont=dict(size=18))
    #ETAPA DE VSITA GESTANTE
    etapa_vd_gestante = gestantes_join_df.groupby(['Etapa'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
    etapa_vd_gestante = etapa_vd_gestante.rename(columns=  {"Número de Documento":"Gestantes","Etapa":"Etapa Visita"})
    fig_etapa_vd = px.pie(etapa_vd_gestante, values='Gestantes', names='Etapa Visita',
                        title='Estado de Visitas de Gestantes')
    fig_etapa_vd.update_traces(textposition='inside', textinfo='percent+label+value',insidetextfont=dict(size=18))
    #contrastando
    etapavd_estado_df = gestantes_join_df.groupby(['Etapa','ESTADO_NACIMIENTO'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
    
    fig_etapavd_estado_df = px.bar(etapavd_estado_df, x="Etapa", y="Número de Documento",color = "ESTADO_NACIMIENTO",
                                    text="Número de Documento", orientation='v',title = "Número de Puerperas por Etapa de Visita Gestante")
    fig_etapavd_estado_df.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_etapavd_estado_df.update_layout(xaxis=dict(title=dict(text="Etapa de Visitas")),yaxis=dict(title=dict(text="Número de Gestantes")),font=dict(size=16))

    columnas_add = st.columns(2)
    with columnas_add[0]:
        tab1_carga, tab2_carga ,tab_vdmovil,tab_vdweb= st.tabs(["Cargados", "Visitas Totales","Visitas MOVIL","Visitas WEB"])
        with tab1_carga:
            st.plotly_chart(fig_eess_count)
        with tab2_carga:
            st.plotly_chart(fig_eess_top_visitas)
        with tab_vdmovil:
            st.plotly_chart(fig_eess_top_visitas_movil)
        with tab_vdweb:
            st.plotly_chart(fig_eess_top_visitas_web)
    with columnas_add[1]:
        st.plotly_chart(fig_etapavd_estado_df)

    columnas_two= st.columns(3)
    with columnas_two[0]:
        st.plotly_chart(fig_tipodoct_ges)
    with columnas_two[1]:
        st.plotly_chart(fig_puerpera_ges)
    with columnas_two[2]:
        st.plotly_chart(fig_etapa_vd)

    st.warning(f'Número de Puerperas {num_puerperas}', icon="⚠️")
    #df.to_parquet('.\\data\\carga_nino.parquet', engine='pyarrow', index=False)
    """
    CORTE CADA PERIODO CERRADO DE EVALIACION DEL MES
    gestantes_join_df.to_parquet(".\\data\\1.3\\indicador_gestantes_enero.parquet")
    """
    with st.expander("Descargas"):
        st.download_button(
                label="Descargar Reporte Gestantes",
                data=convert_excel_df(gestantes_join_df),
                file_name=f"gestantes_reporte_{select_mes}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )













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
        #l.ye
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