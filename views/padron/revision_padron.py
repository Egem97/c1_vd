import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import plotly.graph_objects as go
from io import BytesIO
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
    
    
    df = df[[  
            'CÓDIGO DE PADRON', 'CNV', 'CUI', 'DNI',  'DATOS NIÑO PADRON', 'SEXO',
            'FECHA DE NACIMIENTO', 'EJE VIAL', 'DIRECCION PADRON',
            'REFERENCIA DE DIRECCION','MENOR VISITADO', '¿MENOR ENCONTRADO?', 'FECHA DE VISITA',
            'FUENTE DE DATOS', 'FECHA DE FUENTE DE DATOS', 'EESS NACIMIENTO',
            'EESS', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN', 'TIPO DE SEGURO',
            'TIPO DE DOCUMENTO DE LA MADRE',
            'NUMERO DE DOCUMENTO  DE LA MADRE','DATOS MADRE PADRON',
            'NUMERO DE CELULAR', 'CELULAR_CORREO', 'GRADO DE LA MADRE',
            'LENGUA DE LA MADRE','TIPO DE DOCUMENTO DEL JEFE DE FAMILIA',
            'NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA','DATOS JEFE PADRON',
            'FECHA DE MODIFICACIÓN DEL REGISTRO', 'USUARIO QUE MODIFICA', 'ENTIDAD',
            'TIPO REGISTRO', 'Tipo_file', 'Tipo de Documento',
            'EDAD', 'EDAD MESES']
        ]
    print(df.info())
    
    
    
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
    def actualizacion_col(entidad,usuario,fecha_mod):
        try:
            year_mod = fecha_mod.year
        except:
            year_mod = 2000
        
        if (usuario == "18215881" or usuario == "SERVICIO DNI ESTADO") and entidad =="MUNICIPIO":
            if year_mod == 2025:
                return f"ACTUALIZADO MUNICIPIO ({year_mod})"
            else:
                return f"ACTUALIZADO MUNICIPIO ({year_mod})"
        else:
            return "SIN ACTUALIZACIÓN"
    
    df["Estado"] = df.apply(lambda x: actualizacion_col(x['ENTIDAD'], x['USUARIO QUE MODIFICA'],x['FECHA DE MODIFICACIÓN DEL REGISTRO']),axis=1)
    
    
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
    
    df = df.rename(columns={
        "EESS":"Establecimiento de Salud Atención",
        "Tipo_file":"Tipo Registro",
        'EDAD':"Edad", 
        'EDAD MESES':"Edad Meses"
    })
    resumen_dff = df.groupby(["Establecimiento de Salud Atención","Estado"])[["Tipo Registro"]].count().reset_index()
    resumen_dff = resumen_dff[resumen_dff["Establecimiento de Salud Atención"].isin(EESS_MICRORED)]
    df_pivot = resumen_dff.pivot_table(index='Establecimiento de Salud Atención', columns='Estado', values='Tipo Registro', aggfunc='sum', fill_value=0)
    df_pivot = df_pivot.reset_index()
    st.dataframe(df_pivot)
    #'ARANJUEZ'
    aranjuez_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="ARANJUEZ"]
    #,'CLUB DE LEONES'
    club_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="CLUB DE LEONES"]
    #,'DE ESPECIALIDADES BASICAS LA NORIA',
    noria_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="DE ESPECIALIDADES BASICAS LA NORIA"]
    #'EL BOSQUE'
    bosque_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="EL BOSQUE"]
    #,'LA UNION'
    union_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="LA UNION"]
    #,'LIBERTAD'
    libertad_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="LIBERTAD"]
    #,'LOS GRANADOS "SAGRADO CORAZON"'
    granados_datahomo_df =  df[df["Establecimiento de Salud Atención"]=='LOS GRANADOS "SAGRADO CORAZON"']
    #,'LOS JARDINES'
    jardines_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="LOS JARDINES"]
    #,'PESQUEDA II'
    pesqueda2_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="PESQUEDA II"]
    #,'PESQUEDA III'
    pesqueda3_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="PESQUEDA III"]
    #,'SAN MARTIN DE PORRES'
    sanmartin_datahomo_df =  df[df["Establecimiento de Salud Atención"]=="SAN MARTIN DE PORRES"]
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_pivot.to_excel(writer, sheet_name='Resumen', index=False)
        aranjuez_datahomo_df.to_excel(writer, sheet_name='ARANJUEZ', index=False)
        club_datahomo_df.to_excel(writer, sheet_name='CLUB DE LEONES', index=False)
        noria_datahomo_df.to_excel(writer, sheet_name='NORIA', index=False)
        bosque_datahomo_df.to_excel(writer, sheet_name='EL BOSQUE', index=False)
        union_datahomo_df.to_excel(writer, sheet_name='LA UNION', index=False)
        libertad_datahomo_df.to_excel(writer, sheet_name='LIBERTAD', index=False)
        granados_datahomo_df.to_excel(writer, sheet_name='SAGRADO CORAZON', index=False)
        jardines_datahomo_df.to_excel(writer, sheet_name='LOS JARDINES', index=False)
        pesqueda2_datahomo_df.to_excel(writer, sheet_name='PESQUEDA II', index=False)
        pesqueda3_datahomo_df.to_excel(writer, sheet_name='PESQUEDA III', index=False)
        sanmartin_datahomo_df.to_excel(writer, sheet_name='SAN MARTIN DE PORRES', index=False)
    output.seek(0)
    
    
    st.download_button(
        label="📥 Descargar Actualizados",
        data=output,
        file_name=f"padron_actualizados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
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
   