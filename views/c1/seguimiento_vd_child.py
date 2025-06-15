import streamlit as st
import pandas as pd
import plotly.express as px
from utils.cache_handler import fetch_vd_childs, fetch_carga_childs, fetch_padron
from utils.functions_data import *
from utils.charts import *
from utils.helpers import *
from styles import styles
from datetime import datetime
from constans import *
from st_aggrid import AgGrid, GridOptionsBuilder,JsCode



def visitas_ninos_dashboard():
        
        styles(2)
        
        actvd_df = fetch_vd_childs()
        carga_df = fetch_carga_childs()
        padron_df = fetch_padron()
        datos_ninos_df = pd.read_parquet('datos_niños.parquet', engine='pyarrow')
        fecha_update = str(carga_df["update"].unique()[0])[:-7]
        fecha_actual = str(datetime.now().strftime("%Y-%m-%d %H:%M"))

        #fecha_update = dt.strftime("%Y-%m-%d-%H-%M")
        list_mes = [mes_short(x) for x in sorted(list(carga_df["Mes"].unique()))]
        
        col_head1, col_head2, col_head3, col_head4 = st.columns([3,4,2,2])
        with col_head1:
            st.title("Visitas a Niños")
        with col_head2:
            st.subheader(f"Actualizado: {fecha_update}", divider=True)
        with col_head3:
            select_year  = st.selectbox("Año:", ["2025"], key="select1")
            
        with col_head4:
            select_mes  = st.selectbox("Mes:",list_mes , key="select2",index=len(list_mes) - 1)
        try:
        
            datos_ninos_df = datos_ninos_df[datos_ninos_df["Periodo"]==f"{select_year}-{select_mes}"]
            datos_ninos_df = fix_data_childs(datos_ninos_df)
            #st.dataframe(datos_ninos_df)
            carga_filt_df = carga_df[(carga_df['Año']==int(select_year))&(carga_df['Mes']==int(mestext_short(select_mes)))]
            actvd_filt_df = actvd_df[(actvd_df['Año']==select_year)&(actvd_df['Mes']==select_mes)]
            niños_unicos_vd = childs_unicos_visitados(actvd_filt_df,'Número de Documento de Niño',"ALL CHILDS W DUPLICADOS")

            ## CALCULAR INDICADORES
            num_carga = carga_filt_df.shape[0]
            num_visitas_programadas = carga_filt_df["Total de visitas completas para la edad"].sum()
            num_visitas = carga_filt_df["Total de Intervenciones"].sum()
            num_child_vd = niños_unicos_vd.shape[0]
            num_vd_movil = carga_filt_df["Total de VD presencial Válidas MOVIL"].sum()
            porcentaje_child_visita = f"{round((num_child_vd/num_carga)*100,2)}%"

            ###
            

            ###
            actvd_filt_df = actvd_filt_df.groupby(['Número de Documento de Niño','Actores Sociales','Etapa'])[['Año']].count().reset_index()
            actvd_filt_df = actvd_filt_df.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
            actvd_filt_df = actvd_filt_df.drop_duplicates(subset='Número de Documento de Niño', keep='first')
            actvd_filt_df.columns = ["Doc_Ultimo_Mes","Actor Social Ultimo Mes","Estado_Visita_Ult","count"]
            actvd_filt_df = actvd_filt_df[["Doc_Ultimo_Mes","Actor Social Ultimo Mes","Estado_Visita_Ult"]]
            actvd_filt_df["Doc_Ultimo_Mes"] = actvd_filt_df["Doc_Ultimo_Mes"].astype(str)
            
            dataframe_pn = padron_df[COLUMNS_PADRON_C1_VD]  
            join_df = pd.merge(carga_filt_df, dataframe_pn, left_on='Número de Documento del niño', right_on='Documento', how='left')
            
            
            join_df['Prioridad'] = join_df['Tipo de Documento'].map(PRIORIDAD_TIPO_DOCUMENTO)
            
            ###
            new_col_estado_padron = join_df.groupby(['Número de Documento del niño'])[['Prioridad']].count().reset_index()
            new_col_estado_padron["Prioridad"] = new_col_estado_padron["Prioridad"].replace({0: "NO EXISTE REGISTRO",1: "REGISTRO UNICO", 2: "REGISTRO DUPLICADO", 3: "REGISTRO TRIPLICADO"})
            new_col_estado_padron.columns = ["Número de Documento del niño","Estado Padrón Nominal"]
            new_col_estado_padron["Número de Documento del niño"] = new_col_estado_padron["Número de Documento del niño"].astype(int).astype(str)

            ###
            join_df = join_df.sort_values(by=['Número de Documento del niño', 'Prioridad'])
            join_df = join_df.drop_duplicates(subset='Número de Documento del niño', keep='first')
            join_df = join_df.drop(columns=['Prioridad'])
            join_df['Número de Documento del niño'] = join_df['Número de Documento del niño'].astype(int).astype(str)
            join_df = pd.merge(join_df, new_col_estado_padron, left_on='Número de Documento del niño', right_on='Número de Documento del niño', how='left')
            ##
            dataframe_ = pd.merge(join_df, actvd_filt_df, left_on='Número de Documento del niño', right_on='Doc_Ultimo_Mes', how='left')
            
            #datos_ninos_df["Documento_c1"] = datos_ninos_df["Documento_c1"].astype(int).astype(str)
            
            #dataframe_["Número de Documento del niño"] = dataframe_["Número de Documento del niño"].astype(int).astype(str)
            
            del join_df

            dataframe_ = pd.merge(dataframe_, datos_ninos_df, left_on='Número de Documento del niño', right_on='Documento_c1', how='left')
            dataframe_['DATOS NIÑO PADRON'] = dataframe_['DATOS NIÑO PADRON'].fillna(dataframe_['Niño'])
            dataframe_['Tipo de Documento'] = dataframe_['Tipo de Documento'].fillna(dataframe_['Tipo de Documento del niño'])
            dataframe_['MENOR VISITADO'] = dataframe_['MENOR VISITADO'].fillna("SIN MODIFICACION EN EL PADRON")
            dataframe_['TIPO DE DOCUMENTO DE LA MADRE'] = dataframe_['TIPO DE DOCUMENTO DE LA MADRE'].fillna("MADRE DE GOLONDRINO")
            dataframe_['EESS NACIMIENTO'] = dataframe_['EESS NACIMIENTO'].fillna("No Especificado")
            dataframe_['EESS'] = dataframe_['EESS'].fillna("No Especificado")
            dataframe_['FRECUENCIA DE ATENCION'] = dataframe_['FRECUENCIA DE ATENCION'].fillna("No Especificado")
            dataframe_['EESS ADSCRIPCIÓN'] = dataframe_['EESS ADSCRIPCIÓN'].fillna("No Especificado")
            dataframe_['Tipo_file'] = dataframe_['Tipo_file'].fillna("En Otro Padrón Nominal")
            dataframe_['ENTIDAD'] = dataframe_['ENTIDAD'].fillna("En Otro Padrón Nominal")
            dataframe_['USUARIO QUE MODIFICA'] = dataframe_['USUARIO QUE MODIFICA'].fillna(f"Usuario no definido")
            
            del datos_ninos_df
            
            dataframe_ = dataframe_[COL_ORDER_VD_CHILD_C1]
            dataframe_.columns = COL_ORDER_VD_CHILD_C1_2
            dataframe_['Estado Visitas'] =  dataframe_.apply(lambda x: estado_visitas_completas(x['N° Visitas Completas'], x['Total de VD presenciales Válidas'],x['Estado Niño']),axis=1)
            dataframe_['Estado Niño'] = dataframe_['Estado Niño'].fillna(f"Sin Visita ({select_mes})")
            dataframe_['Edad'] = dataframe_['Fecha de Nacimiento'].apply(calcular_edad)

            dataframe_['Edad Dias'] = dataframe_['Fecha de Nacimiento'].apply(lambda x: (datetime.now() - x).days)
            #dataframe_['Edad 170-209 Dias'] = dataframe_['Edad Dias'].apply(lambda x: 1 if 170 <= x <= 209 else 0)
            primer_dia_mes = datetime(int(select_year), int(mestext_short(select_mes)), 1)
            if int(mestext_short(select_mes)) == 12:
                ultimo_dia_mes = datetime(int(select_year) + 1, 1, 1) - pd.Timedelta(days=1)
            else:
                ultimo_dia_mes = datetime(int(select_year), int(mestext_short(select_mes)) + 1, 1) - pd.Timedelta(days=1)

            dataframe_['Edad en días (primer día del mes)'] = dataframe_['Fecha de Nacimiento'].apply(lambda x: (primer_dia_mes - x).days)
            dataframe_['Edad en días (último día del mes)'] = dataframe_['Fecha de Nacimiento'].apply(lambda x: (ultimo_dia_mes - x).days)

            dataframe_['Niños 170-209 días en mes'] = dataframe_.apply(
                lambda row: "SI" if (
                    (row['Edad en días (primer día del mes)'] <= 209 and row['Edad en días (último día del mes)'] >= 170)
                ) else "NO", axis=1
            )

            dataframe_['Niños 350-389 días en mes'] = dataframe_.apply(
                lambda row: "SI" if (
                    (row['Edad en días (primer día del mes)'] <= 389 and row['Edad en días (último día del mes)'] >= 350)
                ) else "NO", axis=1
            )
            metric_col = st.columns(7)
            metric_col[0].metric("Niños Cargados",num_carga,f"Con Visita {num_child_vd}({num_carga-num_child_vd})",border=True)
            metric_col[1].metric("Total de Visitas",num_visitas,f"VD Programadas: {num_visitas_programadas}",border=True)
            


            #########################################################
            vd_geo_percent_df = dataframe_[(dataframe_["Estado Visitas"]=="Visitas Completas")]#&(dataframe_["Celular Madre"]!=0)
            num_ninos_result = vd_geo_percent_df.shape[0]
            total_vd_movil_completas = vd_geo_percent_df["Total de VD presencial Válidas MOVIL"].sum()
            #total_meta_vd = round(num_visitas_validas*0.75)
            total_meta_vd = round(num_visitas_programadas*PORCENTAJE_GEOS_VD)
            #num_visitas_programadas
            total_faltante_vd_meta = total_meta_vd-total_vd_movil_completas
            percent_vd_movil_validate = safe_percent(total_vd_movil_completas, num_visitas_programadas)
            percent_vd_completas_movil = safe_percent(total_vd_movil_completas, num_vd_movil)
            
            ###
            fuera_padron_df = dataframe_[(dataframe_["Tipo Registro Padrón Nominal"]=="En Otro Padrón Nominal")]
            num_excluyen_childs = fuera_padron_df.shape[0]

            #con_visita_cel = dataframe_[(dataframe_["Total de Intervenciones"]!=0)]
            #num_con_visita_cel = con_visita_cel.shape[0]
            con_celular = (dataframe_["Celular Madre"]!=0).sum()
            percent_reg_tel = safe_percent(con_celular, num_carga)
            percent_total_vd_12 = safe_percent(num_ninos_result, num_carga)
            ########################################################
            metric_col[2].metric("Visitas Movil",num_vd_movil,f"VD Completas:{total_vd_movil_completas}({percent_vd_completas_movil}%)",border=True)
            metric_col[3].metric("Visitas Completas - Movil",total_vd_movil_completas,f"Meta (64%): {total_meta_vd}",border=True)
            metric_col[4].metric("% VD Georreferenciadas",f"{percent_vd_movil_validate}%",f"VD Faltantes {total_faltante_vd_meta}",border=True)
            metric_col[5].metric("% Registros Telefonicos",f"{percent_reg_tel}%",f"Sin celular : {num_carga-con_celular}",border=True)
            metric_col[6].metric("% Niños Oportunos y Completos",f"{percent_total_vd_12}%",f"Positivos:{num_ninos_result}",border=True)
            
            #########################################################################################################################
            dataframe_efec = dataframe_[dataframe_["Estado Niño"].isin([
                "Visita Domiciliaria (6 a 12 Meses)", "Visita Domiciliaria (1 a 5 meses)"
            ])]

            # Groupby y renombrado
            child_programados_df = dataframe_.groupby("Establecimiento de Salud")["N° Visitas Completas"].count().reset_index(name="Niños Programados")
            vd_programadas_df = dataframe_.groupby("Establecimiento de Salud")["N° Visitas Completas"].sum().reset_index(name="Visitas Programadas")
            childs_encontrados_df = dataframe_efec.groupby("Establecimiento de Salud")["Estado Niño"].count().reset_index(name="Niños Encontrados")
            vd_movil_df = dataframe_efec.groupby("Establecimiento de Salud")["Total de VD presencial Válidas MOVIL"].sum().reset_index(name="Visitas Realizadas MOVIL GEO")

            # Merge de todos los datos
            dfs = [child_programados_df, vd_programadas_df, childs_encontrados_df, vd_movil_df]
            from functools import reduce
            proyectado_dff = reduce(lambda left, right: pd.merge(left, right, on="Establecimiento de Salud", how="left"), dfs)

            # Rellenar nulos
            proyectado_dff[["Niños Encontrados", "Visitas Realizadas MOVIL GEO"]] = proyectado_dff[["Niños Encontrados", "Visitas Realizadas MOVIL GEO"]].fillna(0)

            # Cálculos vectorizados
            proyectado_dff["Valla Visitas GEO 64%"] = (proyectado_dff["Visitas Programadas"] * PORCENTAJE_GEOS_VD).round()
            proyectado_dff["Visitas Faltantes Valla GEO"] = proyectado_dff["Valla Visitas GEO 64%"] - proyectado_dff["Visitas Realizadas MOVIL GEO"]

            # Visitas proyectadas y tolerancias
            visitas_for_completar_df = dataframe_efec[dataframe_efec["Estado Visitas"] != "Visitas Completas"].copy()
            visitas_for_completar_df["Visitas GEO Proyectadas"] = visitas_for_completar_df["N° Visitas Completas"] - visitas_for_completar_df["Total de VD presenciales Válidas"]
            vd_completar_df = visitas_for_completar_df.groupby("Establecimiento de Salud")["Visitas GEO Proyectadas"].sum().reset_index()

            proyectado_dff = proyectado_dff.merge(vd_completar_df, on="Establecimiento de Salud", how="left")
            proyectado_dff["Visitas GEO Proyectadas"] = proyectado_dff["Visitas GEO Proyectadas"].fillna(0)
            #proyectado_dff["Tolerancia Visitas WEB"] = proyectado_dff["Visitas GEO Proyectadas"] - proyectado_dff["Visitas Faltantes Valla GEO"]
            #proyectado_dff["Tolerancia Niños WEB"] = (proyectado_dff["Tolerancia Visitas WEB"] / 3).round()

            # Fila de totales
            total_row = pd.DataFrame({
                "Establecimiento de Salud": ["TOTAL"],
                "Niños Programados": [proyectado_dff["Niños Programados"].sum()],
                "Visitas Programadas": [proyectado_dff["Visitas Programadas"].sum()],
                "Niños Encontrados": [proyectado_dff["Niños Encontrados"].sum()],
                "Visitas Realizadas MOVIL GEO": [proyectado_dff["Visitas Realizadas MOVIL GEO"].sum()],
                "Valla Visitas GEO 64%": [proyectado_dff["Valla Visitas GEO 64%"].sum()],
                "Visitas Faltantes Valla GEO": [proyectado_dff["Visitas Faltantes Valla GEO"].sum()],
                "Visitas GEO Proyectadas": [proyectado_dff["Visitas GEO Proyectadas"].sum()],
                #"Tolerancia Visitas WEB": [proyectado_dff["Tolerancia Visitas WEB"].sum()],
                #"Tolerancia Niños WEB": [proyectado_dff["Tolerancia Niños WEB"].sum()],
            })

            proyectado_dff = pd.concat([proyectado_dff, total_row], ignore_index=True)

            # Estado y porcentaje
            proyectado_dff['Estado'] = proyectado_dff.apply(
                lambda x: estado_proyectado(x['Visitas Faltantes Valla GEO'], x['Visitas GEO Proyectadas']), axis=1
            )
            proyectado_dff["% Actual GEO"] = ((proyectado_dff["Visitas Realizadas MOVIL GEO"] / proyectado_dff["Visitas Programadas"]) * 100).round(1).astype(str) + "%"

            # Selección y orden de columnas
            cols = [
                'Establecimiento de Salud', 'Niños Programados', 'Visitas Programadas',
                'Niños Encontrados', 'Visitas Realizadas MOVIL GEO', '% Actual GEO',
                'Valla Visitas GEO 64%', 'Visitas Faltantes Valla GEO', 'Visitas GEO Proyectadas',
                #'Tolerancia Visitas WEB', 'Tolerancia Niños WEB', 
                'Estado'
            ]
            proyectado_dff = proyectado_dff[cols]

            # Ordenar por 'Niños Programados', dejando TOTAL al final
            proyectado_dff_no_total = proyectado_dff[proyectado_dff["Establecimiento de Salud"] != "TOTAL"]
            total_row = proyectado_dff[proyectado_dff["Establecimiento de Salud"] == "TOTAL"]
            proyectado_dff_no_total = proyectado_dff_no_total.sort_values("Niños Programados", ascending=False)
            proyectado_dff = pd.concat([proyectado_dff_no_total, total_row], ignore_index=True)

            
            gb = GridOptionsBuilder.from_dataframe(proyectado_dff)
            gb.configure_default_column(cellStyle={'fontSize': '17px'}) 
            gb.configure_column("Establecimiento de Salud", width=380)
            # Formato condicional para la columna Estado
            
            grid_options = gb.build()
            #grid_options['getRowStyle'] = row_style

            grid_response = AgGrid(proyectado_dff, # Dataframe a mostrar
                                    gridOptions=grid_options,
                                    enable_enterprise_modules=False,
                                    #theme='balham',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                                    update_mode='MODEL_CHANGED',
                                    fit_columns_on_grid_load=True,
                                    height=370
                                
            )
            # Filtra duplicados de Celular Madre
            df_con_num_cel = dataframe_[dataframe_["Celular Madre"] != 0].copy()
            df_con_num_cel["Celular Madre"] = df_con_num_cel["Celular Madre"].astype(str)

            # Detecta duplicados de Número Doc Madre
            duplicados_num_doc_madre = df_con_num_cel["Número Doc Madre"].duplicated(keep=False)

            # Filtra duplicados de Celular Madre y excluye duplicados de Número Doc Madre
            cel_duplicados_df = df_con_num_cel[
                df_con_num_cel.duplicated(subset=["Celular Madre"], keep=False) &
                ~duplicados_num_doc_madre
            ]
            

            groupings = [
                # (df, x, y, title, text, orientation, color, barmode, xaxis_title, yaxis_title)
                (dataframe_.groupby(['Establecimiento de Salud'])[['Número de Documento']].count()
                    .rename(columns={"Número de Documento":"Registros"})
                    .sort_values("Registros", ascending=True).reset_index(),
                "Registros", "Establecimiento de Salud", "Niños Asignados por Establecimiento de Salud", "Registros", 'h', None, None, "Número de Niños Cargados", None),
                (dataframe_.groupby(['Establecimiento de Salud'])[['Total de VD presenciales Válidas']].sum()
                    .rename(columns={"Total de VD presenciales Válidas":"Visitas"})
                    .sort_values("Visitas", ascending=True).reset_index(),
                "Visitas", "Establecimiento de Salud", "Niños Visitados por Establecimiento de Salud", "Visitas", 'h', None, None, "Número de Visitas", None),
                (dataframe_.groupby(["Estado Niño"])[["Tipo Documento"]].count().rename(columns={"Tipo Documento":"Niños"}).reset_index(),
                "Niños", "Estado Niño", f"Estado de los Niños Cargados {select_mes}", "Niños", 'h', None, None, "Niños", None),
                (dataframe_.groupby(["Entidad Actualiza"])[["Tipo Documento"]].count().rename(columns={"Tipo Documento":"Niños"}).reset_index(),
                "Niños", "Entidad Actualiza", f"Niños C1 - Estado Actualizaciones Padrón Nominal {select_mes}", "Niños", 'h', None, None, "Niños", None),
                (dataframe_.groupby(["Estado Visitas"])[["Tipo Documento"]].count().rename(columns={"Tipo Documento":"Niños"}).reset_index(),
                "Niños", "Estado Visitas", f"Estado de las Visitas en {select_mes}", "Niños", 'h', None, None, "Niños", None),
                (dataframe_.groupby(['Establecimiento de Salud'])[['Total de VD presencial Válidas MOVIL']].sum()
                    .rename(columns={"Total de VD presencial Válidas MOVIL":"Visitas"})
                    .sort_values("Visitas", ascending=True).reset_index(),
                "Visitas", "Establecimiento de Salud", "Visitas Registradas por MOVIL", "Visitas", 'h', None, None, "Número de Visitas", None),
                (dataframe_.groupby(['Establecimiento de Salud'])[['Total de VD presencial Válidas WEB']].sum()
                    .rename(columns={"Total de VD presencial Válidas WEB":"Visitas"})
                    .sort_values("Visitas", ascending=True).reset_index(),
                "Visitas", "Establecimiento de Salud", "Visitas Registradas por WEB", "Visitas", 'h', None, None, "Número de Visitas", None),
            ]

            # Gráficos de barras
            figs = [plot_bar(*args) for args in groupings]

            # Gráficos especiales
            # Niños No Encontrados
            no_encontrados_df = dataframe_[dataframe_["Estado Niño"]=="No Encontrado"] \
                .groupby(["Establecimiento de Salud"])[["Estado Niño"]].count() \
                .rename(columns={"Estado Niño":"Registros"}).sort_values("Registros", ascending=True).reset_index()
            fig_eess_count_noencon = plot_bar(no_encontrados_df, "Registros", "Establecimiento de Salud", "Niños No Encontrados por Establecimiento de Salud", "Registros", 'h', None, None, "Número de Niños No Encontrados", None)

            # Niños Rechazados
            rechazado_df = dataframe_[dataframe_["Estado Niño"]=="Rechazado"] \
                .groupby(["Establecimiento de Salud"])[["Estado Niño"]].count() \
                .rename(columns={"Estado Niño":"Registros"}).sort_values("Registros", ascending=True).reset_index()
            fig_eess_count_rechazado = plot_bar(rechazado_df, "Registros", "Establecimiento de Salud", "Niños Rechazados por Establecimiento de Salud", "Registros", 'h', None, None, "Número de Niños Rechazados", None)

            # Niños sin Visita
            sinvd_dff = dataframe_[dataframe_["Estado Niño"]==f"Sin Visita ({select_mes})"]
            sinvd_df = sinvd_dff.groupby(["Establecimiento de Salud"])[["Estado Niño"]].count() \
                .rename(columns={"Estado Niño":"Niños"}).sort_values("Niños", ascending=True).reset_index()
            fig_eess_sinvd = plot_bar(sinvd_df, "Niños", "Establecimiento de Salud", "Niños sin Visita por Establecimiento", "Niños", 'h', None, None, "Número de Niños", None)

            # Niños Transito
            child_transito_df = dataframe_[dataframe_["Tipo Registro Padrón Nominal"]=="Activos Transito"] \
                .groupby(["Establecimiento de Salud"])[["Tipo Registro Padrón Nominal"]].count() \
                .rename(columns={"Tipo Registro Padrón Nominal":"Niños"}).sort_values("Niños", ascending=True).reset_index()
            fig_eess_transito = plot_bar(child_transito_df, "Niños", "Establecimiento de Salud", "Niños Transito por Establecimiento", "Niños", 'h', None, None, "Número de Niños", None)

            # Niños Otro Padrón
            child_deri_df = dataframe_[dataframe_["Tipo Registro Padrón Nominal"]=="En Otro Padrón Nominal"] \
                .groupby(["Establecimiento de Salud"])[["Tipo Registro Padrón Nominal"]].count() \
                .rename(columns={"Tipo Registro Padrón Nominal":"Niños"}).sort_values("Niños", ascending=True).reset_index()
            fig_eess_derivados = plot_bar(child_deri_df, "Niños", "Establecimiento de Salud", "Niños En otro Distrito Padrón por Establecimiento", "Niños", 'h', None, None, "Número de Niños", None)

            # Estado de Derivados y Transitos
            registro_padron_df = dataframe_[dataframe_["Tipo Registro Padrón Nominal"].isin(["Activos Transito","En Otro Padrón Nominal"])]
            registro_padron_group_df = registro_padron_df.groupby(["Estado Niño","Tipo Registro Padrón Nominal"])[["Número de Documento"]].count().rename(columns={"Número de Documento":"Niños"}).reset_index()
            fig_reg_padron = px.bar(registro_padron_group_df, x="Estado Niño", y="Niños", color="Tipo Registro Padrón Nominal",
                                    text="Niños", orientation='v', title="Niños Derivados y Transitos por Estado de Visita", barmode='group')
            fig_reg_padron.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
            fig_reg_padron.update_layout(xaxis=dict(title=dict(text="Estado de Visita de los Niños")), yaxis=dict(title=dict(text="Número de Niños")), font=dict(size=16))

            # Tipo de Seguro por Establecimiento
            tipo_seguro_df = dataframe_.groupby(["Establecimiento de Salud","Tipo de Seguro"])[["Número de Documento"]].count().rename(columns={"Número de Documento":"Niños"}).reset_index()
            fig_tipo_seguro = plot_bar(tipo_seguro_df, "Niños", "Establecimiento de Salud", "Tipo de Seguro por Establicimiento de salud", "Niños", 'h', "Tipo de Seguro", 'stack', "Número de Niños", "Establecimiento de Salud")

            # Tipo de Seguro general
            tipo_seguro_all_df = dataframe_.groupby(["Tipo de Seguro"])[["Número de Documento"]].count().rename(columns={"Número de Documento":"Niños"}).reset_index()
            fig_seguro_all = px.pie(tipo_seguro_all_df, values='Niños', names='Tipo de Seguro', title='Tipo de Seguro')
            fig_seguro_all.update_traces(textposition='inside', textinfo='percent+label+value', insidetextfont=dict(size=18))
            
            with st.expander("Charts"):
                col1, col2 = st.columns(2)
                with col1:
                    tab1, tab2, tab3, tab4,tab5 = st.tabs(["Asignados", "Visitados","Sin Visitas","Visitas Movil","Visitas Web"])
                    with tab1:
                        st.plotly_chart(figs[0], use_container_width=True)  # Niños Asignados
                    with tab2:
                        st.plotly_chart(figs[1], use_container_width=True) 
                    with tab3:
                        st.plotly_chart(fig_eess_sinvd, use_container_width=True)
                    with tab4:
                        st.plotly_chart(figs[5], use_container_width=True)
                    with tab5:
                        st.plotly_chart(figs[6], use_container_width=True)


                with col2:
                    tab1, tab2, tab3, tab4,tab5 = st.tabs(["Transitos/Derivados","Niños Otro Padrón","Niños Transito","Niños No Encontrados", "Niños Rechazados"])
                    with tab1:
                        st.plotly_chart(fig_reg_padron, use_container_width=True)
                    with tab2:
                        st.plotly_chart(fig_eess_derivados, use_container_width=True)
                    with tab3:
                        st.plotly_chart(fig_eess_transito, use_container_width=True)
                        
                    with tab4:
                        st.plotly_chart(fig_eess_count_rechazado, use_container_width=True)  # Niños Rechazados
                    with tab5:
                        st.plotly_chart(fig_eess_count_noencon, use_container_width=True)  # Niños No Encontrados
                
                col1_, col2_= st.columns(2)
                with col1_:
                    tab1_, tab2_, tab3_ = st.tabs(["Tipo de Etapa","Etapa por Visitas","Entidad Actualiza"])
                    with tab1_:
                        st.plotly_chart(figs[2], use_container_width=True)
                    with tab2_:
                        st.plotly_chart(figs[4], use_container_width=True)
                    with tab3_:
                        st.plotly_chart(figs[3], use_container_width=True)
                with col2_: 
                    st.plotly_chart(fig_seguro_all, use_container_width=True)
            #fecha_actual
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.download_button(
                        label="Descargar Reporte Completo",
                        icon=":material/download:",
                        data=convert_excel_df(dataframe_),
                        file_name=f"EstadoVisitas_{select_year}_{select_mes}_{fecha_actual}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            with col2:
                st.download_button( 
                        label="Descargar Reporte C1",
                        icon=":material/download:",
                        data=convert_excel_df(dataframe_[COLS_DATAFRAME_RESUMIDO_CHILS]),
                        file_name=f"EstadoVisitas_{select_year}_{select_mes}_{fecha_actual}_r.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            with col3:
                st.download_button(
                        label="Descargar Reporte Padron Nominal",
                        icon=":material/download:",
                        data=convert_excel_df(dataframe_[COLS_DATAFRAME_PADRON_CHILS]),
                        file_name=f"EstadoVisitas_{select_year}_{select_mes}_{fecha_actual}_r.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            with col4:
                st.download_button(
                        label="Descargar Reporte Duplicados",
                        icon=":material/download:",
                        data=convert_excel_df(cel_duplicados_df[COLS_DATAFRAME_DUPLICADOS_CHILDS]),
                        file_name=f"Duplicados_{select_year}_{select_mes}_{fecha_actual}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            
            
            
        
            
        except:
            st.warning("No existen datos para este periodo")

    
    
    



def estadisticas_dashboard():
    styles(2)
    c1_carga_df = fetch_carga_childs()
    #padron_df = fetch_padron()
    st.title("Indicador: Niños sin anemia")
    #jun_seg_nominal_df = c1_carga_df[(c1_carga_df["Mes"] == 6) & (c1_carga_df["Año"] == 2025)]
    #jun_seg_nominal_df = jun_seg_nominal_df[[
    #    "Establecimiento de Salud","Nombres del Actor Social","Tipo de Documento del niño","Número de Documento del niño","Fecha de Nacimiento","Rango de Edad","DNI de la madre","Celular de la madre",
    #    "Mes","Año"
    #]]
    all_c1_carga_df = c1_carga_df[(c1_carga_df["Año"] == 2025)]
    all_c1_carga_df["Mes_name"] = all_c1_carga_df["Mes"].apply(mes_short)
    all_c1_carga_df["Mes_name"] = all_c1_carga_df["Mes_name"] + "-"
    all_c1_carga_df = all_c1_carga_df.sort_values(by="Mes", ascending=True)
    all_c1_carga_df["Mes"] = all_c1_carga_df["Mes"].astype(str)
    all_c1_carga_df['Edad_Meses'] = all_c1_carga_df['Fecha de Nacimiento'].apply(lambda x: (datetime.now() - x).days / 30.44)
    all_c1_carga_df['Tiene_6_Meses'] = all_c1_carga_df['Edad_Meses'].apply(lambda x: 'Sí' if x >= 6 else 'No')
    total = all_c1_carga_df.groupby(["Número de Documento del niño"]).agg({"Mes": "sum","Mes_name": "sum"}).reset_index()
    
    all_c1_carga_df = all_c1_carga_df[all_c1_carga_df["Tiene_6_Meses"]=="Sí"]

    unique_childs25_df = all_c1_carga_df.groupby(["Número de Documento del niño"]).agg({"Mes": "sum","Mes_name": "sum"}).reset_index()
    unique_childs25_df.columns = ["Documento", "Periodos","Periodos_name"]
    unique_childs25_df["Periodos_name"] = unique_childs25_df["Periodos_name"].str[:-1] 
    unique_childs25_df['Es_Consecutivo'] = unique_childs25_df['Periodos'].apply(es_consecutivo)  
    unique_childs25_df = unique_childs25_df[["Documento","Periodos_name","Es_Consecutivo"]]
    unique_childs25_df.columns = ["Documento","Periodos","¿Es consecutivo?"]
    unique_childs25_df["Documento"] = unique_childs25_df["Documento"].astype(str)
    

    childs_total =total.shape[0]
    childs_consecutivos = (unique_childs25_df["¿Es consecutivo?"]=="Consecutivo").sum()
    #childs_no_consecutivos = (unique_childs25_df["¿Es consecutivo?"]=="No Consecutivo").sum()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Niños Cargados 2025", childs_total)
    with col2:
        st.metric("Total de Niños Consecutivos de 6 meses", childs_consecutivos)
    with col3:
        st.metric("Umbral Minimo 30%", round(childs_consecutivos*0.3,0))
    with col4:
        st.metric("Umbral Minimo 37%", round(childs_consecutivos*0.37,0))


    #st.dataframe(all_c1_carga_df)
    
    #padron_df = padron_df[
    #    [
    #        "Tipo_file","Tipo de Documento","Documento","DATOS NIÑO PADRON","DIRECCION PADRON","REFERENCIA DE DIRECCION","NUMERO DE DOCUMENTO  DE LA MADRE","DATOS MADRE PADRON","NUMERO DE CELULAR",
    #        "TIPO DE SEGURO","EESS NACIMIENTO","EESS","FRECUENCIA DE ATENCION"
    #    ]
    #]
    # dff = pd.merge(all_c1_carga_df,padron_df, left_on='Número de Documento del niño', right_on='Documento', how='left')
    #st.write(dff.shape)
    #st.dataframe(dff)
    #st.dataframe(dff)

