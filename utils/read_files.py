import pandas as pd
import os

def read_files_padron():
    padron_act_df = pd.read_excel(".\\src\\files\\padron\\rp_all.xlsx",skiprows=4)
    padron_act_df['Tipo_file'] = "Activos"
    padron_act_ob_df = pd.read_excel(".\\src\\files\\padron\\rp_observados.xlsx",skiprows=4)
    padron_act_ob_df['Tipo_file'] = "Activos Observados"
    padron_act_tran_df = pd.read_excel(".\\src\\files\\padron\\rp_transito.xlsx",skiprows=4)
    padron_act_tran_df['Tipo_file'] = "Activos Transito"
    padron_df = pd.concat([padron_act_df, padron_act_ob_df, padron_act_tran_df], ignore_index=True)
    del padron_act_df
    del padron_act_ob_df
    del padron_act_tran_df
    return padron_df

def read_files_cargavd():
    directory_2024 = '.\\src\\files\\c1\\2024\\carga niños'
    directory_2025 = '.\\src\\files\\c1\\2025\\carga niños'
    f_cargar_2024 = os.listdir(directory_2024)
    f_cargar_2025 = os.listdir(directory_2025)
    f_cargar = f_cargar_2024+f_cargar_2025
    cvd_df=pd.DataFrame()
    for file in f_cargar:
        if file == "det_nino_jul.xls":
            det_nino_jul_df = pd.read_excel(f'{directory_2024}\\{file}',skiprows=7)
            det_nino_jul_df = det_nino_jul_df[det_nino_jul_df['Tipo de Documento del niño']!="-"]
            cvd_df = cvd_df._append(det_nino_jul_df,ignore_index=True)
            del det_nino_jul_df
        else:
            if file in f_cargar_2024:
                cvd_df = cvd_df._append(pd.read_excel(f'{directory_2024}\\{file}',skiprows=7),ignore_index=True)
            else:
                cvd_df = cvd_df._append(pd.read_excel(f'{directory_2025}\\{file}',skiprows=7),ignore_index=True)
    
    return cvd_df

def read_files_actividadvd():
    directory_2024 = '.\\src\\files\\c1\\2024\\visitas domiciliarias'
    directory_2025 = '.\\src\\files\\c1\\2025\\visitas domiciliarias'
    f_cargar_2024 = os.listdir(directory_2024)
    f_cargar_2025 = os.listdir(directory_2025)
    f_cargar = f_cargar_2024+f_cargar_2025
    visitas_df=pd.DataFrame()
    for file in f_cargar:
        if file in f_cargar_2024:
            visitas_df = visitas_df._append(pd.read_excel(f'{directory_2024}\\{file}',skiprows=7),ignore_index=True)
        else:
            visitas_df = visitas_df._append(pd.read_excel(f'{directory_2025}\\{file}',skiprows=7),ignore_index=True)
    return visitas_df

def read_files_carga_gestantes():
    directory = '.\\src\\files\\gestantes\\carga\\'
    files_gestantes = os.listdir(directory)
    gestantes_carga_df = pd.DataFrame()
    
    for file in files_gestantes:
        df = pd.read_excel(f'{directory}\\{file}',skiprows=7,dtype={"Número de Documento": "str"})
        df = df.drop_duplicates(subset='Número de Documento', keep='first')
        gestantes_carga_df = gestantes_carga_df._append(df,ignore_index=True)
        
    gestantes_carga_df["Número de Documento"] = gestantes_carga_df["Número de Documento"].str.strip()
    gestantes_carga_df['Mes'] = gestantes_carga_df['Fecha Mínima de Inicio de Intervención'].str[5:7]
    gestantes_carga_df['Año'] = gestantes_carga_df['Fecha Mínima de Inicio de Intervención'].str[:4]
    return gestantes_carga_df      

def read_files_actividad_gestantes():
    directory = '.\\src\\files\\gestantes\\visitas\\' 
    files_gestantes = os.listdir(directory)
    gestantes_act_df = pd.DataFrame()
    for file in files_gestantes:
        gestantes_act_df = gestantes_act_df._append(pd.read_excel(f'{directory}\\{file}',skiprows=7,dtype={"Número de Documento": "str"}),ignore_index=True)
    
    return gestantes_act_df    
        