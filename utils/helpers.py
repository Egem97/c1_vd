import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from dateutil.relativedelta import relativedelta

@st.cache_data
def convert_excel_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
        workbook  = writer.book
        worksheet = writer.sheets['Datos']
        # Define el rango de la tabla
        (max_row, max_col) = df.shape
        column_settings = [{'header': col} for col in df.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {
            'columns': column_settings,
            'name': 'TablaExportada',
            'style': 'Table Style Medium 2'  # Estilo visual como en la imagen
        })
        # Ajusta el ancho de las columnas automáticamente
        for i, width in enumerate([max(len(str(s)) for s in df[col].astype(str).values.tolist() + [col]) for col in df.columns]):
            worksheet.set_column(i, i, width + 2)
    processed_data = output.getvalue()
    return processed_data
    

def documento_unique(cnv , cui, dni, cod, tipo):
    if dni !=0:
        resultado = dni
        doc = 'DNI'
    elif dni == 0 and cui != 0:
        resultado = cui
        doc = 'CUI'
    elif cui == 0 and dni == 0 and cnv !=0:
        resultado = cnv
        doc = 'CNV'
    elif cui == 0 and dni == 0 and cnv ==0:
        resultado = cod
        doc = 'CÓDIGO DE PADRON'
    return resultado if tipo == 'DOC' else doc

def concatenar_datos(ap,am,nombres):
    if len(ap) != 0 and len(nombres) != 0 and  len(am) != 0:
        resultado = ap+' '+am+' '+nombres     
    elif len(ap) == 0 and len(nombres) == 0 and len(am) != 0:
        resultado = am
    elif len(ap) != 0 and len(nombres) != 0 and len(am) == 0:
        resultado = ap+' '+nombres   
    elif len(ap) != 0 and len(nombres) == 0 and len(am) == 0:
        resultado = ap
    elif len(ap) == 0 and len(nombres) != 0 and len(am) == 0:
        resultado = nombres
    elif len(ap) == 0 and len(nombres) == 0 and  len(am) == 0:
        resultado = 'SIN DATOS'
    return resultado

def completar_names_col(name_padron,name_c1):
    if name_padron != name_padron:
        return name_c1
    else:
        return name_padron
    
def estado_nino(x,y):
    if x != x:
        if y == None:
            return "Niño Nuevo" 
        else: 
            return "Niño antiguo"
    else:
        return x
    
def estado_gestante(x,y):
    if x != x:
        if y == None:
            return "Gestante Nueva" 
        else: 
            return "Gestante Antigua"
    else:
        return x
    
def verificar_numeros(valor):
    # Contar los números en el string
    numeros = sum(c.isdigit() for c in valor)
    if numeros > 6:
        return valor
    else:
        return ''
    
