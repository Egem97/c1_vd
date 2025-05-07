import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import plotly.graph_objects as go
from styles import styles
from dateutil.relativedelta import relativedelta
from utils.cache_handler import *
from utils.helpers import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def actualizados_mes_padron():
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

    columnas_head = st.columns([4,3,3])
    with columnas_head[0]:
        st.title(":blue[Nacidos por Mes] :child:")
    with columnas_head[1]:
        st.subheader(f"Actualizado: {fecha_maxima}", divider=True)
    with columnas_head[2]:
        select_year = st.multiselect("Año:", years,[years[0], years[1]],)
        if len(select_year)> 0:
            df = df[df["Año"].isin(select_year)]
    
   
    #st.dataframe(df)
    dff = df.groupby(["Periodo","Año","Mes"])[["Tipo de Documento"]].count().sort_values(["Año","Mes"],ascending=True).reset_index()
    dff.columns = ["Periodo","Año","Mes","Niños"]
    #st.dataframe(dff)
    test_df = df[(df["ENTIDAD"]=="MUNICIPIO")&(df["USUARIO QUE MODIFICA"].isin(["18215881","SERVICIO DNI ESTADO"]))&(df["EJE VIAL"]!=" ")&(df["REFERENCIA DE DIRECCION"].notna())]#
    actu_mod_df = test_df.groupby(["Periodo","Año","Mes"])[["Tipo de Documento"]].count().sort_values(["Año","Mes"],ascending=True).reset_index()
    last_df = pd.merge(dff, actu_mod_df, left_on=["Periodo","Año","Mes"], right_on=["Periodo","Año","Mes"], how='left')
    last_df.columns = ["Periodo","Año","Mes","Nacidos","Actualizados"]
    last_df["Actualizados"] = last_df["Actualizados"].fillna(0)
    #st.write(test_df.shape)
    
    fig = go.Figure(data=[
    go.Bar(name='Nacidos', x=last_df["Periodo"], y=last_df["Nacidos"],text=last_df["Nacidos"]),
    go.Bar(name='Actualizados', x=last_df["Periodo"], y=last_df["Actualizados"],text=last_df["Actualizados"])
    ])
    # Change the bar mode
    fig.update_layout(barmode='group',title="Nacidos por Cada Mes (Población - Actualizaciones)")
    fig.update_traces(textposition='outside')
    fig.update_layout(uniformtext_minsize=16, uniformtext_mode='hide')
    st.plotly_chart(fig)
    table_df = last_df.copy()
    table_df["% Actualizacion"]= round((table_df["Actualizados"] / table_df["Nacidos"])*100,1)
    table_df['% Actualizacion'] = table_df['% Actualizacion'].astype(str)
    table_df['% Actualizacion'] = table_df['% Actualizacion']+"%"
    table_df["Sin Actualizar"] = table_df["Nacidos"] - table_df["Actualizados"]
    st.dataframe(table_df,hide_index=True)
    st.download_button(
                label="Descargar Fuente",
                data=convert_excel_df(df),
                file_name=f"act_nacidos_mes_padron.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )