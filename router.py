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
        #st.Page(page=c1_2025_avances, title="Avances C1 2025", icon="🎯", url_path="/avances-c1-2025"),
        #st.Page(page=generar_excel_seguimiento_nominal, title="Seguimiento Nominal", icon="🎯", url_path="/seguimiento-nominal"),
        st.Page(page=summary_tramo3_test, title="Tramo 3", icon="🎯", url_path="/tramo-3")
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