def test(dataframe, col_name):
    distrito_condiciones = {
        'ARANJUEZ': ["URB. PALERMO", "PALERMO", "CHICAGO", "ARANJUEZ", "LAS MALVINAS", "MERCADO MAYORISTA", "SECTOR ATAHUALPA", "SECTOR SICHI ROCA"],
        'EL BOSQUE': ["SANTO DOMINGUITO", "URB. STO", "VILLA SANTA MARIA", "CARLOS WIES", "NORIA", "ASCENCIO DE SALAS", "SEMIRUSTICA EL BOSQUE", "PUEBLO JOVEN", "NUEVO SANTA ROSA", "EL BOSQUE", "MERCADO ASCOMAPAAT", "VILLA EL CONTADOR", "DIDEROT", "NUEVA SANTA ROSA", "SALAZAR BONDY", "VILLA DE CONTADORES", "TORRES DE QUEVEDO", "LUCIO SENECA", "JOSE LUIS DE CASTRO", "SINGAPUR", "LAS PAPAS", "SANTA ROSA", "ASCOMAPAT"],
        'LOS JARDINES': ["MAMPUESTO", "MANPUESTO", "LOS JARDINES", "SANTA TERESA DE AVILA", "SAN ISIDRO", "LOS CEDROS", "SAN FERNANDO", "PRIMAVERA", "SANTA INES", "LOS FRESNOS", "MOCHICA", "VIRGEN", "MERCADO LIBERTAD", "LA HERMELINDA", "LOS NARANJOS", "SANTA LUCIA", "NICOLAS DE PIEROLA", "SEMI RUSTICA SAN MIGUEL", "VILLA BOLIVARIANA", "WILFREDO TORRES", "HERMANOS UCEDA MEZA", "VILLA HERMOSA", "ELVIRA GARCIA Y GARCIA", "FAUSTINO SARMIENTO", "MIRAFLORES", "LORD COCKRANE", "JOSE VASCONCELLOS", "ROSAS DE AMERICA", "SAN LUIS", "TAKAYNAMO", "SANTA LEONOR", "ALTO MOCHICA", "VIRGEN DE LA PUERTA", "LAS ORQUIDEAS", "VILLA POLICIAL", "SOLILUZ", "GIRASOLES DE SAN ISIDRO", "ALAMEDA", "SEÑOR DE LOS MILAGROS"],
        'LOS GRANADOS "SAGRADO CORAZON"': ["EL SOL DEL CHACARERO", "LOS GRANADOS", "MARQUEZA", "DANIEL HOYLE", "CHIMU", "EL HUERTO", "LAS MALVINAS", "GRANADOS", "LAS ESMERALDAS", "LOS DIAMANTES", "LOS EUCALIPTOS", "LOS TOPACIO", "LOS TORNILLOS", "LOS ZAFIROS", "MANUEL UBALDE", "ZARUMILLA", "RAZURI", "EL PALOMAR", "RINCONADA"],
        'SAN MARTIN DE PORRES': ["CRISTOBAL DE MOLINA", "FRANCISCO FALCON", "SANTA MARIA", "TORRES ARAUJO", "GALENO", "GALENOS", "COVIDUNT", "JAZMINES", "JASMINES", "MONSERRATE", "LA MERCED", "LAS CASUARINAS", "SAN VICENTE", "EL RECREO", "LA PERLA", "REPUBLICA DE PANAMA", "29 DE DICIEMBRE", "LA ARBOLEDA", "LOS ALAMOS", "SAN LUIS", "VISTA HERMOSA", "LOS LAURELES", "REAL PLAZA", "ARMANDO VILLANUEVA DEL CAMPO", "SANTA OLGA", "LOS PINOS"],
        'PESQUEDA III': ["PESQUEDA III", "LAS CASUARINAS", "SAN FRANCISCO DE ASIS", "NUEVA RINCONDA", "LUIS DE LA PUENTE UCEDA", "PASAJE GRAU", "BOLOGNESI", "5 DE ABRIL", "LOS ESPINOS", "ATAHUALPA", "PASAJE N 5", "JOSE CARLOS MAREATEGUI", "JOSECARLOS MAREATEGUI", "LOS RUBIS", "LOS DIAMANTES"],
        'CLUB DE LEONES': ["COVICORTI", "CORTIJO", "SANCHEZ CARRION", "CAPULLANAS", "NATASHA", "TRUPAL", "VISTA HERMOSA", "HUERTA GRANDEE", "COVIRT", "SAN NICOLAS", "EL ALAMBRE", "SAN ANDRES", "SAN ANDRÉS", "CENTRO CIVICO", "LA ESMERALDA", "JUAN VELASCO ALVARADO", "LOS PINOS", "GERONIMO DE LA TORRE", "SANTA ISABEL", "SAN SALVADOR", "SOLILUZ", "CIRO ALEGRIA", "CENTRO TRUJILLO", "CENTRO HISTORICO", "SANTA ISABEL", "20 DE ABRIL", "PEDRO MUÑIZ", "JUAN PABLO II", "MANUEL VERA ENRIQUEZ", "JORGE CHAVEZ", "MARIANO BEJAR", "SAN JUDAS TADEO", "LUIS ALBRECHT", "GIRASOLES", "FRANCISCO BOLOGNESI", "LAS FLORES", "NATASHA ALTA", "ROSALES DE SAN ANDRES", "TIERRA VERDE", "JESUS DE NAZARETH", "JESUS DE NAZARET", "JESUS DE NAZATETH", "ALBERTH"],
        'CENTRO DE SALUD LA UNION': ["LA INTENDENCIA", "EL MOLINO", "LA UNION", "BARRIO OBRERO", "PROLONGACION SANTA", "EL EJERCITO", "EL EJÉRCITO"],
        'LIBERTAD': ["HUERTA BELLA", "ANIMAS", "INDEPENDENCIA", "LIBERTAD", "LOS PORTALES", "EX FUNDO DE LAS ANIMAS", "LA RICONADA MZ"],
        'PESQUEDA II': ["JUAN PABLO", "SANTA SOFIA", "LAS MALVAS", "PESQUEDA II", "HUASCARAN"]
    }

    condlist = []
    for distrito, condiciones in distrito_condiciones.items():
        condicion = dataframe[col_name].str.contains('|'.join(condiciones), case=False, na=False)
        condlist.append(condicion)

    choicelist = list(distrito_condiciones.keys())
    return np.select(condlist, choicelist, default='No Especificado')
    
def mes_short(x):
    dict_mes = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Oct',11:'Nov',12:'Dic'}
    return dict_mes[x] 

def mes_compname(x):
    dict_mes = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',7:'Julio',8:'Agosto',9:'Setiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}
    return dict_mes[x] 

