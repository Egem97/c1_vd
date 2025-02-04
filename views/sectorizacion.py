import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from styles import styles
from utils.cache_handler import *

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode 

def sectorizacion_helper():
    styles(1)
    carga_df = fetch_carga_childs()
    vd_df = fetch_vd_childs()
    dff = carga_df[[
        "Dirección",'Zona', 'Manzana', 'Sector', 'Establecimiento de Salud',"Total de visitas completas para la edad"
    ]]
    only_direccion_sector = dff.groupby(['Dirección','Zona', 'Manzana', 'Sector','Establecimiento de Salud'])[["Total de visitas completas para la edad"]].count().reset_index()
    
    cols = st.columns([3,5,2])
    with cols[0]:
        st.title("Sectorización")
    with cols[1]:
        direccion = st.text_input("Ingrese dirección")
    with cols[2]:
         parMapa = st.selectbox('Tipo Mapa',options=["open-street-map", "carto-positron","carto-darkmatter"])
    #with cols[1]:
    #     )
    if direccion:
    #if btn:
        dfff = only_direccion_sector[only_direccion_sector["Dirección"].str.contains(direccion.upper())]
        dfff = dfff[['Dirección', 'Zona', 'Manzana', 'Sector', 'Establecimiento de Salud']]
        gb = GridOptionsBuilder.from_dataframe(dfff)
        gb.configure_selection('multiple', use_checkbox=True) 
        grid_options = gb.build()
        grid_response = AgGrid(dfff, # Dataframe a mostrar
                            gridOptions=grid_options,
                            enable_enterprise_modules=False,
                            #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                            update_mode='MODEL_CHANGED',
                            fit_columns_on_grid_load=True,
                        
        )
        
        try:
            seleccionados = list(grid_response['selected_rows']["Dirección"])
            vd_dff_check = vd_df[vd_df["Dirección"].isin(seleccionados)]
            vd_dff_check = vd_dff_check[vd_dff_check["Dispositivo Intervención"]=="MOVIL"]
            
            vd_dff_check = vd_dff_check.groupby(['Establecimiento de Salud','Dirección','Latitud Intervención', 'Longitud Intervención'])[["Año"]].count().reset_index()
            #st.write(seleccionados)
            fig = px.scatter_mapbox(
                    vd_dff_check,lat="Latitud Intervención",lon="Longitud Intervención", 
                    color="Establecimiento de Salud", hover_name="Dirección",
                    #hover_data=["Fecha Intervención"],
                    zoom=16,
                    height=500,
                    #color_continuous_scale=px.colors.cyclical.IceFire
                )
            fig.update_layout(mapbox_style=parMapa)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            fig.update_layout(legend=dict(
                    orientation="h",
                    #entrywidth=70,
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))
            st.plotly_chart(fig,use_container_width=True)
        except:
            st.warning("Click en Dirección para ver mapa")
            #st.dataframe(vd_dff_check)