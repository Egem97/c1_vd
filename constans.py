EESS_MICRORED = ['ARANJUEZ','CLUB DE LEONES','DE ESPECIALIDADES BASICAS LA NORIA','EL BOSQUE','LA UNION','LIBERTAD',
     'LOS GRANADOS "SAGRADO CORAZON"','LOS JARDINES','PESQUEDA II','PESQUEDA III','SAN MARTIN DE PORRES'
]
PRIORIDAD_TIPO_DOCUMENTO = {'DNI': 1, 'CUI': 2, 'CNV': 3}

COLUMNS_PADRON_C1_VD =[
            'Tipo_file', 'Documento', 'Tipo de Documento','DATOS NIÑO PADRON','CELULAR2_PADRON','SEXO',
            'FECHA DE NACIMIENTO', 'EJE VIAL', 'DIRECCION PADRON','REFERENCIA DE DIRECCION','MENOR VISITADO','¿MENOR ENCONTRADO?',
            'EESS NACIMIENTO','EESS', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN','TIPO DE DOCUMENTO DE LA MADRE',
            'NUMERO DE DOCUMENTO  DE LA MADRE','DATOS MADRE PADRON','TIPO DE DOCUMENTO DEL JEFE DE FAMILIA',
            'NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA','DATOS JEFE PADRON','ENTIDAD','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA','NUMERO DE CELULAR', 'CELULAR_CORREO',
            'TIPO DE SEGURO'
]

REEMPLAZO_TIPO_SEGURO = {
        "0": "NINGUNO",
        "1": "SIS",
        "2": "ESSALUD",
        "3": "SANIDAD",
        "4": "PRIVADO"
        }
COL_ORDER_VD_CHILD_C1 = [
     'Establecimiento de Salud','Nombres del Actor Social','Tipo de Documento del niño','Tipo de Documento','Número de Documento del niño',
     'DATOS NIÑO PADRON','Fecha de Nacimiento','Rango de Edad','Total de visitas completas para la edad','Total de Intervenciones','Total de VD presenciales Válidas','Total de VD presencial Válidas WEB','Total de VD presencial Válidas MOVIL',
     'MENOR VISITADO','¿MENOR ENCONTRADO?', 'DIRECCION PADRON','REFERENCIA DE DIRECCION','Dirección', 'TIPO DE DOCUMENTO DE LA MADRE','NUMERO DE DOCUMENTO  DE LA MADRE',
     'DNI de la madre','DATOS MADRE PADRON','NUMERO DE DOCUMENTO DEL JEFE DE FAMILIA','DATOS JEFE PADRON','Celular de la madre','NUMERO DE CELULAR','CELULAR2_PADRON',
     'EESS NACIMIENTO', 'EESS','FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN',
     'EESS_C1', 'Fecha_ult_at_c1','Zona', 'Manzana', 'Sector','TIPO DE SEGURO','Tipo_file','ENTIDAD','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA','Estado_Visita_Ult','Estado Padrón Nominal', 'Mes', 'Año'
]

COL_ORDER_VD_CHILD_C1_2 = ['Establecimiento de Salud','Actor Social', 'Tipo Documento','Tipo Documento(P)', 'Número de Documento',
'Datos del niño', 'Fecha de Nacimiento', 'Rango de Edad','N° Visitas Completas', 'Total de Intervenciones','Total de VD presenciales Válidas','Total de VD presencial Válidas WEB','Total de VD presencial Válidas MOVIL',
                'MENOR VISITADO','¿MENOR ENCONTRADO?',
                'Dirección(P)', 'Referencia Dirección(P)', 'Dirección Compromiso 1',
                'Tipo Documento Madre(P)', 'Número Doc Madre(P)',
                'Número Doc Madre', 'Datos Madre(P)',
                'Número Doc Jefe Familia(P)', 'Datos Jefe Famlia(P)',
                'Celular Madre', 'Celular(P)', 'Celular2(P)',
                'EESS NACIMIENTO', 'EESS ULTIMA ATENCION(P)', 'FRECUENCIA DE ATENCION', 'EESS ADSCRIPCIÓN',
                'EESS ULTIMA ATENCION', 'Fecha Ultima Atención', 'Zona', 'Manzana', 'Sector','Tipo de Seguro', 'Tipo Registro Padrón Nominal',
                'Entidad Actualiza','FECHA DE MODIFICACIÓN DEL REGISTRO','USUARIO QUE MODIFICA', 'Estado Niño','Estado Padrón Nominal', 'Mes', 'Año'
]

COLS_DATAFRAME_DUPLICADOS_CHILDS =['Establecimiento de Salud', 'Actor Social',
       'Tipo Documento(P)', 'Número de Documento', 'Datos del niño',
       'Fecha de Nacimiento', 'Rango de Edad', 'N° Visitas Completas',
       'Total de Intervenciones',
       'Dirección Compromiso 1', 
       'Número Doc Madre(P)','Datos Madre(P)',
       'Celular Madre','Celular(P)', 'Estado Niño', 'Mes',
       'Año', 'Estado Visitas', 'Edad']


COLS_DATAFRAME_RESUMIDO_CHILS =['Establecimiento de Salud', 'Actor Social',
       'Tipo Documento(P)', 'Número de Documento', 'Datos del niño',
       'Fecha de Nacimiento', 'Rango de Edad', 'N° Visitas Completas',
       'Total de Intervenciones', 'Total de VD presenciales Válidas',
       'Total de VD presencial Válidas WEB',
       'Total de VD presencial Válidas MOVIL','Dirección(P)', 'Referencia Dirección(P)',
       'Dirección Compromiso 1', 'Tipo Documento Madre(P)',
        'Número Doc Madre', 'Datos Madre(P)','Celular Madre',
       'Celular(P)', 'Celular2(P)','EESS ULTIMA ATENCION(P)','Tipo de Seguro', 'Tipo Registro Padrón Nominal',
       'Estado Niño','Estado Visitas', 'Edad','Niños 120-149 días en mes', 'Niños 180-209 días en mes','Niños 270-299 días en mes','Niños 360-389 días en mes'
]

COLS_DATAFRAME_PADRON_CHILS =['Establecimiento de Salud', 'Actor Social', 
       'Tipo Documento(P)', 'Número de Documento', 'Datos del niño',
       'Fecha de Nacimiento', 'Rango de Edad', 'MENOR VISITADO',
       '¿MENOR ENCONTRADO?', 'Dirección(P)', 'Referencia Dirección(P)',
      'Tipo Documento Madre(P)', 'Número Doc Madre', 'Datos Madre(P)',
       'Celular Madre','Celular(P)', 'Celular2(P)', 
       'EESS ULTIMA ATENCION(P)', 'FRECUENCIA DE ATENCION', 'Tipo de Seguro', 
       'Tipo Registro Padrón Nominal','Entidad Actualiza', 'FECHA DE MODIFICACIÓN DEL REGISTRO',
       'USUARIO QUE MODIFICA', 'Estado Niño', 'Estado Padrón Nominal', 'Edad'
]




PORCENTAJE_GEOS_VD = 0.64