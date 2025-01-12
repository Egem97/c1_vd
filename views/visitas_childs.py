import streamlit as st
import pandas as pd
import plotly.express as px
import folium #Librería de mapas en Python
from streamlit_folium import st_folium #Widget de Streamlit para mostrar los mapas
from folium.plugins import MarkerCluster #Plugin para agrupar marcadores
from styles import styles
from utils.cache_handler import fetch_vd_childs

def vd_childs():
    styles(2)
    
    df = fetch_vd_childs()
    dff = df[df["Dispositivo Intervención"]=="MOVIL"]
    
    eess = list(dff["Establecimiento de Salud"].unique())
    year = list(dff["Año"].unique())
    month = list(dff["Mes"].unique())
    latitud_name = "Latitud Intervención"
    longitud_name = "Longitud Intervención"
    col_filt = st.columns([3,6,1,1])
    with col_filt[0]:
        st.title("Georef a Niños")
    with col_filt[1]:
        eess_selected = st.multiselect("Establecimientos de Salud",eess,placeholder="Escoja un Establecimiento de Salud")
        if len(eess_selected) > 0:
            dff = dff[dff["Establecimiento de Salud"].isin(eess_selected)]
    with col_filt[2]:
        year_selected = st.selectbox("Año",year)
        dff = dff[dff["Año"]==year_selected]
    with col_filt[3]:
        month_selected = st.selectbox("Mes",month)
        dff = dff[dff["Mes"]==month_selected]
    
    #st.write(dff.shape)
    
    tab1,tab2,=st.tabs(['Mapa','Datos'])
    with tab1:    
        #
        col_filt_map = st.columns([3,3,3,3])
        with col_filt_map[0]:
            as_selected = st.selectbox('Actor Social',options=sorted(list(dff["Actores Sociales"].unique())),placeholder="Escoja un actor social",index=None) 
            if as_selected != None:
                dff = dff[dff["Actores Sociales"] == as_selected]
        
        with col_filt_map[1]:
            doc_input = st.text_input("Buscar por Doc Niño")
            if len(doc_input) == 8 :
                dff = dff[dff["Número de Documento de Niño"] == doc_input]
                
            
        with col_filt_map[3]:
            parMapa = st.selectbox('Tipo Mapa',options=["open-street-map", "carto-positron","carto-darkmatter"])        

        
        fig = px.scatter_mapbox(
            dff,lat=latitud_name,lon=longitud_name, 
            color="Establecimiento de Salud", hover_name="Actores Sociales",
            hover_data=["Número de Documento de Niño","Fecha Intervención"],
            zoom=14,
            height=600,
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
        map_ = st.plotly_chart(fig, on_select="rerun")
        try:
            st.dataframe(dff[dff["Número de Documento de Niño"]==map_["selection"]["points"][0]["customdata"][0]])
        except:
            st.warning("Seleccione Niño Georreferenciado")
        
    with tab2:
        st.dataframe(dff,use_container_width=True)
        #st.dataframe(dff)
    