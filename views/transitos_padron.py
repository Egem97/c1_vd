import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from styles import styles
from dateutil.relativedelta import relativedelta
from utils.cache_handler import *
from utils.helpers import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode



def analisis_transitos():
    styles(2)
    df = fetch_padron()
    carga_df = fetch_carga_childs()
    MESES = ["Ene","Feb","Mar","Abr","May"]
    df["Documento"]= df["Documento"].astype(str)
    df['EESS'] = df['EESS'].fillna("NO ESPECIFICADO")
    df["NUMERO DE CELULAR"] = df["NUMERO DE CELULAR"].str.strip()
    df["FECHA DE MODIFICACIÓN DEL REGISTRO"] = pd.to_datetime(df["FECHA DE MODIFICACIÓN DEL REGISTRO"])
    
    carga_df["Número de Documento del niño"] = carga_df["Número de Documento del niño"].astype(str)
    
    
    #df["FECHA DE MODIFICACIÓN DEL REGISTRO"] = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].dt.strftime("%Y-%m-%d")
    fecha_maxima = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].max().strftime("%Y-%m-%d")
    fecha_minima = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].min().strftime("%Y-%m-%d")
    transitos_df = df[df["Tipo_file"]=="Activos Transito"]

    columnas_head = st.columns([6,3,3])
    with columnas_head[0]:
        st.title(":blue[Niños Transito] :child:")
    with columnas_head[1]:
        st.subheader(f"Actualizado: {fecha_maxima}", divider=True)
    with columnas_head[2]:
        st.subheader(f"N° Niños Transito: {transitos_df.shape[0]}", divider=True)
    
    del df

    #st.dataframe(transitos_df)
    transitos_df['FECHA DE MODIFICACIÓN DEL REGISTRO'] =pd.to_datetime(transitos_df['FECHA DE MODIFICACIÓN DEL REGISTRO'], format="%Y-%m-%d")#.dt.strftime('%Y-%m-%d')
    transitos_df['Año'] = transitos_df['FECHA DE MODIFICACIÓN DEL REGISTRO'].dt.year
    transitos_df["Año"] = transitos_df["Año"].astype(str)
    transitos_df['Mes'] = transitos_df['FECHA DE MODIFICACIÓN DEL REGISTRO'].dt.month
    transitos_df["Mes_"] = transitos_df.apply(lambda x:mes_short(x['Mes']),axis=1)
    transitos_df["Periodo"] = transitos_df["Año"]+' - '+transitos_df["Mes_"]


    line_time_fecha_df = transitos_df.groupby(["FECHA DE MODIFICACIÓN DEL REGISTRO"])[["Tipo de Documento"]].count().reset_index()
    line_time_fecha_df.columns = ["FECHA DE MODIFICACIÓN DEL REGISTRO","Niños"]
    line_time_year_df = transitos_df.groupby(["Año"])[["Tipo de Documento"]].count().reset_index()
    line_time_year_df.columns = ["Año","Niños"]
    line_time_month_df = transitos_df.groupby(["Periodo","Año","Mes"])[["Tipo de Documento"]].count().sort_values(["Año","Mes"],ascending=True).reset_index()
    line_time_month_df.columns = ["Periodo","Año","Mes","Niños"]

    eess_top = transitos_df.groupby(["EESS"])[["Tipo de Documento"]].count().sort_values("Tipo de Documento").reset_index()
    eess_top = eess_top[eess_top["Tipo de Documento"]>1]
    eess_top.columns = ["Establecimiento de salud","Niños"]
    fig_eess_top = px.bar(eess_top, x="Niños", y="Establecimiento de salud", title='Establecimientos de Salud con Transitos')
    
    
    fig_year_count = px.bar(line_time_year_df, x="Año", y="Niños",text="Niños", title='Niños Transito por Año')
    fig_year_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_year_count.update_layout(xaxis=dict(title=dict(text="Año")),yaxis=dict(title=dict(text="Niños")),font=dict(size=16))
    fig_year_count.update_xaxes(type='category')
    
    fig_periodo_count = px.bar(line_time_month_df, x="Periodo", y="Niños",text="Niños", title='Niños Transito por Mes')
    fig_periodo_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_periodo_count.update_layout(xaxis=dict(title=dict(text="Periodo")),yaxis=dict(title=dict(text="Niños")),font=dict(size=16))
    fig_periodo_count.update_xaxes(type='category')
    




    columnas_add = st.columns(2)
    with columnas_add[0]:
        tab1, tab2 ,tab3= st.tabs(["Mensual", "Diario","Anual"])
        with tab1:
            st.plotly_chart(fig_periodo_count)
        with tab2:
            st.plotly_chart(px.line(line_time_fecha_df, x="FECHA DE MODIFICACIÓN DEL REGISTRO", y="Niños", title='Niños Transito Dirarios'))
        with tab3:
            
            st.plotly_chart(fig_year_count)
    with columnas_add[1]:
        select_mes  = st.selectbox("Compromiso 1 Tramo III Mes", MESES,index=len(MESES) - 1)
        carga_filt_df = carga_df[(carga_df['Año']==2025)&(carga_df['Mes']==int(mestext_short(select_mes)))]
        carga_filt_df = carga_filt_df[["Número de Documento del niño","Establecimiento de Salud","Rango de Edad","Dirección"]]
        data_transitos = transitos_df[["Documento","DATOS NIÑO PADRON","FECHA DE MODIFICACIÓN DEL REGISTRO","USUARIO QUE MODIFICA","ENTIDAD",
                                       "EESS","DIRECCION PADRON","REFERENCIA DE DIRECCION",
                                       "NUMERO DE DOCUMENTO  DE LA MADRE","DATOS MADRE PADRON"]]
        join_df = pd.merge(data_transitos, carga_filt_df, left_on='Documento', right_on='Número de Documento del niño', how='inner')
        line_join_fecha_df = join_df.groupby(["FECHA DE MODIFICACIÓN DEL REGISTRO"])[["Número de Documento del niño"]].count().reset_index()
        line_join_fecha_df.columns = ["FECHA DE MODIFICACIÓN DEL REGISTRO","Niños"]
        #st.text(f"Niños Transito C1: {join_df.shape[0]}")
        st.plotly_chart(px.line(line_join_fecha_df, x="FECHA DE MODIFICACIÓN DEL REGISTRO", y="Niños", title=f'Niños Transito Compromiso1 ({join_df.shape[0]})'))
        gb = GridOptionsBuilder.from_dataframe(join_df)
        gb.configure_default_column(cellStyle={'fontSize': '10px'}) 
        grid_options = gb.build()
        
        
        grid_response = AgGrid(join_df, # Dataframe a mostrar
                                gridOptions=grid_options,
                                enable_enterprise_modules=False,
                                #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                                update_mode='MODEL_CHANGED',
                                #fit_columns_on_grid_load=True,
                            
        )
    #columnas_sec = st.columns(2)
    with columnas_add[0]:
        st.plotly_chart(fig_eess_top)
    
    with st.expander("Descargas"):
        st.download_button(
                label="Descargar Transito C1",
                data=convert_excel_df(join_df),
                file_name=f"Transitos_Compromiso1.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        