def mestext_short(x):
    dict_mes = {'Ene':1,'Feb':2,'Mar':3,'Abr':4,'May':5,'Jun':6,'Jul':7,'Ago':8,'Set':9,'Oct':10,'Nov':11,'Dic':12}
    return dict_mes[x] 

def validar_primer_digito_cel(x):
  if x[0] == "9":
    return True
  else:
    return False
  
def estado_visitas_completas(x,y,estado):
    if estado == "No Encontrado" or estado == "Rechazado":
        return f"Visita Niño:{estado}"
    else:

        if x == y:
            return "Visitas Completas"
        elif x > y:
            res = x-y
            return f"Visitas Incompletas(faltantes:{res})"
        elif y > x:
            return "Visitas Completas (exedido)"

def validar_vd_gestante(x):
    if x > 1:
        return "Visita Completa"
    else:
        return "Visita Incompleta"
    
def calcular_edad(fecha_nacimiento):
    hoy = pd.to_datetime('today')
    diferencia = relativedelta(hoy, fecha_nacimiento)
    return f"{diferencia.years} año(s), {diferencia.months} mes(es)"

def calcular_edad_dias(fecha_nacimiento):
    hoy = pd.to_datetime('today')
    diferencia = relativedelta(hoy, fecha_nacimiento)
    return f"{diferencia.years} año(s), {diferencia.months} mes(es), {diferencia.days} día(s)"

def calcular_edad_anios(fecha_nacimiento):
    hoy = pd.to_datetime('today')
    return relativedelta(hoy, fecha_nacimiento).years

def estado_proyectado(vd_faltantes,proyectado):
        if vd_faltantes<proyectado:
            return "OK"
        else:
            return "EN RIESGO"
        
def safe_percent(numerator, denominator):
    return round((numerator / denominator) * 100, 2) if denominator else 0

