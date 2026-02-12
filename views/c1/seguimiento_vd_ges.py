import streamlit as st
import pandas as pd
import os
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_gestantes,fetch_padron,fetch_carga_gestantes
from utils.helpers import *
from datetime import datetime
from utils.functions_data import gestantes_unicas_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def gestantes_status_vd():
        styles(2)
        fecha_actual = datetime.now()
        vd_df = fetch_vd_gestantes()
        vd_df["Año"] = vd_df["Año"].astype(str)
        carga_df = fetch_carga_gestantes()
        carga_df["Mes"] = carga_df["Mes"].astype(int)
        carga_df["Establecimiento de Salud"] = carga_df["Establecimiento de Salud"].fillna("Sin Asignar")

        padron_df = fetch_padron()
        
        
        eess = list(carga_df["Establecimiento de Salud"].unique())
        #MESES = ["Ene","Feb","Mar","Abr","May","Jun"]
        list_mes = [mes_short(x) for x in sorted(list(carga_df["Mes"].unique()))]
        columns_row1 = st.columns([3,2,2,4])
        columns_row1[0].title("Visitas a Gestantes")
        with columns_row1[1]:
            select_year  = st.selectbox("Año:", ["2026"], key="select1")
            
        with columns_row1[2]:
            select_mes  = st.selectbox("Mes:", ["Feb"], key="select2",index=0)
        with columns_row1[3]:
            select_eess  = st.multiselect("Establecimiento de Salud:", eess, key="select3",placeholder="Seleccione EESS")
            
            if len(select_eess)> 0:    
                select_eess_recorted = [s[11:] for s in select_eess]
                
                carga_df = carga_df[carga_df["Establecimiento de Salud"].isin(select_eess)]
                vd_df = vd_df[vd_df["Establecimiento de Salud"].isin(select_eess_recorted)]

    #try:
        carga_filt_df = carga_df[(carga_df['Año']==str(select_year))&(carga_df['Mes']==mestext_short(select_mes))]
        actvd_filt_df_last = vd_df[(vd_df['Año']==str(select_year))&(vd_df['Mes']==select_mes)]  
        archivos_parquet = [f for f in os.listdir(f'./data/puerperas/{select_mes}') if f.endswith(".parquet")]
        #################REPORTE DE ACTIVIDAD GESTANTES########################
        
        vd_movil_df = actvd_filt_df_last[actvd_filt_df_last["Dispositivo Intervención"]=="MOVIL"]
        vd_web_df = actvd_filt_df_last[actvd_filt_df_last["Dispositivo Intervención"]=="WEB"]

        #########################################################
        
        #totales
        num_carga = carga_filt_df.shape[0]
        num_visitas_programadas = carga_filt_df["Total de visitas completas para la edad"].sum()
        num_visitas = actvd_filt_df_last.shape[0]
        
        gestantes_unicas_vd = gestantes_unicas_visitados(actvd_filt_df_last,'Número de Documento',"ALL GESTANTE W DUPLICADOS")
        num_gestantes_vd = gestantes_unicas_vd.shape[0]
        num_vd_movil = vd_movil_df.shape[0]
        
        #metricas cards
        metric_col = st.columns(6)
        metric_col[0].metric("Gestantes Cargadas",num_carga,f"Con Visita {num_gestantes_vd}({num_carga-num_gestantes_vd})",border=True)
        metric_col[1].metric("Total de Visitas",num_visitas,f"VD Programadas: {num_visitas_programadas}",border=True)
        #metric_col[2].metric("Visitas Movil",num_vd_movil,"-",border=True)#,f"Visitas Válidas: {num_visitas_validas}"
        gestantes_unicas_vd.columns = ["Doc_gestante","Actor Social Ultimo Mes","Etapa","Número Visitas"]
        gestantes_unicas_vd = gestantes_unicas_vd[["Doc_gestante","Etapa","Número Visitas"]]
        
        #try:
        #    puerperas_df=pd.read_parquet(f'./data/puerperas/puerperas_verificadas_{select_mes}.parquet', engine='pyarrow')
        #    puerperas_df = puerperas_df[['Número de Documento','FECHA DE NACIMIENTO','EDAD_MESES']]
        #    gest_dff = pd.merge(carga_filt_df, puerperas_df, left_on='Número de Documento', right_on='Número de Documento', how='left')
        #except:
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
        
        num_puerperas = (gest_dff["FECHA DE NACIMIENTO"].notna()).sum()
        if len(archivos_parquet)>0:
            puerperas_add_df = pd.concat([pd.read_parquet(os.path.join(f'./data/puerperas/{select_mes}', archivo)) for archivo in archivos_parquet], ignore_index=True)
            #puerperas_add_df = puerperas_add_df.rename(columns={'FECHA DE NACIMIENTO': 'ESTADO_NACIMIENTO'})
            #st.write(puerperas_add_df.shape)
            #st.dataframe(puerperas_add_df)
            #gest_dff['EDAD_MESES'] = gest_dff['Número de Documento'].map(puerperas_add_df.set_index('Número de Documento')['EDAD_MESES'])
            gest_dff['EDAD_MESES'] = gest_dff.apply(
                lambda row: puerperas_add_df.loc[puerperas_add_df['Número de Documento'] == row['Número de Documento'], 'EDAD_MESES'].values[0] 
                if row['Número de Documento'] in puerperas_add_df['Número de Documento'].values else row['EDAD_MESES'], axis=1
            )
            gest_dff['FECHA DE NACIMIENTO'] = gest_dff.apply(
                lambda row: puerperas_add_df.loc[puerperas_add_df['Número de Documento'] == row['Número de Documento'], 'FECHA DE NACIMIENTO'].values[0] 
                if row['Número de Documento'] in puerperas_add_df['Número de Documento'].values else row['FECHA DE NACIMIENTO'], axis=1
            )
            #gest_dff['ESTADO_NACIMIENTO'] = gest_dff['Número de Documento'].map(puerperas_add_df.set_index('Número de Documento')['FECHA DE NACIMIENTO'])
        try:
            num_puerperas_ext = (puerperas_add_df["FECHA DE NACIMIENTO"].notna()).sum()
        except:
            num_puerperas_ext = 0
        gest_dff['ESTADO_NACIMIENTO'] = gest_dff['FECHA DE NACIMIENTO'].apply(
            lambda fecha: 'GESTANTE' if pd.isna(fecha) 
            else 'PUERPERA'
        )
        gest_dff = gest_dff.rename(columns={"FECHA DE NACIMIENTO":"Fecha Nacimiento Hijo","EDAD_MESES":"Edad en Meses Hijo"})
        gestantes_join_df = pd.merge(gest_dff, gestantes_unicas_vd, left_on='Número de Documento', right_on='Doc_gestante', how='left')
        gestantes_join_df["Etapa"] = gestantes_join_df["Etapa"].fillna("No Visitadas")
        
        vd_gest_completa_df = gestantes_join_df[(gestantes_join_df["Etapa"].isin(["Visita Domiciliaria (Adolescente)","Visita Domiciliaria (Adulta)"]))]
        #st.dataframe(vd_gest_completa_df)
        
        vd_completa_gestante_df = gestantes_join_df[gestantes_join_df["Estado Gestante"]=="Visita Completa"]

        con_visita_cel = gestantes_join_df[(gestantes_join_df["Celular de la Madre"].notna())]
        #num_con_visita_cel = con_visita_cel.shape[0]
        percent_reg_tel = round((con_visita_cel.shape[0]/num_carga)*100,2)

        num_ges_result = vd_completa_gestante_df.shape[0]
        #total_visitas_validas_movil = vd_completa_gestante_df["Total de VD presencial Válidas MOVIL"].sum()
        #percent_vd_completas_movil = round((total_visitas_validas_movil/num_vd_movil)*100,2)
        percent_vd_movil_validate = round((num_vd_movil/num_visitas_programadas)*100,2)
        total_meta_vd = round(num_visitas_programadas*0.75)
        total_faltante_vd_meta = total_meta_vd-num_vd_movil

        percent_total_vd_12 = round((num_ges_result/(num_carga))*100,2)


        metric_col[2].metric("Visitas Movil",num_vd_movil,f"Web: {num_visitas-num_vd_movil}",border=True)
        #metric_col[3].metric("Visitas Completas - Movil",total_visitas_validas_movil,f"Meta (75%): {total_meta_vd}",border=True)
        metric_col[3].metric("% VD Georreferenciadas",f"{percent_vd_movil_validate}%",f"VD Faltantes {total_faltante_vd_meta}",border=True)#
        metric_col[4].metric("% Registros Telefonicos",f"{percent_reg_tel}%",f"-",border=True)
        metric_col[5].metric("% Gestantes Oportunos y Completos",f"{percent_total_vd_12}%",f"Positivos:{vd_gest_completa_df.shape[0]}",border=True)#,f"Positivos:{num_ninos_result} Excluidos:{num_excluyen_childs}"
        

        
        #CARGA GESTANTES
        eess_top_cargados = gestantes_join_df.groupby(['Establecimiento de Salud'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
        eess_top_cargados = eess_top_cargados.rename(columns=  {"Número de Documento":"Registros"})
        fig_eess_count = px.bar(eess_top_cargados, x="Registros", y="Establecimiento de Salud",
                                        text="Registros", orientation='h',title = "Gestantes Asignadas por Establecimiento de Salud")
        fig_eess_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_count.update_layout(xaxis=dict(title=dict(text="Número de Gestantes Cargadas")),font=dict(size=16))
        
        #############################################################################################################
        #VISITAS GESTANTES
        eess_top_visitas = actvd_filt_df_last.groupby(['Establecimiento de Salud'])[['UBIGEO']].count().sort_values(["UBIGEO"]).reset_index()
        eess_top_visitas = eess_top_visitas.rename(columns=  {"UBIGEO":"Visitas"})
        fig_eess_top_visitas = px.bar(eess_top_visitas, x="Visitas", y="Establecimiento de Salud",
                                        text="Visitas", orientation='h',title = "Gestantes Visitadas por Establecimiento de Salud")
        fig_eess_top_visitas.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_top_visitas.update_layout(xaxis=dict(title=dict(text="Número de Visitas")),font=dict(size=16))
        #VISITAS MOVIL
        
        eess_top_visitas_movil = vd_movil_df.groupby(['Establecimiento de Salud'])[['UBIGEO']].count().sort_values(["UBIGEO"]).reset_index()
        eess_top_visitas_movil = eess_top_visitas_movil.rename(columns=  {"UBIGEO":"Visitas"})
        
        fig_eess_top_visitas_movil = px.bar(eess_top_visitas_movil, x="Visitas", y="Establecimiento de Salud",
                                        text="Visitas", orientation='h',title = "Gestantes con VD MOVIL por Establecimiento de Salud")
        fig_eess_top_visitas_movil.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_top_visitas_movil.update_layout(xaxis=dict(title=dict(text="Número de Visitas")),font=dict(size=16))

        #VISITAS WEB
        eess_top_visitas_web = vd_web_df.groupby(['Establecimiento de Salud'])[['UBIGEO']].count().sort_values(["UBIGEO"]).reset_index()
        eess_top_visitas_web = eess_top_visitas_web.rename(columns=  {"UBIGEO":"Visitas"})
        
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

        
    
        

        

        #########################tabla
        #st.write(gestantes_join_df.columns)
        #carga
        
        
        gestantes_carga_df = gestantes_join_df.groupby(['Establecimiento de Salud'])[['Número de Documento']].count().sort_values("Número de Documento",ascending=False).reset_index()
        gestantes_carga_df = gestantes_carga_df.rename(columns=  {"Número de Documento":"Gestantes Programadas"})
            
            #visitas programadas
        vd_prog_df = gestantes_join_df.groupby(['Establecimiento de Salud'])[['Total de visitas completas para la edad']].sum().reset_index()
        vd_prog_df = vd_prog_df.rename(columns=  {"Total de visitas completas para la edad":"Visitas Programadas"})
        gestantes_tabla_df = pd.merge(gestantes_carga_df,vd_prog_df , left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')
        gestantes_tabla_df['Establecimiento de Salud'] = gestantes_tabla_df['Establecimiento de Salud'].str[11:]
        
        
            
        actvd_last_geo_df = actvd_filt_df_last[actvd_filt_df_last["Dispositivo Intervención"]=="MOVIL"]
        #vd_geo_dff = actvd_last_geo_df.groupby(["Establecimiento de Salud","Número de Documento","Etapa"])[["Estado Intervención"]].count().sort_values("Estado Intervención",ascending=False).reset_index()
        #vd_geo_dff['Etapa'] = vd_geo_dff['Etapa'].replace({'Visita Domiciliaria (Adulta)': 'Visita Domiciliaria','Visita Domiciliaria (Adolescente)': 'Visita Domiciliaria'})
        vd_geo_dff = actvd_last_geo_df.groupby(["Establecimiento de Salud"])[["Estado Intervención"]].count().sort_values("Estado Intervención",ascending=False).reset_index()
        vd_geo_dff.columns = ["Establecimiento de Salud","Visitas Realizadas GEO"]
        gestantes_tabla_df = pd.merge(gestantes_tabla_df,vd_geo_dff , left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')
        gestantes_tabla_df["Visitas Realizadas GEO"] = gestantes_tabla_df["Visitas Realizadas GEO"].fillna(0)
            
            #gestantes_tabla_df["Visitas Realizadas GEO"] = gestantes_tabla_df["Visita Domiciliaria"]+gestantes_tabla_df["No Encontrado"]
        #st.dataframe(gestantes_tabla_df)    

        try:
            actvd_last_web_df = actvd_filt_df_last[actvd_filt_df_last["Dispositivo Intervención"]=="WEB"]
            #vd_web_dff = actvd_last_web_df.groupby(["Establecimiento de Salud","Número de Documento","Etapa"])[["Estado Intervención"]].count().sort_values("Estado Intervención",ascending=False).reset_index()
            #vd_web_dff['Etapa'] = vd_web_dff['Etapa'].replace({'Visita Domiciliaria (Adulta)': 'Visita Domiciliaria','Visita Domiciliaria (Adolescente)': 'Visita Domiciliaria'})
            vd_web_dff = actvd_last_web_df.groupby(["Establecimiento de Salud"])[["Estado Intervención"]].count().sort_values("Estado Intervención",ascending=False).reset_index()
            vd_web_dff.columns = ["Establecimiento de Salud","Visitas Realizadas WEB"]
            gestantes_tabla_df = pd.merge(gestantes_tabla_df,vd_web_dff , left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')
            gestantes_tabla_df["Visitas Realizadas WEB"] = gestantes_tabla_df["Visitas Realizadas WEB"].fillna(0)
            gestantes_tabla_df["Visitas Realizadas"] = gestantes_tabla_df["Visitas Realizadas GEO"]+gestantes_tabla_df["Visitas Realizadas WEB"]
            total_row_2 = pd.DataFrame({
                    "Establecimiento de Salud": ["TOTAL"],  # Nombre de la fila
                    "Gestantes Programadas":gestantes_tabla_df["Gestantes Programadas"].sum(),
                    "Visitas Programadas":gestantes_tabla_df["Visitas Programadas"].sum(),
                    "Visitas Realizadas GEO":gestantes_tabla_df["Visitas Realizadas GEO"].sum(),
                    "Visitas Realizadas WEB":gestantes_tabla_df["Visitas Realizadas WEB"].sum(),
                    "Visitas Realizadas":gestantes_tabla_df["Visitas Realizadas"].sum(),
                    #"Gestantes Encontradas":gestantes_tabla_df["Gestantes Encontradas"].sum(),
                    #"Visitas Realizadas GEO":gestantes_tabla_df["Visitas Realizadas GEO"].sum(),

            })
        except:
            gestantes_tabla_df["Visitas Realizadas"] = gestantes_tabla_df["Visitas Realizadas GEO"]
            total_row_2 = pd.DataFrame({
                    "Establecimiento de Salud": ["TOTAL"],  # Nombre de la fila
                    "Gestantes Programadas":gestantes_tabla_df["Gestantes Programadas"].sum(),
                    "Visitas Programadas":gestantes_tabla_df["Visitas Programadas"].sum(),
                    "Visitas Realizadas GEO":gestantes_tabla_df["Visitas Realizadas GEO"].sum(),
                    "Visitas Realizadas":gestantes_tabla_df["Visitas Realizadas"].sum(),

                })
           
        gestantes_tabla_df = pd.concat([gestantes_tabla_df, total_row_2], ignore_index=True)
            
            
        gestantes_tabla_df = gestantes_tabla_df.fillna(0)
        gestantes_tabla_df["% Actual GEO"] = round((gestantes_tabla_df["Visitas Realizadas GEO"] / gestantes_tabla_df["Visitas Programadas"])*100,1)
        gestantes_tabla_df['% Actual GEO'] = gestantes_tabla_df['% Actual GEO'].astype(str)
        gestantes_tabla_df['% Actual GEO'] = gestantes_tabla_df['% Actual GEO']+"%" 
            #st.dataframe(gestantes_tabla_df)
            
            
        gb = GridOptionsBuilder.from_dataframe(gestantes_tabla_df)
        gb.configure_default_column(cellStyle={'fontSize': '21px'}) 
        gb.configure_column("Establecimiento de Salud", width=350)
        grid_options = gb.build()
            
            
        grid_response = AgGrid(gestantes_tabla_df, # Dataframe a mostrar
                            gridOptions=grid_options,
                            enable_enterprise_modules=False,
                                    #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                            update_mode='MODEL_CHANGED',
                            fit_columns_on_grid_load=True,
                                
        )
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
            tab_bar, tab_doc ,tab_estado,tab_etapa= st.tabs(["Distribución", "Tipo Documento","Estado","Etapa"])
            with tab_bar:
                st.plotly_chart(fig_etapavd_estado_df,key="eess_count")
            with tab_doc:
                st.plotly_chart(fig_tipodoct_ges,key="tipodoct_ges")
            with tab_estado:
                st.plotly_chart(fig_puerpera_ges,key="puerpera_ges")
            with tab_etapa:
                st.plotly_chart(fig_etapa_vd,key="etapa_vd")
        #df.to_parquet('.\\data\\carga_nino.parquet', engine='pyarrow', index=False)
        
        #CORTE CADA PERIODO CERRADO DE EVALIACION DEL MES
        #gestantes_join_df.to_parquet(".\\data\\1.3\\indicador_gestantes_febrero.parquet")
        st.warning(f'Número de Puerperas Trujillo: {num_puerperas}', icon="⚠️")#- Otro distrito: No definido
        with st.expander("Descargas"):
            st.download_button(
                    label="Descargar Reporte Gestantes",
                    data=convert_excel_df(gestantes_join_df),
                    file_name=f"gestantes_reporte_{select_mes}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            st.download_button(
                    label="Descargar GEOS",
                    data=convert_excel_df(gestantes_tabla_df),
                    file_name=f"gestantes_GEO_{select_mes}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            