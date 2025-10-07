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



def pages():
    page_dict = {}
    
    # Home
    page_dict["Home"] = [
        st.Page(page = index, title="Home", icon = ":material/home:", url_path="/")
    ]
    
    # Dashboards de Seguimiento VD Niños
    page_dict["Compromiso 1"] = [
        st.Page(page=visitas_ninos_dashboard, title="Visitas a Niños", icon="👶", url_path="/seguimiento-vd-ninos"),
        #st.Page(page=, title="Visitas a Niños", icon="👶", url_path="/vd-ninos"),
        #st.Page(page=hb_data_c1, title="Hemoglobina", icon="🩸", url_path="/datos-hemoglobina"),
        #st.Page(page=estadisticas_dashboard, title="Indicador Niños", icon="📈", url_path="/indicador-anemia-ninos"),
        st.Page(page=gestantes_status_vd, title="Visitas a Gestantes", icon="🤰", url_path="/seguimiento-vd-gestantes"),
        #st.Page(page=resumen25, title="Avances C1 2025", icon="🎯", url_path="/avances-c1-2025"),
        #st.Page(page=generar_excel_seguimiento_nominal, title="Seguimiento Nominal", icon="🎯", url_path="/seguimiento-nominal"),
        #st.Page(page=summary_tramo3_test, title="Tramo 3", icon="🎯", url_path="/tramo-3"),
        st.Page(page=geo_childs, title="Geo Niños", icon="📍", url_path="/visitas-childs"),
        st.Page(page=geo_gestantes, title="Geo Gestantes", icon="📍", url_path="/visitas-gestantes"),
        st.Page(page=seg_nominal_view, title="Seguimiento Nominal", icon="🎯", url_path="/seguimiento-nominal"),
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