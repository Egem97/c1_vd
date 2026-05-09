import pandas as pd 

def childs_unicos_visitados( dataframe = pd.DataFrame, col_name_doc = "", estado = "ALL CHILDS" ):
    
    if estado == "ALL CHILDS":
        vd_ref = dataframe.groupby([col_name_doc,"Etapa"])[["Año"]].count().reset_index()
        vd_ref.columns = ["Documento","Etapa","count"]
        return vd_ref
    elif estado == "CHILDS ETAPA":
        vd_ref = dataframe.groupby([col_name_doc,"Etapa"])[["Año"]].count().reset_index()
        vd_ref.columns = ["Documento","Etapa","count"]
        vd_ref_df = vd_ref.groupby(["Etapa"])[["count"]].count().reset_index()
        vd_ref_df = vd_ref_df.rename(columns=  {"count":"Registros"})
        return vd_ref_df
    elif estado == "ALL CHILDS W DUPLICADOS":
        vd_ref = dataframe.groupby([col_name_doc,"Etapa"])[["Año"]].count().reset_index()
        vd_ref = vd_ref.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
        vd_ref = vd_ref.drop_duplicates(subset = col_name_doc, keep='first')
        vd_ref.columns = ["Documento","Etapa","count"]
        return vd_ref
    elif estado == "CHILDS ETAPA W DUPLICADOS":
        vd_ref = dataframe.groupby([col_name_doc,"Etapa"])[["Año"]].count().reset_index()
        vd_ref = vd_ref.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
        vd_ref = vd_ref.drop_duplicates(subset = col_name_doc, keep='first')
        vd_ref.columns = ["Documento","Etapa","count"]
        vd_ref_df = vd_ref.groupby(["Etapa"])[["count"]].count().reset_index()
        vd_ref_df = vd_ref_df.rename(columns=  {"count":"Registros"})
        return vd_ref_df
    
def gestantes_unicas_visitados( dataframe = pd.DataFrame, col_name_doc = "", estado = "ALL GESTANTE" ):
    
    if estado == "ALL GESTANTE":
        vd_ref = dataframe.groupby([col_name_doc,"Actores Sociales","Etapa"])[["Año"]].count().reset_index()
        vd_ref.columns = ["Documento","Actores Sociales","Etapa","count"]
        vd_ref["Documento"] = vd_ref["Documento"].str.strip()    
        return vd_ref
    elif estado == "GESTANTE ETAPA":
        
        return ""
    elif estado == "ALL GESTANTE W DUPLICADOS":
        vd_ref = dataframe.groupby([col_name_doc,"Actores Sociales","Etapa"])[["Año"]].count().reset_index()
        vd_ref = vd_ref.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
        vd_ref = vd_ref.drop_duplicates(subset='Número de Documento', keep='first')
        vd_ref.columns = ["Documento","Actores Sociales","Etapa","count"]
        vd_ref["Documento"] = vd_ref["Documento"].str.strip()  
        return vd_ref
    elif estado == "GESTANTE ETAPA W DUPLICADOS":
        
        return ""
    
def fix_data_childs(df = pd.DataFrame):
    periodo = df["Periodo"].unique()[0]
    if  periodo == "2025-Jun" or periodo == "2025-Jul":#or periodo == "2025-Nov"
        #periodo_error = "2025-Jun"
        df_ = df.copy()
        df["Documento_c1"] = df_["Tipo_Doc"]
        df["Niño"] = df_["Documento_c1"]
        df["Tipo_Doc"] = ""
        df["Fecha_ult_at_c1"] = df_["EESS_C1"]
        df["EESS_C1"] = ""
        del df_
        return df
    else:
        return df


def childs_unicos_visitados_month( dataframe = pd.DataFrame, col_name_doc = "", estado = "ALL CHILDS" ):
    
    if estado == "ALL CHILDS":
        vd_ref = dataframe.groupby([col_name_doc,"Etapa","Mes"])[["Año"]].count().reset_index()
        vd_ref.columns = ["Documento","Etapa","Mes","count"]
        return vd_ref
    elif estado == "CHILDS ETAPA":
        vd_ref = dataframe.groupby([col_name_doc,"Etapa","Mes"])[["Año"]].count().reset_index()
        vd_ref.columns = ["Documento","Etapa","Mes","count"]
        vd_ref_df = vd_ref.groupby(["Etapa"])[["count"]].count().reset_index()
        vd_ref_df = vd_ref_df.rename(columns=  {"count":"Registros"})
        return vd_ref_df
    elif estado == "ALL CHILDS W DUPLICADOS":
        vd_ref = dataframe.groupby([col_name_doc,"Etapa","Mes"])[["Año"]].count().reset_index()
        vd_ref = vd_ref.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
        #vd_ref = vd_ref.drop_duplicates(subset = col_name_doc, keep='first')
        vd_ref.columns = ["Documento","Etapa","Mes","count"]
        prioridad_map = {
            'Rechazo': 0,
            'No Encontrado': 1,
            'Visita Domiciliaria (1 a 5 meses)': 2,
            'Visita Domiciliaria (6 a 12 Meses)': 2,
        }
        vd_ref['prioridad'] = vd_ref['Etapa'].map(prioridad_map)
        vd_ref = vd_ref.sort_values(['Documento', 'Mes', 'prioridad'])
        vd_ref = vd_ref.drop_duplicates(subset=['Documento', 'Mes'], keep='first')    
        vd_ref = vd_ref.drop('prioridad', axis=1)
        return vd_ref
    elif estado == "CHILDS ETAPA W DUPLICADOS":
        vd_ref = dataframe.groupby([col_name_doc,"Etapa","Mes"])[["Año"]].count().reset_index()
        vd_ref = vd_ref.sort_values(by='Etapa', key=lambda x: x.isin(['No Encontrado', 'Rechazado']))
        vd_ref = vd_ref.drop_duplicates(subset = col_name_doc, keep='first')
        vd_ref.columns = ["Documento","Etapa","Mes","count"]
        vd_ref_df = vd_ref.groupby(["Etapa","Mes"])[["count"]].count().reset_index()
        vd_ref_df = vd_ref_df.rename(columns=  {"count":"Registros"})
        return vd_ref_df