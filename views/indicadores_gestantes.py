import streamlit as st
import pandas as pd
from styles import styles
from utils.cache_handler import fetch_carga_childs,fetch_vd_childs
from utils.helpers import *

def indicadores_gestantes():
    st.title("Indicadores 1.3")