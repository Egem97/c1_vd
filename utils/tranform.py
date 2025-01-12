import pandas as pd
import datetime
import re
from constants import *
from utils.helpers import *

def transform_padron(dataframe):
    dataframe.columns = PADRON_COLS
    dataframe= dataframe.drop(DROP_COLS_PADRON, axis=1)
    dataframe['SEXO'] = dataframe['SEXO'].map({1: 'MASCULINO', 2: 'FEMENINO'})
    dataframe[['CNV', 'CUI', 'DNI']]=dataframe[['CNV', 'CUI', 'DNI']].fillna(0)#.astype('int')
    dataframe[['CNV', 'CUI', 'DNI']]=dataframe[['CNV', 'CUI', 'DNI']].astype('int')
    dataframe['Documento']= dataframe.apply(lambda x: documento_unique(x['CNV'], x['CUI'],x['DNI'],x['CÓDIGO DE PADRON'],'DOC'),axis=1)
    dataframe['Tipo de Documento'] = dataframe.apply(lambda x: documento_unique(x['CNV'], x['CUI'],x['DNI'],x['CÓDIGO DE PADRON'],'TIPO'),axis=1)
    #iterando todas las columnas de fechas
    for columna in COLUMNS_FECHAS:
        dataframe[columna]=dataframe[columna].astype(str)
        dataframe[columna] = pd.to_datetime(dataframe[columna].str.strip(), format='%d/%m/%Y', errors='coerce')
    #iterando todas las columnas relacionados a nombres y apellidos
    for columnas in COLUMNS_DATOSP:
        dataframe[columnas]=dataframe[columnas].fillna('')    
        
    dataframe['DATOS NIÑO PADRON'] = dataframe.apply(lambda x: concatenar_datos(x['APELLIDO PATERNO DEL NIÑO'], x['APELLIDO MATERNO DEL NIÑO'],x['NOMBRES DEL NIÑO']),axis=1)
    dataframe['DATOS MADRE PADRON'] = dataframe.apply(lambda x: concatenar_datos(x['APELLIDO PATERNO DE LA MADRE'], x['APELLIDO MATERNO DE LA MADRE'],x['NOMBRES DE LA MADRE']),axis=1)
    dataframe['DATOS JEFE PADRON'] = dataframe.apply(lambda x: concatenar_datos(x['APELLIDO PATERNO DEL JEFE DE FAMILIA'], x['APELLIDO MATERNO DEL JEFE DE FAMILIA'],x['NOMBRES DEL JEFE DE FAMILIA']),axis=1)
    dataframe['CELULAR2_PADRON'] = dataframe.apply(lambda x: verificar_numeros(x['CELULAR_CORREO']),axis=1)
    dataframe[['CÓDIGO DE PADRON','CNV', 'CUI', 'DNI']]=dataframe[['CÓDIGO DE PADRON','CNV', 'CUI', 'DNI']].astype(str)
    return dataframe

def transform_carga_vd(dataframe):
    dataframe['Mes'] = dataframe['Fecha Mínima de Inicio de Intervención'].str[5:7]
    dataframe['Año'] = dataframe['Fecha Mínima de Inicio de Intervención'].str[:4]
    dataframe['Mes'] = dataframe['Mes'].astype(int)
    dataframe['Año'] = dataframe['Año'].astype(int)
    dataframe['Celular de la madre'] = dataframe['Celular de la madre'].fillna(0).astype(int)
    dataframe['Motivo referencia'] = dataframe['Motivo referencia'].fillna("Sin Referencia")
    dataframe= dataframe.drop(DROP_COLS_CVD, axis=1)
    return dataframe

def transform_actividad_vd(dataframe):
    dataframe= dataframe.drop(DROP_COLS_AVD, axis=1)
    dataframe['Número de Documento de Niño'] = dataframe['Número de Documento de Niño'].astype(str)
    dataframe['Año'] = dataframe['Año'].astype(str)
    dataframe['Celular de la Madre'] = dataframe['Celular de la Madre'].astype(str)
    return dataframe