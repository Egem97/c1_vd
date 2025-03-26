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

def status24_nominal_ges():
    styles(2)
    fecha_actual = datetime.now()
    carga_df = fetch_carga_gestantes()
    vd_df = fetch_vd_gestantes()
    st.title("Visitas a Gestantes")
    
    
    dff = carga_df[(carga_df["Año"]=="2024")&(carga_df["Mes"].isin(["08","09","10","11","12"]))]
    #st.dataframe(dff)
    #dff = dff[dff["Nombres del Actor Social"]=="FLORES SALAZAR, TERESA"]
    #st.write(dff.shape)
    #print(dff.columns)
    #st.dataframe(dff)
    #ssd = dff.groupby(["Mes"])[["Año"]].count().reset_index()
    
    mes_ess_df = dff.groupby(["Establecimiento de Salud"])[['Total de VD presencial Válidas WEB','Total de VD presencial Válidas MOVIL']].sum().reset_index()
    mes_ess_df =mes_ess_df.sort_values("Total de VD presencial Válidas WEB",ascending=False)
    total_row = pd.DataFrame({'Establecimiento de Salud': ['Total'], 
                 'Total de VD presencial Válidas WEB': mes_ess_df['Total de VD presencial Válidas WEB'].sum(),
                 'Total de VD presencial Válidas MOVIL': mes_ess_df['Total de VD presencial Válidas MOVIL'].sum()})
   
    mes_ess_df = pd.concat([mes_ess_df, total_row], ignore_index=True)
    #####
    mes_df = dff.groupby(["Mes"])[['Total de VD presencial Válidas WEB','Total de VD presencial Válidas MOVIL']].sum().reset_index()
    mes_df =mes_df.sort_values("Total de VD presencial Válidas WEB",ascending=False)
    total_row = pd.DataFrame({'Mes': ['Total'], 
                 'Total de VD presencial Válidas WEB': mes_df['Total de VD presencial Válidas WEB'].sum(),
                 'Total de VD presencial Válidas MOVIL': mes_df['Total de VD presencial Válidas MOVIL'].sum()})
   
    mes_df = pd.concat([mes_df, total_row], ignore_index=True)
    mes_df["Mes"] = mes_df["Mes"].replace({
        "08":"Agosto","09":"Setiembre","10":"Octubre","11":"Noviembre","12" : "Diciembre"
    })
    #ref_dff = dff.groupby(["Establecimiento de Salud","Número de Documento"])[["Total de VD presencial Válidas WEB","Total de VD presencial Válidas MOVIL"]].sum().reset_index()
    #st.write(ref_dff.shape)
    #st.dataframe(ref_dff)

    as_dff = dff.groupby(["Nombres del Actor Social","Mes"])[["Total de VD presencial Válidas WEB","Total de VD presencial Válidas MOVIL"]].sum().reset_index()
    as_dff.columns = ["Nombres del Actor Social","Mes","VD WEB","VD MOVIL"]
    asignados_dff = dff.groupby(["Nombres del Actor Social","Mes"])[["Número de Documento"]].count().reset_index()
    asignados_dff.columns = ["Nombres del Actor Social","Mes","Gestantes Asignados"]
    
    #total_row = pd.DataFrame({'Nombres del Actor Social': ['Total'], 
                 #'Total de VD presencial Válidas WEB': mes_df['Total de VD presencial Válidas WEB'].sum(),
                 #'Total de VD presencial Válidas MOVIL': mes_df['Total de VD presencial Válidas MOVIL'].sum()})
    #as_dff = pd.concat([as_dff, total_row], ignore_index=True)
    st.write(as_dff.shape)    
    st.dataframe(as_dff)
    join_df = pd.merge(asignados_dff, as_dff, left_on=["Nombres del Actor Social","Mes"], right_on=["Nombres del Actor Social","Mes"], how='left')
    
    as_c = ["BARRETO SANTA MARIA, ETHEL YAJAIRA",
        "CUEVA SANTOS, ANA ISABEL",
        "CUEVA SANTOS, KATY JUDITH",
        "DIAZ PASCUAL, KATERINE",
        "ESPINOLA CARRION, MALENI MEDALI",
        "GONZALEZ FERNANDEZ, DIANA CAROLINA",
        "HERNANDEZ SANCHEZ, KEILA CRISS",
        "IPANAQUE ROCHA, ANALI VALERIA",
        "LOPEZ CALDERON, PETRONILA HAYDEE",
        "LOYOLA LUJAN, YESSENIA ANALI",
        "LUJAN REYES, ROSA MARLENI",
        "MEZA ESPINO, MARIA DE LOS ANGELES LIZED",
        "ORUNA JULIAN, SHANELL IVETT",
        "PANTOJA DIAZ, CLAUDIA VANESSA",
        "RAMOS QUISPE, SEGUNDO BRAYAN",
        "RODRIGUEZ SAONA, KATHERIN LISSETH",
        "ROJAS HUATAY, YAJAIRA NICOL",
        "RUIZ FALLA, GLADYS GIOVANA",
        "RUIZ FALLA, MARGARITA CELINDA",
        "SANCHEZ VARGAS DE ULLOA, JESSICA YAJAIRA",
        "SILVA CASANOVA, REINA ELIZABETH",
        "TASILLA VIGO, MARTHA AMY",
        "TELLO CORONEL, TAMARA SASHENKA",
        "TERRONES SOBERON, LEONARDA",
        "VILOCHE JARA, SARITA",
    ]
    join_df = join_df[join_df["Nombres del Actor Social"].isin(as_c)].reset_index()
    st.write(join_df.shape)
    st.dataframe(join_df)
    df_pivot = join_df.pivot_table(
        index=['Nombres del Actor Social'], 
        columns='Mes', 
        values=["Gestantes Asignados","VD WEB","VD MOVIL"],
        aggfunc="sum", 
        fill_value=0
    )
    df_pivot = df_pivot.reset_index()
    st.write(df_pivot.shape)
    st.dataframe(df_pivot)

    """
    
        SDSADSADAS
    
    """
    st.subheader("Reporte de Actividades Gestantes",divider=True)
    vd_df = vd_df[(vd_df['Año']==2024)&(vd_df['Mes'].isin(["Ago"]))]#,"Set","Oct","Nov","Dic"
    
    asignados_dff = asignados_dff[asignados_dff["Nombres del Actor Social"].isin(as_c)].reset_index()
    asignados_dff['Nombres del Actor Social'] = asignados_dff['Nombres del Actor Social'].str.replace(',', '', regex=True)
    asignados_dff = asignados_dff.rename(columns={"Nombres del Actor Social":"Actores Sociales"})
    asignados_dff['Mes'] = asignados_dff['Mes'].replace({
    '08': 'Ago',
    '09': 'Set',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dic',
    })

    #asignados_dff = asignados_dff.groupby(["Actores Sociales","Mes"])[["Número de Documento"]].count().reset_index()
    st.write(asignados_dff.shape)
    st.write(asignados_dff)

    
    #WEB
    web_vd_df = vd_df[vd_df["Dispositivo Intervención"]=="WEB"]
    web_vd_df = web_vd_df.groupby(["Actores Sociales","Mes"])[["Dispositivo Intervención"]].count().reset_index()
    web_vd_df = web_vd_df.rename(columns={"Dispositivo Intervención":"VD Web"})
    
    # MOVIL
    movil_vd_df = vd_df[vd_df["Dispositivo Intervención"]=="MOVIL"]
    movilvd_df = movil_vd_df.groupby(["Actores Sociales","Mes"])[["Dispositivo Intervención"]].count().reset_index()
    movilvd_df = movilvd_df.rename(columns={"Dispositivo Intervención":"VD Movil"})
 


    st.subheader("wwwww",divider=True)
    st.write(asignados_dff)
    st.write(web_vd_df)
    st.write(movilvd_df)
    jopinss = pd.merge(asignados_dff, web_vd_df, left_on=["Actores Sociales","Mes"], right_on=["Actores Sociales","Mes"], how='left')
    
    jopinss = pd.merge(jopinss, movilvd_df, left_on=["Actores Sociales","Mes"], right_on=["Actores Sociales","Mes"], how='left')
    st.write(jopinss.shape)
    st.write(jopinss)
    df_pivot2 = jopinss.pivot_table(
        index=['Actores Sociales'], 
        columns='Mes', 
        values=["Gestantes Asignados","VD Web","VD Movil"],
        aggfunc="sum", 
        fill_value=0
    )
    df_pivot2 = df_pivot2.reset_index()
    st.write(df_pivot2.shape)
    st.write(df_pivot2)
    """
    st.download_button(
                label="Descargar resumen tramo 2",
                data=convert_excel_df(df_pivot),
                file_name=f"resultados_25_ac_tramo2.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    




    with st.expander("Descargas"):
        st.download_button(
                label="Descargar Reporte",
                data=convert_excel_df(mes_ess_df),
                file_name=f"TIPO_VD_POR_EESS_TRAMO2.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar Reporte2",
                data=convert_excel_df(mes_df),
                file_name=f"TIPO_VD_POR_MES_TRAMO2.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        #st.download_button(
        #        label="Descargar GESTANTE UNICAS 2024",
        #        data=convert_excel_df(ref_dff),
        #        file_name=f"Gestantes_Unicas_tramo2.xlsx",
        #        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #)"
"""