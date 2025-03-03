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


def pivot_actividad_gestante():
    styles(2)
    st.title("Pivot Actividad Gestante")
    uploaded_file = st.file_uploader(
        "Ingresa Reporte Actividad Gestante", accept_multiple_files=False
    )
    if uploaded_file is not None:
        dataframe = pd.read_excel(uploaded_file,skiprows=7,dtype={"Número de Documento": "str"})
        st.write(dataframe.shape[0])
        st.write(dataframe)
        print(dataframe.columns)
        dff = dataframe.groupby(["Número de Documento","Etapa","Distrito","Establecimiento de Salud"])[["UBIGEO"]].count().reset_index()
        dff['Etapa'] = dff['Etapa'].replace({
        'Visita Domiciliaria (Adulta)': 'Visita Domiciliaria',
        'Visita Domiciliaria (Adolescente)': 'Visita Domiciliaria'
        })
        df_pivot = dff.pivot_table(
            index=["Distrito","Establecimiento de Salud","Número de Documento"], 
            columns='Etapa', 
            values='UBIGEO',
            aggfunc="sum", 
            fill_value=0
        )
        df_pivot = df_pivot.reset_index()
        def new_col(vd_noen,vd_encontrada,vd_rechazo):
            if vd_rechazo == 0:
                if vd_noen > 0 or vd_encontrada > 0 :
                    if vd_noen == vd_encontrada:
                        return "Visita Domiciliaria - No Encontrada"
                    else:
                        if vd_noen > vd_encontrada:
                            return "No Encontrado"
                        elif vd_encontrada > vd_noen :
                            return "Visita Domiciliaria"
            elif  vd_rechazo > 0:
                if vd_noen == vd_rechazo:
                    return "No Encontrado - Rechazado"
                elif vd_noen == 0 and vd_rechazo == vd_encontrada:
                    return "Visita Domiciliaria - Rechazado"
                else:

                    return "Rechazado"
        df_pivot["Estado"] = df_pivot.apply(lambda x:new_col(x['No Encontrado'],x['Visita Domiciliaria'],x["Rechazado"]),axis=1)
        #st.dataframe(df_pivot)
        st.write(df_pivot.shape[0])
        gb = GridOptionsBuilder.from_dataframe(df_pivot)
        gb.configure_default_column(cellStyle={'fontSize': '20px'}) 
        grid_options = gb.build()
        
        
        grid_response = AgGrid(df_pivot, # Dataframe a mostrar
                                gridOptions=grid_options,
                                enable_enterprise_modules=False,
                                #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                                update_mode='MODEL_CHANGED',
                                fit_columns_on_grid_load=True,
                            
        )
        st.download_button(
                label="Descargar Pivot VD Gestantes",
                data=convert_excel_df(df_pivot),
                file_name=f"gestantes_pivot_visitas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

def pivot_actividad_childs():
    styles(2)
    st.title("Generar Reporte Niños")
    uploaded_file = st.file_uploader(
        "Ingresa Reporte Niños", accept_multiple_files=False
    )
    if uploaded_file is not None:
        detalle_df = pd.read_excel(uploaded_file,skiprows=7,sheet_name="REPORTE DE DETALLE POR NIÑO")
        detalle_df["Número de Documento del niño"] = detalle_df["Número de Documento del niño"].astype(str)
        actividad_df = pd.read_excel(uploaded_file,skiprows=7,sheet_name="REPORTE DE ACTIVIDADES")
        actividad_df["Número de Documento de Niño"] = actividad_df["Número de Documento de Niño"].astype(str)
        #CON EL DETALLE DEL NIÑO CONTAMOS LA CANTIDAD DE NIÑOS POR DISTRITO
        distrito_carga_df = detalle_df.groupby(["Distrito"])[["Ubigeo"]].count().sort_values("Ubigeo",ascending=False).reset_index()
        distrito_carga_df = distrito_carga_df.rename(columns=  {"Ubigeo":"Niños Programados"})
        #AGRUPAR LAS VISITAS 
        etapa_vd_df= actividad_df.groupby(['Número de Documento de Niño','Etapa'])[['Año']].count().reset_index()
        #REVISION VERIFICACION DE REGISTROS
        etapa_vd_df_dup =etapa_vd_df.groupby(['Número de Documento de Niño'])["Año"].count().reset_index()
        etapa_vd_df_dup = etapa_vd_df_dup.rename(columns=  {"Año":"Verificacion"})
        etapa_vd_df_dup['Verificacion'] = etapa_vd_df_dup['Verificacion'].replace({
            1: 'Registro Regular',
            2: 'Registro Irregular'
        })
        etapa_vd_unique_df = etapa_vd_df.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
        etapa_vd_unique_df = etapa_vd_unique_df.drop_duplicates(subset='Número de Documento de Niño', keep='first')
        etapa_vd_unique_df.columns = ["Doc_Ultimo_Mes","Estado_Visita_Ult","count"]
        etapa_vd_join_df = pd.merge(etapa_vd_unique_df,etapa_vd_df_dup , left_on='Doc_Ultimo_Mes', right_on='Número de Documento de Niño', how='left')
        etapa_vd_join_df = etapa_vd_join_df[["Número de Documento de Niño","Estado_Visita_Ult","Verificacion"]]
        etapa_vd_join_df.columns = ["Número de Documento de Niño","ETAPA","Verificacion"]
        
        
        ####JOIN CON EL DETALLE DE NIÑO
        det_join_vd_df = pd.merge(detalle_df,etapa_vd_join_df , left_on='Número de Documento del niño', right_on='Número de Documento de Niño', how='left')
        det_join_vd_df['Estado Visitas'] =  det_join_vd_df.apply(lambda x: estado_visitas_completas(x['Total de visitas completas para la edad'], x['Total de VD presenciales Válidas'],x['ETAPA']),axis=1)
        #FILTRAR INCOMPLETOS
        data_incompleta_df = det_join_vd_df[(det_join_vd_df["Estado Visitas"].isin(["Visitas Incompletas(faltantes:3)","Visitas Incompletas(faltantes:2)","Visitas Incompletas(faltantes:1)"]))]
        data_incompleta_df['Estado Visitas'] = data_incompleta_df['Estado Visitas'].replace({
            "Visitas Incompletas(faltantes:3)": 'Visitas Incompletas',
            "Visitas Incompletas(faltantes:2)": 'Visitas Incompletas',
            "Visitas Incompletas(faltantes:1)": 'Visitas Incompletas',
        })
        data_incompleta_df = data_incompleta_df.groupby(["Distrito","Estado Visitas"])[["Verificacion"]].count().reset_index()
        data_incompleta_df = data_incompleta_df.pivot_table(
            index=["Distrito"], 
            columns='Estado Visitas', 
            values='Verificacion',
            aggfunc="sum", 
            fill_value=0
        ).reset_index()
        
        ##### FILTRAR PARA EVALUACIONES SOLO VISITAS COMPLETAS Y REGULARES
        dataframe_ = det_join_vd_df[(det_join_vd_df["Verificacion"]=='Registro Regular')&(det_join_vd_df["Estado Visitas"]=='Visitas Completas')]
        
        ##### FILTRAR PARA EVALUACIONES SOLO NO ENCONTRADOS Y RECHAZADOS
        data_negativa_df = det_join_vd_df[(det_join_vd_df["ETAPA"].isin(["No Encontrado","Rechazado"]))]
        vd_no_efectivas_df = data_negativa_df.groupby(["Distrito","ETAPA"])[["Verificacion"]].count().reset_index()
        vd_no_efectivas_df = vd_no_efectivas_df.pivot_table(
            index=["Distrito"], 
            columns='ETAPA', 
            values='Verificacion',
            aggfunc="sum", 
            fill_value=0
        ).reset_index()
        vd_no_efectivas_df["NNE y Rechazo"] = vd_no_efectivas_df["No Encontrado"] + vd_no_efectivas_df["Rechazado"]
        ###
        
        ### AGREGAR COLUMNAS SOLO VISITAS EFECTIVAS Y COMPLETAS
        vd_efectivas_df = dataframe_.groupby(["Distrito","ETAPA"])[["Verificacion"]].count().reset_index()
        vd_efectivas_pivot_df = vd_efectivas_df.pivot_table(
            index=["Distrito"], 
            columns='ETAPA', 
            values='Verificacion',
            aggfunc="sum", 
            fill_value=0
        ).reset_index()
        vd_efectivas_pivot_df["Niños con Visitas Efectivas O Y C"] = vd_efectivas_pivot_df["Visita Domiciliaria (1 a 5 meses)"] + vd_efectivas_pivot_df["Visita Domiciliaria (6 a 12 Meses)"]
        
        ### FULL JOINS
        distrito_carga_df = pd.merge(distrito_carga_df, vd_efectivas_pivot_df, left_on='Distrito', right_on='Distrito', how='left')
        
        distrito_carga_df = pd.merge(distrito_carga_df, vd_no_efectivas_df, left_on='Distrito', right_on='Distrito', how='left')
        distrito_carga_df["No Encontrado"] = distrito_carga_df["No Encontrado"].fillna(0)
        distrito_carga_df["Rechazado"] = distrito_carga_df["Rechazado"].fillna(0)
        distrito_carga_df["NNE y Rechazo"] = distrito_carga_df["NNE y Rechazo"].fillna(0)
        distrito_carga_df = pd.merge(distrito_carga_df, data_incompleta_df, left_on='Distrito', right_on='Distrito', how='left')
        distrito_carga_df["Visitas Incompletas"] = distrito_carga_df["Visitas Incompletas"].fillna(0)
        total_row = pd.DataFrame({
            "Distrito": ["TOTAL"],  # Nombre de la fila
            "Niños Programados":distrito_carga_df["Niños Programados"].sum(),
            "Visita Domiciliaria (1 a 5 meses)":distrito_carga_df["Visita Domiciliaria (1 a 5 meses)"].sum(),
            "Visita Domiciliaria (6 a 12 Meses)":distrito_carga_df["Visita Domiciliaria (6 a 12 Meses)"].sum(),
            "Niños con Visitas Efectivas O Y C":distrito_carga_df["Niños con Visitas Efectivas O Y C"].sum(),
            "No Encontrado":distrito_carga_df["No Encontrado"].sum(),
            "Rechazado":distrito_carga_df["Rechazado"].sum(),
            "NNE y Rechazo":distrito_carga_df["NNE y Rechazo"].sum(),
            "Visitas Incompletas":distrito_carga_df["Visitas Incompletas"].sum(),

        })
        distrito_carga_df = pd.concat([distrito_carga_df, total_row], ignore_index=True)
        distrito_carga_df["% Niños con Visitas Efectivas O y C"] = round((distrito_carga_df["Niños con Visitas Efectivas O Y C"]/distrito_carga_df["Niños Programados"])*100,2)
        distrito_carga_df["% NNE y Rechazo"] = round((distrito_carga_df["NNE y Rechazo"]/distrito_carga_df["Niños Programados"])*100,2)
        distrito_carga_df = distrito_carga_df[[
            'Distrito', 'Niños Programados', 'Visita Domiciliaria (1 a 5 meses)','Visita Domiciliaria (6 a 12 Meses)', 
            'Niños con Visitas Efectivas O Y C','% Niños con Visitas Efectivas O y C', 'No Encontrado', 'Rechazado',
            'NNE y Rechazo',
            '% NNE y Rechazo',
            "Visitas Incompletas"
        ]]
        gb = GridOptionsBuilder.from_dataframe(distrito_carga_df)
        gb.configure_default_column(cellStyle={'fontSize': '15px'}) 
        grid_options = gb.build()
        
        
        grid_response = AgGrid(distrito_carga_df, # Dataframe a mostrar
                                gridOptions=grid_options,
                                enable_enterprise_modules=False,
                                #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                                update_mode='MODEL_CHANGED',
                                fit_columns_on_grid_load=True,
                                height=810
                            
        )
        data = {
            'Categoría': ['A', 'A', 'B', 'B', 'C', 'C'],
            'Subcategoría': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
            'Valor': [100, 200, 150, 250, 200, 100]
        }

        df = pd.DataFrame(data)

        # Calcular porcentaje relativo dentro de cada categoría
        df['Porcentaje'] = df.groupby('Categoría')['Valor'].transform(lambda x: (x / x.sum()) * 100)

        # Crear gráfico de barras apiladas relativas
        fig = px.bar(df, 
                    x='Categoría', 
                    y='Porcentaje', 
                    color='Subcategoría',  # Diferenciar por subcategoría
                    text=df['Porcentaje'].map(lambda x: f'{x:.1f}%'),  # Mostrar porcentaje en cada barra
                    labels={'Porcentaje': 'Porcentaje (%)'}, 
                    title="Barras Relativas en Porcentaje",
                    barmode="relative")  # Modo relativo

        # Ajustar formato del texto en las barras
        fig.update_traces(textposition='inside')

        # Mostrar en Streamlit
        st.plotly_chart(fig)
        st.download_button(
                label="Descargar Detalle de Niño",
                data=convert_excel_df(det_join_vd_df),
                file_name=f"Detalle_niño_actividades.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar Porcentajes",
                data=convert_excel_df(distrito_carga_df),
                file_name=f"Distrito_avances_vd_op.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        #st.dataframe(detalle_df)
        #st.dataframe(actividad_df)
        """
        st.write(dataframe.shape[0])
        st.write(dataframe)
        print(dataframe.columns)
        dff = dataframe.groupby(["Número de Documento","Etapa","Distrito","Establecimiento de Salud"])[["UBIGEO"]].count().reset_index()
        dff['Etapa'] = dff['Etapa'].replace({
        'Visita Domiciliaria (Adulta)': 'Visita Domiciliaria',
        'Visita Domiciliaria (Adolescente)': 'Visita Domiciliaria'
        })
        df_pivot = dff.pivot_table(
            index=["Distrito","Establecimiento de Salud","Número de Documento"], 
            columns='Etapa', 
            values='UBIGEO',
            aggfunc="sum", 
            fill_value=0
        )
        df_pivot = df_pivot.reset_index()
        def new_col(vd_noen,vd_encontrada,vd_rechazo):
            if vd_rechazo == 0:
                if vd_noen > 0 or vd_encontrada > 0 :
                    if vd_noen == vd_encontrada:
                        return "Visita Domiciliaria - No Encontrada"
                    else:
                        if vd_noen > vd_encontrada:
                            return "No Encontrado"
                        elif vd_encontrada > vd_noen :
                            return "Visita Domiciliaria"
            elif  vd_rechazo > 0:
                if vd_noen == vd_rechazo:
                    return "No Encontrado - Rechazado"
                elif vd_noen == 0 and vd_rechazo == vd_encontrada:
                    return "Visita Domiciliaria - Rechazado"
                else:

                    return "Rechazado"
        df_pivot["Estado"] = df_pivot.apply(lambda x:new_col(x['No Encontrado'],x['Visita Domiciliaria'],x["Rechazado"]),axis=1)
        #st.dataframe(df_pivot)
        st.write(df_pivot.shape[0])
        gb = GridOptionsBuilder.from_dataframe(df_pivot)
        gb.configure_default_column(cellStyle={'fontSize': '20px'}) 
        grid_options = gb.build()
        
        
        grid_response = AgGrid(df_pivot, # Dataframe a mostrar
                                gridOptions=grid_options,
                                enable_enterprise_modules=False,
                                #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                                update_mode='MODEL_CHANGED',
                                fit_columns_on_grid_load=True,
                            
        )
        st.download_button(
                label="Descargar Pivot VD Gestantes",
                data=convert_excel_df(df_pivot),
                file_name=f"gestantes_pivot_visitas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        """