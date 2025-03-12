import streamlit as st
import pandas as pd
import plotly.express as px
from styles import styles
from utils.cache_handler import fetch_vd_childs,fetch_carga_childs,fetch_padron
from utils.helpers import *
from utils.functions_data import childs_unicos_visitados
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def childs_status_vd():
    styles(2)
    actvd_df = fetch_vd_childs()
    carga_df = fetch_carga_childs()
    padron_df = fetch_padron()
    datos_ninos_df = pd.read_parquet('datos_niños.parquet', engine='pyarrow')
    eess = list(carga_df["Establecimiento de Salud"].unique())
    eess.remove(None)
    MESES = ["Ene","Feb","Mar"]
    columns_row1 = st.columns([3,2,2,4])
    columns_row1[0].title("Visitas a Niños")
    with columns_row1[1]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with columns_row1[2]:
        select_mes  = st.selectbox("Mes:",MESES , key="select2",index=len(MESES) - 1)
    with columns_row1[3]:
        select_eess  = st.multiselect("Establecimiento de Salud:", eess, key="select3",placeholder="Seleccione EESS")
        if len(select_eess)> 0:    
            carga_df = carga_df[carga_df["Establecimiento de Salud"].isin(select_eess)]
            actvd_df = actvd_df[actvd_df["Establecimiento de Salud"].isin(select_eess)]
    
    

    datos_ninos_df = datos_ninos_df[datos_ninos_df["Periodo"]==f"{select_year} - {select_mes}"]
    carga_filt_df = carga_df[(carga_df['Año']==int(select_year))&(carga_df['Mes']==int(mestext_short(select_mes)))]
    actvd_filt_df = actvd_df[(actvd_df['Año']==select_year)&(actvd_df['Mes']==select_mes)]
    niños_unicos_vd = childs_unicos_visitados(actvd_filt_df,'Número de Documento de Niño',"ALL CHILDS W DUPLICADOS")
    
    ##
    
    num_carga = carga_filt_df.shape[0]
    num_visitas_programadas = carga_filt_df["Total de visitas completas para la edad"].sum()
    #st.write(num_visitas_programadas)
    num_visitas = carga_filt_df["Total de Intervenciones"].sum()
    num_visitas_validas = carga_filt_df["Total de VD presenciales Válidas"].sum()
    num_child_vd = niños_unicos_vd.shape[0]
    num_vd_movil = carga_filt_df["Total de VD presencial Válidas MOVIL"].sum()
    porcentaje_child_visita = f"{round((num_child_vd/num_carga)*100,2)}%"
    #CARDS
    metric_col = st.columns(7)
    metric_col[0].metric("Niños Cargados",num_carga,f"Con Visita {num_child_vd}({num_carga-num_child_vd})",border=True)
    metric_col[1].metric("Total de Visitas",num_visitas,f"VD Programadas: {num_visitas_programadas}",border=True)
    #metric_col[2].metric("N° Visitas Realizadas Válidas",num_vd_actu,f"Visitas observadas {visitas_invalidas_sistema}",border=True)
    #metric_col[3].metric("N° Visitas Realizadas MOVIL",num_vd_movil,"-",border=True)
    #metric_col[4].metric("% Registros por Movil",f"{round((num_vd_movil/num_vd_actu)*100,2)}%","-",border=True)
    #metric_col[5].metric("% Registro Celular",porcentaje_celular,"-",border=True)

    
    actvd_filt_df = actvd_filt_df.groupby(['Número de Documento de Niño','Actores Sociales','Etapa'])[['Año']].count().reset_index()
    actvd_filt_df = actvd_filt_df.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
    actvd_filt_df = actvd_filt_df.drop_duplicates(subset='Número de Documento de Niño', keep='first')
    actvd_filt_df.columns = ["Doc_Ultimo_Mes","Actor Social Ultimo Mes","Estado_Visita_Ult","count"]
    actvd_filt_df = actvd_filt_df[["Doc_Ultimo_Mes","Actor Social Ultimo Mes","Estado_Visita_Ult"]]
    
    
    dataframe_pn = padron_df[[
        'Tipo_file', 'Documento', 'Tipo de Documento','DATOS NIÑO PADRON','CELULAR2_PADRON','SEXO',
        'FECHA DE NACIMIENTO', 'EJE VIAL', 'DIRECCION PADRON','REFERENCIA DE DIRECCION','MENOR VISITADO',
        'EESS NACIMIENTO','EESS', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN','TIPO DE DOCUMENTO DE LA MADRE',
        'NUMERO DE DOCUMENTO  DE LA MADRE','DATOS MADRE PADRON','TIPO DE DOCUMENTO DEL JEFE DE FAMILIA',
        'NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA','DATOS JEFE PADRON','ENTIDAD','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA','NUMERO DE CELULAR', 'CELULAR_CORREO',
        'TIPO DE SEGURO'
    ]]
            #JOIN
    join_df = pd.merge(carga_filt_df, dataframe_pn, left_on='Número de Documento del niño', right_on='Documento', how='left')
    prioridad = {'DNI': 1, 'CUI': 2, 'CNV': 3}
    join_df['Prioridad'] = join_df['Tipo de Documento'].map(prioridad)
    join_df = join_df.sort_values(by=['Número de Documento del niño', 'Prioridad'])
    join_df = join_df.drop_duplicates(subset='Número de Documento del niño', keep='first')
    join_df = join_df.drop(columns=['Prioridad'])
    join_df['Número de Documento del niño'] = join_df['Número de Documento del niño'].astype(str)
    dataframe_ = pd.merge(join_df, actvd_filt_df, left_on='Número de Documento del niño', right_on='Doc_Ultimo_Mes', how='left')
    del join_df , actvd_filt_df
    dataframe_['Pre Asignación'] = test(dataframe_,"Dirección")
    dataframe_['Pre Asignación_Padron'] = test(dataframe_,"DIRECCION PADRON")
    reemplazo = {
        "0": "NINGUNO",
        "1": "SIS",
        "2": "ESSALUD",
        "3": "SANIDAD",
        "4": "PRIVADO"
    }
    dataframe_["TIPO DE SEGURO"] = dataframe_["TIPO DE SEGURO"].fillna("SIN DATOS").apply(
        lambda x: "SIN DATOS" if x == "SIN DATOS" else 
              ", ".join([reemplazo.get(num.strip(), num.strip()) 
                         for num in x.split(",") if num.strip()])
    )
            
    dataframe_ = pd.merge(dataframe_, datos_ninos_df, left_on='Número de Documento del niño', right_on='Documento_c1', how='left')
    dataframe_['DATOS NIÑO PADRON'] = dataframe_.apply(lambda x: completar_names_col(x['DATOS NIÑO PADRON'], x['Niño']),axis=1)
    dataframe_['Tipo de Documento'] = dataframe_.apply(lambda x: completar_names_col(x['Tipo de Documento'], x['Tipo de Documento del niño']),axis=1)
    dataframe_['MENOR VISITADO'] = dataframe_['MENOR VISITADO'].fillna("SIN MODIFICACION EN EL PADRON")
            
    #dataframe_['Estado_Visita_Ult'] = dataframe_.apply(lambda x: estado_nino(x['Estado_Visita_Ult'], x['Establecimiento de Salud']),axis=1)
            
    dataframe_['TIPO DE DOCUMENTO DE LA MADRE'] = dataframe_['TIPO DE DOCUMENTO DE LA MADRE'].fillna("MADRE DE GOLONDRINO")
    dataframe_['EESS NACIMIENTO'] = dataframe_['EESS NACIMIENTO'].fillna("No Especificado")
    dataframe_['EESS'] = dataframe_['EESS'].fillna("No Especificado")
    dataframe_['FRECUENCIA DE ATENCION'] = dataframe_['FRECUENCIA DE ATENCION'].fillna("No Especificado")
    dataframe_['EESS ADSCRIPCIÓN'] = dataframe_['EESS ADSCRIPCIÓN'].fillna("No Especificado")
    dataframe_['Tipo_file'] = dataframe_['Tipo_file'].fillna("En Otro Padrón Nominal")
    dataframe_['ENTIDAD'] = dataframe_['ENTIDAD'].fillna("En Otro Padrón Nominal")
    
    del datos_ninos_df
    cols = [
            'Establecimiento de Salud','Nombres del Actor Social','Tipo de Documento del niño','Tipo de Documento','Número de Documento del niño',
             'DATOS NIÑO PADRON','Fecha de Nacimiento','Rango de Edad','Total de visitas completas para la edad','Total de Intervenciones','Total de VD presenciales Válidas','Total de VD presencial Válidas WEB','Total de VD presencial Válidas MOVIL',
            'MENOR VISITADO', 'DIRECCION PADRON','REFERENCIA DE DIRECCION','Dirección', 'TIPO DE DOCUMENTO DE LA MADRE','NUMERO DE DOCUMENTO  DE LA MADRE',
            'DNI de la madre','DATOS MADRE PADRON','NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA','DATOS JEFE PADRON','Celular de la madre','NUMERO DE CELULAR','CELULAR2_PADRON',
            'EESS NACIMIENTO', 'EESS','FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN',
            'EESS_C1', 'Fecha_ult_at_c1','Zona', 'Manzana', 'Sector','TIPO DE SEGURO','Tipo_file','ENTIDAD','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA','Estado_Visita_Ult', 'Mes', 'Año'
            ]
    dataframe_ = dataframe_[cols]
    dataframe_.columns = ['Establecimiento de Salud',
                'Actor Social', 'Tipo Documento',
                'Tipo Documento(P)', 'Número de Documento',
                'Datos del niño', 'Fecha de Nacimiento', 'Rango de Edad',
                'N° Visitas Completas', 'Total de Intervenciones','Total de VD presenciales Válidas','Total de VD presencial Válidas WEB','Total de VD presencial Válidas MOVIL',
                'MENOR VISITADO',
                'Dirección(P)', 'Referencia Dirección(P)', 'Dirección Compromiso 1',
                'Tipo Documento Madre(P)', 'Número Doc Madre(P)',
                'Número Doc Madre', 'Datos Madre(P)',
                'Número Doc Jefe Familia(P)', 'Datos Jefe Famlia(P)',
                'Celular Madre', 'Celular(P)', 'Celular2(P)',
                'EESS NACIMIENTO', 'EESS ULTIMA ATENCION(P)', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN',
                'EESS ULTIMA ATENCION', 'Fecha Ultima Atención', 'Zona', 'Manzana', 'Sector','Tipo de Seguro', 'Tipo Registro Padrón Nominal',
                'Entidad Actualiza','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA', 'Estado Niño', 'Mes', 'Año'
            ]
    dataframe_['Estado Visitas'] =  dataframe_.apply(lambda x: estado_visitas_completas(x['N° Visitas Completas'], x['Total de VD presenciales Válidas'],x['Estado Niño']),axis=1)#.apply(lambda x: completar_names_col(x['DATOS NIÑO PADRON'], x['Niño']),axis=1)
    dataframe_['Estado Niño'] = dataframe_['Estado Niño'].fillna(f"Sin Visita ({select_mes})")
    dataframe_['USUARIO QUE MODIFICA'] = dataframe_['USUARIO QUE MODIFICA'].fillna(f"Usuario no definido")

    #add prueba
    #dataframe_['Edad'] = dataframe_['Fecha de Nacimiento'].apply(calcular_edad)
    ######################## FALTANTES
    dataframe_efec = dataframe_[dataframe_["Estado Niño"].isin(["Visita Domiciliaria (6 a 12 Meses)","Visita Domiciliaria (1 a 5 meses)"])]
    vd_programadas_df = dataframe_.groupby(["Establecimiento de Salud"])[["N° Visitas Completas"]].sum().sort_values("N° Visitas Completas",ascending=False).reset_index()#,"Total de VD presencial Válidas WEB",
    child_programados_df = dataframe_.groupby(["Establecimiento de Salud"])[["N° Visitas Completas"]].count().sort_values("N° Visitas Completas",ascending=False).reset_index()
    child_programados_df = child_programados_df.rename(columns=  {"N° Visitas Completas":"Niños Programados"})

    vd_movil_df = dataframe_efec.groupby(["Establecimiento de Salud"])[["Total de VD presencial Válidas MOVIL"]].sum().reset_index()
    childs_encontrados_df = dataframe_efec.groupby(["Establecimiento de Salud"])[["Estado Niño"]].count().reset_index()
    childs_encontrados_df = childs_encontrados_df.rename(columns=  {"Estado Niño":"Niños Encontrados"})
    proyectado_dff = pd.merge(child_programados_df,vd_programadas_df , left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')

    proyectado_dff = pd.merge(proyectado_dff, childs_encontrados_df, left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')
    proyectado_dff = pd.merge(proyectado_dff, vd_movil_df, left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')

    proyectado_dff["Valla 75% Georref"] = round(proyectado_dff["N° Visitas Completas"]*0.75)
    proyectado_dff["Visitas Faltantes"] = proyectado_dff["Valla 75% Georref"] - proyectado_dff["Total de VD presencial Válidas MOVIL"]
    visitas_for_completar_df = dataframe_efec[dataframe_efec["Estado Visitas"]!="Visitas Completas"]
    visitas_for_completar_df["Visitas Proyectadas"] = visitas_for_completar_df["N° Visitas Completas"] - visitas_for_completar_df["Total de VD presenciales Válidas"]
    vd_completar_df = visitas_for_completar_df.groupby(["Establecimiento de Salud"])[["Visitas Proyectadas"]].sum().reset_index()
    
    proyectado_dff = pd.merge(proyectado_dff, vd_completar_df, left_on='Establecimiento de Salud', right_on='Establecimiento de Salud', how='left')

    proyectado_dff["Tolerancia Visitas WEB"] = proyectado_dff["Visitas Proyectadas"] - proyectado_dff["Visitas Faltantes"]
    proyectado_dff["Tolerancia Niños WEB"] = (proyectado_dff["Tolerancia Visitas WEB"]/3).round()
    total_row = pd.DataFrame({
        "Establecimiento de Salud": ["TOTAL"],  # Nombre de la fila
        "Niños Programados":proyectado_dff["Niños Programados"].sum(),
        "Niños Encontrados":proyectado_dff["Niños Encontrados"].sum(),
        "N° Visitas Completas": [proyectado_dff["N° Visitas Completas"].sum()],
        
        "Total de VD presencial Válidas MOVIL": [proyectado_dff["Total de VD presencial Válidas MOVIL"].sum()],
        "Valla 75% Georref": [proyectado_dff["Valla 75% Georref"].sum()],
        "Visitas Faltantes": [proyectado_dff["Visitas Faltantes"].sum()],
        "Visitas Proyectadas": [proyectado_dff["Visitas Proyectadas"].sum()],
        "Tolerancia Visitas WEB": [proyectado_dff["Tolerancia Visitas WEB"].sum()],
        "Tolerancia Niños WEB": [proyectado_dff["Tolerancia Niños WEB"].sum()],

    })
    proyectado_dff = pd.concat([proyectado_dff, total_row], ignore_index=True)
    
    
    proyectado_dff['Estado'] = proyectado_dff.apply(lambda x: estado_proyectado(x['Visitas Faltantes'], x['Visitas Proyectadas']),axis=1)
    proyectado_dff.columns = ['Establecimiento de Salud', 'Niños Programados', 'Visitas Programadas',
       'Niños Encontrados', 'Visitas Realizadas MOVIL GEO',
       'Valla Visitas GEO 75%', 'Visitas Faltantes Valla GEO', 'Visitas GEO Proyectadas',
       'Tolerancia Visitas WEB', 'Tolerancia Niños WEB', 'Estado']
    
    proyectado_dff["% Actual GEO"] = round((proyectado_dff["Visitas Realizadas MOVIL GEO"] / proyectado_dff["Visitas Programadas"])*100,1)
    proyectado_dff = proyectado_dff[
        ['Establecimiento de Salud', 'Niños Programados', 'Visitas Programadas',
       'Niños Encontrados', 'Visitas Realizadas MOVIL GEO','% Actual GEO', 'Valla Visitas GEO 75%', 
       'Visitas Faltantes Valla GEO', 'Visitas GEO Proyectadas',
       'Tolerancia Visitas WEB', 'Tolerancia Niños WEB', 'Estado',
       ]
    ]
    proyectado_dff['% Actual GEO'] = proyectado_dff['% Actual GEO'].astype(str)
    proyectado_dff['% Actual GEO'] = proyectado_dff['% Actual GEO']+"%"
    #####################
    #df_con_num_cel = (ene25_carga_df[ene25_carga_df["Celular de la madre"]!=0])
    df_con_num_cel = (dataframe_[dataframe_["Celular Madre"]!=0])
    df_con_num_cel["Celular Madre"] = df_con_num_cel["Celular Madre"].astype(str)
    cel_duplicados_df = df_con_num_cel[df_con_num_cel.duplicated(subset=["Celular Madre"], keep=False)]
    #st.dataframe(cel_duplicados_df)
    #PROCENTAJE
    vd_geo_percent_df = dataframe_[(dataframe_["Estado Visitas"]=="Visitas Completas")]#&(dataframe_["Celular Madre"]!=0)
    num_ninos_result = vd_geo_percent_df.shape[0]
    total_vd_movil_completas = vd_geo_percent_df["Total de VD presencial Válidas MOVIL"].sum()
    #total_meta_vd = round(num_visitas_validas*0.75)
    total_meta_vd = round(num_visitas_programadas*0.75)
    #num_visitas_programadas
    total_faltante_vd_meta = total_meta_vd-total_vd_movil_completas
    percent_vd_movil_validate = round((total_vd_movil_completas/num_visitas_programadas)*100,2)
    percent_vd_completas_movil = round((total_vd_movil_completas/num_vd_movil)*100,2)
    
    ###
    fuera_padron_df = dataframe_[(dataframe_["Tipo Registro Padrón Nominal"]=="En Otro Padrón Nominal")]
    try:
        num_excluyen_childs = fuera_padron_df.shape[0]
    except:
        num_excluyen_childs = 0

    #con_visita_cel = dataframe_[(dataframe_["Total de Intervenciones"]!=0)]
    #num_con_visita_cel = con_visita_cel.shape[0]
    con_celular = (dataframe_["Celular Madre"]!=0).sum()
    percent_reg_tel = round((con_celular/num_carga)*100,2)
    percent_total_vd_12 = round((num_ninos_result/(num_carga))*100,2)
    ##
    
    #retomar metrics 
    metric_col[2].metric("Visitas Movil",num_vd_movil,f"VD Completas:{total_vd_movil_completas}({percent_vd_completas_movil}%)",border=True)
    metric_col[3].metric("Visitas Completas - Movil",total_vd_movil_completas,f"Meta (75%): {total_meta_vd}",border=True)
    metric_col[4].metric("% VD Georreferenciadas",f"{percent_vd_movil_validate}%",f"VD Faltantes {total_faltante_vd_meta}",border=True)
    metric_col[5].metric("% Registros Telefonicos",f"{percent_reg_tel}%",f"Sin celular : {num_carga-con_celular}",border=True)
    metric_col[6].metric("% Niños Oportunos y Completos",f"{percent_total_vd_12}%",f"Positivos:{num_ninos_result}",border=True)

    eess_top_cargados = dataframe_.groupby(['Establecimiento de Salud'])[['Número de Documento']].count().sort_values("Número de Documento").reset_index()
    eess_top_cargados = eess_top_cargados.rename(columns=  {"Número de Documento":"Registros"})
    fig_eess_count = px.bar(eess_top_cargados, x="Registros", y="Establecimiento de Salud",
                                    text="Registros", orientation='h',title = "Niños Asignados por Establecimiento de Salud")
    fig_eess_count.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_count.update_layout(xaxis=dict(title=dict(text="Número de Niños Cargados")),font=dict(size=16))
    #
    eess_top_visitas = dataframe_.groupby(['Establecimiento de Salud'])[['Total de VD presenciales Válidas']].sum().sort_values(["Total de VD presenciales Válidas"]).reset_index()
    eess_top_visitas = eess_top_visitas.rename(columns=  {"Total de VD presenciales Válidas":"Visitas"})
    fig_eess_top_visitas = px.bar(eess_top_visitas, x="Visitas", y="Establecimiento de Salud",
                                    text="Visitas", orientation='h',title = "Niños Visitados por Establecimiento de Salud")
    fig_eess_top_visitas.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_top_visitas.update_layout(xaxis=dict(title=dict(text="Número de Visitas")),font=dict(size=16))

    ####
    estado_act_child_df = dataframe_.groupby(["Estado Niño"])[["Tipo Documento"]].count().sort_values("Tipo Documento").reset_index()
    estado_act_child_df = estado_act_child_df.rename(columns = {"Tipo Documento":"Niños"})
    entidad_act_child_df = dataframe_.groupby(["Entidad Actualiza"])[["Tipo Documento"]].count().sort_values("Tipo Documento").reset_index()
    entidad_act_child_df = entidad_act_child_df.rename(columns = {"Tipo Documento":"Niños"})
    estado_visitas_act_child_df = dataframe_.groupby(["Estado Visitas"])[["Tipo Documento"]].count().sort_values("Tipo Documento").reset_index()
    estado_visitas_act_child_df = estado_visitas_act_child_df.rename(columns = {"Tipo Documento":"Niños"})
    
    #movil vd
    eess_top_visitas = dataframe_.groupby(['Establecimiento de Salud'])[['Total de VD presencial Válidas MOVIL']].sum().sort_values("Total de VD presencial Válidas MOVIL").reset_index()
    eess_top_visitas = eess_top_visitas.rename(columns=  {"Total de VD presencial Válidas MOVIL":"Visitas"})
    fig_eess_top_visitas_movil = px.bar(eess_top_visitas, x="Visitas", y="Establecimiento de Salud",
                                    text="Visitas", orientation='h',title = "Visitas Registradas por MOVIL")
    fig_eess_top_visitas_movil.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_top_visitas_movil.update_layout(xaxis=dict(title=dict(text="Número de Visitas")),font=dict(size=16))
    #web vd
    eess_top_visitas_web = dataframe_.groupby(['Establecimiento de Salud'])[['Total de VD presencial Válidas WEB']].sum().sort_values("Total de VD presencial Válidas WEB").reset_index()
    eess_top_visitas_web = eess_top_visitas_web.rename(columns=  {"Total de VD presencial Válidas WEB":"Visitas"})
    fig_eess_top_visitas_web = px.bar(eess_top_visitas_web, x="Visitas", y="Establecimiento de Salud",
                                    text="Visitas", orientation='h',title = "Visitas Registradas por WEB")
    fig_eess_top_visitas_web.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_top_visitas_web.update_layout(xaxis=dict(title=dict(text="Número de Visitas")),font=dict(size=16))

    #fig 1
    fig_estado_child = px.bar(estado_act_child_df, x="Niños", y="Estado Niño",
                                    text="Niños", orientation='h',title = f"Estado de los Niños Cargados {select_mes}")
    fig_estado_child.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
    fig_estado_child.update_layout(xaxis=dict(title=dict(text="Niños")),font=dict(size=14))
    fig_estado_child.update_layout(margin=dict(t=30, b=20))

    fig_entidad_child = px.bar(entidad_act_child_df, x="Niños", y="Entidad Actualiza",
                                    text="Niños", orientation='h',title = f"Niños C1 - Estado Actualizaciones Padrón Nominal {select_mes}")
    fig_entidad_child.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
    fig_entidad_child.update_layout(xaxis=dict(title=dict(text="Niños")),font=dict(size=14))
    fig_entidad_child.update_layout(margin=dict(t=30, b=20))

    fig_estado_vd_child = px.bar(estado_visitas_act_child_df, x="Niños", y="Estado Visitas",
                                    text="Niños", orientation='h',title = f"Estado de las Visitas en {select_mes}",)
    fig_estado_vd_child.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
    fig_estado_vd_child.update_layout(xaxis=dict(title=dict(text="Niños")),font=dict(size=14))
    fig_estado_vd_child.update_layout(margin=dict(t=30, b=20))
    #
    #Estado Niño
    no_encontrados_df = dataframe_[dataframe_["Estado Niño"]=="No Encontrado"]
    no_encontrados_df = no_encontrados_df.groupby(["Establecimiento de Salud"])[["Estado Niño"]].count().sort_values("Estado Niño").reset_index()
    no_encontrados_df = no_encontrados_df.rename(columns=  {"Estado Niño":"Registros"})
    fig_eess_count_noencon = px.bar(no_encontrados_df, x="Registros", y="Establecimiento de Salud",
                                    text="Registros", orientation='h',title = "Niños No Encontrados por Establecimiento de Salud")
    fig_eess_count_noencon.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_count_noencon.update_layout(xaxis=dict(title=dict(text="Número de Niños No Encontrados")),font=dict(size=16))
    #rechazado
    rechazado_df = dataframe_[dataframe_["Estado Niño"]=="Rechazado"]
    rechazado_df = rechazado_df.groupby(["Establecimiento de Salud"])[["Estado Niño"]].count().sort_values("Estado Niño").reset_index()
    rechazado_df = rechazado_df.rename(columns=  {"Estado Niño":"Registros"})
    fig_eess_count_rechazado = px.bar(rechazado_df, x="Registros", y="Establecimiento de Salud",
                                    text="Registros", orientation='h',title = "Niños Rechazados por Establecimiento de Salud")
    fig_eess_count_rechazado.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_count_rechazado.update_layout(xaxis=dict(title=dict(text="Número de Niños Rechazados")),font=dict(size=16))

    
    sinvd_dff = dataframe_[dataframe_["Estado Niño"]==f"Sin Visita ({select_mes})"]
    sinvd_df = sinvd_dff.groupby(["Establecimiento de Salud"])[["Estado Niño"]].count().sort_values("Estado Niño").reset_index()
    sinvd_df = sinvd_df.rename(columns=  {"Estado Niño":"Niños"})

    fig_eess_sinvd = px.bar(sinvd_df, x="Niños", y="Establecimiento de Salud",
                                    text="Niños", orientation='h',title = "Niños sin Visita por Establecimiento")
    fig_eess_sinvd.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_sinvd.update_layout(xaxis=dict(title=dict(text="Número de Niños")),font=dict(size=16))

    child_transito_df = dataframe_[dataframe_["Tipo Registro Padrón Nominal"]=="Activos Transito"]
    child_transito_df = child_transito_df.groupby(["Establecimiento de Salud"])[["Tipo Registro Padrón Nominal"]].count().sort_values("Tipo Registro Padrón Nominal").reset_index()
    child_transito_df = child_transito_df.rename(columns=  {"Tipo Registro Padrón Nominal":"Niños"})

    fig_eess_transito = px.bar(child_transito_df, x="Niños", y="Establecimiento de Salud",
                                    text="Niños", orientation='h',title = "Niños Transito por Establecimiento")
    fig_eess_transito.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_transito.update_layout(xaxis=dict(title=dict(text="Número de Niños")),font=dict(size=16))

    child_deri_df = dataframe_[dataframe_["Tipo Registro Padrón Nominal"]=="En Otro Padrón Nominal"]
    child_deri_df = child_deri_df.groupby(["Establecimiento de Salud"])[["Tipo Registro Padrón Nominal"]].count().sort_values("Tipo Registro Padrón Nominal").reset_index()
    child_deri_df = child_deri_df.rename(columns=  {"Tipo Registro Padrón Nominal":"Niños"})

    fig_eess_derivados = px.bar(child_deri_df, x="Niños", y="Establecimiento de Salud",
                                    text="Niños", orientation='h',title = "Niños En otro Distrito Padrón por Establecimiento")
    fig_eess_derivados.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_eess_derivados.update_layout(xaxis=dict(title=dict(text="Número de Niños")),font=dict(size=16))

    #ver globalmente EL ESTADO DE LOS TRANSITOS Y EN OTRO DISTRITO
    registro_padron_df = dataframe_[dataframe_["Tipo Registro Padrón Nominal"].isin(["Activos Transito","En Otro Padrón Nominal"])]
    registro_padron_group_df = registro_padron_df.groupby(["Estado Niño","Tipo Registro Padrón Nominal"])[["Número de Documento"]].count().reset_index()
    registro_padron_group_df = registro_padron_group_df.rename(columns=  {"Número de Documento":"Niños"})

    fig_reg_padron = px.bar(registro_padron_group_df, x="Estado Niño", y="Niños",color = "Tipo Registro Padrón Nominal",
                                    text="Niños", orientation='v',title = "Niños Derivados y Transitos por Estado de Visita",barmode='group',)
    fig_reg_padron.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_reg_padron.update_layout(xaxis=dict(title=dict(text="Estado de Visita de los Niños")),yaxis=dict(title=dict(text="Número de Niños")),font=dict(size=16))
    
    tipo_seguro_df = dataframe_.groupby(["Establecimiento de Salud","Tipo de Seguro"])[["Número de Documento"]].count().sort_values("Número de Documento").reset_index()
    tipo_seguro_df = tipo_seguro_df.rename(columns=  {"Número de Documento":"Niños"})
    fig_tipo_seguro = px.bar(tipo_seguro_df, x="Niños", y="Establecimiento de Salud",color = "Tipo de Seguro",
                                    text="Niños", orientation='h',title = "Tipo de Seguro por Establicimiento de salud",barmode='stack',)
    fig_tipo_seguro.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig_tipo_seguro.update_layout(xaxis=dict(title=dict(text="Número de Niños")),yaxis=dict(title=dict(text="Establecimiento de Salud")),font=dict(size=14))
    
    tipo_seguro_all_df = dataframe_.groupby(["Tipo de Seguro"])[["Número de Documento"]].count().sort_values("Número de Documento").reset_index()
    tipo_seguro_all_df = tipo_seguro_all_df.rename(columns=  {"Número de Documento":"Niños"})
    
    fig_seguro_all = px.pie(tipo_seguro_all_df, values='Niños', names='Tipo de Seguro',
                        title='Tipo de Seguro')
    fig_seguro_all.update_traces(textposition='inside', textinfo='percent+label+value',insidetextfont=dict(size=18))
    ####
    columnas_add = st.columns(2)
    with columnas_add[0]:
        tab1_carga, tab2_carga,tab3_carga,tab4_carga = st.tabs(["Niños Cargados", "Visitas","No Encontrados","Rechazados"])
        with tab1_carga:
            st.plotly_chart(fig_eess_count)
            
        with tab2_carga:
            st.plotly_chart(fig_eess_top_visitas)
        with tab3_carga:
            st.plotly_chart(fig_eess_count_noencon)
        with tab4_carga:
            st.plotly_chart(fig_eess_count_rechazado)
    with columnas_add[1]:
        tab1_carga, tab2_carga,tab3_carga,tab4_carga,tab5_carga = st.tabs(["Visitas Registrados MOVIL", "Visitas Registrados WEB","Niños Faltantes","Niños Transito","Niños Otro Padrón"])
        with tab1_carga:
            st.plotly_chart(fig_eess_top_visitas_movil)
        with tab2_carga:
            st.plotly_chart(fig_eess_top_visitas_web)
        with tab3_carga:
            st.plotly_chart(fig_eess_sinvd)
        with tab4_carga:
            st.plotly_chart(fig_eess_transito)
        
        with tab5_carga:
            st.plotly_chart(fig_eess_derivados)

    columnas = st.columns(2)
    #columnas[0].text("Estado Actual Niños Visitados")
    with columnas[0]:
        tab_estado1, tab_estado2 = st.tabs(["Estado de Niños", "Estado de Visitas"])
        with tab_estado1:
            st.plotly_chart(fig_estado_child)
        with tab_estado2:
            st.plotly_chart(fig_estado_vd_child)
            
    #columnas[1].text("Entidad que Actualiza Padrón")
    with columnas[1]:
            tab_estado1, tab_estado2 = st.tabs(["Estado Visitas Transito - Derivados", "Estado de Visitas Actualizaciones Padrón"])
            with tab_estado1:
                st.plotly_chart(fig_reg_padron)
            with tab_estado2:
                st.plotly_chart(fig_entidad_child)
            #
    #columnas[2].text("Estado Actual de las Visitas")
    columnas_last = st.columns([8,4])
    with columnas_last[0]:
        st.plotly_chart(fig_tipo_seguro)
    with columnas_last[1]:
        st.plotly_chart(fig_seguro_all)
    """
    con la linea podemos hacer corte del mes
    """
    gb = GridOptionsBuilder.from_dataframe(proyectado_dff)
    gb.configure_default_column(cellStyle={'fontSize': '20px'}) 
    grid_options = gb.build()
    
    
    grid_response = AgGrid(proyectado_dff, # Dataframe a mostrar
                            gridOptions=grid_options,
                            enable_enterprise_modules=False,
                            #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                            update_mode='MODEL_CHANGED',
                            fit_columns_on_grid_load=True,
                        
    )
    
    #st.dataframe(proyectado_dff)
    with st.expander("Descargas"):
        st.download_button(
                label="Descargar Reporte",
                data=convert_excel_df(dataframe_),
                file_name=f"EstadoVisitas_{select_year}_{select_mes}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar Meta Visitas",
                data=convert_excel_df(proyectado_dff),
                file_name=f"VD_GEO_REF_{select_year}_{select_mes}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
                label="Descargar Reporte Duplicados",
                data=convert_excel_df(cel_duplicados_df),
                file_name=f"Duplicados_{select_year}_{select_mes}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

def geo_childs():
    styles(2)
    
    df = fetch_vd_childs()
    dff = df[df["Dispositivo Intervención"]=="MOVIL"]
    
    eess = list(dff["Establecimiento de Salud"].unique())
    year = list(dff["Año"].unique())
    month = list(dff["Mes"].unique())
    latitud_name = "Latitud Intervención"
    longitud_name = "Longitud Intervención"
    col_filt = st.columns([3,6,1,1])
    with col_filt[0]:
        st.title("Georef a Niños")
    with col_filt[1]:
        eess_selected = st.multiselect("Establecimientos de Salud",eess,placeholder="Escoja un Establecimiento de Salud")
        if len(eess_selected) > 0:
            dff = dff[dff["Establecimiento de Salud"].isin(eess_selected)]
    with col_filt[2]:
        year_selected = st.selectbox("Año",year)
        dff = dff[dff["Año"]==year_selected]
    with col_filt[3]:
        month_selected = st.selectbox("Mes",month)
        dff = dff[dff["Mes"]==month_selected]
    
    #st.write(dff.shape)
    
    tab1,tab2,=st.tabs(['Mapa','Datos'])
    with tab1:    
        #
        col_filt_map = st.columns([3,3,3,3])
        with col_filt_map[0]:
            as_selected = st.selectbox('Actor Social',options=sorted(list(dff["Actores Sociales"].unique())),placeholder="Escoja un actor social",index=None) 
            if as_selected != None:
                dff = dff[dff["Actores Sociales"] == as_selected]
        
        with col_filt_map[1]:
            doc_input = st.text_input("Buscar por Doc Niño")
            if len(doc_input) == 8 :
                dff = dff[dff["Número de Documento de Niño"] == doc_input]

        with col_filt_map[2]:  
            parMapa = st.selectbox('Tipo Mapa',options=["open-street-map", "carto-positron","carto-darkmatter"])          
            
        with col_filt_map[3]:
            st.metric("N° de Georreferencias",dff.shape[0]) 
            

        
        fig = px.scatter_mapbox(
            dff,lat=latitud_name,lon=longitud_name, 
            color="Establecimiento de Salud", hover_name="Actores Sociales",
            hover_data=["Número de Documento de Niño","Fecha Intervención"],
            zoom=14,
            height=600,
            #color_continuous_scale=px.colors.cyclical.IceFire
        )
        
        fig.update_layout(mapbox_style=parMapa)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        fig.update_layout(legend=dict(
            orientation="h",
            #entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        map_ = st.plotly_chart(fig, on_select="rerun",theme=None)
        try:
            st.dataframe(dff[dff["Número de Documento de Niño"]==map_["selection"]["points"][0]["customdata"][0]])
        except:
            st.warning("Seleccione Niño Georreferenciado")
        
    with tab2:
        st.dataframe(dff,use_container_width=True)
        #st.dataframe(dff)
    

