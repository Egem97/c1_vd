import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import plotly.graph_objects as go
from io import BytesIO
from styles import styles
from utils.cache_handler import fetch_padron
from utils.helpers import *
from constans import EESS_MICRORED

def revision_padron():
    styles(2)
    
    # Cargar y procesar datos una sola vez
    df = fetch_padron()
    
    # Optimizar tipos de datos
    df["Documento"] = df["Documento"].astype(str)
    df['EESS'] = df['EESS'].fillna("NO ESPECIFICADO")
    df["NUMERO DE CELULAR"] = df["NUMERO DE CELULAR"].str.strip()
    
    # Calcular edades una sola vez
    df['EDAD'] = df['FECHA DE NACIMIENTO'].apply(calcular_edad_anios)
    df['EDAD MESES'] = df['FECHA DE NACIMIENTO'].apply(calcular_edad)
    
    # Obtener fecha máxima una sola vez
    fecha_maxima = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].max().strftime("%Y-%m-%d")
    edades_list = sorted(df["EDAD"].unique())
    
    # Seleccionar solo las columnas necesarias desde el inicio
    columnas_necesarias = [  
        'CÓDIGO DE PADRON', 'CNV', 'CUI', 'DNI', 'DATOS NIÑO PADRON', 'SEXO',
        'FECHA DE NACIMIENTO', 'EJE VIAL', 'DIRECCION PADRON',
        'REFERENCIA DE DIRECCION', 'MENOR VISITADO', '¿MENOR ENCONTRADO?', 'FECHA DE VISITA',
        'FUENTE DE DATOS', 'FECHA DE FUENTE DE DATOS', 'EESS NACIMIENTO',
        'EESS', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN', 'TIPO DE SEGURO',
        'TIPO DE DOCUMENTO DE LA MADRE', 'NUMERO DE DOCUMENTO  DE LA MADRE', 'DATOS MADRE PADRON',
        'NUMERO DE CELULAR', 'CELULAR_CORREO', 'GRADO DE LA MADRE',
        'LENGUA DE LA MADRE', 'TIPO DE DOCUMENTO DEL JEFE DE FAMILIA',
        'NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA', 'DATOS JEFE PADRON',
        'FECHA DE MODIFICACIÓN DEL REGISTRO', 'USUARIO QUE MODIFICA', 'ENTIDAD',
        'TIPO REGISTRO', 'Tipo_file', 'Tipo de Documento',
        'EDAD', 'EDAD MESES'
    ]
    df = df[columnas_necesarias]
    
    # UI Elements
    col_filt = st.columns([3,3,2,3])
    
    with col_filt[0]:
        st.title(":blue[Padrón Trujillo] :child:")
    with col_filt[1]:
        st.subheader(f"Fecha de corte: {fecha_maxima}", divider=True)
    with col_filt[2]:
        select_edad = st.selectbox("Edad:", edades_list, key="select", placeholder="Seleccione Edad", index=None)
        if select_edad is not None:
            df = df[df["EDAD"] == select_edad]
            
    edad_meses_list = sorted(df["EDAD MESES"].unique())
    with col_filt[3]:
        select_edadmes = st.multiselect("Edad Mes:", edad_meses_list, key="select12", placeholder="Seleccione Mes")
        if select_edadmes:
            df = df[df["EDAD MESES"].isin(select_edadmes)]
    
    # Función optimizada para actualización
    def actualizacion_col(row):
        try:
            year_mod = row['FECHA DE MODIFICACIÓN DEL REGISTRO'].year
        except:
            year_mod = 2000
        
        if (row['USUARIO QUE MODIFICA'] in ["18215881", "SERVICIO DNI ESTADO"]) and row['ENTIDAD'] == "MUNICIPIO":
            return f"ACTUALIZADO MUNICIPIO ({year_mod})"
        return "SIN ACTUALIZACIÓN"
    
    # Aplicar actualización de manera vectorizada
    df["Estado"] = df.apply(actualizacion_col, axis=1)
    
    # Calcular métricas principales
    total = len(df)
    microred_df = df[df["EESS"].isin(EESS_MICRORED)]
    
    # Calcular estadísticas de microred
    general_microred_df = (microred_df.groupby("EESS")["Tipo de Documento"]
                          .count()
                          .sort_values()
                          .reset_index()
                          .rename(columns={"EESS": "Establecimiento de Salud", "Tipo de Documento": "Registros"}))
    
    promedio_registros_general = general_microred_df["Registros"].mean()
    num_general_microred = len(microred_df)
    
    # Calcular actualizaciones de microred
    mask_actualizados = (microred_df["ENTIDAD"] == "MUNICIPIO") & (microred_df["USUARIO QUE MODIFICA"].isin(["18215881"])& (microred_df["FECHA DE MODIFICACIÓN DEL REGISTRO"]>="2026-01-01"))
    #st.dataframe(microred_df[mask_actualizados], use_container_width=True)
    act_microred_df = (microred_df[mask_actualizados]
                      .groupby("EESS")["Tipo de Documento"]
                      .count()
                      .sort_values()
                      .reset_index()
                      .rename(columns={"EESS": "Establecimiento de Salud", "Tipo de Documento": "Registros"}))
    
    num_act_microred = len(microred_df[mask_actualizados])
    promedio_registros_act = act_microred_df["Registros"].mean()
    
    # Calcular porcentajes de actualización
    general_dff = pd.merge(general_microred_df, act_microred_df, 
                          on='Establecimiento de Salud', 
                          how='inner',
                          suffixes=('_x', '_y'))
    
    general_dff["%"] = round((general_dff["Registros_y"]/general_dff["Registros_x"])*100, 1)
    general_dff.columns = ["Establecimiento de Salud", "Población", "Actualización", "%"]
    
    # Calcular estadísticas de otros establecimientos
    others_df = df[~df["EESS"].isin(EESS_MICRORED)]
    sin_eess = len(others_df[others_df["EESS"] == "NO ESPECIFICADO"])
    others_eess = len(others_df[others_df["EESS"] != "NO ESPECIFICADO"])
    
    eess_others_df = (others_df[others_df["EESS"] != "NO ESPECIFICADO"]
                     .groupby("EESS")["Tipo de Documento"]
                     .count()
                     .sort_values()
                     .reset_index()
                     .rename(columns={"EESS": "Establecimiento de Salud", "Tipo de Documento": "Registros"}))
    eess_others_df = eess_others_df[eess_others_df["Registros"] > 1]
    
    # Mostrar métricas
    metric_col = st.columns(4)
    metric_col[0].metric("Población Padron", total, "100%", border=True)
    metric_col[1].metric("Población EE. SS", num_general_microred, f"{round((num_general_microred/total)*100,2)}%", border=True)
    metric_col[2].metric("Sin EE. SS", sin_eess, f"{round((sin_eess/total)*100,2)}%", border=True)
    metric_col[3].metric("Otros EE. SS", others_eess, f"{round((others_eess/total)*100,2)}%", border=True)
    
    # Crear pestañas para visualizaciones
    tab_1, tab_2= st.tabs(["Población","% de Actualizaciones"])
    
    with tab_1:
        fig_eess_count = px.bar(general_microred_df, 
                               x="Establecimiento de Salud", 
                               y="Registros",
                               text="Registros", 
                               orientation='v',
                               title=f"Población por Establecimiento de Salud ({num_general_microred})")
        fig_eess_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_count.update_layout(xaxis=dict(title=dict(text="")), font=dict(size=16))
        fig_eess_count.add_hline(y=promedio_registros_general, 
                                line=dict(color="red", dash="dash"),
                                annotation_text=f"Promedio: {promedio_registros_general:.0f}",
                                annotation_position="top left")
        st.plotly_chart(fig_eess_count)
        
    
        
    with tab_2:
        fig_comparativo = go.Figure(data=[
            go.Bar(name='Población',
                  x=general_dff["Establecimiento de Salud"],
                  y=general_dff["Población"],
                  text=general_dff["Población"],
                  textposition='outside',
                  textfont=dict(size=16)),
            go.Bar(name='Actualización',
                  x=general_dff["Establecimiento de Salud"],
                  y=general_dff["Actualización"],
                  text=general_dff["Actualización"],
                  textposition='outside',
                  textfont=dict(size=16))
        ])
        fig_comparativo.update_layout(barmode='group',
                                    title="Población y Actualización en el Padrón Nominal")
        st.plotly_chart(fig_comparativo)
        
        general_dff = general_dff.sort_values("%")
        general_dff["%_formatted"] = general_dff["%"].astype(str) + '%'
        fig_eess_percent = px.bar(general_dff,
                                 x="Establecimiento de Salud",
                                 y="%",
                                 text="%_formatted",
                                 orientation='v',
                                 title="Porcentaje de Actualizaciones por Establecimiento")
        fig_eess_percent.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_percent.update_layout(xaxis=dict(title=dict(text="")), font=dict(size=16))
        st.plotly_chart(fig_eess_percent)
    
    # Mostrar otros establecimientos
    #columnas_add = st.columns(2)
    #with columnas_add[0]:
    #    fig_eess_other = px.bar(eess_others_df,
    #                           x="Registros",
    #                           y="Establecimiento de Salud",
   #                            text="Registros",
   #                            orientation='h',
   #                            title=f"Población de Otros Establecimientos de Salud ({others_eess})")
   #        fig_eess_other.update_traces(textfont_size=18, textangle=0, textposition='outside', cliponaxis=False)
   #        fig_eess_other.update_layout(xaxis=dict(title=dict(text="")), font=dict(size=16))
        #st.plotly_chart(fig_eess_other)
    
    # Preparar datos para exportación
    df = df.rename(columns={
        "EESS": "Establecimiento de Salud Atención",
        "Tipo_file": "Tipo Registro",
        'EDAD': "Edad",
        'EDAD MESES': "Edad Meses"
    })
    
    # Crear resumen para exportación
    resumen_dff = (df.groupby(["Establecimiento de Salud Atención", "Estado"])["Tipo Registro"]
                  .count()
                  .reset_index())
    resumen_dff = resumen_dff[resumen_dff["Establecimiento de Salud Atención"].isin(EESS_MICRORED)]
    df_pivot = (resumen_dff.pivot_table(index='Establecimiento de Salud Atención',
                                      columns='Estado',
                                      values='Tipo Registro',
                                      aggfunc='sum',
                                      fill_value=0)
                .reset_index())
    
    #st.dataframe(df_pivot)
    
    # Preparar datos para exportación por establecimiento
    establecimientos = {
        'ARANJUEZ': df[df["Establecimiento de Salud Atención"] == "ARANJUEZ"],
        'CLUB DE LEONES': df[df["Establecimiento de Salud Atención"] == "CLUB DE LEONES"],
        'NORIA': df[df["Establecimiento de Salud Atención"] == "DE ESPECIALIDADES BASICAS LA NORIA"],
        'EL BOSQUE': df[df["Establecimiento de Salud Atención"] == "EL BOSQUE"],
        'LA UNION': df[df["Establecimiento de Salud Atención"] == "LA UNION"],
        'LIBERTAD': df[df["Establecimiento de Salud Atención"] == "LIBERTAD"],
        'SAGRADO CORAZON': df[df["Establecimiento de Salud Atención"] == 'LOS GRANADOS "SAGRADO CORAZON"'],
        'LOS JARDINES': df[df["Establecimiento de Salud Atención"] == "LOS JARDINES"],
        'PESQUEDA II': df[df["Establecimiento de Salud Atención"] == "PESQUEDA II"],
        'PESQUEDA III': df[df["Establecimiento de Salud Atención"] == "PESQUEDA III"],
        'SAN MARTIN DE PORRES': df[df["Establecimiento de Salud Atención"] == "SAN MARTIN DE PORRES"]
    }
    
    # Exportar a Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_pivot.to_excel(writer, sheet_name='Resumen', index=False)
        for nombre, datos in establecimientos.items():
            datos.to_excel(writer, sheet_name=nombre, index=False)
    output.seek(0)
    
    # Botones de descarga
    st.download_button(
        label="📥 Descargar Actualizados",
        data=output,
        file_name="padron_actualizados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.download_button(
        label="📥 Descargar Padrón Nominal",
        data=convert_excel_df(df),
        file_name="padron_trujillo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
   