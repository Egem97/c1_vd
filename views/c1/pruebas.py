import streamlit as st
import pandas as pd
import plotly.express as px
import re
from utils.cache_handler import fetch_vd_childs, fetch_carga_childs, fetch_padron
from utils.functions_data import *
from utils.charts import *
from utils.helpers import *
from styles import styles
from datetime import datetime
from constans import *
from st_aggrid import AgGrid, GridOptionsBuilder,JsCode
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font, Alignment, Protection
from io import BytesIO
from utils.g_sheet import *



def pruebas_seg():    
    styles(2)
    st.title("Pruebas de Seguimiento")
    @st.cache_data(show_spinner="Cargando datos...",ttl=6000)  # ,ttl=600
    def load_seg_nominal_data(select_mes):
        sn_month = {
            "Jun": "11nk2Z1DmVKaXthy_TRsYK8wYzQ_BW8sdcRSXGxuq4Zo",
            "Jul": "11nk2Z1DmVKaXthy_TRsYK8wYzQ_BW8sdcRSXGxuq4Zo",
            "Ago": "1-jE3mNODE9UXj3dN9G9ae5WLl_Kyow96gWxcB0pOAxo",
            "Set": "1-jE3mNODE9UXj3dN9G9ae5WLl_Kyow96gWxcB0pOAxo",
            "Oct": "1VUARWulWk039rov4fsyM8NJRNd-zWRHyKYhG9tHBefI",
            "Nov": "1XgsYbeYeX9nwyz7jj2PHBYiGcxZcXb9HIiw757XLCcQ",
            "Dic": "1XgsYbeYeX9nwyz7jj2PHBYiGcxZcXb9HIiw757XLCcQ",
        }
        return read_and_concatenate_sheets_optimized(          
            key_sheet=sn_month[select_mes],
                        sheet_names=[
                            "ARANJUEZ","CLUB DE LEONES","EL BOSQUE",'LOS GRANADOS "SAGRADO CORAZON"',
                            "CENTRO DE SALUD LA UNION","HOSPITAL DE ESPECIALIDADES BASI",
                            "LIBERTAD","LOS JARDINES","PESQUEDA III","SAN MARTIN DE PORRES"
                        ],
                        add_sheet_column=True  # Añade columna 'sheet_origen'
                    )
    df = load_seg_nominal_data("Oct")
    st.write(df.shape)
    st.dataframe(df)
    print(df.columns)
    print(df["Resultado de Hemoglobina de 06 MESES"].unique())
    print(df["Resultado de Hemoglobina de 12 MESES"].unique())