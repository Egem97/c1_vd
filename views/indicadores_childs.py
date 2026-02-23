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
        select_mes  = st.selectbox("Mes:", ["Ene","Feb"], key="select2",index=True)
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


def capacitaciones_c1():
    st.subheader("Capacitaciones C1")
    df = pd.read_excel("Reporte_capacitacion_nivel_nominal (1).xls", skiprows=8)
    df = df[df["AS Activo/Inactivo"] == "Activo"]
    df = df.drop(columns=[
        'Ubigeo', 'Departamento', 'Provincia', 'Distrito', 'Nro de Documento AS',
        'Código de EESS', 'AS Habilitado'
    ], errors='ignore')
    
    col_evaluacion = [
        'Protocolo VD y ST - Capacitado', 'Protocolo VD y ST - Aprobado',
        'Anemia, prevención y Tratramiento - Capacitado',
        'Anemia, prevención y Tratramiento - Aprobado',
        'Lactancia materna exclusiva - Capacitado',
        'Lactancia materna exclusiva - Aprobado',
        'Alimentación complementaria - Capacitado',
        'Alimentación complementaria - Aprobado',
        'Lavado de manos - Capacitado', 'Lavado de manos - Aprobado',
        'Cumpliendo con las vacunas - Capacitado',
        'Cumpliendo con las vacunas - Aprobado',
        'Control de crecimiento y desarrollo de mi niño(a) - Capacitado',
        'Control de crecimiento y desarrollo de mi niño(a) - Aprobado',
        'Otros - Capacitado', 'Otros - Aprobado', 'Apego Seguro - Capacitado',
        'Apego Seguro - Aprobado', 'Previniendo el Coronavirus - Capacitado',
        'Previniendo el Coronavirus - Aprobado', 'VD/Calidad - Capacitado',
        'VD/Calidad - Aprobado', 'Aprendizaje a través del juego - Capacitado',
        'Aprendizaje a través del juego - Aprobado',
        'Atención Prenatal: Importancia - Capacitado',
        'Atención Prenatal: Importancia - Aprobado',
        'El Embarazo: Señales de peligro - Capacitado',
        'El Embarazo: Señales de peligro - Aprobado',
        'La Alimentación Saludable: Para la prevención de la anemia - Capacitado',
        'La Alimentación Saludable: Para la prevención de la anemia - Aprobado',
        'Anemia: Suplementación con hierro - Capacitado',
        'Anemia: Suplementación con hierro - Aprobado',
        'Plan de parto: Importancia - Capacitado',
        'Plan de parto: Importancia - Aprobado',
        'Parto Institucional: Importancia - Capacitado',
        'Parto Institucional: Importancia - Aprobado',
        'El Puerperio: Señales de peligro - Capacitado',
        'El Puerperio: Señales de peligro - Aprobado',
        'Derecho a la Identidad - Capacitado',
        'Derecho a la Identidad - Aprobado'
    ]
    
    # Identificar columnas que no son de evaluación para mantenerlas como identificadores
    id_vars = [c for c in df.columns if c not in col_evaluacion]
    
    # Transformar columnas a filas (Melt)
    df_melted = df.melt(
        id_vars=id_vars,
        value_vars=col_evaluacion,
        var_name='Evaluacion',
        value_name='Estado'
    )
    df_melted = df_melted[df_melted["Evaluacion"].str.contains("Aprobado")]
    st.write("Dimensiones del dataframe transformado:", df_melted.shape)
    
    # Botón de descarga para la tabla de evaluaciones
    excel_eval = convert_excel_df(df_melted)
    st.download_button(
        label="📥 Descargar Evaluaciones en Excel",
        data=excel_eval,
        file_name='Evaluaciones_Capacitaciones.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        key='btn_descarga_eval'
    )
    st.dataframe(df_melted)

    # --- NUEVA SECCIÓN DE GRÁFICOS ---
    # Filtrar solo los que tienen "SI" en la columna Estado
    df_si = df_melted[df_melted["Estado"] == "SI"].copy()

    if not df_si.empty:
        col1, col2 = st.columns(2)

        with col1:
            # Cantidad de capacitados (SI) por Evaluación
            df_count_eval = df_si.groupby("Evaluacion").size().reset_index(name="Cantidad")
            df_count_eval = df_count_eval.sort_values("Cantidad", ascending=True)
            
            fig_eval = px.bar(
                df_count_eval, 
                x="Cantidad", 
                y="Evaluacion", 
                orientation='h',
                title="Cantidad de 'SI' por Evaluación",
                text="Cantidad"
            )
            st.plotly_chart(fig_eval, use_container_width=True)

        with col2:
            # Cantidad de evaluados (SI) por Establecimiento de Salud
            df_count_eess = df_si.groupby("Establecimiento de Salud").size().reset_index(name="Cantidad")
            df_count_eess = df_count_eess.sort_values("Cantidad", ascending=True)
            
            fig_eess = px.bar(
                df_count_eess, 
                x="Cantidad", 
                y="Establecimiento de Salud", 
                orientation='h',
                title="Cantidad de 'SI' por Establecimiento",
                text="Cantidad"
            )
            st.plotly_chart(fig_eess, use_container_width=True)
    else:
        st.warning("No hay registros con 'SI' para mostrar en los gráficos.")

    # --- RESUMEN POR ESTABLECIMIENTO (Pivoteada) ---
    st.markdown("---")
    st.subheader("Resumen de Aprobados por Establecimiento de Salud")
    
    if not df_si.empty:
        # Crear la tabla dinámica: Filas = EESS, Columnas = Evaluaciones, Valores = Conteo de registros (con Estado SI)
        df_pivot = df_si.pivot_table(
            index="Establecimiento de Salud", 
            columns="Evaluacion", 
            aggfunc="size", 
            fill_value=0
        ).reset_index()
        
        # Botón de descarga para el resumen
        excel_resumen = convert_excel_df(df_pivot)
        st.download_button(
            label="📥 Descargar Resumen por EESS en Excel",
            data=excel_resumen,
            file_name='Resumen_Aprobados_por_EESS.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='btn_descarga_pivot'
        )
        st.dataframe(df_pivot)
    else:
        st.info("No hay datos aprobados para generar el resumen por establecimiento.")

    # --- ACTORES SOCIALES SIN CAPACITACIONES ---

    st.markdown("---")
    st.subheader("Actores Sociales sin ninguna Capacitación")
    
    # Columnas que específicamente indican capacitación
    cols_capacitado = [c for c in col_evaluacion if "Capacitado" in c]
    
    # Creamos una columna que cuente cuántos "SI" tiene el AS en capacitaciones
    # Nota: Trabajamos sobre el 'df' original filtrado por AS Activo
    df_check = df.copy()
    df_check['Total_Capacitaciones'] = (df_check[cols_capacitado] == "SI").sum(axis=1)
    
    # Filtramos los que tienen 0 capacitaciones
    as_sin_capacitacion = df_check[df_check['Total_Capacitaciones'] == 0][
        ["Apellidos y Nombres del AS", "Establecimiento de Salud", "Total de Sesiones"]
    ]
    
    if not as_sin_capacitacion.empty:
        st.error(f"Se encontraron {len(as_sin_capacitacion)} Actores Sociales sin capacitaciones registradas.")
        
        # Botón de descarga para AS sin capacitación
        excel_sin_cap = convert_excel_df(as_sin_capacitacion)
        st.download_button(
            label="📥 Descargar Lista AS sin Capacitación",
            data=excel_sin_cap,
            file_name='AS_Sin_Capacitacion.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='btn_descarga_sin_cap'
        )
        st.dataframe(as_sin_capacitacion)
    else:
        st.success("Todos los Actores Sociales activos tienen al menos una capacitación.")


