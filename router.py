import streamlit as st

from views.home import index
from views.visitas_childs import geo_childs
from views.visitas_gestantes import geo_gestantes
from views.padron_nominal import dash_padron
from views.actualizaciones_padron import dash_padron_modreg
from views.indicadores_childs import indicadores_childs
from views.indicadores_gestantes import indicadores_gestantes
#if 'key' not in st.session_state:
#    with open("config.yaml", "r") as f:
#        config = yaml.safe_load(f)
        
home = [st.Page(page = index,title="Home",icon = ":material/home:")]

visitas = [
    st.Page(page = geo_childs,title="Georeferencias Niños",icon = ":material/home:"),
    st.Page(page = geo_gestantes,title="Georeferencias Gestantes",icon = ":material/home:"),
]
padron = [
    st.Page(page = dash_padron,title="Padrón Nominal",icon = ":material/home:"),
    st.Page(page = dash_padron_modreg,title="Actualización Padrón",icon = ":material/home:"),
]

indicadores = [
    st.Page(page = indicadores_childs,title="Indicador 1.2",icon = ":material/home:"),
    st.Page(page = indicadores_gestantes,title="Indicador 1.3",icon = ":material/home:"),
]

#monitores = [
#    st.Page("./views/monitores/pages/monitorAbastecimiento.py",title="Monitor Abastecimiento",icon = ":material/inventory:",),
    
#]


def pages():
    page_dict = {}
    page_dict["Home"] = home
    page_dict["Geo"] = visitas
    page_dict["Padron N"] = padron
    page_dict["Indicadores C1"] = indicadores
    return page_dict