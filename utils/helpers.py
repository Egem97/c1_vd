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
    condlist=[

    ####-----------------ARANJUEZ
    (dataframe[col_name].str.contains("URB. PALERMO")) |
    (dataframe[col_name].str.contains("URB. PALERMO 1 ETAPA")) |
    (dataframe[col_name].str.contains("PALERMO")) |
    (dataframe[col_name].str.contains("CHICAGO")) |
    (dataframe[col_name].str.contains("ARANJUEZ")) |
    (dataframe[col_name].str.contains("LAS MALVINAS")) |
    (dataframe[col_name].str.contains("MERCADO MAYORISTA")) |
    (dataframe[col_name].str.contains("SECTOR ATAHUALPA")) |
    (dataframe[col_name].str.contains("SECTOR SICHI ROCA")),
    
    ####-----------------EL BOSQUE
    (dataframe[col_name].str.contains("URB. SANTO DOMINGUITO")) |
    (dataframe[col_name].str.contains("SANTO DOMINGUITO")) |
    (dataframe[col_name].str.contains("URB. STO")) |
    (dataframe[col_name].str.contains("URB. VILLA SANTA MARIA")) |
    (dataframe[col_name].str.contains("CARLOS WIES")) |
    (dataframe[col_name].str.contains("NORIA")) |
    (dataframe[col_name].str.contains("ASCENCIO DE SALAS")) |
    (dataframe[col_name].str.contains("SEMIRUSTICA EL BOSQUE")) |
    (dataframe[col_name].str.contains("SEMI RUSTICA EL BOSQUE")) |
    (dataframe[col_name].str.contains("PUEBLO JOVEN")) |
    (dataframe[col_name].str.contains("NUEVO SANTA ROSA")) |
    (dataframe[col_name].str.contains("URB. EL BOSQUE")) |
    (dataframe[col_name].str.contains("URB.STO")) |
    (dataframe[col_name].str.contains("MERCADO ASCOMAPAAT")) |
    (dataframe[col_name].str.contains("URB EL BOSQUE")) |
    (dataframe[col_name].str.contains("VILLA EL CONTADOR")) |
    (dataframe[col_name].str.contains("URB.EL BOSQUE")) |
    (dataframe[col_name].str.contains("DIDEROT")) |
    (dataframe[col_name].str.contains("NUEVA SANTA ROSA")) |
    (dataframe[col_name].str.contains("SALAZAR BONDY")) |
    (dataframe[col_name].str.contains("VILLA DE CONTADORES")) |
    (dataframe[col_name].str.contains("TORRES DE QUEVEDO")) |
    (dataframe[col_name].str.contains("CALLE LUCIO SENECA")) |
    (dataframe[col_name].str.contains("JOSE LUIS DE CASTRO")) |
    (dataframe[col_name].str.contains("VILLA SANTA MARIA")) |
    (dataframe[col_name].str.contains("URB. SINGAPUR")) |
    (dataframe[col_name].str.contains("LAS PAPAS")) |
    (dataframe[col_name].str.contains("URB SANTA ROSA")) |
    (dataframe[col_name].str.contains("URB RESIDENCIA TORRES DE QUEVEDO")) |
    (dataframe[col_name].str.contains("URB. ASCOMAPAT")),
    
    ####-----------------LOS JARDINES
    (dataframe[col_name].str.contains("MAMPUESTO")) |
    (dataframe[col_name].str.contains("MANPUESTO")) |
    (dataframe[col_name].str.contains("URB. LOS JARDINES")) |
    (dataframe[col_name].str.contains("URB. SANTA TERESA DE AVILA")) |
    (dataframe[col_name].str.contains("URB SANTA TERESA DE AVILA")) |
    (dataframe[col_name].str.contains("URB. STA. TERESA")) |
    (dataframe[col_name].str.contains("SAN ISIDRO")) |
    (dataframe[col_name].str.contains("URB. LOS CEDROS")) |
    (dataframe[col_name].str.contains("URB LOS CEDROS")) |
    (dataframe[col_name].str.contains("SAN FERNANDO")) |
    (dataframe[col_name].str.contains("URB. SAN FERNANDO")) |
    (dataframe[col_name].str.contains("PRIMAVERA")) |
    (dataframe[col_name].str.contains("SANTA INES")) |
    (dataframe[col_name].str.contains("URB. LOS FRESNOS")) |
    (dataframe[col_name].str.contains("MOCHICA")) |
    (dataframe[col_name].str.contains("AA.HH VIRGEN")) |
    (dataframe[col_name].str.contains("AA.HH. VIRGEN")) |
    (dataframe[col_name].str.contains("MERCADO LIBERTAD")) |
    (dataframe[col_name].str.contains("MERCADO LA LIBERTAD")) |
    (dataframe[col_name].str.contains("LA HERMELINDA")) |
    (dataframe[col_name].str.contains("URB. LOS NARANJOS")) |
    (dataframe[col_name].str.contains("URB. LOS NARANJOS")) |
    (dataframe[col_name].str.contains("URB. SANTA LUCIA")) |
    (dataframe[col_name].str.contains("LOS NARANJOS")) |
    (dataframe[col_name].str.contains("URB.LOS CEDROS")) |
    (dataframe[col_name].str.contains("SAN ISISDRO")) |
    (dataframe[col_name].str.contains("AV. NICOLAS DE PIEROLA")) |
    (dataframe[col_name].str.contains("SEMI RUSTICA SAN MIGUEL")) |
    (dataframe[col_name].str.contains("SEMIRUSTICA SAN MIGUEL")) |
    (dataframe[col_name].str.contains("URB. LOS CEDROS")) |
    (dataframe[col_name].str.contains("URB LOS CEDROS")) |
    (dataframe[col_name].str.contains("SAN FERNANDO")) |
    (dataframe[col_name].str.contains("URB. SAN FERNANDO")) |
    (dataframe[col_name].str.contains("PRIMAVERA")) |
    (dataframe[col_name].str.contains("SANTA INES")) |
    (dataframe[col_name].str.contains("URB. LOS FRESNOS")) |
    (dataframe[col_name].str.contains("MOCHICA")) |
    (dataframe[col_name].str.contains("AA.HH VIRGEN")) |
    (dataframe[col_name].str.contains("AA.HH. VIRGEN")) |
    (dataframe[col_name].str.contains("MERCADO LIBERTAD")) |
    (dataframe[col_name].str.contains("MERCADO LA LIBERTAD")) |
    (dataframe[col_name].str.contains("LA HERMELINDA")) |
    (dataframe[col_name].str.contains("URB. LOS NARANJOS")) |
    (dataframe[col_name].str.contains("URB.LOS NARANJOS")) |
    (dataframe[col_name].str.contains("URB. SANTA LUCIA")) |
    (dataframe[col_name].str.contains("LOS NARANJOS")) |
    (dataframe[col_name].str.contains("URB.LOS CEDROS")) |
    (dataframe[col_name].str.contains("SAN ISISDRO")) |
    (dataframe[col_name].str.contains("AV. NICOLAS DE PIEROLA")) |
    (dataframe[col_name].str.contains("SEMI RUSTICA SAN MIGUEL")) |
    (dataframe[col_name].str.contains("SEMIRUSTICA SAN MIGUEL")) |
    (dataframe[col_name].str.contains("VILLA BOLIVARIANA")) |
    (dataframe[col_name].str.contains("WILFREDO TORRES")) |
    (dataframe[col_name].str.contains("AV. HERMANOS UCEDA MEZA")) |
    (dataframe[col_name].str.contains("URB.VILLA HERMOSA")) |
    (dataframe[col_name].str.contains("URB. VILLA HERMOSA")) |
    (dataframe[col_name].str.contains("ELVIRA GARCIA Y GARCIA")) |
    (dataframe[col_name].str.contains("FAUSTINO SARMIENTO")) |
    (dataframe[col_name].str.contains("URB. MIRAFLORES")) |
    (dataframe[col_name].str.contains("CALLE LORD COCKRANE")) |
    (dataframe[col_name].str.contains("FAUSTINO SARMIENTO")) |
    (dataframe[col_name].str.contains("JOSE VASCONCELLOS")) |
    (dataframe[col_name].str.contains("ROSAS DE AMERICA")) |
    (dataframe[col_name].str.contains("ROSAS DE AMÉRICA")) |
    (dataframe[col_name].str.contains("ROSA DE AMERICA")) |
    (dataframe[col_name].str.contains("RESIDENCIAL LOS JARDINES")) |
    (dataframe[col_name].str.contains("URB.SANTA TERESA DE AVILA")) |
    (dataframe[col_name].str.contains("URB. SAN LUIS")) |
    (dataframe[col_name].str.contains("TAKAYNAMO")) |
    (dataframe[col_name].str.contains("URB. SANTA LEONOR")) |
    (dataframe[col_name].str.contains("URB. SANTA LEONOR 2 ETAPA")) |
    (dataframe[col_name].str.contains("URB. ALTO MOCHICA")) |
    (dataframe[col_name].str.contains("URB. VIRGEN DE LA PUERTA"))|
    (dataframe[col_name].str.contains("URB. SAN MUGUEL")) |
    (dataframe[col_name].str.contains("URB. LAS ORQUIDEAS")) |
    (dataframe[col_name].str.contains("URB ROSAS DE AMERICA")) |
    (dataframe[col_name].str.contains("URB. VILLA POLICIAL")) |
    (dataframe[col_name].str.contains("URB. SOLILUZ")) |
    (dataframe[col_name].str.contains("URB. SAN ISIDRO")) |
    (dataframe[col_name].str.contains("URB. GIRASOLES DE SAN ISIDRO")) |
    (dataframe[col_name].str.contains("RESIDENCIAL LOS JARDINES")) |
    (dataframe[col_name].str.contains("URB. ALAMEDA")) |
    (dataframe[col_name].str.contains("E - 12 URB SEÑOR DE LOS MILAGROS")) |
    (dataframe[col_name].str.contains("C-27 LOS CEDROS")) |
    (dataframe[col_name].str.contains("URB. ALAMEDA")) ,
    
    
    ####-----------------LOS GRANADOS "SAGRADO CORAZON"
    (dataframe[col_name].str.contains("URB. EL SOL DEL CHACARERO")) |
    (dataframe[col_name].str.contains("LOS GRANADOS")) |
    (dataframe[col_name].str.contains("MARQUEZA")) |
    (dataframe[col_name].str.contains("DANIEL HOYLE")) |
    (dataframe[col_name].str.contains("CHIMU")) |
    (dataframe[col_name].str.contains("URB. EL HUERTO")) |
    (dataframe[col_name].str.contains("LAS MALVINAS")) |
    (dataframe[col_name].str.contains("GRANADOS")) |
    (dataframe[col_name].str.contains("CALLE LAS ESMERALDAS")) |
    (dataframe[col_name].str.contains("CALLE LOS DIAMANTES")) |
    (dataframe[col_name].str.contains("CALLE LOS EUCALIPTOS")) |
    (dataframe[col_name].str.contains("CALLE LOS TOPACIO")) |
    (dataframe[col_name].str.contains("CALLE LOS TORNILLOS")) |
    (dataframe[col_name].str.contains("CALLE LOS ZAFIROS")) |
    (dataframe[col_name].str.contains("MANUEL UBALDE")) |
    (dataframe[col_name].str.contains("CALLE ZARUMILLA")) |
    (dataframe[col_name].str.contains("RAZURI")) |
    (dataframe[col_name].str.contains("RAZURI 1 ETAPA")) |
    (dataframe[col_name].str.contains("RAZURI 2 ETAPA")) |
    (dataframe[col_name].str.contains("URB. RAZURI")) |
    (dataframe[col_name].str.contains("URB. EL PALOMAR")) |
    (dataframe[col_name].str.contains("URB. EL SOL DE CHACARERO")) |
    (dataframe[col_name].str.contains("URB. RINCONADA")) |
    (dataframe[col_name].str.contains("RINCONADA")),
        
    ####-----------------SAN MARTIN DE PORRES
    (dataframe[col_name].str.contains("CALLE CRISTOBAL DE MOLINA")) |
    (dataframe[col_name].str.contains("CALLE FRANCISCO FALCON")) |
    (dataframe[col_name].str.contains("URB. SANTA MARIA")) |
    (dataframe[col_name].str.contains("TORRES ARAUJO")) |
    (dataframe[col_name].str.contains("GALENO")) |
    (dataframe[col_name].str.contains("GALENOS")) |
    (dataframe[col_name].str.contains("COVIDUNT")) |
    (dataframe[col_name].str.contains("JAZMINES")) |
    (dataframe[col_name].str.contains("JASMINES")) |
    (dataframe[col_name].str.contains("MONSERRATE")) |
    (dataframe[col_name].str.contains("LA MERCED")) |
    (dataframe[col_name].str.contains("URB. LAS CASUARINAS")) |
    (dataframe[col_name].str.contains("URB. SAN VICENTE")) |
    (dataframe[col_name].str.contains("EL RECREO")) |
    (dataframe[col_name].str.contains("URB. LA PERLA")) |
    (dataframe[col_name].str.contains("CALLE REPUBLICA DE PANAMA")) |
    (dataframe[col_name].str.contains("AV. 29 DE DICIEMBRE")) |
    (dataframe[col_name].str.contains("URB. LA ARBOLEDA")) |
    (dataframe[col_name].str.contains("LOS ALAMOS DE SANTA MARIA")) |
    (dataframe[col_name].str.contains("ASENT.H. SAN LUIS")) |
    (dataframe[col_name].str.contains("URB. VISTA HERMOSA")) |
    (dataframe[col_name].str.contains("URB. LOS LAURELES")) |
    (dataframe[col_name].str.contains("URB. REAL PLAZA")) |
    (dataframe[col_name].str.contains("AA.HH. ARMANDO VILLANUEVA DEL CAMPO")) |
    (dataframe[col_name].str.contains("URB. SANTA OLGA")) |
    (dataframe[col_name].str.contains("URB. LOS PINOS")) |
    (dataframe[col_name].str.contains("URB. LA ARBOLEDA")) |
    (dataframe[col_name].str.contains("URB. LAS CAUARINAS")),
    
    ####-----------------PESQUEDA III
    (dataframe[col_name].str.contains("PESQUEDA III")) |
    (dataframe[col_name].str.contains("CALLE LAS CASUARINAS")) |
    (dataframe[col_name].str.contains("AA.HH SAN FRANCISCO DE ASIS")) |
    (dataframe[col_name].str.contains("AA.HH. SAN FRANCISCO DE ASIS")) |
    (dataframe[col_name].str.contains("NUEVA RINCONDA")) |
    (dataframe[col_name].str.contains("LUIS DE LA PUENTE UCEDA")) |
    (dataframe[col_name].str.contains("PASAJE GRAU")) |
    (dataframe[col_name].str.contains("BOLOGNESI")) |
    (dataframe[col_name].str.contains("AVENIDA 5 DE ABRIL")) |
    (dataframe[col_name].str.contains("LOS ESPINOS")) |
    (dataframe[col_name].str.contains("ATAHUALPA")) |
    (dataframe[col_name].str.contains("PASAJE N 5")) |
    (dataframe[col_name].str.contains("JOSE CARLOS MAREATEGUI")) |
    (dataframe[col_name].str.contains("JOSECARLOS MAREATEGUI")) |
    (dataframe[col_name].str.contains("LOS RUBIS")) |
    (dataframe[col_name].str.contains("LOS DIAMANTES")),
    
    
    
    
    
    ####---------------------CLUB DE LEONES
    (dataframe[col_name].str.contains("COVICORTI")) |
    (dataframe[col_name].str.contains("CORTIJO")) |
    (dataframe[col_name].str.contains("URB. SANCHEZ CARRION")) |
    (dataframe[col_name].str.contains("CAPULLANAS")) |
    (dataframe[col_name].str.contains("NATASHA")) |
    (dataframe[col_name].str.contains("TRUPAL")) |
    (dataframe[col_name].str.contains("VISTA HERMOSA")) |
    (dataframe[col_name].str.contains("HUERTA GRANDEE")) |
    (dataframe[col_name].str.contains("COVIRT")) |
    (dataframe[col_name].str.contains("SAN NICOLAS")) |
    (dataframe[col_name].str.contains("EL ALAMBRE")) |
    (dataframe[col_name].str.contains("SAN ANDRES")) |
    (dataframe[col_name].str.contains("SAN ANDRÉS")) |
    (dataframe[col_name].str.contains("CENTRO CIVICO")) |
    (dataframe[col_name].str.contains("URB. LA ESMERALDA")) |
    (dataframe[col_name].str.contains("JUAN VELASCO ALVARADO")) |
    (dataframe[col_name].str.contains("URB. LOS PINOS")) |
    (dataframe[col_name].str.contains("LA ESMERALDA")) |
    (dataframe[col_name].str.contains("GERONIMO DE LA TORRE")) |
    (dataframe[col_name].str.contains("URB. SANTA ISABEL")) |
    (dataframe[col_name].str.contains("URB. SAN SALVADOR")) |
    (dataframe[col_name].str.contains("URB. SOLILUZ")) |
    (dataframe[col_name].str.contains("URB. CIRO ALEGRIA")) |
    (dataframe[col_name].str.contains("URB CIRO ALEGRIA")) |
    (dataframe[col_name].str.contains("CENTRO TRUJILLO")) |
    (dataframe[col_name].str.contains("CENTRO HISTORICO")) |
    (dataframe[col_name].str.contains("PP.JJ SANTA ISABEL")) |
    (dataframe[col_name].str.contains("20 DE ABRIL")) |
    (dataframe[col_name].str.contains("AV. PEDRO MUÑIZ")) |
    (dataframe[col_name].str.contains("URB. JUAN PABLO II")) |
    (dataframe[col_name].str.contains("AV. MANUEL VERA ENRIQUEZ")) |
    (dataframe[col_name].str.contains("JORGE CHAVEZ")) |
    (dataframe[col_name].str.contains("MARIANO BEJAR")) |
    (dataframe[col_name].str.contains("COOP VIV. SAN JUDAS TADEO")) |
    (dataframe[col_name].str.contains("LUIS ALBRECHT")) |
    (dataframe[col_name].str.contains("JARDIN DE LOS GIRASOLES")) |
    (dataframe[col_name].str.contains("JR. FRANCISCO BOLOGNESI")) |
    (dataframe[col_name].str.contains("URB. LAS FLORES")) |
    (dataframe[col_name].str.contains("NATASHA ALTA")) |
    (dataframe[col_name].str.contains("URB. LOS ROSALES DE SAN ANDRES")) |
    (dataframe[col_name].str.contains("SECTOR CONDOMINIO TIERRA VERDE")) |
    (dataframe[col_name].str.contains("SECTOR AV. JESUS DE NAZARETH")) |
    (dataframe[col_name].str.contains("AV. JESUS DE NAZARET")) |
    (dataframe[col_name].str.contains("AV. JESUS DE NAZATETH")) |
    (dataframe[col_name].str.contains("PEDRO MUÑIZ")) |
    (dataframe[col_name].str.contains("URB. SANCHEZ CARRION")) |
    (dataframe[col_name].str.contains("EL ALAMBRE")) |
    (dataframe[col_name].str.contains("URB. SANTA ISABEL")) |
    (dataframe[col_name].str.contains("SECTOR ALBERTH")) |
    (dataframe[col_name].str.contains("URB. SAN ANDRES")),
    
       
    
    ####---------------------CENTRO DE SALUD LA UNION
    (dataframe[col_name].str.contains("LA INTENDENCIA")) |
    (dataframe[col_name].str.contains("EL MOLINO")) |
    (dataframe[col_name].str.contains("SECTOR LA UNION")) |
    (dataframe[col_name].str.contains("BARRIO OBRERO")) |
    (dataframe[col_name].str.contains("SECTOR PROLONGACION SANTA")) |
    (dataframe[col_name].str.contains("SECTOR AV. EL EJERCITO")) |
    (dataframe[col_name].str.contains("AV. EL EJERCITO")) |
    (dataframe[col_name].str.contains("AV. EL EJÉRCITO")),    
  
    ####---------------------LIBERTAD
    (dataframe[col_name].str.contains("HUERTA BELLA")) |
    (dataframe[col_name].str.contains("ANIMAS")) |
    (dataframe[col_name].str.contains("URB. INDEPENDENCIA")) |
    (dataframe[col_name].str.contains("URB. LIBERTAD")) |
    (dataframe[col_name].str.contains("URB. LOS PORTALES")) |
    (dataframe[col_name].str.contains("URB. HUERTA BELLA")) |
    (dataframe[col_name].str.contains("URB. EX FUNDO DE LAS ANIMAS"))|
    (dataframe[col_name].str.contains("URB LOS PORTALES")) |
    (dataframe[col_name].str.contains("URBANIZACION LOS PORTALES")) |
    (dataframe[col_name].str.contains("URB. LA LIBERTAD")) |
    (dataframe[col_name].str.contains("URB. LA RICONADA MZ.")),
    
    
    #------PESQUEDA II
    (dataframe[col_name].str.contains("ASENT.H. JUAN PABLO")) |
    (dataframe[col_name].str.contains("SANTA SOFIA")) |
    (dataframe[col_name].str.contains("CALLE LAS MALVAS")) |
    (dataframe[col_name].str.contains("ASENT.H. JUAN PABLO")) |
    (dataframe[col_name].str.contains("SANTA SOFIA")) |
    (dataframe[col_name].str.contains("AV PESQUEDA II")) |
    (dataframe[col_name].str.contains("AV. PESQUEDA II")) |
    (dataframe[col_name].str.contains("AV. HUASCARAN")) |
    (dataframe[col_name].str.contains("PESQUEDA II SECTOR ")) |
    (dataframe[col_name].str.contains("JUAN PABLO MZ")),   
    
    ]
    choicelist_1 =['ARANJUEZ','EL BOSQUE','LOS JARDINES','LOS GRANADOS "SAGRADO CORAZON"','SAN MARTIN DE PORRES','PESQUEDA III','CLUB DE LEONES','CENTRO DE SALUD LA UNION','LIBERTAD','PESQUEDA II']
    return np.select(condlist,choicelist_1,default='No Especificado')
    
def mes_short(x):
    dict_mes = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Oct',11:'Nov',12:'Dic'}
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

def calcular_edad_anios(fecha_nacimiento):
    hoy = pd.to_datetime('today')
    return relativedelta(hoy, fecha_nacimiento).years