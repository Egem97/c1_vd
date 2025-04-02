import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import plotly.graph_objects as go
from styles import styles
from utils.cache_handler import fetch_padron
from utils.helpers import *
from constans import EESS_MICRORED

def revision_padron():
    styles(2)
    df = fetch_padron()
    df["Documento"]= df["Documento"].astype(str)
    df['EESS'] = df['EESS'].fillna("NO ESPECIFICADO")
    df["NUMERO DE CELULAR"] = df["NUMERO DE CELULAR"].str.strip()
    df['EDAD'] = df['FECHA DE NACIMIENTO'].apply(calcular_edad_anios)
    df['EDAD MESES'] = df['FECHA DE NACIMIENTO'].apply(calcular_edad)
    
    fecha_maxima = df["FECHA DE MODIFICACIÓN DEL REGISTRO"].max().strftime("%Y-%m-%d")
    edades_list = df["EDAD"].unique()
    col_filt = st.columns([3,3,2,3])
    
    with col_filt[0]:
        st.title(":blue[Padrón Trujillo] :child:")
    with col_filt[1]:
        st.subheader(f"Fecha de corte: {fecha_maxima}", divider=True)
    with col_filt[2]:
        select_edad  = st.selectbox("Edad:", edades_list, key="select", placeholder="Seleccione Edad",index=None)
        if select_edad != None:
            df = df[df["EDAD"]==select_edad]
    edad_meses_list = df["EDAD MESES"].unique()
    with col_filt[3]:
        select_edadmes  = st.multiselect("Edad Mes:", edad_meses_list, key="select12", placeholder="Seleccione Mes")
        if len(select_edadmes) > 0:
            df = df[df["EDAD MESES"].isin(select_edadmes)]
    
    
    total = df.shape[0]
    microred_df = df[df["EESS"].isin(EESS_MICRORED)]
    ##EESS MICRORED GENERAL
    general_microred_df = microred_df.groupby(["EESS"])[["Tipo de Documento"]].count().sort_values("Tipo de Documento").reset_index()
    general_microred_df.columns = ["Establecimiento de Salud","Registros"]
    promedio_registros_general = general_microred_df["Registros"].mean()
    num_general_microred = microred_df.shape[0]
    
     
    ##
    act_microred_df = microred_df[(microred_df["ENTIDAD"]=="MUNICIPIO")&(microred_df["USUARIO QUE MODIFICA"].isin(["18215881","SERVICIO DNI ESTADO"]))]
    
    num_act_microred = act_microred_df.shape[0]
    act_microred_df = act_microred_df.groupby(["EESS"])[["Tipo de Documento"]].count().sort_values("Tipo de Documento").reset_index()
    act_microred_df.columns = ["Establecimiento de Salud","Registros"]
    promedio_registros_act = act_microred_df["Registros"].mean()
    
    general_dff = pd.merge(general_microred_df, act_microred_df, left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='inner')
    general_dff["%"] = round((general_dff["Registros_y"]/general_dff["Registros_x"])*100,1)
    general_dff.columns = ["Establecimiento de Salud","Población","Actualización","%"]
    
    ##########################
    others_df = df[~df["EESS"].isin(EESS_MICRORED)]
    
    sin_eess_df = others_df[others_df["EESS"]=="NO ESPECIFICADO"]
    sin_eess = sin_eess_df.shape[0]
    
    others_eess_df = others_df[others_df["EESS"]!="NO ESPECIFICADO"]
    others_eess = others_eess_df.shape[0]
    eess_others_df = others_eess_df.groupby(["EESS"])[["Tipo de Documento"]].count().sort_values("Tipo de Documento").reset_index()
    eess_others_df = eess_others_df[eess_others_df["Tipo de Documento"]>1]
    eess_others_df.columns = ["Establecimiento de Salud","Registros"]
    
    #st.dataframe(others_eess_df)
    
    
    
    
    metric_col = st.columns(4)
    metric_col[0].metric("Población Padron",total,"100%",border=True)
    metric_col[1].metric("Población EE. SS",num_general_microred,f"{round((num_general_microred/total)*100,2)}%",border=True)
    metric_col[2].metric("Sin EE. SS",sin_eess,f"{round((sin_eess/total)*100,2)}%",border=True)
    metric_col[3].metric("Otros EE. SS",others_eess,f"{round((others_eess/total)*100,2)}%",border=True)
    
    
    #st.dataframe(general_dff)
    tab_1, tab_2, tab3 = st.tabs(["Población", "Actualización","% de Actualizaciones"])
    with tab_1:
        fig_eess_count = px.bar(general_microred_df, x="Establecimiento de Salud", y="Registros",
                                    text="Registros", orientation='v',title = f"Población por Establecimiento de Salud ({num_general_microred})")
        fig_eess_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_count.update_layout(xaxis=dict(title=dict(text="")),font=dict(size=16))
        fig_eess_count.add_hline(y=promedio_registros_general, line=dict(color="red", dash="dash"), 
                         annotation_text=f"Promedio: {promedio_registros_general:.0f}", 
                         annotation_position="top left")
        st.plotly_chart(fig_eess_count)
    with tab_2:
        fig_eess_act = px.bar(act_microred_df, x="Establecimiento de Salud", y="Registros",
                                    text="Registros", orientation='v',title = f"Población Actualizada por Establecimiento de Salud({num_act_microred})")
        fig_eess_act.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_act.update_layout(xaxis=dict(title=dict(text="")),font=dict(size=16))
        fig_eess_act.add_hline(y=promedio_registros_act, line=dict(color="red", dash="dash"), 
                         annotation_text=f"Promedio: {promedio_registros_act:.0f}", 
                         annotation_position="top left")
        st.plotly_chart(fig_eess_act)
    with tab3:
        fig_comparativo = go.Figure(data=[
            go.Bar(
                name='Población', x=general_dff["Establecimiento de Salud"], y=general_dff["Población"],
                text=general_dff["Población"],  textposition='outside', textfont=dict(size=16)
            ),
            go.Bar(
                name='Actualización', x=general_dff["Establecimiento de Salud"], y=general_dff["Actualización"],
                text=general_dff["Actualización"],  textposition='outside', textfont=dict(size=16)
            ),
            
        ])
        fig_comparativo.update_layout(barmode='group',title="Población y Actualización en el Padrón Nominal",)
        st.plotly_chart(fig_comparativo)
        general_dff =general_dff.sort_values("%")
        general_dff["%_formatted"] = general_dff["%"].astype(str) + '%'
        fig_eess_percent = px.bar(general_dff, x="Establecimiento de Salud", y="%",
                                    text="%_formatted", orientation='v',title = f"Porcentaje de Actualizaciones por Establecimiento")
        fig_eess_percent.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_percent.update_layout(xaxis=dict(title=dict(text="")),font=dict(size=16))
        
        st.plotly_chart(fig_eess_percent)
    
    columnas_add = st.columns(2)
    with columnas_add[0]:
        fig_eess_other = px.bar(eess_others_df, x="Registros", y="Establecimiento de Salud",
                                    text="Registros", orientation='h',title = f"Población de Otros Establecimientos de Salud ({others_eess})")
        fig_eess_other.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        fig_eess_other.update_layout(xaxis=dict(title=dict(text="")),font=dict(size=16))
        
        st.plotly_chart(fig_eess_other)
    
    st.download_button(
        label="📥 Descargar Padrón Nominal",
        data=convert_excel_df(df),
        file_name=f"padron_trujillo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    #st.dataframe(df) 
    #prioridad = {'DNI': 1, 'CUI': 2, 'CNV': 3}
    #df['Prioridad'] = df['Tipo de Documento'].map(prioridad)
    #df = df.sort_values(by=['Documento', 'Prioridad'])
    #df = df.drop_duplicates(subset='Documento', keep='first')
    #df = df.drop(columns=['Prioridad'])
    #st.write(df.shape) 
    #st.dataframe(df) 
   