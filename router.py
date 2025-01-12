import streamlit as st

from views.home import index
from views.visitas_childs import vd_childs
#if 'key' not in st.session_state:
#    with open("config.yaml", "r") as f:
#        config = yaml.safe_load(f)
        
home = [st.Page(page = index,title="Home",icon = ":material/home:")]

visitas = [st.Page(page = vd_childs,title="Georeferencias Niños",icon = ":material/home:")]

#monitores = [
#    st.Page("./views/monitores/pages/monitorAbastecimiento.py",title="Monitor Abastecimiento",icon = ":material/inventory:",),
    
#]


def pages():
    page_dict = {}
    page_dict["Home"] = home
    page_dict["Visitas"] = visitas
    return page_dict