def generar_excel_distritos():
    """
    Genera un archivo Excel con la información de los distritos y sus condiciones
    de una manera organizada y visualmente atractiva.
    """
    # Crear un DataFrame con la información
    distrito_condiciones = {
        'ARANJUEZ': ["URB. PALERMO", "PALERMO", "CHICAGO", "ARANJUEZ", "LAS MALVINAS", "MERCADO MAYORISTA", "SECTOR ATAHUALPA", "SECTOR SICHI ROCA"],
        'EL BOSQUE': ["SANTO DOMINGUITO", "URB. STO", "VILLA SANTA MARIA", "CARLOS WIES", "NORIA", "ASCENCIO DE SALAS", "SEMIRUSTICA EL BOSQUE", "PUEBLO JOVEN", "NUEVO SANTA ROSA", "EL BOSQUE", "MERCADO ASCOMAPAAT", "VILLA EL CONTADOR", "DIDEROT", "NUEVA SANTA ROSA", "SALAZAR BONDY", "VILLA DE CONTADORES", "TORRES DE QUEVEDO", "LUCIO SENECA", "JOSE LUIS DE CASTRO", "SINGAPUR", "LAS PAPAS", "SANTA ROSA", "ASCOMAPAT"],
        'LOS JARDINES': ["MAMPUESTO", "MANPUESTO", "LOS JARDINES", "SANTA TERESA DE AVILA", "SAN ISIDRO", "LOS CEDROS", "SAN FERNANDO", "PRIMAVERA", "SANTA INES", "LOS FRESNOS", "MOCHICA", "VIRGEN", "MERCADO LIBERTAD", "LA HERMELINDA", "LOS NARANJOS", "SANTA LUCIA", "NICOLAS DE PIEROLA", "SEMI RUSTICA SAN MIGUEL", "VILLA BOLIVARIANA", "WILFREDO TORRES", "HERMANOS UCEDA MEZA", "VILLA HERMOSA", "ELVIRA GARCIA Y GARCIA", "FAUSTINO SARMIENTO", "MIRAFLORES", "LORD COCKRANE", "JOSE VASCONCELLOS", "ROSAS DE AMERICA", "SAN LUIS", "TAKAYNAMO", "SANTA LEONOR", "ALTO MOCHICA", "VIRGEN DE LA PUERTA", "LAS ORQUIDEAS", "VILLA POLICIAL", "SOLILUZ", "GIRASOLES DE SAN ISIDRO", "ALAMEDA", "SEÑOR DE LOS MILAGROS"],
        'LOS GRANADOS "SAGRADO CORAZON"': ["EL SOL DEL CHACARERO", "LOS GRANADOS", "MARQUEZA", "DANIEL HOYLE", "CHIMU", "EL HUERTO", "LAS MALVINAS", "GRANADOS", "LAS ESMERALDAS", "LOS DIAMANTES", "LOS EUCALIPTOS", "LOS TOPACIO", "LOS TORNILLOS", "LOS ZAFIROS", "MANUEL UBALDE", "ZARUMILLA", "RAZURI", "EL PALOMAR", "RINCONADA"],
        'SAN MARTIN DE PORRES': ["CRISTOBAL DE MOLINA", "FRANCISCO FALCON", "SANTA MARIA", "TORRES ARAUJO", "GALENO", "GALENOS", "COVIDUNT", "JAZMINES", "JASMINES", "MONSERRATE", "LA MERCED", "LAS CASUARINAS", "SAN VICENTE", "EL RECREO", "LA PERLA", "REPUBLICA DE PANAMA", "29 DE DICIEMBRE", "LA ARBOLEDA", "LOS ALAMOS", "SAN LUIS", "VISTA HERMOSA", "LOS LAURELES", "REAL PLAZA", "ARMANDO VILLANUEVA DEL CAMPO", "SANTA OLGA", "LOS PINOS"],
        'PESQUEDA III': ["PESQUEDA III", "LAS CASUARINAS", "SAN FRANCISCO DE ASIS", "NUEVA RINCONDA", "LUIS DE LA PUENTE UCEDA", "PASAJE GRAU", "BOLOGNESI", "5 DE ABRIL", "LOS ESPINOS", "ATAHUALPA", "PASAJE N 5", "JOSE CARLOS MAREATEGUI", "JOSECARLOS MAREATEGUI", "LOS RUBIS", "LOS DIAMANTES"],
        'CLUB DE LEONES': ["COVICORTI", "CORTIJO", "SANCHEZ CARRION", "CAPULLANAS", "NATASHA", "TRUPAL", "VISTA HERMOSA", "HUERTA GRANDEE", "COVIRT", "SAN NICOLAS", "EL ALAMBRE", "SAN ANDRES", "SAN ANDRÉS", "CENTRO CIVICO", "LA ESMERALDA", "JUAN VELASCO ALVARADO", "LOS PINOS", "GERONIMO DE LA TORRE", "SANTA ISABEL", "SAN SALVADOR", "SOLILUZ", "CIRO ALEGRIA", "CENTRO TRUJILLO", "CENTRO HISTORICO", "SANTA ISABEL", "20 DE ABRIL", "PEDRO MUÑIZ", "JUAN PABLO II", "MANUEL VERA ENRIQUEZ", "JORGE CHAVEZ", "MARIANO BEJAR", "SAN JUDAS TADEO", "LUIS ALBRECHT", "GIRASOLES", "FRANCISCO BOLOGNESI", "LAS FLORES", "NATASHA ALTA", "ROSALES DE SAN ANDRES", "TIERRA VERDE", "JESUS DE NAZARETH", "JESUS DE NAZARET", "JESUS DE NAZATETH", "ALBERTH"],
        'CENTRO DE SALUD LA UNION': ["LA INTENDENCIA", "EL MOLINO", "LA UNION", "BARRIO OBRERO", "PROLONGACION SANTA", "EL EJERCITO", "EL EJÉRCITO"],
        'LIBERTAD': ["HUERTA BELLA", "ANIMAS", "INDEPENDENCIA", "LIBERTAD", "LOS PORTALES", "EX FUNDO DE LAS ANIMAS", "LA RICONADA MZ"],
        'PESQUEDA II': ["JUAN PABLO", "SANTA SOFIA", "LAS MALVAS", "PESQUEDA II", "HUASCARAN"]
    }

    data = []
    for distrito, condiciones in distrito_condiciones.items():
        for condicion in condiciones:
            data.append({
                'Distrito': distrito,
                'Condición': condicion
            })
    
    df = pd.DataFrame(data)
    
    # Crear el archivo Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Distritos')
        workbook = writer.book
        worksheet = writer.sheets['Distritos']
        
        # Definir formatos
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        distrito_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        # Aplicar formatos
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Ajustar anchos de columna
        worksheet.set_column('A:A', 30)  # Columna Distrito
        worksheet.set_column('B:B', 50)  # Columna Condición
        
        # Agregar tabla con filtros incluidos
        worksheet.add_table(0, 0, len(df), len(df.columns)-1, {
            'columns': [{'header': col} for col in df.columns],
            'style': 'Table Style Medium 2',
            'autofilter': True
        })
    
    return output.getvalue()

def es_consecutivo(numero):
    # Convertir el número a string para poder iterar sobre sus dígitos
    str_numero = str(numero)
    
    # Si tiene menos de 2 dígitos, no es consecutivo
    if len(str_numero) < 2:
        return "No Consecutivo"
    
    # Convertir cada dígito a entero
    digitos = [int(d) for d in str_numero]
    
    # Verificar si hay al menos dos dígitos consecutivos
    for i in range(len(digitos)-1):
        if digitos[i+1] - digitos[i] == 1:
            return "Consecutivo"
    
    return "No Consecutivo"