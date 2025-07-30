import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_childs,fetch_carga_childs,fetch_padron
from utils.helpers import *
from utils.functions_data import childs_unicos_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def summary_tramo3_test():
    styles(2)
    st.title("Resuemn Tramo III")
    st.subheader("Niños")
    
    df_ene_child = pd.read_parquet(f"./data/1.2/indicador_childs_enero.parquet")
    df_feb_child = pd.read_parquet(f"./data/1.2/indicador_childs_febrero.parquet")
    df_mar_child = pd.read_excel(f"./data/1.2/niños_reporte_Mar_final_mes.xlsx")
    df_abr_child = pd.read_excel(f"./data/1.2/niños_reporte_Abr_final_mes.xlsx")
    df_may_child = pd.read_excel(f"./data/1.2/niños_reporte_May_final_mes.xlsx")
    csummary_df = pd.concat([df_ene_child, df_feb_child, df_mar_child,df_abr_child,df_may_child], ignore_index=True)
    csummary_df["Estado Visitas"] =csummary_df["Estado Visitas"].replace(
        {
            "Visita Niño:No Encontrado": "No Encontrado", 
            "Visita Niño:Rechazado": "Rechazado", 
            "Visitas Incompletas(faltantes:1)": "Visitas Incompletas", 
            "Visitas Incompletas(faltantes:2)": "Visitas Incompletas", 
            "Visitas Incompletas(faltantes:3)": "Visitas Incompletas", 
            }, 
      )
    #csummary_df.to_excel("csummary_df.xlsx", index=False)
    #st.dataframe(csummary_df)
    percent_month_df = csummary_df.groupby(["Mes","Estado Visitas"]).agg({"Año": "count"}).reset_index().rename(columns={"Año": "Cantidad"})
    percent_month_df["Percent"] = (percent_month_df.groupby("Mes")["Cantidad"].transform(lambda x: x / x.sum() * 100)).round(2)
    percent_month_df = percent_month_df.sort_values(by="Estado Visitas", ascending=True)
    #st.dataframe(csummary_df)
    ctable_df = csummary_df.groupby(["Mes"]).agg({
        "Año": "count",
        "N° Visitas Completas": "sum",
        "Total de VD presenciales Válidas": "sum",
        "Total de VD presencial Válidas WEB": "sum",
        "Total de VD presencial Válidas MOVIL": "sum",
        "Sector": "nunique", 
        "Actor Social": "nunique", 
        "Estado Visitas": [
            ("Visitas Completas", lambda x: (x == "Visitas Completas").sum()),
            ("No Encontrado", lambda x: (x == "No Encontrado").sum()),
            ("Rechazado", lambda x: (x == "Rechazado").sum()),
            ("Visitas Incompletas", lambda x: (x == "Visitas Incompletas").sum()),
        ]
        }).reset_index().rename(columns={"Año": "Cantidad"})
    # Aplana la cabecera
    ctable_df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in ctable_df.columns]

    # Renombra las columnas a algo más limpio
    ctable_df = ctable_df.rename(columns={
        'Cantidad count': 'Niños Cargados',
        'N° Visitas Completas sum': 'Visitas Programadas',
        'Total de VD presenciales Válidas sum': 'Visitas Realizadas',
        'Total de VD presencial Válidas WEB sum': 'Visitas WEB',
        'Total de VD presencial Válidas MOVIL sum': 'Visitas MOVIL',
        'Sector nunique': 'N° de Sectores Visitados',
        'Actor Social nunique': 'N° de Actores Sociales',
        'Estado Visitas Visitas Completas': 'Niños Encontrados',
        'Estado Visitas No Encontrado': 'Niños No Encontrados',
        'Estado Visitas Rechazado': 'Niños Rechazados',
        'Estado Visitas Visitas Incompletas': 'Niños con Visitas Incompletas'
    })
    ctable_df["% Geo"] = round(ctable_df["Visitas MOVIL"] / ctable_df["Visitas Programadas"],3)*100
    ctable_df["% Indicador"] = round(ctable_df["Niños Encontrados"] / ctable_df["Niños Cargados"],3)*100
    ctable_df["Mes"] = ctable_df["Mes"].map(mes_compname)
    ####porcentaje por dispositivo
    cdispositivo_df = csummary_df.groupby(["Mes"]).agg({
        "Total de VD presencial Válidas WEB": "sum",
        "Total de VD presencial Válidas MOVIL": "sum",
    }).reset_index()#.rename(columns={"Año": "Cantidad"})
    #cdispositivo_df["Percent"] = (cdispositivo_df.groupby("Mes")["Cantidad"].transform(lambda x: x / x.sum() * 100)).round(2) 
    cdispositivo_df["Mes"] = cdispositivo_df["Mes"].map(mes_compname) 
    cdispositivo_long = cdispositivo_df.melt(
        id_vars=["Mes"],
        value_vars=["Total de VD presencial Válidas WEB", "Total de VD presencial Válidas MOVIL"],
        var_name="Dispositivo",
        value_name="Cantidad"
    )
    cdispositivo_long["Dispositivo"] = cdispositivo_long["Dispositivo"].str.extract(r'(WEB|MOVIL)')
    cdispositivo_long["Percent"] = cdispositivo_long.groupby("Mes")["Cantidad"].transform(lambda x: (x / x.sum() * 100).round(2))

    #st.dataframe(cdispositivo_long)
    
    fig_cdispositivo = px.bar(cdispositivo_long, x="Mes", y="Percent", color="Dispositivo", title="%",
                 #color_discrete_map=color_map,
                 text=cdispositivo_long.apply(lambda x: f"{x['Dispositivo']}<br>{x['Percent']:.1f}%", axis=1)
                )
    fig_cdispositivo.update_layout(
        barmode="relative",
        bargap=0.2,
        bargroupgap=0.1,
        showlegend=False,
        
        yaxis=dict(
            title="Porcentaje (%)",
            ticksuffix="%",
            range=[0, 100]
        )
    )
    fig_cdispositivo.update_traces(textposition="inside", textfont_size=14)
    
    
    
    
    
    st.dataframe(ctable_df)
    
    #fig = go.Figure()
    #fig.add_bar(x=percent_month_df["Mes"],y=percent_month_df["Percent"])
    #fig.add_bar(x=percent_month_df["Mes"],y=[6,5,4,3,2,1])
    #fig.update_layout(barmode="relative")
    orden_estados = [
        "Rechazado",
        "No Encontrado",
        "Visitas Incompletas",
        "Visitas Completas",
    ]
    percent_month_df["Estado Visitas"] = pd.Categorical(
        percent_month_df["Estado Visitas"],
        categories=orden_estados,
        ordered=True
    )
    percent_month_df = percent_month_df.sort_values(["Mes", "Estado Visitas"])
    percent_month_df["Mes"] = percent_month_df["Mes"].map(mes_compname)
    
    
    figure_carg = px.bar(ctable_df, x="Mes", y="Niños Cargados", title="Número de Niños Cargados por Mes - Tramo III",text="Niños Cargados")
    figure_carg.update_traces(textposition="outside", textfont_size=16)
    
    
    
    
    
    
    
    color_map = {
        "Visitas Completas": "#1976D2",    # azul
        "Visita Domiciliaria": "#1976D2",  
        "Visitas Incompletas": "#D32F2F",  # rojo
        "No Encontrado": "#757575",         # plomo
        "Rechazado": "#FFC107"              # ambar
    }
    fig = px.bar(percent_month_df, x="Mes", y="Percent", color="Estado Visitas", title="%",
                 color_discrete_map=color_map,
                 text=percent_month_df.apply(lambda x: f"{x['Estado Visitas']}<br>{x['Percent']:.1f}%", axis=1)
                )
    fig.update_layout(
        barmode="relative",
        bargap=0.2,
        bargroupgap=0.1,
        showlegend=False,
        
        yaxis=dict(
            title="Porcentaje (%)",
            ticksuffix="%",
            range=[0, 100]
        )
    )
    fig.update_traces(textposition="inside", textfont_size=14)
    
    fig_cdispositivo.update_layout(title_text="Porcentaje de Visitas por Dispositivo - Niños Tramo III")
    figure_carg.update_layout(title_text="Número de Niños Cargados por Mes - Tramo III")
    fig.update_layout(title_text="Distribución porcentual de Estado de Visitas - Niños Tramo III")
    
    col_1 , col_2 = st.columns([8,4])
    with col_1:
        st.plotly_chart(fig, use_container_width=False)
    with col_2:
        st.plotly_chart(figure_carg)
    col_1r, col_2r = st.columns(2)
    with col_1r:
        st.plotly_chart(fig_cdispositivo)
    
    #####################################################################################################
    st.subheader("Gestantes")
    df_gestantes = pd.read_parquet(f"./data/1.3/indicador_gestantes_enero.parquet")
    df_gestantes_feb = pd.read_parquet(f"./data/1.3/indicador_gestantes_febrero.parquet")
    df_gestantes_mar = pd.read_excel(f"./data/1.3/gestantes_reporte_Mar_final_mes.xlsx")
    df_gestantes_abr = pd.read_excel(f"./data/1.3/gestantes_reporte_Abr_final_mes.xlsx")
    df_gestantes_may = pd.read_excel(f"./data/1.3/gestantes_reporte_May_final_mes.xlsx")
    csummary_gestantes = pd.concat([df_gestantes, df_gestantes_feb, df_gestantes_mar,df_gestantes_abr,df_gestantes_may], ignore_index=True)
    csummary_gestantes["Etapa"] = csummary_gestantes["Etapa"].replace({
        "Visita Domiciliaria (Adolescente)": "Visita Domiciliaria",
        "Visita Domiciliaria (Adulta)": "Visita Domiciliaria",
    })
    #csummary_gestantes.to_excel("csummary_gestantes.xlsx", index=False)
    #st.dataframe(csummary_gestantes)
    #st.write(csummary_gestantes)
    ###PORCENTAJE INDICADOR
    percent_month_gestantes_df = csummary_gestantes.groupby(["Mes","Etapa"]).agg({"Año": "count"}).reset_index().rename(columns={"Año": "Cantidad"})
    percent_month_gestantes_df["Percent"] = (percent_month_gestantes_df.groupby("Mes")["Cantidad"].transform(lambda x: x / x.sum() * 100)).round(2)
    percent_month_gestantes_df = percent_month_gestantes_df.sort_values(by="Etapa", ascending=True)
    orden_estados_2 = [
        "Rechazado",
        "No Encontrado",
        "Visitas Incompletas",
        "Visita Domiciliaria",
    ]
    percent_month_gestantes_df["Etapa"] = pd.Categorical(
        percent_month_gestantes_df["Etapa"],
        categories=orden_estados_2,
        ordered=True
    )
    percent_month_gestantes_df = percent_month_gestantes_df.sort_values(["Mes", "Etapa"])
    percent_month_gestantes_df["Mes"] = percent_month_gestantes_df["Mes"].map(mes_compname)
    
    
    
    gtable_df = csummary_gestantes.groupby(["Mes"]).agg({
        "Año": "count",
        "Total de visitas completas para la edad": "sum",
        "Sector": "nunique", 
        "Nombres del Actor Social": "nunique",
        "Edad en Meses Hijo": lambda x: x.notna().sum(),
        "Etapa": lambda x: (x == "Visita Domiciliaria").sum()
    }).reset_index()#.rename(columns={"Año": "Cantidad"})
    #print(gtable_df.columns)
    gtable_df.columns = ['Mes', 'Gestantes Cargadas', 'Visitas Programadas', 'N° de Sectores Visitados',
       'N° de Actores Sociales', 'Puerperas', 'Gestantes Encontradas']
    csummary_vdges = pd.concat([
        pd.read_excel(f"./data/1.3/2025/vdges_2025_ene.xls",skiprows=7),
        pd.read_excel(f"./data/1.3/2025/vdges_2025_feb.xls",skiprows=7),
        pd.read_excel(f"./data/1.3/2025/vdges_2025_mar.xls",skiprows=7),
        pd.read_excel(f"./data/1.3/2025/vdges_2025_abr.xls",skiprows=7),
        pd.read_excel(f"./data/1.3/2025/vdges_2025_may.xls",skiprows=7),
    ], ignore_index=True)
    csummary_vdges["Mes"] = csummary_vdges["Mes"].map(mestext_short)
    
    #PROCENTAJE VD
    dispositivo_gest_df = csummary_vdges.groupby(["Mes","Dispositivo Intervención"]).agg({"Año": "count"}).reset_index().rename(columns={"Año": "Cantidad"})
    dispositivo_gest_df["Percent"] = (dispositivo_gest_df.groupby("Mes")["Cantidad"].transform(lambda x: x / x.sum() * 100)).round(2) 
    dispositivo_gest_df["Mes"] = dispositivo_gest_df["Mes"].map(mes_compname)
    #### PUERPERA - GESTANTES
    #st.dataframe(csummary_gestantes)
    csummary_gestantes["ESTADO_NACIMIENTO"] = csummary_gestantes["ESTADO_NACIMIENTO"].replace({"SIN DATO": "GESTANTE","MESES PASADOS": "PUERPERA"})
    etap_gest_df = csummary_gestantes.groupby(["Mes","ESTADO_NACIMIENTO"]).agg({"Año": "count"}).reset_index().rename(columns={"Año": "Cantidad"})
    etap_gest_df["Percent"] = (etap_gest_df.groupby("Mes")["Cantidad"].transform(lambda x: x / x.sum() * 100)).round(2) 
    etap_gest_df["Mes"] = etap_gest_df["Mes"].map(mes_compname)
    
    fig_etap_gest = px.bar(etap_gest_df, x="Mes", y="Percent", color="ESTADO_NACIMIENTO", title="%",
                 #color_discrete_map=color_map,
                 text=etap_gest_df.apply(lambda x: f"{x['ESTADO_NACIMIENTO']}<br>{x['Percent']:.1f}%", axis=1)
                )
    fig_etap_gest.update_layout(
        barmode="relative",
        bargap=0.2,     
        bargroupgap=0.1,
        showlegend=False,
        
        yaxis=dict(
            title="Porcentaje (%)",
            ticksuffix="%",
            range=[0, 100]  
        )
    )
    fig_etap_gest.update_traces(textposition="inside", textfont_size=14)
    fig_etap_gest.update_layout(title_text="Distribución porcentual del Estado Gestante - Gestantes Tramo III")
    
    
    
    
    
    
    fig_gest_disp= px.bar(dispositivo_gest_df, x="Mes", y="Percent", color="Dispositivo Intervención", title="%",
                 #color_discrete_map=color_map,
                 text=dispositivo_gest_df.apply(lambda x: f"{x['Dispositivo Intervención']}<br>{x['Percent']:.1f}%", axis=1)
                )
    fig_gest_disp.update_layout(
        barmode="relative",
        bargap=0.2,
        bargroupgap=0.1,
        showlegend=False,
        
        yaxis=dict(
            title="Porcentaje (%)",
            ticksuffix="%",
            range=[0, 100]
        )
    )
    fig_gest_disp.update_traces(textposition="inside", textfont_size=14)
    
    ####################
    
    gtable_vdges = csummary_vdges.groupby(["Mes"]).agg({
        "Dispositivo Intervención": [
            ("Visitas WEB", lambda x: (x == "WEB").sum()),
            ("Visitas MOVIL", lambda x: (x == "MOVIL").sum()),
        ]
    }).reset_index()
    
    # Aplanar la cabecera
    gtable_vdges.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in gtable_vdges.columns]
    gtable_vdges.columns = ["Mes","Visitas WEB","Visitas MOVIL"]
    gtable_vdges["Visitas Realizadas"] = gtable_vdges["Visitas WEB"] + gtable_vdges["Visitas MOVIL"]
    gtable_vdges = gtable_vdges[["Mes","Visitas Realizadas","Visitas WEB","Visitas MOVIL"]]
    
    # Unir los dataframes
    gtable_df = pd.merge(gtable_df, gtable_vdges, on="Mes", how="left")
    gtable_df["% Geo"] = round(gtable_df["Visitas MOVIL"] / gtable_df["Visitas Programadas"],3)*100
    gtable_df["% Indicador"] = round(gtable_df["Gestantes Encontradas"] / gtable_df["Gestantes Cargadas"],3)*100
    st.dataframe(gtable_df) 
    ######### CARGA POR MES
    carga_mes_gest_df = gtable_df.groupby("Mes").agg({"Gestantes Cargadas": "sum"}).reset_index()
    carga_mes_gest_df["Mes"] = carga_mes_gest_df["Mes"].map(mes_compname)
    #st.dataframe(carga_mes_gest_df)
    figure_carg_gest = px.bar(carga_mes_gest_df, x="Mes", y="Gestantes Cargadas", title="Número de Gestantes Cargadas por Mes - Tramo III",text="Gestantes Cargadas")
    figure_carg_gest.update_traces(textposition="outside", textfont_size=16)
    
    
    
    fig_gest = px.bar(percent_month_gestantes_df, x="Mes", y="Percent", color="Etapa", title="%",
                 color_discrete_map=color_map,
                 text=percent_month_gestantes_df.apply(lambda x: f"{x['Etapa']}<br>{x['Percent']:.1f}%", axis=1)
                )
    fig_gest.update_layout(
        barmode="relative",
        bargap=0.2,
        bargroupgap=0.1,
        showlegend=False,
        
        yaxis=dict(
            title="Porcentaje (%)",
            ticksuffix="%",
            range=[0, 100]
        )
    )
    fig_gest.update_traces(textposition="inside", textfont_size=14)
    
    fig_gest_disp.update_layout(title_text="Porcentaje de Visitas por Dispositivo - Gestantes Tramo III")
    figure_carg_gest.update_layout(title_text="Número de Gestantes Cargadas por Mes - Tramo III")
    fig_gest.update_layout(title_text="Distribución porcentual de Etapas - Gestantes Tramo III")
    
    col_1_r2 , col_2_r2 = st.columns([8,4])
    with col_1_r2:
            st.plotly_chart(fig_gest)
    with col_2_r2:
        st.plotly_chart(figure_carg_gest)
    col_1_r3 , col_2_r3 = st.columns(2)
    with col_1_r3:
        
        st.plotly_chart(fig_gest_disp)
    with col_2_r3:
        st.plotly_chart(fig_etap_gest)
     
    gtable_df["Mes"] = gtable_df["Mes"].map(mes_compname)   
    st.download_button(
                label="Tabla Niños",
                data=convert_excel_df(ctable_df),
                file_name=f"tramo3_niños.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button(
                label="Tabla Gestantes",
                data=convert_excel_df(gtable_df),
                file_name=f"tramo3_gestantes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

def summary_tramo3():
    styles(2)
    st.title("Resuemn Tramo test")
    
    #####################################################################################################
    color_map = {
        "Visitas Completas": "#1976D2",    # azul
        "Visita Domiciliaria": "#1976D2",  
        "Visitas Incompletas": "#D32F2F",  # rojo
        "No Encontrado": "#757575",         # plomo
        "Rechazado": "#FFC107"              # ambar
    }
    st.subheader("Gestantes")
    df_gestantes = pd.read_parquet(f"./data/1.3/indicador_gestantes_enero.parquet")
    df_gestantes_feb = pd.read_parquet(f"./data/1.3/indicador_gestantes_febrero.parquet")
    df_gestantes_mar = pd.read_excel(f"./data/1.3/gestantes_reporte_Mar_final_mes.xlsx")
    df_gestantes_abr = pd.read_excel(f"./data/1.3/gestantes_reporte_Abr_final_mes.xlsx")
    df_gestantes_may = pd.read_excel(f"./data/1.3/gestantes_reporte_May_final_mes.xlsx")
    csummary_gestantes = pd.concat([df_gestantes, df_gestantes_feb, df_gestantes_mar,df_gestantes_abr,df_gestantes_may], ignore_index=True)
    csummary_gestantes["Etapa"] = csummary_gestantes["Etapa"].replace({
        "Visita Domiciliaria (Adolescente)": "Visita Domiciliaria",
        "Visita Domiciliaria (Adulta)": "Visita Domiciliaria",
    })
    csummary_gestantes["ESTADO_NACIMIENTO"] = csummary_gestantes["ESTADO_NACIMIENTO"].replace({
        "SIN DATO": "GESTANTE",
        "MESES PASADOS": "PUERPERA",
    })
    
    csummary_gestantes["Mes"] = csummary_gestantes["Mes"].map(mes_short)
    
    csummary_gestantes["Status"] = csummary_gestantes["Etapa"]+" - "+csummary_gestantes["ESTADO_NACIMIENTO"]
    st.dataframe(csummary_gestantes)
    st.write(len(csummary_gestantes["Número de Documento"].unique()))
    csummary_gestantes["Fecha Nacimiento Hijo"] = csummary_gestantes["Fecha Nacimiento Hijo"].fillna("-")
    dff = csummary_gestantes.groupby(["Número de Documento","Mes"])[["Status"]].sum().reset_index()
    csummary_gestantes["Mes_"] = csummary_gestantes["Mes"]+" - "
    csummary_gestantes["Estado Visita"] = csummary_gestantes["Etapa"]+" - "
    periodos_dff = csummary_gestantes.groupby(["Número de Documento"])[["Mes_","Estado Visita"]].sum().reset_index()
    periodos_dff["Mes_"] = periodos_dff["Mes_"].str[:-2]
    periodos_dff["Fue NO ENCONTRADO?"] = periodos_dff["Estado Visita"].apply(lambda x: True if "No Encontrado" in str(x) else False) 
    #st.write(periodos_dff)
    dff_pivot = dff.pivot(index=["Número de Documento"], columns="Mes", values="Status")
    #st.write(dff.shape[0])
    #st.write(dff_pivot.shape)
    #st.dataframe(dff_pivot)
    merge_df = pd.merge(dff_pivot, periodos_dff, on="Número de Documento", how="left")
    merge_df = merge_df[['Número de Documento','Mes_','Fue NO ENCONTRADO?',  'Ene', 'Feb', 'Mar','Abr', 'May']]
    
    st.write(merge_df.shape)
    st.dataframe(merge_df)
    datos_gestantes = pd.read_parquet(f"datos_gestantes.parquet")
    datos_gestantes = datos_gestantes.groupby(["Documento","Gestante"])[["Visitas_num"]].sum().reset_index()
    datos_gestantes = datos_gestantes[["Documento","Gestante"]]
    datos_gestantes.columns = ["Número de Documento","Datos Gestante"]

    st.dataframe(datos_gestantes)
    merge_dff = pd.merge(merge_df, datos_gestantes, on="Número de Documento", how="left")
    merge_dff = merge_dff[['Número de Documento','Datos Gestante', 'Mes_', 'Fue NO ENCONTRADO?', 'Ene', 'Feb',
       'Mar', 'Abr', 'May']]
    merge_dff = merge_dff.rename(columns={"Mes_": "Periodos"})
    st.write(merge_dff.shape)
    

    fecha_nac_df = csummary_gestantes.groupby(["Número de Documento","Fecha Nacimiento Hijo"])[["Status"]].count().reset_index()
    fecha_nac_df = fecha_nac_df[fecha_nac_df["Fecha Nacimiento Hijo"] != "-"]
    #fecha_nac_df.to_excel("fecha_nac_df.xlsx", index=False)
    st.write(fecha_nac_df.shape)
    merge_dff = pd.merge(merge_dff, fecha_nac_df, on="Número de Documento", how="left")
    merge_dff = merge_dff[['Número de Documento','Datos Gestante', 'Periodos', 'Fue NO ENCONTRADO?', 'Ene', 'Feb',
       'Mar', 'Abr', 'May','Fecha Nacimiento Hijo']]
    merge_dff["Datos Gestante"] = merge_dff["Datos Gestante"].str.upper()
    st.write(merge_dff.shape)
    st.dataframe(merge_dff)
    merge_dff.to_excel("Estado Gestantes TRAMO III.xlsx", index=False)
   
    #st.dataframe(csummary_gestantes)
    #st.write(csummary_gestantes)
    ###PORCENTAJE INDICADOR







































    """
    percent_month_gestantes_df = csummary_gestantes.groupby(["Mes","Etapa"]).agg({"Año": "count"}).reset_index().rename(columns={"Año": "Cantidad"})
    percent_month_gestantes_df["Percent"] = (percent_month_gestantes_df.groupby("Mes")["Cantidad"].transform(lambda x: x / x.sum() * 100)).round(2)
    percent_month_gestantes_df = percent_month_gestantes_df.sort_values(by="Etapa", ascending=True)
    orden_estados_2 = [
        "Rechazado",
        "No Encontrado",
        "Visitas Incompletas",
        "Visita Domiciliaria",
    ]
    percent_month_gestantes_df["Etapa"] = pd.Categorical(
        percent_month_gestantes_df["Etapa"],
        categories=orden_estados_2,
        ordered=True
    )
    percent_month_gestantes_df = percent_month_gestantes_df.sort_values(["Mes", "Etapa"])
    percent_month_gestantes_df["Mes"] = percent_month_gestantes_df["Mes"].map(mes_compname)
    
    
    
    gtable_df = csummary_gestantes.groupby(["Mes"]).agg({
        "Año": "count",
        "Total de visitas completas para la edad": "sum",
        "Sector": "nunique", 
        "Nombres del Actor Social": "nunique",
        "Edad en Meses Hijo": lambda x: x.notna().sum(),
        "Etapa": lambda x: (x == "Visita Domiciliaria").sum()
    }).reset_index()#.rename(columns={"Año": "Cantidad"})
    #print(gtable_df.columns)
    gtable_df.columns = ['Mes', 'Gestantes Cargadas', 'Visitas Programadas', 'N° de Sectores Visitados',
       'N° de Actores Sociales', 'Puerperas', 'Gestantes Encontradas']
    csummary_vdges = pd.concat([
        pd.read_excel(f"./data/1.3/2025/vdges_2025_ene.xls",skiprows=7),
        pd.read_excel(f"./data/1.3/2025/vdges_2025_feb.xls",skiprows=7),
        pd.read_excel(f"./data/1.3/2025/vdges_2025_mar.xls",skiprows=7),
        pd.read_excel(f"./data/1.3/2025/vdges_2025_abr.xls",skiprows=7),
        pd.read_excel(f"./data/1.3/2025/vdges_2025_may.xls",skiprows=7),
    ], ignore_index=True)
    csummary_vdges["Mes"] = csummary_vdges["Mes"].map(mestext_short)
    
    #PROCENTAJE VD
    dispositivo_gest_df = csummary_vdges.groupby(["Mes","Dispositivo Intervención"]).agg({"Año": "count"}).reset_index().rename(columns={"Año": "Cantidad"})
    dispositivo_gest_df["Percent"] = (dispositivo_gest_df.groupby("Mes")["Cantidad"].transform(lambda x: x / x.sum() * 100)).round(2) 
    dispositivo_gest_df["Mes"] = dispositivo_gest_df["Mes"].map(mes_compname)
    #### PUERPERA - GESTANTES
    #st.dataframe(csummary_gestantes)
    csummary_gestantes["ESTADO_NACIMIENTO"] = csummary_gestantes["ESTADO_NACIMIENTO"].replace({"SIN DATO": "GESTANTE","MESES PASADOS": "PUERPERA"})
    etap_gest_df = csummary_gestantes.groupby(["Mes","ESTADO_NACIMIENTO"]).agg({"Año": "count"}).reset_index().rename(columns={"Año": "Cantidad"})
    etap_gest_df["Percent"] = (etap_gest_df.groupby("Mes")["Cantidad"].transform(lambda x: x / x.sum() * 100)).round(2) 
    etap_gest_df["Mes"] = etap_gest_df["Mes"].map(mes_compname)
    
    fig_etap_gest = px.bar(etap_gest_df, x="Mes", y="Percent", color="ESTADO_NACIMIENTO", title="%",
                 #color_discrete_map=color_map,
                 text=etap_gest_df.apply(lambda x: f"{x['ESTADO_NACIMIENTO']}<br>{x['Percent']:.1f}%", axis=1)
                )
    fig_etap_gest.update_layout(
        barmode="relative",
        bargap=0.2,     
        bargroupgap=0.1,
        showlegend=False,
        
        yaxis=dict(
            title="Porcentaje (%)",
            ticksuffix="%",
            range=[0, 100]  
        )
    )
    fig_etap_gest.update_traces(textposition="inside", textfont_size=14)
    fig_etap_gest.update_layout(title_text="Distribución porcentual del Estado Gestante - Gestantes Tramo III")
    
    
    
    
    
    
    fig_gest_disp= px.bar(dispositivo_gest_df, x="Mes", y="Percent", color="Dispositivo Intervención", title="%",
                 #color_discrete_map=color_map,
                 text=dispositivo_gest_df.apply(lambda x: f"{x['Dispositivo Intervención']}<br>{x['Percent']:.1f}%", axis=1)
                )
    fig_gest_disp.update_layout(
        barmode="relative",
        bargap=0.2,
        bargroupgap=0.1,
        showlegend=False,
        
        yaxis=dict(
            title="Porcentaje (%)",
            ticksuffix="%",
            range=[0, 100]
        )
    )
    fig_gest_disp.update_traces(textposition="inside", textfont_size=14)
    
    ####################
    
    gtable_vdges = csummary_vdges.groupby(["Mes"]).agg({
        "Dispositivo Intervención": [
            ("Visitas WEB", lambda x: (x == "WEB").sum()),
            ("Visitas MOVIL", lambda x: (x == "MOVIL").sum()),
        ]
    }).reset_index()
    
    # Aplanar la cabecera
    gtable_vdges.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in gtable_vdges.columns]
    gtable_vdges.columns = ["Mes","Visitas WEB","Visitas MOVIL"]
    gtable_vdges["Visitas Realizadas"] = gtable_vdges["Visitas WEB"] + gtable_vdges["Visitas MOVIL"]
    gtable_vdges = gtable_vdges[["Mes","Visitas Realizadas","Visitas WEB","Visitas MOVIL"]]
    
    # Unir los dataframes
    gtable_df = pd.merge(gtable_df, gtable_vdges, on="Mes", how="left")
    gtable_df["% Geo"] = round(gtable_df["Visitas MOVIL"] / gtable_df["Visitas Programadas"],3)*100
    gtable_df["% Indicador"] = round(gtable_df["Gestantes Encontradas"] / gtable_df["Gestantes Cargadas"],3)*100
    st.dataframe(gtable_df) 
    ######### CARGA POR MES
    carga_mes_gest_df = gtable_df.groupby("Mes").agg({"Gestantes Cargadas": "sum"}).reset_index()
    carga_mes_gest_df["Mes"] = carga_mes_gest_df["Mes"].map(mes_compname)
    #st.dataframe(carga_mes_gest_df)
    
    figure_carg_gest = px.bar(carga_mes_gest_df, x="Mes", y="Gestantes Cargadas", title="Número de Gestantes Cargadas por Mes - Tramo III",text="Gestantes Cargadas")
    figure_carg_gest.update_traces(textposition="outside", textfont_size=16)
    
    
    
    fig_gest = px.bar(percent_month_gestantes_df, x="Mes", y="Percent", color="Etapa", title="%",
                 color_discrete_map=color_map,
                 text=percent_month_gestantes_df.apply(lambda x: f"{x['Etapa']}<br>{x['Percent']:.1f}%", axis=1)
                )
    fig_gest.update_layout(
        barmode="relative",
        bargap=0.2,
        bargroupgap=0.1,
        showlegend=False,
        
        yaxis=dict(
            title="Porcentaje (%)",
            ticksuffix="%",
            range=[0, 100]
        )
    )
    fig_gest.update_traces(textposition="inside", textfont_size=14)
    
    fig_gest_disp.update_layout(title_text="Porcentaje de Visitas por Dispositivo - Gestantes Tramo III")
    figure_carg_gest.update_layout(title_text="Número de Gestantes Cargadas por Mes - Tramo III")
    fig_gest.update_layout(title_text="Distribución porcentual de Etapas - Gestantes Tramo III")
    
    col_1_r2 , col_2_r2 = st.columns([8,4])
    with col_1_r2:
            st.plotly_chart(fig_gest)
    with col_2_r2:
        st.plotly_chart(figure_carg_gest)
    col_1_r3 , col_2_r3 = st.columns(2)
    with col_1_r3:
        
        st.plotly_chart(fig_gest_disp)
    with col_2_r3:
        st.plotly_chart(fig_etap_gest)
     
    gtable_df["Mes"] = gtable_df["Mes"].map(mes_compname)   
    st.download_button(
                label="Tabla Niños",
                data=convert_excel_df(ctable_df),
                file_name=f"tramo3_niños.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button(
                label="Tabla Gestantes",
                data=convert_excel_df(gtable_df),
                file_name=f"tramo3_gestantes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
"""