"""
import streamlit as st

from views.home import index
from views.visitas_childs import geo_childs,childs_status_vd
from views.visitas_gestantes import geo_gestantes,gestantes_status_vd
from views.padron_nominal import dash_padron
from views.actualizaciones_padron import dash_padron_modreg
from views.indicadores_childs import indicadores_childs
from views.indicadores_gestantes import indicadores_gestantes
from views.revision_asignacion import asignacion_mes
from views.sectorizacion import sectorizacion_helper
from views.child_review import review_child
from views.actores_sociales import as_vd
from views.helper_actividad_gestante import pivot_actividad_gestante,pivot_actividad_childs
from views.transitos_padron import analisis_transitos
from views.edad_padron import edades_padron
from views.seguimiento_childs import geo_vd_childs
from views.nacidos_padron import nacimientos_padron
from views.revision_2024 import status24
from views.testing import status24_nominal
from views.testing_gestantes import status24_nominal_ges
from views.no_cargados_childs import periodo_excluyentes
from views.padron.revision_padron import revision_padron
from views.padron.actualizados_mes import actualizados_mes_padron
from views.avances_25 import resumen25
from views.tramo_3.tramo3 import summary_tramo3
from views.padron.rn_obs import rn_verificacion_insert
from views.padron.estado_rn import rn_month_insert
#if 'key' not in st.session_state:
#    with open("config.yaml", "r") as f:
#        config = yaml.safe_load(f)
        
home = [st.Page(page = index,title="Home",icon = ":material/home:")]

visitas = [
    st.Page(page = geo_childs,title="Georeferencias Niños",icon = ":material/home:"),
    st.Page(page = geo_gestantes,title="Georeferencias Gestantes",icon = ":material/home:"),
    #st.Page(page = geo_vd_childs,title="Seguimiento Geo Niños",icon = ":material/home:"),
]
padron = [
    st.Page(page = dash_padron,title="Padrón Nominal",icon = ":material/home:"),
    st.Page(page = dash_padron_modreg,title="Actualización Padrón",icon = ":material/home:"),
    st.Page(page = analisis_transitos,title="Niños Transito",icon = ":material/home:"),
    st.Page(page = edades_padron,title="Edades Padrón",icon = ":material/home:"),
    st.Page(page = nacimientos_padron,title="Nacimientos",icon = ":material/home:"),
    st.Page(page = actualizados_mes_padron,title="Nacidos por Mes",icon = ":material/home:"),
    st.Page(page = revision_padron,title="EESS",icon = ":material/home:"),
    st.Page(page = rn_month_insert,title="Actualizaciones RN",icon = ":material/home:")
]

c1 = [
    st.Page(page = childs_status_vd,title="Indicador 1.2",icon = ":material/home:"),
    st.Page(page = gestantes_status_vd,title="Indicador 1.3",icon = ":material/home:"),
    st.Page(page = summary_tramo3,title="Resumen 2025",icon = ":material/home:"),
    
]

#indicadores = [
    
    #st.Page(page = as_vd,title="Actores Sociales",icon = ":material/home:"),
    #st.Page(page = periodo_excluyentes,title="No Cargados Periodo",icon = ":material/home:"),
    #st.Page(page = status24,title="Revisión 2024",icon = ":material/home:"),
    #st.Page(page = status24_nominal,title="Revisión Niños24",icon = ":material/home:"),
    #st.Page(page = status24_nominal_ges,title="Revisión Gestantes24",icon = ":material/home:"),
    #st.Page(page = indicadores_childs,title="Niños",icon = ":material/home:"),
    #st.Page(page = indicadores_gestantes,title="Gestantes",icon = ":material/home:"),
#]

helpers = [
    st.Page(page = asignacion_mes,title="Asignación Mes",icon = ":material/home:"),
    st.Page(page = sectorizacion_helper,title="Sectorización Help",icon = ":material/home:"),
    st.Page(page = review_child,title="Niño Revisión",icon = ":material/home:"),
    st.Page(page = pivot_actividad_childs,title="Generar Reporte Niño",icon = ":material/home:"),
    st.Page(page = pivot_actividad_gestante,title="Pivot VD Gestante",icon = ":material/home:"),
    st.Page(page = rn_verificacion_insert,title="Revisión RN EXCEL",icon = ":material/home:")
]
#monitores = [
#    st.Page("./views/monitores/pages/monitorAbastecimiento.py",title="Monitor Abastecimiento",icon = ":material/inventory:",),
    
#]


def pages():
    page_dict = {}
    page_dict["Home"] = home
    page_dict["Geo"] = visitas
    page_dict["Padron N"] = padron
    page_dict["Visitas C1"] = c1
    #page_dict["C1 Estatus"] = indicadores
    page_dict["Helpers"] = helpers
    return page_dict
"""