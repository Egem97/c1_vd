import streamlit as st
from views.home import index
from views.c1.seguimiento_vd_child import *
from views.c1.seguimiento_vd_ges import *
from views.actualizaciones_padron import dash_padron_modreg
from views.transitos_padron import analisis_transitos
from views.edad_padron import edades_padron
from views.padron.actualizados_mes import actualizados_mes_padron
from views.padron.revision_padron import revision_padron
from views.padron.estado_rn import rn_month_insert
from views.tramo_3.tramo3 import *
from views.visitas_childs import geo_childs
from views.visitas_gestantes import geo_gestantes
from views.c1.seguimiento_nominal import seg_nominal_view
from views.avances_25 import resumen25
from views.c1.pruebas import pruebas_seg
from views.indicadores_childs import capacitaciones_c1

def pages():
    page_dict = {}
    
    # Home
    page_dict["Home"] = [
        st.Page(page = index, title="Home", icon = ":material/home:", url_path="/")
    ]
    
    # Dashboards de Seguimiento VD Niños
    page_dict["Compromiso 1"] = [
        st.Page(page=visitas_ninos_dashboard, title="Visitas a Niños", icon="👶", url_path="/seguimiento-vd-ninos"),
        st.Page(page=gestantes_status_vd, title="Visitas a Gestantes", icon="🤰", url_path="/seguimiento-vd-gestantes"),
        st.Page(page=capacitaciones_c1, title="Capacitaciones C1", icon="🎓", url_path="/capacitaciones-c1"),
        #st.Page(page=summary_tramo3_test, title="Resumen 2025", icon="🎯", url_path="/resumen2025"),
        st.Page(page=geo_childs, title="Geo Niños", icon="📍", url_path="/visitas-childs"),
        #st.Page(page=geo_gestantes, title="Geo Gestantes", icon="📍", url_path="/visitas-gestantes"),
        #st.Page(page=wwww, title="TWWWWW", icon="🎯", url_path="/wwwww"),
        st.Page(page=buscar_sector_childs, title="Buscar Sector Niños", icon="🎯", url_path="/buscar-sector-childs"),
    ]
    page_dict["Padrón Nominal"] = [
        st.Page(page=dash_padron_modreg, title="Actualizaciones General", icon="💡", url_path="/actualizaciones-padron"),
        st.Page(page=analisis_transitos, title="Transitos", icon="🚗", url_path="/transitos-padron"),
        st.Page(page=edades_padron, title="Avances-Edades", icon="🧒", url_path="/edades-padron"),
        st.Page(page=actualizados_mes_padron, title="Nacimientos-Mes", icon="🧙‍♀️", url_path="/nacimientos-mes"),
        st.Page(page=revision_padron, title="Población-EESS", icon="🔍", url_path="/poblacion-eess"),
        st.Page(page=rn_month_insert, title="RN-Mes", icon="🔍", url_path="/rn-mes"),
    ]
    	

    return page_dict