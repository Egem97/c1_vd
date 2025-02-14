import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from styles import styles
from utils.cache_handler import *
from utils.functions_data import childs_unicos_visitados
from utils.helpers import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode 

def review_child():
    #styles(1)
    st.markdown(
            """
            <style>
                .custom-container {
                    
                    background-color: #1e1e1e;
                    border-radius: 10px;
                }
                .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 2.5rem;
                    padding-right: 2.5rem;
                }
                
            </style>
            """,
            unsafe_allow_html=True
        )
    actvd_df = fetch_vd_childs()
    carga_df = fetch_carga_childs()
    padron_df = fetch_padron()
    datos_ninos_df = pd.read_parquet('datos_niños.parquet', engine='pyarrow')

    
    cols = st.columns([3,2,2,3])
    with cols[0]:
        st.title("Revision de Niños")
    with cols[1]:
        select_year  = st.selectbox("Año:", ["2025"], key="select1")
        
    with cols[2]:
        select_mes  = st.selectbox("Mes:", ["Ene","Feb"], key="select2",index=True)
    with cols[3]:
        doc = st.text_input("Ingrese Documento")
    
    datos_ninos_df = datos_ninos_df[datos_ninos_df["Periodo"]==f"{select_year} - {select_mes}"]
    carga_filt_df = carga_df[(carga_df['Año']==int(select_year))&(carga_df['Mes']==int(mestext_short(select_mes)))]
    actvd_filt_df = actvd_df[(actvd_df['Año']==select_year)&(actvd_df['Mes']==select_mes)]

   
    niños_unicos_vd = childs_unicos_visitados(actvd_filt_df,'Número de Documento de Niño',"ALL CHILDS W DUPLICADOS")
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
            'EESS_C1', 'Fecha_ult_at_c1','Zona', 'Manzana', 'Sector','Tipo_file','ENTIDAD','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA','Estado_Visita_Ult', 'Mes', 'Año'
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
                'EESS ULTIMA ATENCION', 'Fecha Ultima Atención', 'Zona', 'Manzana', 'Sector', 'Tipo Registro Padrón Nominal',
                'Entidad Actualiza','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA', 'Estado Niño', 'Mes', 'Año'
            ]
    dataframe_['Estado Visitas'] =  dataframe_.apply(lambda x: estado_visitas_completas(x['N° Visitas Completas'], x['Total de VD presenciales Válidas'],x['Estado Niño']),axis=1)#.apply(lambda x: completar_names_col(x['DATOS NIÑO PADRON'], x['Niño']),axis=1)
    dataframe_['Estado Niño'] = dataframe_['Estado Niño'].fillna(f"Sin Visita ({select_mes})")
    dataframe_['USUARIO QUE MODIFICA'] = dataframe_['USUARIO QUE MODIFICA'].fillna(f"Usuario no definido")
    dataframe_['EDAD FORMATO'] = dataframe_['Fecha de Nacimiento'].apply(calcular_edad)

    if doc:
        dataframe_ = dataframe_[dataframe_["Número de Documento"]==doc]
        
        
        
        cols_info = st.columns(4)
        with cols_info[0]:
            with st.container(border=True):
                st.markdown('<div class="custom-container">', unsafe_allow_html=True)
                st.write("DATOS DEL NIÑO")
                st.text_input("Nombres",list(dataframe_["Datos del niño"])[0],disabled=True )
                cols_child = st.columns([3,6])
                cols_child[0].text_input("Tipo Doc",list(dataframe_["Tipo Documento(P)"])[0],disabled=True )
                cols_child[1].text_input("Fecha Nacimiento",list(dataframe_["Fecha de Nacimiento"])[0],disabled=True )
                cols_child2 = st.columns([3,3])
                cols_child2[0].text_input("Edad",list(dataframe_["EDAD FORMATO"])[0],disabled=True )
                cols_child2[1].text_input("Tipo Reg",list(dataframe_["Tipo Registro Padrón Nominal"])[0],disabled=True )
                cols_child3 = st.columns([3,3])
                cols_child3[0].text_input("Doc Madre Padrón",list(dataframe_["Número Doc Madre(P)"])[0],disabled=True )
                cols_child3[1].text_input("Doc Madre C1",list(dataframe_["Número Doc Madre"])[0],disabled=True )
                st.text_input("Datos Madre",list(dataframe_["Datos Madre(P)"])[0],disabled=True )
                cols_child4 = st.columns([2,3])
                cols_child4[0].text_input("Doc Padre",list(dataframe_["Número Doc Jefe Familia(P)"])[0],disabled=True )
                cols_child4[1].text_input("Doc Padre",list(dataframe_["Datos Jefe Famlia(P)"])[0],disabled=True )

                st.markdown('</div>', unsafe_allow_html=True)
        with cols_info[1]:
            with st.container(border=True):
                st.markdown('<div class="custom-container">', unsafe_allow_html=True)
                st.write("DATOS DE ACTUALIZACIÓN")
                st.text_input("Dirección Padrón",list(dataframe_["Dirección(P)"])[0],disabled=True )
                st.text_input("Dirección C1",list(dataframe_["Dirección Compromiso 1"])[0],disabled=True )
                st.text_input("Referencia Padrón",list(dataframe_["Referencia Dirección(P)"])[0],disabled=True )
                cols_child_d= st.columns([3,3,3])
                cols_child_d[0].text_input("Celular P",list(dataframe_["Celular(P)"])[0],disabled=True )
                cols_child_d[1].text_input("Celular C1",list(dataframe_["Celular Madre"])[0],disabled=True )
                cols_child_d[2].text_input("Celular P2",list(dataframe_["Celular2(P)"])[0],disabled=True )
                cols_child_c= st.columns([2,3])
                #cols_child_c[0].text_input("Celular Padrón 2",list(dataframe_["Celular2(P)"])[0],disabled=True )
                cols_child_c[0].text_input("Visita Padrón",list(dataframe_["MENOR VISITADO"])[0],disabled=True )
                cols_child_c[1].text_input("Usuariario-Actualización",list(dataframe_["USUARIO QUE MODIFICA"])[0],disabled=True )
                cols_child_x= st.columns([3,3])
                cols_child_x[0].text_input("Entidad",list(dataframe_["Entidad Actualiza"])[0],disabled=True )
                cols_child_x[1].text_input("Fecha Actualización",list(dataframe_["FECHA DE MODIFICACIÓN DEL REGISTRO"])[0],disabled=True )
                #st.text_input("Establecimiento ULTIMA ATENCION C1",f"{list(dataframe_["EESS ULTIMA ATENCION"])[0]} - {list(dataframe_["Fecha Ultima Atención"])[0]}",disabled=True )
                #FRECUENCIA DE ATENCION
                #st.text_input("Frecuencia de Atención Padrón",f"{list(dataframe_["FRECUENCIA DE ATENCION"])[0]}",disabled=True )
                st.markdown('</div>', unsafe_allow_html=True)
        with cols_info[2]:
            with st.container(border=True):
                st.markdown('<div class="custom-container">', unsafe_allow_html=True)
                st.write("DATOS DE ESTABLECIMIENTOS DE SALUD")
                st.text_input("Establecimiento de Nacimiento",list(dataframe_["EESS NACIMIENTO"])[0],disabled=True )
                st.text_input("Establecimiento de Ultima Atención",list(dataframe_["EESS ULTIMA ATENCION(P)"])[0],disabled=True )
                st.text_input("Establecimiento de ADSCRIPCIÓN",list(dataframe_["EESS ADSCRIPCIÓN"])[0],disabled=True )
                st.text_input("Establecimiento ULTIMA ATENCION C1",f"{list(dataframe_["EESS ULTIMA ATENCION"])[0]} - {list(dataframe_["Fecha Ultima Atención"])[0]}",disabled=True )
                #FRECUENCIA DE ATENCION
                st.text_input("Frecuencia de Atención Padrón",f"{list(dataframe_["FRECUENCIA DE ATENCION"])[0]}",disabled=True )
                st.markdown('</div>', unsafe_allow_html=True)
        with cols_info[3]:
            with st.container(border=True):
                st.markdown('<div class="custom-container">', unsafe_allow_html=True)
                st.write("DATOS DE VISITA DOMICILIARIA")
                st.text_input("Establecimiento de Salud",list(dataframe_["Establecimiento de Salud"])[0],disabled=True )
                st.text_input("Actor Social",list(dataframe_["Actor Social"])[0],disabled=True )
                st.text_input("Estado de las Visitas",list(dataframe_["Estado Visitas"])[0],disabled=True )
                #FRECUENCIA DE ATENCION
                
                st.markdown('</div>', unsafe_allow_html=True)
        only_doc_df = actvd_df[actvd_df["Número de Documento de Niño"]==doc]
        
        only_doc_df = only_doc_df[["Establecimiento de Salud","Número de Documento de Niño","Año","Mes","Etapa","Celular de la Madre","Dirección"]]
        only_doc_df["Celular de la Madre"] = only_doc_df["Celular de la Madre"].astype(float)
        #st.dataframe(only_doc_df)
        gb = GridOptionsBuilder.from_dataframe(only_doc_df)
        #gb.configure_selection('multiple', use_checkbox=True) 
        grid_options = gb.build()
        grid_response = AgGrid(only_doc_df, # Dataframe a mostrar
                            gridOptions=grid_options,
                            enable_enterprise_modules=False,
                            #theme='alpine',  # Cambiar tema si se desea ('streamlit', 'light', 'dark', 'alpine', etc.)
                            update_mode='MODEL_CHANGED',
                            fit_columns_on_grid_load=True,
                        
        )
        #st.write(dataframe_.columns)