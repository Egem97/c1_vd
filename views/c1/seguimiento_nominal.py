import streamlit as st
import pandas as pd
import plotly.express as px
import re
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
from utils.g_sheet import *



@st.cache_data(show_spinner="Cargando datos...",ttl=600)  # ,ttl=600
def load_seg_nominal_data(select_mes):
    sn_month = {
                            "Jun": "11nk2Z1DmVKaXthy_TRsYK8wYzQ_BW8sdcRSXGxuq4Zo",
                            "Jul": "11nk2Z1DmVKaXthy_TRsYK8wYzQ_BW8sdcRSXGxuq4Zo",
                            "Ago": "1-jE3mNODE9UXj3dN9G9ae5WLl_Kyow96gWxcB0pOAxo",
                            "Set": "1XgsYbeYeX9nwyz7jj2PHBYiGcxZcXb9HIiw757XLCcQ",
                            "Oct": "1XgsYbeYeX9nwyz7jj2PHBYiGcxZcXb9HIiw757XLCcQ",
                            "Nov": "1XgsYbeYeX9nwyz7jj2PHBYiGcxZcXb9HIiw757XLCcQ",
                            "Dic": "1XgsYbeYeX9nwyz7jj2PHBYiGcxZcXb9HIiw757XLCcQ",
                    }
    return read_and_concatenate_sheets_optimized(
                        
                        key_sheet=sn_month[select_mes],
                        sheet_names=[
                            "ARANJUEZ","CLUB DE LEONES","EL BOSQUE",'LOS GRANADOS "SAGRADO CORAZON"',
                            "CENTRO DE SALUD LA UNION","HOSPITAL DE ESPECIALIDADES BASI",
                            "LIBERTAD","LOS JARDINES","PESQUEDA III","SAN MARTIN DE PORRES"
                        ],
                        add_sheet_column=True  # Añade columna 'sheet_origen'
     )


