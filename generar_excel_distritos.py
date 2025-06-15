"""
from utils.helpers import generar_excel_distritos
from datetime import datetime
import os

    # Generar el Excel
excel_data = generar_excel_distritos()
    
    # Crear un nombre de archivo con la fecha actual
fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
nombre_archivo = f"distritos_{fecha_actual}.xlsx"
    
    # Guardar el archivo
with open(nombre_archivo, 'wb') as f:
    f.write(excel_data)
    
print(f"Archivo Excel generado exitosamente: {nombre_archivo}")
print(f"Ruta completa: {os.path.abspath(nombre_archivo)}")


"""