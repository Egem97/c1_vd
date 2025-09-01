import cloudscraper
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
from datetime import datetime

# Ajuste regresión lineal con tus datos reales
def estimar_id_actual(hora_base="14:52", base_id=28821362.38, velocidad=15.16):
    ahora = datetime.now()
    base = ahora.replace(hour=int(hora_base.split(":")[0]), minute=int(hora_base.split(":")[1]), second=0, microsecond=0)
    if ahora < base:
        base = base.replace(day=base.day - 1)

    minutos_transcurridos = (ahora - base).total_seconds() / 60
    return round(base_id + velocidad * minutos_transcurridos)

login_url = "http://seaap.minsa.gob.pe/web/login"
archivo_url = f"http://seaap.minsa.gob.pe/web/content/{str(estimar_id_actual())}/Detalle_nino.xls?download=true"

usuario = "43601728"
password = "mamita1"

scraper = cloudscraper.create_scraper()  # Bypasses Cloudflare

# Paso 1: Obtener CSRF token
response_get = scraper.get(login_url)
soup = BeautifulSoup(response_get.text, "html.parser")

csrf_input = soup.find("input", {"name": "csrf_token"})
if csrf_input is None:
    raise Exception("❌ No se encontró el token CSRF (incluso con cloudscraper).")

csrf_token = csrf_input.get("value")

# Paso 2: Enviar POST con login
payload = {
    "csrf_token": csrf_token,
    "login": usuario,
    "password": password,
    "redirect": ""
}

response_post = scraper.post(login_url, data=payload)

# Verificar login
if response_post.status_code == 200 and "session_id" in scraper.cookies.get_dict():
    print("✅ Login exitoso con cloudscraper.")

    # Paso 3: Descargar archivo
    response_archivo = scraper.get(archivo_url)
    if response_archivo.status_code == 200 and "application/vnd.ms-excel" in response_archivo.headers.get("Content-Type", ""):
        with open("Detalle_nino.xls", "wb") as f:
            f.write(response_archivo.content)
        print("📥 Archivo descargado correctamente.")
    else:
        print("❌ No se pudo descargar el archivo.")
else:
    print("❌ Login fallido.")