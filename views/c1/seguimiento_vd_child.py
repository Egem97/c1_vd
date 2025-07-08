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
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font, Alignment, Protection
from io import BytesIO



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
            
            #st.dataframe(datos_ninos_df)
            datos_ninos_df = datos_ninos_df[datos_ninos_df["Periodo"]==f"{select_year}-{select_mes}"]
            #st.write(f"{select_year}-{select_mes}")
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
          
            primer_dia_mes = datetime(int(select_year), int(mestext_short(select_mes)), 1)
            if int(mestext_short(select_mes)) == 12:
                ultimo_dia_mes = datetime(int(select_year) + 1, 1, 1) - pd.Timedelta(days=1)
            else:
                ultimo_dia_mes = datetime(int(select_year), int(mestext_short(select_mes)) + 1, 1) - pd.Timedelta(days=1)

            dataframe_['Edad en días (primer día del mes)'] = dataframe_['Fecha de Nacimiento'].apply(lambda x: (primer_dia_mes - x).days)
            dataframe_['Edad en días (último día del mes)'] = dataframe_['Fecha de Nacimiento'].apply(lambda x: (ultimo_dia_mes - x).days)


            dataframe_['Niños 120-149 días en mes'] = dataframe_.apply(
                lambda row: "SI" if (
                    (row['Edad en días (primer día del mes)'] <= 149 and row['Edad en días (último día del mes)'] >= 120)
                ) else "NO", axis=1
            )

            dataframe_['Niños 180-209 días en mes'] = dataframe_.apply(
                lambda row: "SI" if (
                    (row['Edad en días (primer día del mes)'] <= 209 and row['Edad en días (último día del mes)'] >= 180)
                ) else "NO", axis=1
            )

            dataframe_['Niños 270-299 días en mes'] = dataframe_.apply(
                lambda row: "SI" if (
                    (row['Edad en días (primer día del mes)'] <= 299 and row['Edad en días (último día del mes)'] >= 270)
                ) else "NO", axis=1
            )

            dataframe_['Niños 360-389 días en mes'] = dataframe_.apply(
                lambda row: "SI" if (
                    (row['Edad en días (primer día del mes)'] <= 389 and row['Edad en días (último día del mes)'] >= 360)
                ) else "NO", axis=1
            )
            metric_col = st.columns(7)
            metric_col[0].metric("Niños Cargados",num_carga,f"Con Visita {num_child_vd}({num_carga-num_child_vd})",border=True)
            metric_col[1].metric("Total de Visitas",num_visitas,f"VD Programadas: {num_visitas_programadas}",border=True)
            


            #########################################################
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Seguimiento Visitas Georreferenciadas","Seguimiento Niños que cumplen 120-149 días en el mes","Seguimiento Niños que cumplen 180-209 días en el mes","Seguimiento Niños que cumplen 270-299 días en el mes","Seguimiento Niños que cumplen 360-389 días en el mes"])
            with tab1:
                st.subheader("📱Seguimiento Visitas Georreferenciadas")
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
                gb.configure_column("Establecimiento de Salud", width=340)
                # Formato condicional para la columna Estado
                
                grid_options = gb.build()
                #grid_options['getRowStyle'] = row_style

                grid_response = AgGrid(proyectado_dff, # Dataframe a mostrar
                                        gridOptions=grid_options,
                                        enable_enterprise_modules=False,
                                        #theme='balham',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                                        update_mode='MODEL_CHANGED',
                                        fit_columns_on_grid_load=True,
                                        height=370,
                                        key="grid_geo"
                                    )
            with tab2:
                st.subheader("🍼 Seguimiento Niños que cumplen 120-149 días en el mes")
                soon4_dff = dataframe_[(dataframe_["Niños 120-149 días en mes"]=="SI")]
                soon4_dff["Estado Niño"] = soon4_dff["Estado Niño"].replace({"Visita Domiciliaria (6 a 12 Meses)":"Visita Domiciliaria","Visita Domiciliaria (1 a 5 meses)":"Visita Domiciliaria"})
                soon4_dff_group = soon4_dff.groupby(["Establecimiento de Salud"]).agg(
                    Niños_Programados=("Número de Documento", "count"),
                    Niños_Encontrados_Efectivos=("Estado Niño", lambda x: (x == "Visita Domiciliaria").sum()),
                    Niños_SEGURO_SIS=("Tipo de Seguro", lambda x: ((x != "ESSALUD") & (x != "PRIVADO")).sum()),
                    Niños_OTRO_SEGURO=("Tipo de Seguro", lambda x: ((x == "ESSALUD")|(x == "PRIVADO")).sum()),
                ).reset_index()
                soon4_dff_group = soon4_dff_group.sort_values("Niños_Programados", ascending=False)
                
                # Agregar fila de total
                total_row_4 = pd.DataFrame({
                    "Establecimiento de Salud": ["TOTAL"],
                    "Niños_Programados": [soon4_dff_group["Niños_Programados"].sum()],
                    "Niños_Encontrados_Efectivos": [soon4_dff_group["Niños_Encontrados_Efectivos"].sum()],
                    "Niños_SEGURO_SIS": [soon4_dff_group["Niños_SEGURO_SIS"].sum()],
                    "Niños_OTRO_SEGURO": [soon4_dff_group["Niños_OTRO_SEGURO"].sum()],
                })
                soon4_dff_group = pd.concat([soon4_dff_group, total_row_4], ignore_index=True)
                soon4_dff_group["% Niños Encontrados"] = (soon4_dff_group["Niños_Encontrados_Efectivos"]/soon4_dff_group["Niños_Programados"]*100).round(1).astype(str) + "%"
                
                soon4_dff_group = soon4_dff_group[["Establecimiento de Salud", "Niños_Programados", "Niños_Encontrados_Efectivos","% Niños Encontrados", "Niños_SEGURO_SIS", "Niños_OTRO_SEGURO"]]
                soon4_dff_group.columns = ["Establecimiento de Salud", "Niños Programados", "Niños Encontrados Efectivos","% Niños Encontrados", "Niños SEGURO SIS", "Niños OTRO SEGURO"]
                gb = GridOptionsBuilder.from_dataframe(soon4_dff_group)
                gb.configure_default_column(cellStyle={'fontSize': '17px'}) 
                #gb.configure_selection(selection_mode="single", use_checkbox=True)
                gb.configure_column("Establecimiento de Salud", width=350)
                
                grid_options = gb.build()
                
                grid_tab4 = AgGrid(soon4_dff_group,
                                        gridOptions=grid_options,
                                        enable_enterprise_modules=False,
                                        update_mode='MODEL_CHANGED',
                                        fit_columns_on_grid_load=True,
                                        height=340,
                                        allow_unsafe_jscode=True,
                                        key="grid_120_149"
                )
                

            with tab3:
                
                st.subheader("👩‍🍼 Seguimiento Niños que cumplen 180-209 días en el mes")
                #replace({0: "NO EXISTE REGISTRO",1: "REGISTRO UNICO", 2: "REGISTRO DUPLICADO", 3: "REGISTRO TRIPLICADO"})
                soon6_dff = dataframe_[(dataframe_["Niños 180-209 días en mes"]=="SI")]
                soon6_dff["Estado Niño"] = soon6_dff["Estado Niño"].replace({"Visita Domiciliaria (6 a 12 Meses)":"Visita Domiciliaria","Visita Domiciliaria (1 a 5 meses)":"Visita Domiciliaria"})
                soon6_dff_group = soon6_dff.groupby(["Establecimiento de Salud"]).agg(
                    Niños_Programados=("Número de Documento", "count"),
                    Niños_Encontrados_Efectivos=("Estado Niño", lambda x: (x == "Visita Domiciliaria").sum()),
                    Niños_SEGURO_SIS=("Tipo de Seguro", lambda x: ((x != "ESSALUD") & (x != "PRIVADO")).sum()),
                    Niños_OTRO_SEGURO=("Tipo de Seguro", lambda x: ((x == "ESSALUD")|(x == "PRIVADO")).sum()),
                ).reset_index()
                soon6_dff_group = soon6_dff_group.sort_values("Niños_Programados", ascending=False)
                
                #
                
                # Agregar fila de total
                total_row_6 = pd.DataFrame({
                    "Establecimiento de Salud": ["TOTAL"],
                    "Niños_Programados": [soon6_dff_group["Niños_Programados"].sum()],
                    "Niños_Encontrados_Efectivos": [soon6_dff_group["Niños_Encontrados_Efectivos"].sum()],
                    "Niños_SEGURO_SIS": [soon6_dff_group["Niños_SEGURO_SIS"].sum()],
                    "Niños_OTRO_SEGURO": [soon6_dff_group["Niños_OTRO_SEGURO"].sum()],

                })
                soon6_dff_group = pd.concat([soon6_dff_group, total_row_6], ignore_index=True)
                soon6_dff_group["% Niños Encontrados"] = (soon6_dff_group["Niños_Encontrados_Efectivos"]/soon6_dff_group["Niños_Programados"]*100).round(1).astype(str) + "%"
                
                soon6_dff_group = soon6_dff_group[["Establecimiento de Salud", "Niños_Programados", "Niños_Encontrados_Efectivos","% Niños Encontrados", "Niños_SEGURO_SIS", "Niños_OTRO_SEGURO"]]
                soon6_dff_group.columns = ["Establecimiento de Salud", "Niños Programados", "Niños Encontrados Efectivos","% Niños Encontrados", "Niños SEGURO SIS", "Niños OTRO SEGURO"]
                gb = GridOptionsBuilder.from_dataframe(soon6_dff_group)
                gb.configure_default_column(cellStyle={'fontSize': '17px'}) 
                #gb.configure_selection(selection_mode="single", use_checkbox=True)
                gb.configure_column("Establecimiento de Salud", width=350)
                # Formato condicional para la columna Estado
                
                grid_options = gb.build()
                #grid_options['getRowStyle'] = row_style
                
                grid_tab11 = AgGrid(soon6_dff_group, # Dataframe a mostrar
                                        gridOptions=grid_options,
                                        enable_enterprise_modules=False,
                                        #theme='balham',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                                        update_mode='MODEL_CHANGED',
                                        fit_columns_on_grid_load=True,
                                        height=340,
                                        allow_unsafe_jscode=True,
                                        key="grid_180_209"
                )
                
            with tab4:
                st.subheader("👶 Seguimiento Niños que cumplen 270-299 días en el mes")
                soon9_dff = dataframe_[(dataframe_["Niños 270-299 días en mes"]=="SI")]
                soon9_dff["Estado Niño"] = soon9_dff["Estado Niño"].replace({"Visita Domiciliaria (6 a 12 Meses)":"Visita Domiciliaria","Visita Domiciliaria (1 a 5 meses)":"Visita Domiciliaria"})
                soon9_dff_group = soon9_dff.groupby(["Establecimiento de Salud"]).agg(
                    Niños_Programados=("Número de Documento", "count"),
                    Niños_Encontrados_Efectivos=("Estado Niño", lambda x: (x == "Visita Domiciliaria").sum()),
                    Niños_SEGURO_SIS=("Tipo de Seguro", lambda x: ((x != "ESSALUD") & (x != "PRIVADO")).sum()),
                    Niños_OTRO_SEGURO=("Tipo de Seguro", lambda x: ((x == "ESSALUD")|(x == "PRIVADO")).sum()),
                ).reset_index()
                soon9_dff_group = soon9_dff_group.sort_values("Niños_Programados", ascending=False)
                
                # Agregar fila de total
                total_row_9 = pd.DataFrame({
                    "Establecimiento de Salud": ["TOTAL"],
                    "Niños_Programados": [soon9_dff_group["Niños_Programados"].sum()],
                    "Niños_Encontrados_Efectivos": [soon9_dff_group["Niños_Encontrados_Efectivos"].sum()],
                    "Niños_SEGURO_SIS": [soon9_dff_group["Niños_SEGURO_SIS"].sum()],
                    "Niños_OTRO_SEGURO": [soon9_dff_group["Niños_OTRO_SEGURO"].sum()],
                })
                soon9_dff_group = pd.concat([soon9_dff_group, total_row_9], ignore_index=True)
                soon9_dff_group["% Niños Encontrados"] = (soon9_dff_group["Niños_Encontrados_Efectivos"]/soon9_dff_group["Niños_Programados"]*100).round(1).astype(str) + "%"
                
                soon9_dff_group = soon9_dff_group[["Establecimiento de Salud", "Niños_Programados", "Niños_Encontrados_Efectivos","% Niños Encontrados", "Niños_SEGURO_SIS", "Niños_OTRO_SEGURO"]]
                soon9_dff_group.columns = ["Establecimiento de Salud", "Niños Programados", "Niños Encontrados Efectivos","% Niños Encontrados", "Niños SEGURO SIS", "Niños OTRO SEGURO"]
                
                gb3 = GridOptionsBuilder.from_dataframe(soon9_dff_group)
                gb3.configure_default_column(cellStyle={'fontSize': '17px'}) 
                #gb3.configure_selection(selection_mode="single", use_checkbox=True)
                gb3.configure_column("Establecimiento de Salud", width=350)
                
                grid_options3 = gb3.build()
                
                grid_tab8 = AgGrid(soon9_dff_group,
                                        gridOptions=grid_options3,
                                        enable_enterprise_modules=False,
                                        update_mode='MODEL_CHANGED',
                                        fit_columns_on_grid_load=True,
                                        height=340,
                                        allow_unsafe_jscode=True,
                                        key="grid_270_299"
                )
                
                
            with tab5:
                st.subheader("👶 Seguimiento Niños que cumplen 360-389 días en el mes")
                soon12_dff = dataframe_[(dataframe_["Niños 360-389 días en mes"]=="SI")]
                soon12_dff["Estado Niño"] = soon12_dff["Estado Niño"].replace({"Visita Domiciliaria (6 a 12 Meses)":"Visita Domiciliaria","Visita Domiciliaria (1 a 5 meses)":"Visita Domiciliaria"})
                soon12_dff_group = soon12_dff.groupby(["Establecimiento de Salud"]).agg(
                    Niños_Programados=("Número de Documento", "count"),
                    Niños_Encontrados_Efectivos=("Estado Niño", lambda x: (x == "Visita Domiciliaria").sum()),
                    Niños_SEGURO_SIS=("Tipo de Seguro", lambda x: ((x != "ESSALUD") & (x != "PRIVADO")).sum()),
                    Niños_OTRO_SEGURO=("Tipo de Seguro", lambda x: ((x == "ESSALUD")|(x == "PRIVADO")).sum()),
                ).reset_index()
                soon12_dff_group = soon12_dff_group.sort_values("Niños_Programados", ascending=False)
                
                # Agregar fila de total
                total_row_12 = pd.DataFrame({
                    "Establecimiento de Salud": ["TOTAL"],
                    "Niños_Programados": [soon12_dff_group["Niños_Programados"].sum()],
                    "Niños_Encontrados_Efectivos": [soon12_dff_group["Niños_Encontrados_Efectivos"].sum()],
                    "Niños_SEGURO_SIS": [soon12_dff_group["Niños_SEGURO_SIS"].sum()],
                    "Niños_OTRO_SEGURO": [soon12_dff_group["Niños_OTRO_SEGURO"].sum()],
                })
                soon12_dff_group = pd.concat([soon12_dff_group, total_row_12], ignore_index=True)
                soon12_dff_group["% Niños Encontrados"] = (soon12_dff_group["Niños_Encontrados_Efectivos"]/soon12_dff_group["Niños_Programados"]*100).round(1).astype(str) + "%"
                
                soon12_dff_group = soon12_dff_group[["Establecimiento de Salud", "Niños_Programados", "Niños_Encontrados_Efectivos","% Niños Encontrados", "Niños_SEGURO_SIS", "Niños_OTRO_SEGURO"]]
                soon12_dff_group.columns = ["Establecimiento de Salud", "Niños Programados", "Niños Encontrados Efectivos","% Niños Encontrados", "Niños SEGURO SIS", "Niños OTRO SEGURO"]
                
                gb2 = GridOptionsBuilder.from_dataframe(soon12_dff_group)
                gb2.configure_default_column(cellStyle={'fontSize': '17px'}) 
                #gb2.configure_selection(selection_mode="single", use_checkbox=True)
                gb2.configure_column("Establecimiento de Salud", width=350)
                
                grid_options2 = gb2.build()
                
                grid_tab2 = AgGrid(soon12_dff_group,
                                        gridOptions=grid_options2,
                                        enable_enterprise_modules=False,
                                        update_mode='MODEL_CHANGED',
                                        fit_columns_on_grid_load=True,
                                        height=340,
                                        allow_unsafe_jscode=True,
                                        key="grid_360_389"
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

def generar_excel_seguimiento_nominal():
    styles(2)
    c1_carga_df = fetch_carga_childs()
    padron_df = fetch_padron()
    padron_df = padron_df[
        [
            "Tipo_file","Tipo de Documento","Documento","DATOS NIÑO PADRON","DIRECCION PADRON","REFERENCIA DE DIRECCION","NUMERO DE DOCUMENTO  DE LA MADRE","DATOS MADRE PADRON","NUMERO DE CELULAR",
            "TIPO DE SEGURO","EESS NACIMIENTO","EESS","FRECUENCIA DE ATENCION"
        ]
    ]
    
    list_mes = [mes_short(x) for x in sorted(list(c1_carga_df["Mes"].unique()))]
    col1, col2 = st.columns(2)
    with col1:
        st.title("Manejador deSeguimiento Nominal")
    with col2:
        select_mes  = st.selectbox("Mes:",list_mes , key="select2",index=len(list_mes) - 1)
    mes = mestext_short(select_mes)
    seg_nominal_df =c1_carga_df[(c1_carga_df["Mes"] ==  mes) & (c1_carga_df["Año"] == 2025)]
    seg_nominal_df = seg_nominal_df[[
        "Establecimiento de Salud","Nombres del Actor Social","Tipo de Documento del niño","Número de Documento del niño","Fecha de Nacimiento","Rango de Edad","DNI de la madre","Celular de la madre",
        "Mes","Año"
    ]]
    dff = pd.merge(seg_nominal_df,padron_df, left_on='Número de Documento del niño', right_on='Documento', how='left')
    prioridad = {'DNI': 1, 'CUI': 2, 'CNV': 3}
    dff['Prioridad'] = dff['Tipo de Documento'].map(prioridad)
    dff = dff.sort_values(by=['Número de Documento del niño', 'Prioridad'])
    dff = dff.drop_duplicates(subset='Número de Documento del niño', keep='first')
    dff = dff.drop(columns=['Prioridad'])
    dff['Tipo_file'] = dff['Tipo_file'].fillna('Otro Ubigeo')
    pre_final_df = dff[[
        "Establecimiento de Salud","Nombres del Actor Social","Tipo de Documento","Número de Documento del niño","DATOS NIÑO PADRON",
        "Fecha de Nacimiento","Rango de Edad","DIRECCION PADRON","REFERENCIA DE DIRECCION","DNI de la madre","NUMERO DE DOCUMENTO  DE LA MADRE",
        "DATOS MADRE PADRON","NUMERO DE CELULAR","Celular de la madre","Tipo_file","TIPO DE SEGURO",'EESS NACIMIENTO', 'EESS', 'FRECUENCIA DE ATENCION'
    ]]
    pre_final_df["Número de Documento del niño"] = pre_final_df["Número de Documento del niño"].astype(str)
    nuevas_columnas = {
        'N°': pd.Series(dtype='int'),
        '¿Es prematuro?': pd.Series(dtype='str'),
        'FECHA del tamizaje de Hemoglobina de 06 MESES': pd.Series(dtype='str'),
        'Resultado de Hemoglobina de 06 MESES': pd.Series(dtype='str'),
        '¿Fue HISEADO(Tamizaje 6 meses)?': pd.Series(dtype='str'),
        '¿Tiene ANEMIA? - de 10.5 a menos': pd.Series(dtype='str'),
        '¿Está suplementado?': pd.Series(dtype='str'),
        'Tipo de SUPLEMENTO': pd.Series(dtype='str'),
        '07 MESES: Fecha y resultado de Hemoglobina': pd.Series(dtype='str'),
        '08 MESES: Fecha y resultado de Hemoglobina': pd.Series(dtype='str'),
        '09 MESES: Fecha y resultado de Hemoglobina': pd.Series(dtype='str'),
        '12 MESES: Fecha y resultado de Hemoglobina': pd.Series(dtype='str'),
        'Si estuvo en un cuadro de ANEMIA, y ya tiene 12 MESES: ¿Es un Niño recuperado que ya no tiene ANEMIA?': pd.Series(dtype='str'),
        '12 MESES: Fecha y resultado de Hemoglobina': pd.Series(dtype='str'),
        '¿Fue parte de una Sesion demostrativa?': pd.Series(dtype='str'),
        '¿Fue HISEADO(SD)?': pd.Series(dtype='str'),
    }
    def obs_periodos_consecutivos(df):
        all_c1_carga_df = df[(df["Año"] == 2025)]
        all_c1_carga_df["Mes_name"] = all_c1_carga_df["Mes"].apply(mes_short)
        all_c1_carga_df["Mes_name"] = all_c1_carga_df["Mes_name"] + "-"
        all_c1_carga_df = all_c1_carga_df.sort_values(by="Mes", ascending=True)
        all_c1_carga_df["Mes"] = all_c1_carga_df["Mes"].astype(str)
        unique_childs25_df = all_c1_carga_df.groupby(["Número de Documento del niño"]).agg({"Mes": "sum","Mes_name": "sum"}).reset_index()
        unique_childs25_df.columns = ["Documento", "Periodos","Periodos_name"]
        unique_childs25_df["Periodos_name"] = unique_childs25_df["Periodos_name"].str[:-1]
        unique_childs25_df['Es_Consecutivo'] = unique_childs25_df['Periodos'].apply(es_consecutivo)
        unique_childs25_df = unique_childs25_df[["Documento","Periodos_name","Es_Consecutivo"]]
        unique_childs25_df.columns = ["Documento","Periodos","¿Es consecutivo?"]
        unique_childs25_df["Documento"] = unique_childs25_df["Documento"].astype(str)
        return unique_childs25_df
    periodos_consecutivos_df = obs_periodos_consecutivos(c1_carga_df)
    pre_final_df = pd.merge(pre_final_df, periodos_consecutivos_df, left_on="Número de Documento del niño", right_on="Documento", how="left")
    primer_dia_mes = datetime(int(2025), int(mes), 1)
    print(primer_dia_mes)
    if int(mes) == 12:
            ultimo_dia_mes = datetime(int(2025) + 1, 1, 1) - pd.Timedelta(days=1)
    else:
            ultimo_dia_mes = datetime(int(2025), int(mes) + 1, 1) - pd.Timedelta(days=1)

    pre_final_df['Edad en días (primer día del mes)'] = pre_final_df['Fecha de Nacimiento'].apply(lambda x: (primer_dia_mes - x).days)
    pre_final_df['Edad en días (último día del mes)'] = pre_final_df['Fecha de Nacimiento'].apply(lambda x: (ultimo_dia_mes - x).days)

    pre_final_df['Niños 180-209 días en mes'] = pre_final_df.apply(
            lambda row: "SI" if (
                (row['Edad en días (primer día del mes)'] <= 209 and row['Edad en días (último día del mes)'] >= 180)
            ) else "NO", axis=1
    )

    pre_final_df['Niños 360-389 días en mes'] = pre_final_df.apply(
            lambda row: "SI" if (
                (row['Edad en días (primer día del mes)'] <= 389 and row['Edad en días (último día del mes)'] >= 360)
            ) else "NO", axis=1
    )
    pre_final_df["Edad"] = pre_final_df['Fecha de Nacimiento'].apply(lambda x: calcular_edad(x))
    final_df = pre_final_df.assign(**nuevas_columnas)
    final_df = final_df[
        ['Establecimiento de Salud', 'Nombres del Actor Social','N°',
        'Tipo de Documento', 'Número de Documento del niño','DATOS NIÑO PADRON',
        'Fecha de Nacimiento', 'Rango de Edad','Edad', 'DIRECCION PADRON',
        'REFERENCIA DE DIRECCION', 'DNI de la madre','DATOS MADRE PADRON',
        'NUMERO DE CELULAR', 'Celular de la madre', 'Tipo_file',
        'TIPO DE SEGURO', 'EESS NACIMIENTO', 'EESS',
        'Periodos', '¿Es consecutivo?',
        'Niños 180-209 días en mes',
        'Niños 360-389 días en mes', 
        '¿Es prematuro?',
        'FECHA del tamizaje de Hemoglobina de 06 MESES',
        'Resultado de Hemoglobina de 06 MESES',
        '¿Fue HISEADO(Tamizaje 6 meses)?',
        '¿Tiene ANEMIA? - de 10.5 a menos', '¿Está suplementado?',
        'Tipo de SUPLEMENTO', '07 MESES: Fecha y resultado de Hemoglobina',
        '08 MESES: Fecha y resultado de Hemoglobina',
        '09 MESES: Fecha y resultado de Hemoglobina',
        '12 MESES: Fecha y resultado de Hemoglobina',
        'Si estuvo en un cuadro de ANEMIA, y ya tiene 12 MESES: ¿Es un Niño recuperado que ya no tiene ANEMIA?',
        '¿Fue parte de una Sesion demostrativa?',
        '¿Fue HISEADO(SD)?'
    ]
    ]
    final_df["Establecimiento de Salud"] = final_df["Establecimiento de Salud"].str.replace('LOS GRANADOS "SAGRADO CORAZON"', "LOS GRANADOS SAGRADO CORAZON")
    final_df = final_df.sort_values(by=["Establecimiento de Salud",'Nombres del Actor Social'])
    del pre_final_df
    # Crear el archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Crear hoja de resumen SIN formato ni tabla
        resumen = pd.DataFrame({
            'Establecimiento de Salud': final_df['Establecimiento de Salud'].unique(),
            'Total de Registros': [len(final_df[final_df['Establecimiento de Salud'] == est]) 
                                for est in final_df['Establecimiento de Salud'].unique()]
        })
        resumen = resumen.sort_values(by='Total de Registros',ascending=False)
        resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Crear hojas por establecimiento CON formato de tabla
        establecimientos = final_df['Establecimiento de Salud'].unique()
        for establecimiento in establecimientos:
            df_establecimiento = final_df[final_df['Establecimiento de Salud'] == establecimiento]
            df_establecimiento['N°'] = range(1, len(df_establecimiento) + 1)
            nombre_hoja = str(establecimiento)[:31]
            df_establecimiento.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
            worksheet = writer.sheets[nombre_hoja]
            max_row = len(df_establecimiento) + 1  # +1 para encabezado
            max_col = len(df_establecimiento.columns)
            table_range = f'A1:{get_column_letter(max_col)}{max_row}'
            table_name = f"Table_{nombre_hoja.replace(' ', '_').replace('-', '_')}"
            
            # Solo agregar la tabla si hay datos
            if len(df_establecimiento) > 0:
                table = Table(displayName=table_name, ref=table_range)
                style = TableStyleInfo(
                    name="TableStyleMedium9",
                    showFirstColumn=False,
                    showLastColumn=False,
                    showRowStripes=True,
                    showColumnStripes=False
                )
                table.tableStyleInfo = style
                worksheet.add_table(table)
            
            # Ajustar ancho de columnas
            for idx, col in enumerate(df_establecimiento.columns):
                max_length = max(
                    df_establecimiento[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[get_column_letter(idx + 1)].width = max_length + 2
            
            worksheet.freeze_panes = 'A2'
            # Desbloquear todas las celdas primero
            for row in worksheet.iter_rows():
                for cell in row:
                    cell.protection = Protection(locked=False)
            
            # Bloquear la fila de encabezados (nombres de columnas) y aplicar formato
            for cell in worksheet[1]:
                cell.protection = Protection(locked=True)
                cell.font = Font(color="FFFFFF", bold=True)
                cell.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
            worksheet.row_dimensions[1].height = 40
            
            # Proteger solo la columna "Número de Documento del niño"
            col_to_lock_name = 'Número de Documento del niño'
            header_row = worksheet[1]
            col_to_lock_idx = None
            for idx, cell in enumerate(header_row, 1):
                if cell.value == col_to_lock_name:
                    col_to_lock_idx = idx
                    break
            if col_to_lock_idx:
                for row in range(2, max_row + 1):  # Empezar desde la fila 2 (después del encabezado)
                    cell = worksheet.cell(row=row, column=col_to_lock_idx)
                    cell.protection = Protection(locked=True)
            # Habilitar la protección de la hoja permitiendo la mayoría de las acciones
            worksheet.protection.sheet = True
            worksheet.protection.sort = False
            worksheet.protection.autoFilter = False
            worksheet.protection.formatCells = False
            worksheet.protection.formatColumns = False
            worksheet.protection.formatRows = False
    
    # Obtener los datos del archivo Excel
    excel_data = output.getvalue()
    
    st.download_button(
            label="Descargar Reporte Seguimiento Nominal",
            icon=":material/download:",
            data=excel_data,
            file_name=f"seguimiento_nominal_por_establecimiento_{select_mes}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
     )
    st.write(final_df.shape)
    st.dataframe(final_df)
    