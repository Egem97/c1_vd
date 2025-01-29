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
    
