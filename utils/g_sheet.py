import re
import pandas as pd
import gspread
import streamlit as st
import time
from oauth2client.service_account import ServiceAccountCredentials

# Paso 1: Autenticación
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("nifty-might-269005-cd303aaaa33f.json", scope)
client = gspread.authorize(creds)

@st.cache_data(ttl=180)  # Cache se actualiza cada 3 minutos (180 segundos)
def read_sheet(key_sheet, sheet_name):
    try:
        spreadsheet = client.open_by_key(key_sheet)
        sheet = spreadsheet.worksheet(sheet_name)
        data = sheet.get_all_values()

        return data
    except Exception as e:
        return key_sheet, f"Error: {str(e)}"


def read_sheet_with_polling(key_sheet, sheet_name, refresh_interval=60):
    """
    Función que carga datos de Google Sheets con polling inteligente usando Session State.
    
    Args:
        key_sheet (str): ID de la hoja de Google Sheets
        sheet_name (str): Nombre de la hoja específica
        refresh_interval (int): Intervalo de actualización en segundos (default: 60)
    
    Returns:
        data: Datos de la hoja o mensaje de error
    """
    current_time = time.time()
    
    # Crear una clave única para este sheet específico
    cache_key = f"sheet_data_{key_sheet}_{sheet_name}"
    last_update_key = f"last_update_{key_sheet}_{sheet_name}"
    
    # Inicializar session state si no existe
    if cache_key not in st.session_state:
        st.session_state[cache_key] = None
        st.session_state[last_update_key] = 0
    
    # Verificar si necesitamos actualizar los datos
    time_since_update = current_time - st.session_state[last_update_key]
    
    if (st.session_state[cache_key] is None or 
        time_since_update > refresh_interval):
        
        # Mostrar indicador de carga solo en primera carga o cuando han pasado muchos minutos
        if st.session_state[cache_key] is None or time_since_update > 300:  # 5 minutos
            with st.spinner(f"Cargando datos de {sheet_name}..."):
                new_data = _fetch_sheet_data(key_sheet, sheet_name)
        else:
            # Actualización silenciosa en background
            new_data = _fetch_sheet_data(key_sheet, sheet_name)
        
        # Actualizar session state
        st.session_state[cache_key] = new_data
        st.session_state[last_update_key] = current_time
        
        # Opcional: mostrar mensaje de actualización
        if st.session_state[cache_key] is not None and time_since_update > 0:
            st.success(f"✅ Datos actualizados - {sheet_name}")
    
    return st.session_state[cache_key]


def _fetch_sheet_data(key_sheet, sheet_name):
    """
    Función auxiliar para cargar datos de Google Sheets.
    Separada para facilitar el manejo de errores y testing.
    """
    try:
        spreadsheet = client.open_by_key(key_sheet)
        sheet = spreadsheet.worksheet(sheet_name)
        data = sheet.get_all_values()
        return data
    except Exception as e:
        st.error(f"Error cargando {sheet_name}: {str(e)}")
        return None


def get_sheet_status(key_sheet, sheet_name):
    """
    Función auxiliar para obtener información sobre el estado del cache.
    Útil para debugging y monitoreo.
    """
    cache_key = f"sheet_data_{key_sheet}_{sheet_name}"
    last_update_key = f"last_update_{key_sheet}_{sheet_name}"
    
    if cache_key in st.session_state:
        last_update = st.session_state[last_update_key]
        current_time = time.time()
        time_since_update = current_time - last_update
        
        return {
            "has_data": st.session_state[cache_key] is not None,
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_update)),
            "seconds_since_update": int(time_since_update),
            "minutes_since_update": round(time_since_update / 60, 1)
        }
    return {"has_data": False, "last_update": "Never", "seconds_since_update": 0}


