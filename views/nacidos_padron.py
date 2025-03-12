import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from styles import styles
from dateutil.relativedelta import relativedelta
from utils.cache_handler import *
from utils.helpers import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def nacimientos_padron():
    styles(2)
    df = fetch_padron()
    
    
    df["Documento"]= df["Documento"].astype(str)
    df['EESS'] = df['EESS'].fillna("NO ESPECIFICADO")
    df["NUMERO DE CELULAR"] = df["NUMERO DE CELULAR"].str.strip()
    df["FECHA DE NACIMIENTO"] = pd.to_datetime(df["FECHA DE NACIMIENTO"])
    df['FECHA DE NACIMIENTO'] =pd.to_datetime(df['FECHA DE NACIMIENTO'], format="%Y-%m-%d")#.dt.strftime('%Y-%m-%d')
    df['Año'] = df['FECHA DE NACIMIENTO'].dt.year
    df["Año"] = df["Año"].astype(str)
    df['Mes'] = df['FECHA DE NACIMIENTO'].dt.month
    df["Mes_"] = df.apply(lambda x:mes_short(x['Mes']),axis=1)
    df["Periodo"] = df["Año"]+' - '+df["Mes_"]
    fecha_maxima = df["FECHA DE NACIMIENTO"].max().strftime("%Y-%m-%d")
    years = df["Año"].unique()

    columnas_head = st.columns([6,3,3])
    with columnas_head[0]:
        st.title(":blue[Nacimientos] :child:")
    with columnas_head[1]:
        st.subheader(f"Actualizado: {fecha_maxima}", divider=True)
    with columnas_head[2]:
        select_year = st.multiselect("Año:", years,[years[0], years[1]],)
        if len(select_year)> 0:
            df = df[df["Año"].isin(select_year)]
    dff = df.groupby(["Periodo","Año","Mes"])[["Tipo de Documento"]].count().sort_values(["Año","Mes"],ascending=True).reset_index()
    dff.columns = ["Periodo","Año","Mes","Niños"]
    fig_periodo_count = px.bar(dff, x="Periodo", y="Niños",text="Niños", title='Niños Nacidos por Periodo')
    fig_periodo_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_periodo_count.update_layout(xaxis=dict(title=dict(text="Periodo")),yaxis=dict(title=dict(text="Niños")),font=dict(size=16))
    fig_periodo_count.update_xaxes(type='category')

    df["Año"] = df["Año"].astype(str)
    mesdff = df.groupby(["Mes_","Mes","Año",])[["Tipo de Documento"]].count().sort_values(["Mes"],ascending=True).reset_index()
    mesdff.columns = ["Mes_","Mes","Año","Niños"]
    fig_year_month = px.bar(mesdff, x="Mes_",color="Año", y="Niños",text="Niños", title='Comparativa de Nacimientos por Mes',barmode="group",
                            category_orders={
                            "Año": ["2019", "2020", "2021", "2022","2023","2024","2025"],
                            "Mes_": ["Ene", "Feb", "Mar", "Abr","May","Jun","Jul","Ago","Set","Oct","Nov","Dic"],
                            
                            }
                    )
    fig_year_month.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    
    st.plotly_chart(fig_year_month)
    st.plotly_chart(fig_periodo_count)
    st.download_button(
                label="Descargar DATA",
                data=convert_excel_df(df),
                file_name=f"DATA_{fecha_maxima}_PADRON.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    