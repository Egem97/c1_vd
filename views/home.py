import streamlit as st
import pandas as pd
from styles import styles
from utils.cache_handler import fetch_carga_childs,fetch_vd_childs
from utils.helpers import *

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode 

def index():
    styles(1)
    carga_df = fetch_carga_childs()
    vd_df = fetch_vd_childs()
    carga_df['Mes_'] = carga_df.apply(lambda x: mes_short(x['Mes']),axis=1) 
    VD_ALL = carga_df.groupby(["Año","Mes","Mes_"])[["Total de visitas completas para la edad","Total de VD presenciales Realizadas","Total de VD presenciales Válidas","Total de VD presencial Válidas WEB","Total de VD presencial Válidas MOVIL"]].sum().reset_index()
    #VD_ALL["Valla mínima Georeferencias (73%)"] = round(VD_ALL["Total de VD presenciales Realizadas"] * 0.73,0)
    #VD_ALL["% Georeferencias"] = round((VD_ALL["Total de VD presencial Válidas MOVIL"]/VD_ALL["Total de VD presenciales Realizadas"])*100,2)
    cargados_mes = carga_df.groupby(["Año","Mes","Mes_"])[["Rango de Edad"]].count().reset_index()
    cargados_mes = cargados_mes.rename(columns= {"Rango de Edad":"Niños Programados"})
    #NO ENCONTRADOS
    no_en_actividad_df = vd_df[vd_df["Etapa"].isin(["No Encontrado"])]
    noencon_df = no_en_actividad_df.groupby(["Año","Mes"])[["Rango de Edad"]].count().reset_index()
    noencon_df = noencon_df.rename(columns= {"Rango de Edad":"No Encontrados"})
    noencon_df["Mes_"] = noencon_df.apply(lambda x: mestext_short(x['Mes']),axis=1) 
    noencon_df["Año"] = noencon_df["Año"].astype(int)
    noencon_df["Mes_"] = noencon_df["Mes_"].astype(int)
    #RECHAZADOS 
    rechazados_df = vd_df[vd_df["Etapa"].isin(["Rechazado"])]
    rechazados_df = rechazados_df.groupby(["Año","Mes"])[["Rango de Edad"]].count().reset_index()
    rechazados_df = rechazados_df.rename(columns= {"Rango de Edad":"Rechazados"})
    rechazados_df["Mes_"] = rechazados_df.apply(lambda x: mestext_short(x['Mes']),axis=1) 
    rechazados_df["Año"] = rechazados_df["Año"].astype(int)
    rechazados_df["Mes_"] = rechazados_df["Mes_"].astype(int)
    st.title("resumen")
    #cargados + visitados
    join_df = pd.merge(cargados_mes, VD_ALL, left_on=["Año","Mes"], right_on=["Año","Mes"], how='left')
    join_df= join_df.drop(["Mes__y"], axis=1)
    join_df = join_df.rename(columns= {"Mes__x":"Mes_"})
    print(join_df.info())
    print(noencon_df.info())
    #st.dataframe(join_df)
    #st.dataframe(noencon_df)
    ## TABLA + no encontrados
    join_noen_df = pd.merge(join_df, noencon_df, left_on=["Año","Mes"], right_on=["Año","Mes_"], how='left')
    join_noen_df= join_noen_df.drop(["Mes__y","Mes_y"], axis=1)
    join_noen_df = join_noen_df.rename(columns= {"Mes__x":"Mes_","Mes_x":"Mes"})
    
    ## TABLA JOIN + RECHAZADOS
    join_rech_df = pd.merge(join_noen_df, rechazados_df, left_on=["Año","Mes"], right_on=["Año","Mes_"], how='left')
    join_rech_df= join_rech_df.drop(["Mes__y","Mes_y"], axis=1)
    join_rech_df = join_rech_df.rename(columns= {"Mes__x":"Mes_","Mes_x":"Mes"})
    join_rech_df["Rechazados"] = join_rech_df["Rechazados"].fillna(0)
    AgGrid(join_rech_df, # Dataframe a mostrar
            #height=900, # Altura de la tabla
            width='100%', # Ancho de la tabla
            #theme='alpine'
    )
    #st.dataframe(join_rech_df)
    