def clear_sheet_cache(key_sheet=None, sheet_name=None):
    """
    Función para limpiar manualmente el cache de polling.
    Si no se especifican parámetros, limpia todo el cache relacionado con sheets.
    """
    if key_sheet and sheet_name:
        # Limpiar cache específico
        cache_key = f"sheet_data_{key_sheet}_{sheet_name}"
        last_update_key = f"last_update_{key_sheet}_{sheet_name}"
        
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        if last_update_key in st.session_state:
            del st.session_state[last_update_key]
        
        st.success(f"Cache limpiado para {sheet_name}")
    else:
        # Limpiar todos los caches de sheets
        keys_to_remove = [key for key in st.session_state.keys() 
                         if key.startswith(("sheet_data_", "last_update_"))]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        st.success(f"Cache completo limpiado ({len(keys_to_remove)} items)")


@st.cache_data(ttl=180)  # Cache se actualiza cada 3 minutos (180 segundos)
def _sanitize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y desduplica nombres de columnas para evitar errores de reindex.
    - Quita espacios
    - Reemplaza vacíos por 'Col_i'
    - Desduplica añadiendo sufijos _2, _3, ...
    """
    cols = [str(c).strip() if (c is not None) else '' for c in df.columns]
    cols = [c if c != '' else f'Col_{i+1}' for i, c in enumerate(cols)]
    s = pd.Series(cols)
    s = s.where(~s.duplicated(), s + '_' + (s.groupby(s).cumcount() + 1).astype(str))
    df.columns = s
    return df

@st.cache_data(ttl=180)  # Cache se actualiza cada 3 minutos (180 segundos)
def read_and_concatenate_sheets(key_sheet, sheet_names, add_sheet_column=True):
    """
    Función que lee múltiples hojas de un Google Sheet y las concatena en un solo DataFrame.
    
    Args:
        key_sheet (str): ID de la hoja de Google Sheets
        sheet_names (list): Lista con los nombres de las hojas a leer
        add_sheet_column (bool): Si True, añade una columna con el nombre de la hoja de origen
    
    Returns:
        pandas.DataFrame: DataFrame concatenado con todos los datos o None si hay error
    """
    all_dataframes = []
    successful_sheets = []
    failed_sheets = []
    
    for sheet_name in sheet_names:
        try:
            # Leer datos de la hoja
            data = read_sheet(key_sheet, sheet_name)
            
            # Verificar si hay error en la respuesta
            if isinstance(data, tuple) and len(data) == 2 and "Error:" in str(data[1]):
                failed_sheets.append(f"{sheet_name}: {data[1]}")
                continue
            
            # Convertir a DataFrame si hay datos
            if data and len(data) > 0:
                # Usar la primera fila como headers
                if len(data) > 1:
                    df = pd.DataFrame(data[1:], columns=data[0])
                else:
                    df = pd.DataFrame(data)
                
                # Limpieza de columnas
                df = _sanitize_columns(df)
                
                # Añadir columna con el nombre de la hoja si se solicita
                if add_sheet_column:
                    df['sheet_origen'] = sheet_name
                
                all_dataframes.append(df.reset_index(drop=True))
                successful_sheets.append(sheet_name)
            else:
                failed_sheets.append(f"{sheet_name}: Hoja vacía")
                
        except Exception as e:
            failed_sheets.append(f"{sheet_name}: {str(e)}")
            continue
    
    # Mostrar resumen de resultados
    if successful_sheets:
        st.success(f"✅ Hojas leídas exitosamente: {', '.join(successful_sheets)}")
    
    if failed_sheets:
        st.warning(f"⚠️ Errores en hojas: {'; '.join(failed_sheets)}")
    
    # Concatenar DataFrames si hay datos
    if all_dataframes:
        try:
            concatenated_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
            st.info(f"📊 Total de filas concatenadas: {len(concatenated_df)}")
            return concatenated_df
        except Exception as e:
            st.error(f"Error al concatenar DataFrames: {str(e)}")
            return None
    else:
        st.error("No se pudieron leer datos de ninguna hoja")
        return None


@st.cache_data(ttl=600)  # Cache se actualiza cada 3 minutos (180 segundos)
def read_and_concatenate_sheets_optimized(key_sheet, sheet_names, add_sheet_column=True):
    """
    Versión optimizada que abre el spreadsheet una sola vez y lee todas las hojas.
    Mucho más eficiente para múltiples hojas.
    
    Args:
        key_sheet (str): ID de la hoja de Google Sheets
        sheet_names (list): Lista con los nombres de las hojas a leer
        add_sheet_column (bool): Si True, añade una columna con el nombre de la hoja de origen
    
    Returns:
        pandas.DataFrame: DataFrame concatenado con todos los datos o None si hay error
    """
    all_dataframes = []
    successful_sheets = []
    failed_sheets = []
    
    try:
        # Abrir el spreadsheet UNA SOLA VEZ
        with st.spinner(f"Conectando a Google Sheets..."):
            spreadsheet = client.open_by_key(key_sheet)
        
        # Obtener información de todas las hojas disponibles
        available_sheets = {ws.title: ws for ws in spreadsheet.worksheets()}
        
        with st.spinner(f"Leyendo {len(sheet_names)} hojas..."):

            for sheet_name in sheet_names:
                try:
                    # Verificar si la hoja existe
                    if sheet_name not in available_sheets:
                        failed_sheets.append(f"{sheet_name}: Hoja no encontrada")
                        continue
                    
                    # Obtener datos de la hoja
                    worksheet = available_sheets[sheet_name]
                    data = worksheet.get_all_values()
                   # st.write(sheet_name)
                    #st.write(data)
                    # Convertir a DataFrame si hay datos
                    if data and len(data) > 0:
                        #st.write(data)
                        # Usar la primera fila como headers
                        if len(data) > 1:
                            df = pd.DataFrame(data[1:], columns=data[0])
                            
                        else:
                            df = pd.DataFrame(data)
                        #st.write(df.shape)
                        # Limpiar DataFrame (eliminar filas completamente vacías)
                        df = df.dropna(how='all')
                        
                        if not df.empty:
                            # Normalizar/Desduplicar columnas
                            df = _sanitize_columns(df)
                            # Añadir columna con el nombre de la hoja si se solicita
                            if add_sheet_column:
                                df['sheet_origen'] = sheet_name
                            df = df.reset_index(drop=True)
                            all_dataframes.append(df)
                            successful_sheets.append(sheet_name)
                        else:
                            failed_sheets.append(f"{sheet_name}: Hoja vacía después de limpiar")
                    else:
                        failed_sheets.append(f"{sheet_name}: Sin datos")
                        
                except Exception as e:
                    failed_sheets.append(f"{sheet_name}: {str(e)}")
                    continue
        
        
        # Concatenar DataFrames si hay datos
       
        #st.write(all_dataframes)

        
        if all_dataframes:
            try:
                # Evitar conflictos por índices duplicados entre hojas
                concatenated_df = pd.concat(all_dataframes, ignore_index=True)
                #st.dataframe(concatenated_df)
                return concatenated_df
            except Exception as e:
                st.error(f"Error al concatenar DataFrames: {str(e)}")
                return None
        else:
            st.error("No se pudieron leer datos de ninguna hoja")
            return None
            
    except Exception as e:
        st.error(f"Error al abrir el Seguimiento Nominal: {str(e)}")
        return None


def read_and_concatenate_sheets_optimized_with_polling(key_sheet, sheet_names, add_sheet_column=True, refresh_interval=60):
    """
    Versión optimizada con polling que abre el spreadsheet una sola vez y lee todas las hojas.
    Mucho más eficiente para múltiples hojas.
    
    Args:
        key_sheet (str): ID de la hoja de Google Sheets
        sheet_names (list): Lista con los nombres de las hojas a leer
        add_sheet_column (bool): Si True, añade una columna con el nombre de la hoja de origen
        refresh_interval (int): Intervalo de actualización en segundos (default: 60)
    
    Returns:
        pandas.DataFrame: DataFrame concatenado con todos los datos o None si hay error
    """
    current_time = time.time()
    
    # Crear una clave única para este conjunto de sheets
    sheets_str = "_".join(sorted(sheet_names))  # Ordenar para consistencia
    cache_key = f"concat_optimized_data_{key_sheet}_{hash(sheets_str)}"
    last_update_key = f"concat_optimized_last_update_{key_sheet}_{hash(sheets_str)}"
    
    # Inicializar session state si no existe
    if cache_key not in st.session_state:
        st.session_state[cache_key] = None
        st.session_state[last_update_key] = 0
    
    # Verificar si necesitamos actualizar los datos
    time_since_update = current_time - st.session_state[last_update_key]
    
    if (st.session_state[cache_key] is None or 
        time_since_update > refresh_interval):
        
        # Mostrar indicador de carga solo en primera carga o cuando han pasado muchos minutos
        if st.session_state[cache_key] is None or time_since_update > 300:  # 5 minutos
            with st.spinner(f"Cargando y concatenando {len(sheet_names)} hojas (optimizado)..."):
                new_data = _fetch_and_concatenate_data_optimized(key_sheet, sheet_names, add_sheet_column)
        else:
            # Actualización silenciosa en background
            new_data = _fetch_and_concatenate_data_optimized(key_sheet, sheet_names, add_sheet_column)
        
        # Actualizar session state
        st.session_state[cache_key] = new_data
        st.session_state[last_update_key] = current_time
        
        # Opcional: mostrar mensaje de actualización
        if st.session_state[cache_key] is not None and time_since_update > 0:
            st.success(f"✅ Datos concatenados actualizados (optimizado) - {len(sheet_names)} hojas")
    
    return st.session_state[cache_key]


def _fetch_and_concatenate_data_optimized(key_sheet, sheet_names, add_sheet_column=True):
    """
    Función auxiliar optimizada para cargar y concatenar datos de múltiples hojas de Google Sheets.
    Abre el spreadsheet una sola vez para máxima eficiencia.
    """
    all_dataframes = []
    successful_sheets = []
    failed_sheets = []
    
    try:
        # Abrir el spreadsheet UNA SOLA VEZ
        spreadsheet = client.open_by_key(key_sheet)
        
        # Obtener información de todas las hojas disponibles
        available_sheets = {ws.title: ws for ws in spreadsheet.worksheets()}
        
        for sheet_name in sheet_names:
            try:
                # Verificar si la hoja existe
                if sheet_name not in available_sheets:
                    failed_sheets.append(f"{sheet_name}: Hoja no encontrada")
                    continue
                
                # Obtener datos de la hoja
                worksheet = available_sheets[sheet_name]
                data = worksheet.get_all_values()
                
                # Convertir a DataFrame si hay datos
                if data and len(data) > 0:
                    # Usar la primera fila como headers
                    if len(data) > 1:
                        df = pd.DataFrame(data[1:], columns=data[0])
                    else:
                        df = pd.DataFrame(data)
                    
                    # Limpiar DataFrame (eliminar filas completamente vacías)
                    df = df.dropna(how='all')
                    
                    if not df.empty:
                        # Normalizar/Desduplicar columnas
                        df = _sanitize_columns(df)
                        # Añadir columna con el nombre de la hoja si se solicita
                        if add_sheet_column:
                            df['sheet_origen'] = sheet_name
                        
                        all_dataframes.append(df.reset_index(drop=True))
                        successful_sheets.append(sheet_name)
                    else:
                        failed_sheets.append(f"{sheet_name}: Hoja vacía después de limpiar")
                else:
                    failed_sheets.append(f"{sheet_name}: Sin datos")
                    
            except Exception as e:
                failed_sheets.append(f"{sheet_name}: {str(e)}")
                continue
        
        # Concatenar DataFrames si hay datos
        if all_dataframes:
            try:
                concatenated_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
                return concatenated_df
            except Exception as e:
                st.error(f"Error al concatenar DataFrames: {str(e)}")
                return None
        else:
            return None
            
    except Exception as e:
        st.error(f"Error al abrir el spreadsheet: {str(e)}")
        return None


@st.cache_data(ttl=300)  # Cache por 5 minutos para nombres de hojas
def get_available_sheet_names(key_sheet):
    """
    Obtiene la lista de nombres de todas las hojas disponibles en el spreadsheet.
    
    Args:
        key_sheet (str): ID de la hoja de Google Sheets
    
    Returns:
        list: Lista con los nombres de todas las hojas disponibles, o None si hay error
    """
    try:
        with st.spinner("Obteniendo lista de hojas..."):
            spreadsheet = client.open_by_key(key_sheet)
            sheet_names = [ws.title for ws in spreadsheet.worksheets()]
            
        st.success(f"✅ Se encontraron {len(sheet_names)} hojas: {', '.join(sheet_names)}")
        return sheet_names
        
    except Exception as e:
        st.error(f"Error al obtener lista de hojas: {str(e)}")
        return None


@st.cache_data(ttl=180)  # Cache se actualiza cada 3 minutos
def read_all_sheets_optimized(key_sheet, add_sheet_column=True, exclude_sheets=None):
    """
    Lee TODAS las hojas disponibles en el spreadsheet y las concatena.
    Versión optimizada que abre el spreadsheet una sola vez.
    
    Args:
        key_sheet (str): ID de la hoja de Google Sheets
        add_sheet_column (bool): Si True, añade una columna con el nombre de la hoja de origen
        exclude_sheets (list): Lista de nombres de hojas a excluir (opcional)
    
    Returns:
        pandas.DataFrame: DataFrame concatenado con todos los datos o None si hay error
    """
    try:
        # Obtener todas las hojas disponibles
        all_sheet_names = get_available_sheet_names(key_sheet)
        
        if not all_sheet_names:
            return None
        
        # Filtrar hojas excluidas si se especifican
        if exclude_sheets:
            sheet_names = [name for name in all_sheet_names if name not in exclude_sheets]
            st.info(f"📋 Hojas excluidas: {', '.join(exclude_sheets)}")
        else:
            sheet_names = all_sheet_names
        
        st.info(f"📚 Leyendo TODAS las hojas ({len(sheet_names)} hojas)")
        
        # Usar la función optimizada para leer y concatenar
        return read_and_concatenate_sheets_optimized(key_sheet, sheet_names, add_sheet_column)
        
    except Exception as e:
        st.error(f"Error al leer todas las hojas: {str(e)}")
        return None


def create_sheet_selector(key_sheet, multiselect=True, default_all=False):
    """
    Crea un widget de Streamlit para seleccionar hojas de un spreadsheet.
    
    Args:
        key_sheet (str): ID de la hoja de Google Sheets
        multiselect (bool): Si True, permite selección múltiple, si False selecciona una sola
        default_all (bool): Si True, selecciona todas las hojas por defecto
    
    Returns:
        list/str: Lista de hojas seleccionadas (o string si multiselect=False)
    """
    # Obtener hojas disponibles
    available_sheets = get_available_sheet_names(key_sheet)
    
    if not available_sheets:
        st.error("No se pudieron obtener las hojas disponibles")
        return [] if multiselect else None
    
    if multiselect:
        default_selection = available_sheets if default_all else []
        selected_sheets = st.multiselect(
            "Selecciona las hojas a procesar:",
            options=available_sheets,
            default=default_selection,
            help=f"Hojas disponibles: {len(available_sheets)}"
        )
        return selected_sheets
    else:
        selected_sheet = st.selectbox(
            "Selecciona una hoja:",
            options=available_sheets,
            help=f"Hojas disponibles: {len(available_sheets)}"
        )
        return selected_sheet