def seg_nominal_view():
    styles(2)
    colh,colg,colf = st.columns([7,2,3])
    with colh:
        st.header("📊 Dashboard de Seguimiento Nominal")
    with colg:
        select_mes = st.selectbox("Selecciona el mes", ["Ago","Set"])
    with colf:
       
        select_actividad = st.selectbox("Selecciona la actividad", 
        ['Tamizaje de 12 m.', 'Sin rango específico', 'Tamizaje de Control','Tamizaje de 6 m.', 'Suplementación Preventiva'],
        index=None)
        
    #read_sheet("1-jE3mNODE9UXj3dN9G9ae5WLl_Kyow96gWxcB0pOAxo","")
    #seg_nominal_df = load_seg_nominal_data("Set")s
    if select_mes == "Ago":
        sn_ago_df = load_seg_nominal_data("Ago")
    else:
        sn_ago_df = load_seg_nominal_data("Set")

    if select_actividad != None:
        sn_ago_df = sn_ago_df[sn_ago_df["Actividad a Realizar"] == select_actividad]
    
    #sn_ago_df = pd.read_parquet("ago_seg_nominal.parquet")
    #print(sn_ago_df.columns)
    #sn_set_df = pd.read_parquet("set_seg_nominal.parquet")
    #print()

    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.strip()
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].replace("","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("NO LE CORRESPONDE","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("NO LE CORREPONDE","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("NO CORRESPONDE","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("NO LE QUIERE DAR","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("NO DESEA DARLE","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("NINGUNA","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("NINGUNO","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace(".","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("PEDIATRA NO RECOMIENDA","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("SE EXTRIÑE","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].str.replace("SE ESTRIÑE","NO")
    sn_ago_df["Tipo de SUPLEMENTO"] = sn_ago_df["Tipo de SUPLEMENTO"].replace("-","NO")

    # Función para limpiar valores irregulares en columnas de hemoglobina
    def limpiar_hemoglobina(valor):
        """
        Limpia valores irregulares en columnas de hemoglobina.
        Convierte a 0 los valores que contengan caracteres no válidos.
        Mantiene solo números, puntos y comas.
        """
        if pd.isna(valor) or valor == "" or str(valor).strip() == "":
            return "0"
        
        valor_str = str(valor).strip()
        
        # Si el valor contiene solo números, puntos y comas, lo procesamos
        if re.match(r'^[0-9.,\-\s]*$', valor_str):
            # Reemplazar comas por puntos y guiones por puntos
            valor_limpio = valor_str.replace(",", ".").replace("-", ".")
            # Remover espacios
            valor_limpio = valor_limpio.replace(" ", "")
            
            # Verificar si después de la limpieza es un número válido
            try:
                float(valor_limpio)
                return valor_limpio
            except ValueError:
                return "0"
        else:
            # Si contiene caracteres irregulares, convertir a 0
            return "0"
    
    # Aplicar limpieza a la columna de hemoglobina de 6 meses
    sn_ago_df["Resultado de Hemoglobina de 06 MESES"] = sn_ago_df["Resultado de Hemoglobina de 06 MESES"].apply(limpiar_hemoglobina)
    sn_ago_df["Resultado de Hemoglobina de 06 MESES"] = sn_ago_df["Resultado de Hemoglobina de 06 MESES"].astype(float)

    sn_ago_df["Resultado de Hemoglobina de 12 MESES"] = sn_ago_df["Resultado de Hemoglobina de 12 MESES"].apply(limpiar_hemoglobina)
    sn_ago_df["Resultado de Hemoglobina de 12 MESES"] = sn_ago_df["Resultado de Hemoglobina de 12 MESES"].astype(float)

    # Aplicar limpieza a todas las columnas de hemoglobina
    columnas_hemoglobina = [
        "Resultado de Hemoglobina de 07 MESES",
        "Resultado de Hemoglobina de 08 MESES", 
        "Resultado de Hemoglobina de 09 MESES",
        "Resultado de Hemoglobina de 12 MESES"
    ]
    
    for columna in columnas_hemoglobina:
        if columna in sn_ago_df.columns:
            sn_ago_df[columna] = sn_ago_df[columna].apply(limpiar_hemoglobina)
            sn_ago_df[columna] = sn_ago_df[columna].astype(float)
    
    # Función para clasificar anemia según valores de hemoglobina
    def clasificar_anemia(hemoglobina, edad_meses):
        """
        Clasifica el estado de anemia según los valores de hemoglobina.
        Criterio simplificado: ≥10.5 = Sin anemia, <10.5 = Con anemia
        """
        if pd.isna(hemoglobina) or hemoglobina == 0:
            return "Sin dato"
        
        # Criterio simplificado de anemia
        if hemoglobina >= 10.5:
            return "Sin anemia"
        else:
            return "Con anemia"
    
    def clasificar_tamizaje(hemoglobina):
        """
        Clasifica si se realizó o no el tamizaje de hemoglobina.
        """
        if pd.isna(hemoglobina) or hemoglobina == 0:
            return "Sin tamizaje"
        else:
            return "Con tamizaje"
    
    def clasificar_resultado_final_hb(hb_6m, hb_12m):
        """
        Clasifica el resultado final de hemoglobina basado en los valores de 6 y 12 meses.
        
        Lógica:
        1. Si no hay resultados a los 12 meses (0 o vacío) -> "Sin datos"
        2. Si hay resultados a los 12 meses:
           - Si Hb 12m >= 10.5:
             - Si Hb 6m < 10.5 -> "Recuperado"
             - Si no -> "Sin Anemia"
           - Si Hb 12m < 10.5 -> "Con Anemia"
        """
        # Verificar si hay datos a los 12 meses
        if pd.isna(hb_12m) or hb_12m == 0:
            return "Sin datos"
        
        # Si hay datos a los 12 meses
        if hb_12m >= 10.5:
            # Verificar si hubo recuperación (6m < 10.5 y 12m >= 10.5)
            if not pd.isna(hb_6m) and hb_6m > 0 and hb_6m < 10.5:
                return "Recuperado"
            else:
                return "Sin Anemia"
        else:
            # Si a los 12 meses es menor a 10.5
            return "Con Anemia"


    
    suplementacion_ago_df = sn_ago_df.groupby(["Establecimiento de Salud"]).agg(
        #Cantidad_Suplemento=pd.NamedAgg(column="Tipo de SUPLEMENTO", aggfunc="count"),
        Cantidad_Sin_Suplemento=pd.NamedAgg(column="Tipo de SUPLEMENTO", aggfunc=lambda x: (x!="NO").sum())
    ).reset_index().sort_values(by="Cantidad_Sin_Suplemento", ascending=True)
    


    fig = px.bar(
        suplementacion_ago_df, 
        y="Establecimiento de Salud", 
        x="Cantidad_Sin_Suplemento",
        text = "Cantidad_Sin_Suplemento",
        title="Cantidad de Niños con Suplemento por Establecimiento de Salud",
        labels={
            "Establecimiento de Salud": "Establecimiento de Salud",
            "Cantidad_Sin_Suplemento": "Cantidad con Suplemento"
        },
        orientation="h"
    )
    fig.update_traces( textposition='outside')
    # Rotar las etiquetas del eje x para mejor legibilidad
    fig.update_layout(
        xaxis_tickangle=-45,
        #height=600,
        showlegend=False
    )
    
    # Mostrar el gráfico en Streamlit
    
    
    # ==================== DASHBOARD DE ANÁLISIS DE ANEMIA ====================
 
    
    # Preparar datos para análisis de tamizaje
    # Extraer edad en meses del campo "Edad"
    sn_ago_df['Edad_Meses'] = sn_ago_df['Edad'].str.extract('(\d+)').astype(float)
    
    # Crear clasificaciones de tamizaje para cada edad
    sn_ago_df['Tamizaje_6M'] = sn_ago_df['Resultado de Hemoglobina de 06 MESES'].apply(clasificar_tamizaje)
    sn_ago_df['Tamizaje_9M'] = sn_ago_df['Resultado de Hemoglobina de 09 MESES'].apply(clasificar_tamizaje)
    sn_ago_df['Tamizaje_12M'] = sn_ago_df['Resultado de Hemoglobina de 12 MESES'].apply(clasificar_tamizaje)
    
    # Mantener clasificaciones de anemia solo para métricas
    sn_ago_df['Anemia_6M'] = sn_ago_df.apply(lambda x: clasificar_anemia(x['Resultado de Hemoglobina de 06 MESES'], 6), axis=1)
    
    # Crear la nueva columna Resultado Final Hb
    sn_ago_df['Resultado Final Hb'] = sn_ago_df.apply(
        lambda x: clasificar_resultado_final_hb(
            x['Resultado de Hemoglobina de 06 MESES'], 
            x['Resultado de Hemoglobina de 12 MESES']
        ), axis=1
    )
    
    
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ninos = len(sn_ago_df)
        st.metric("Total de Niños", total_ninos)
    
    with col2:
        con_suplemento = len(sn_ago_df[sn_ago_df['Tipo de SUPLEMENTO'] != 'NO'])
        porcentaje_suplemento = (con_suplemento / total_ninos * 100) if total_ninos > 0 else 0
        st.metric("Con Suplemento", f"{con_suplemento}", f"{porcentaje_suplemento:.1f}%")
    
    
    

    
    # ==================== GRÁFICO DE SUPLEMENTACIÓN ====================
    
    
    # ==================== ANÁLISIS DE TAMIZAJE POR EDADES ====================
    st.subheader("🔬 Cobertura de Tamizaje de Hemoglobina por Establecimiento")
    
    # Crear columnas para los 3 gráficos de tamizaje
    col_6m, col_9m, col_12m = st.columns(3)
    
    # Gráfico de tamizaje a los 6 meses
    with col_6m:
        tamizaje_6m_df = sn_ago_df.groupby(['Establecimiento de Salud', 'Tamizaje_6M']).size().reset_index(name='Cantidad')
        fig_tamizaje_6m = px.bar(
            tamizaje_6m_df, 
            x='Establecimiento de Salud', 
            y='Cantidad',
            color='Tamizaje_6M',
            title='Tamizaje - 6 Meses',
            color_discrete_map={
                'Con tamizaje': '#1f77b4',
                'Sin tamizaje': '#ff7f0e'
            }
        )
        fig_tamizaje_6m.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_tamizaje_6m, use_container_width=True)
    
    # Gráfico de tamizaje a los 9 meses
    with col_9m:
        tamizaje_9m_df = sn_ago_df.groupby(['Establecimiento de Salud', 'Tamizaje_9M']).size().reset_index(name='Cantidad')
        fig_tamizaje_9m = px.bar(
            tamizaje_9m_df, 
            x='Establecimiento de Salud', 
            y='Cantidad',
            color='Tamizaje_9M',
            title='Tamizaje - 9 Meses',
            color_discrete_map={
                'Con tamizaje': '#1f77b4',
                'Sin tamizaje': '#ff7f0e'
            }
        )
        fig_tamizaje_9m.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_tamizaje_9m, use_container_width=True)
    
    # Gráfico de tamizaje a los 12 meses
    with col_12m:
        tamizaje_12m_df = sn_ago_df.groupby(['Establecimiento de Salud', 'Tamizaje_12M']).size().reset_index(name='Cantidad')
        fig_tamizaje_12m = px.bar(
            tamizaje_12m_df, 
            x='Establecimiento de Salud', 
            y='Cantidad',
            color='Tamizaje_12M',
            title='Tamizaje - 12 Meses',
            color_discrete_map={
                'Con tamizaje': '#1f77b4',
                'Sin tamizaje': '#ff7f0e'
            }
        )
        fig_tamizaje_12m.update_layout(xaxis_tickangle=-45, showlegend=True)
        st.plotly_chart(fig_tamizaje_12m, use_container_width=True)
    
    # ==================== ANÁLISIS DE ANEMIA POR ESTABLECIMIENTO Y ACTIVIDAD ====================
    st.subheader("🩸 Niños con Anemia por Establecimiento de Salud y Actividad a Realizar")
    
    # Filtrar solo niños con anemia (usando la clasificación de 6 meses como referencia principal)
    ninos_con_anemia_df = sn_ago_df[sn_ago_df['Anemia_6M'] == 'Con anemia'].copy()
    
    # Agrupar por Establecimiento de Salud y Actividad a Realizar
    anemia_actividad_df = ninos_con_anemia_df.groupby(['Establecimiento de Salud', 'Actividad a Realizar']).size().reset_index(name='Cantidad_Niños')
    
    # Crear gráfico de barras agrupadas
    fig_anemia_actividad = px.bar(
        anemia_actividad_df,
        x='Establecimiento de Salud',
        y='Cantidad_Niños',
        color='Actividad a Realizar',
        title='Distribución de Niños con Anemia por Establecimiento y Actividad a Realizar',
        labels={
            'Cantidad_Niños': 'Número de Niños con Anemia',
            'Establecimiento de Salud': 'Establecimiento de Salud',
            'Actividad a Realizar': 'Actividad a Realizar'
        },
        color_discrete_sequence=px.colors.qualitative.Set3,
        text='Cantidad_Niños'  # Agregar texto con las cantidades
    )
    
    # Personalizar el layout del gráfico
    fig_anemia_actividad.update_layout(
        xaxis_tickangle=-45,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        margin=dict(b=150)  # Margen inferior para los nombres largos de establecimientos
    )
    
    # Configurar el texto en las barras
    fig_anemia_actividad.update_traces(
        texttemplate='%{text}',
        textposition='inside',
        textfont_size=16,
        textfont_color='black',
        textfont_family='Arial Black'
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig_anemia_actividad, use_container_width=True)
    
    # Mostrar tabla resumen
    #st.subheader("📋 Tabla Resumen: Niños con Anemia por Establecimiento y Actividad")
    
    # Crear tabla pivot para mejor visualización
    tabla_pivot = anemia_actividad_df.pivot_table(
        index='Establecimiento de Salud',
        columns='Actividad a Realizar',
        values='Cantidad_Niños',
        fill_value=0,
        aggfunc='sum'
    ).reset_index()
    
    # Agregar columna de total
    tabla_pivot['Total'] = tabla_pivot.select_dtypes(include=[int, float]).sum(axis=1)
    
    # Mostrar la tabla
    #st.dataframe(tabla_pivot, use_container_width=True)
    
    # ==================== ANÁLISIS DE RESULTADO FINAL DE HEMOGLOBINA ====================
    st.subheader("🩸 Análisis de Resultado Final de Hemoglobina")
    
    # Contar la distribución del Resultado Final Hb (excluyendo "Sin datos")
    resultado_final_counts = sn_ago_df[sn_ago_df['Resultado Final Hb'] != 'Sin datos']['Resultado Final Hb'].value_counts().reset_index()
    resultado_final_counts.columns = ['Resultado Final Hb', 'Cantidad']
    
    # Definir colores para cada categoría
    colores_resultado = {
        'Sin datos': '#E0E0E0',      # Gris claro
        'Sin Anemia': '#4CAF50',     # Verde
        'Recuperado': '#2196F3',     # Azul
        'Con Anemia': '#F44336'      # Rojo
    }
    
    # Crear el pie chart
    fig_resultado_final = px.pie(
        resultado_final_counts,
        values='Cantidad',
        names='Resultado Final Hb',
        title='Distribución del Resultado Final de Hemoglobina (Solo casos con datos a los 12 meses)',
        color='Resultado Final Hb',
        color_discrete_map=colores_resultado
    )
    
    # Configurar el diseño del pie chart
    fig_resultado_final.update_traces(
        textposition='inside',
        textinfo='percent+label+value',
        textfont_size=12,
        textfont_color='white',
        textfont_family='Arial'
    )
    
    fig_resultado_final.update_layout(
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        font=dict(size=12)
    )
    
    # Mostrar el gráfico
    col_s,col_f =st.columns(2)
    with col_s:
        st.plotly_chart(fig_resultado_final, use_container_width=True)
    with col_f:  
        st.subheader("Análisis de Suplementación")
        st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar tabla resumen con porcentajes
    
    
    # Calcular porcentajes
    total_casos = resultado_final_counts['Cantidad'].sum()
    resultado_final_counts['Porcentaje'] = (resultado_final_counts['Cantidad'] / total_casos * 100).round(2)
    resultado_final_counts['Porcentaje_Str'] = resultado_final_counts['Porcentaje'].astype(str) + '%'
    
    # Reordenar columnas
    resultado_final_summary = resultado_final_counts[['Resultado Final Hb', 'Cantidad', 'Porcentaje_Str']]
    resultado_final_summary.columns = ['Resultado Final', 'Cantidad de Niños', 'Porcentaje']
    
    # Mostrar la tabla
   
    
    # Mostrar interpretación de los resultados
    st.info("""
    **Interpretación de los Resultados:**
    
    - **Sin datos**: Niños que no tienen resultados de hemoglobina a los 12 meses
    - **Sin Anemia**: Niños con hemoglobina ≥ 10.5 g/dL a los 12 meses (sin anemia previa a los 6 meses)
    - **Recuperado**: Niños que tenían anemia a los 6 meses (< 10.5 g/dL) pero se recuperaron a los 12 meses (≥ 10.5 g/dL)
    - **Con Anemia**: Niños con hemoglobina < 10.5 g/dL a los 12 meses
    """)
    
    