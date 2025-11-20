#!/usr/bin/env python3
"""
Cencosud Web Scraping Script
Automatiza la descarga de archivos de inventario y ventas desde la plataforma Cencosud
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import zipfile
import glob
import os
from datetime import datetime
from google.cloud import storage
import json

# Configuracion principal
DIRECTORIO = r"C:\Users\dani\OneDrive\Web Scaping\Cencosud"  # Cambiar ruta segun necesidad
DIRECTORIO_EXTRAIDOS = os.path.join(DIRECTORIO, "extraidos")

# Configuracion bucket
BUCKET_NAME = "bucket-quickstart_croc_830"
CREDENTIALS_FILE = "croc-454221-e1a3c2e02181.json"
RUTA_VENTAS = "raw/Ventas/moderno/cencosud/ventas"
RUTA_INVENTARIO = "raw/Ventas/moderno/cencosud/inventario"

# Credenciales login
EMAIL = "WRITE EMAIL"
PASSWORD = "WRITE PASSWORD"

def setup_driver():
    """Funcion simplificada que funciona - Selenium estandar"""
    try:
        print("Configurando driver...")
        
        # Configurar opciones de Chrome
        options = Options()
        
        # Configuracion de descarga
        prefs = {
            "download.default_directory": DIRECTORIO,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        # Opciones basicas para estabilidad
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Crear servicio con WebDriverManager (maneja versiones automaticamente)
        service = Service(ChromeDriverManager().install())
        
        # Crear driver
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        
        print("Driver creado exitosamente")
        return driver
        
    except Exception as e:
        print(f"Error al crear driver: {e}")
        return None

def login_process(driver):
    """Proceso de login en la plataforma Cencosud"""
    try:
        print("Iniciando proceso de login...")
        
        # Navegar a la pagina de login
        driver.get("https://ssocencosud.bbr.cl/auth/realms/cencosud/protocol/openid-connect/auth?response_type=code&client_id=superco-client-prod&redirect_uri=https%3A%2F%2Fwww.cenconlineb2b.com%2FSuperCO%2FBBRe-commerce%2Fmain&state=c513e4c3-afe7-404a-a858-67d7c542d261&login=true&scope=openid")
        
        # Insertar datos de login
        email_input = driver.find_element(By.ID, "username")
        email_input.send_keys(EMAIL)
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(PASSWORD)
        
        # Pasar captcha
        print("Esperando interaccion con captcha...")
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")))
        captcha_checkbox = driver.find_element(By.ID, "recaptcha-anchor")
        captcha_checkbox.click()
        time.sleep(2)
        driver.switch_to.default_content()
        
        # Primer login
        login1 = driver.find_element(By.ID, "kc-login")
        login1.click()
        time.sleep(1)
        
        home = driver.find_element(By.CLASS_NAME, "btn-home")
        home.click()
        
        # Seleccionar pais Colombia
        pais = driver.find_element(By.ID, "pais")
        select = Select(pais)
        select.select_by_value("col")
        print("Colombia seleccionado")
        
        # Segundo login
        login2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnIngresar"))
        )
        login2.click()
        
        time.sleep(10)
        print("Login completado exitosamente")
        return True
        
    except Exception as e:
        print(f"Error en proceso de login: {e}")
        return False

def descargar_inventario(driver):
    """Descarga el archivo de inventario"""
    try:
        print("=== DESCARGANDO INVENTARIO ===")
        
        # Hacer clic en Abastecimiento
        abastecimiento_parent = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//span[@class='v-menubar-menuitem' and .//span[text()='Abastecimiento']]"
            ))
        )
        print("Elemento padre de 'Abastecimiento' encontrado")
        abastecimiento_parent.click()
        print("Clic en 'Abastecimiento' realizado")
        time.sleep(3)
        
        # Buscar "Detalle de inventario"
        detalle_inventario = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'detalle') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'inventario')]"))
        )
        print("Encontrado con busqueda flexible")
        detalle_inventario.click()
        print("Clic realizado")
        
        time.sleep(5)
        
        # Generar informe
        boton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Generar Informe']"))
        )
        try:
            boton.click()
            print("Clic realizado en Generar Informe")
        except:
            driver.execute_script("arguments[0].click();", boton)
            print("Clic con JavaScript realizado")
        time.sleep(8)
        
        # Click en el boton descarga
        generar_boton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".bbr-popupbutton"))
        )
        generar_boton.click()
        time.sleep(5)
        
        # Descargar Dato Fuente
        boton_descargar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//div[@role='button' and .//span[text()='Descargar Dato Fuente']]"
            ))
        )
        print("Elemento padre encontrado")
        boton_descargar.click()
        print("Clic realizado en elemento padre")
        time.sleep(8)
        
        # Seleccionar archivo
        seleccionar = driver.find_element(By.XPATH, "//div[@role='button' and .//span[text()='Seleccionar']]")
        seleccionar.click()
        time.sleep(8)
        
        # Descargar archivo
        descargar = driver.find_element(By.XPATH, "//a[contains(@href, 'Inventario')]")
        descargar.click()
        time.sleep(5)
        
        print("Descarga de inventario completada")
        return True
        
    except Exception as e:
        print(f"Error descargando inventario: {e}")
        return False

def descargar_ventas(driver):
    """Descarga el archivo de ventas"""
    try:
        print("=== DESCARGANDO VENTAS ===")
        
        # Click en Comercial
        comercial = driver.find_element(By.XPATH, "//span[@class='v-menubar-menuitem' and .//span[text()='Comercial']]")
        comercial.click()
        time.sleep(2)
        
        # Click en Ventas por Periodo
        ventas_periodo = driver.find_element(By.XPATH, "//span[@role='menuitem' and .//span[text()='Ventas por Período']]")
        ventas_periodo.click()
        
        # Generar informe
        boton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Generar Informe']"))
        )
        try:
            boton.click()
            print("Clic realizado en Generar Informe")
        except:
            driver.execute_script("arguments[0].click();", boton)
            print("Clic con JavaScript realizado")
        time.sleep(10)
        
        # Click en el boton descarga
        generar_boton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".bbr-popupbutton"))
        )
        generar_boton.click()
        
        # Descargar Dato Fuente Periodo
        boton_descargar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//div[@role='button' and .//span[text()='Descargar Dato Fuente Período']]"
            ))
        )
        print("Elemento padre encontrado")
        boton_descargar.click()
        print("Clic realizado en elemento padre")
        time.sleep(5)
        
        # Seleccionar archivo
        seleccionar = driver.find_element(By.XPATH, "//div[@role='button' and .//span[text()='Seleccionar']]")
        seleccionar.click()
        time.sleep(6)
        
        # Descargar archivo
        descargar = driver.find_element(By.XPATH, "//a[contains(@href, 'venta')]")
        descargar.click()
        time.sleep(5)
        
        print("Descarga de ventas completada")
        return True
        
    except Exception as e:
        print(f"Error descargando ventas: {e}")
        return False

def verificar_descargas():
    """Verifica que archivos se descargaron"""
    print(f"\n=== ARCHIVOS EN {DIRECTORIO} ===")
    try:
        archivos = os.listdir(DIRECTORIO)
        if archivos:
            for archivo in archivos:
                ruta_completa = os.path.join(DIRECTORIO, archivo)
                tamaño = os.path.getsize(ruta_completa)
                print(f"📄 {archivo} ({tamaño} bytes)")
        else:
            print("❌ No se encontraron archivos descargados")
    except Exception as e:
        print(f"❌ Error al verificar descargas: {e}")

def extraer_archivos_zip():
    """Extrae todos los archivos XLSX de los ZIP directamente en la carpeta extraidos"""
    print(f"\n📦 Buscando archivos ZIP en {DIRECTORIO}...")
    
    # Crear directorio extraidos si no existe
    if not os.path.exists(DIRECTORIO_EXTRAIDOS):
        os.makedirs(DIRECTORIO_EXTRAIDOS)
    
    # Buscar archivos ZIP
    archivos_zip = glob.glob(os.path.join(DIRECTORIO, "*.zip"))
    
    if not archivos_zip:
        print("❌ No se encontraron archivos ZIP para extraer")
        return []
    
    archivos_extraidos = []
    
    for archivo_zip in archivos_zip:
        nombre_archivo = os.path.basename(archivo_zip)
        print(f"📂 Extrayendo: {nombre_archivo}")
        
        try:
            # Extraer directamente en la carpeta extraidos
            with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
                archivos_en_zip = zip_ref.namelist()
                
                # Filtrar solo archivos XLSX
                archivos_xlsx = [archivo for archivo in archivos_en_zip if archivo.lower().endswith('.xlsx')]
                
                if not archivos_xlsx:
                    print(f"⚠️ No se encontraron archivos .xlsx en {nombre_archivo}")
                    continue
                
                # Extraer solo los archivos XLSX
                for archivo_xlsx in archivos_xlsx:
                    # Extraer archivo
                    zip_ref.extract(archivo_xlsx, DIRECTORIO_EXTRAIDOS)
                    
                    # Si el archivo esta en una subcarpeta dentro del ZIP, moverlo a la raiz
                    ruta_extraida = os.path.join(DIRECTORIO_EXTRAIDOS, archivo_xlsx)
                    if os.path.dirname(archivo_xlsx):  # Si esta en subcarpeta
                        nombre_archivo_solo = os.path.basename(archivo_xlsx)
                        nueva_ruta = os.path.join(DIRECTORIO_EXTRAIDOS, nombre_archivo_solo)
                        
                        # Mover archivo a la raiz y eliminar carpeta vacia si existe
                        if os.path.exists(ruta_extraida):
                            if os.path.exists(nueva_ruta):
                                os.remove(nueva_ruta)  # Eliminar si ya existe
                            os.rename(ruta_extraida, nueva_ruta)
                            
                            # Eliminar carpeta vacia
                            carpeta_vacia = os.path.dirname(ruta_extraida)
                            try:
                                os.rmdir(carpeta_vacia)
                            except:
                                pass  # Ignorar si no se puede eliminar
                    
                    print(f"   ✅ {os.path.basename(archivo_xlsx)}")
                
                archivos_extraidos.extend([os.path.basename(f) for f in archivos_xlsx])
                
        except Exception as e:
            print(f"❌ Error al extraer {nombre_archivo}: {e}")
    
    if archivos_extraidos:
        print(f"\n🎉 Extraccion completada. Archivos XLSX extraidos: {len(archivos_extraidos)}")
        for archivo in archivos_extraidos:
            ruta_completa = os.path.join(DIRECTORIO_EXTRAIDOS, archivo)
            if os.path.exists(ruta_completa):
                tamaño = os.path.getsize(ruta_completa)
                print(f"   📊 {archivo} ({tamaño:,} bytes)")
    else:
        print("⚠️ No se extrajo ningun archivo XLSX")
    
    return archivos_extraidos

def conectar_gcs():
    """Conecta con Google Cloud Storage"""
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        print("✅ Conexion exitosa con Google Cloud Storage")
        return client, bucket
    except Exception as e:
        print(f"❌ Error al conectar con GCS: {e}")
        return None, None

def limpiar_bucket_path(bucket, ruta):
    """Elimina todos los archivos en una ruta especifica del bucket"""
    try:
        blobs = bucket.list_blobs(prefix=ruta)
        archivos_eliminados = []
        
        for blob in blobs:
            if not blob.name.endswith('/'):  # No eliminar "carpetas"
                blob.delete()
                archivos_eliminados.append(blob.name)
        
        if archivos_eliminados:
            print(f"🗑️ Eliminados {len(archivos_eliminados)} archivo(s) de {ruta}:")
            for archivo in archivos_eliminados:
                print(f"   - {archivo}")
        else:
            print(f"📂 No hay archivos que eliminar en {ruta}")
        
        return True
    except Exception as e:
        print(f"❌ Error al limpiar {ruta}: {e}")
        return False

def clasificar_archivos():
    """Clasifica los archivos extraidos como inventario o ventas"""
    archivos_xlsx = glob.glob(os.path.join(DIRECTORIO_EXTRAIDOS, "*.xlsx"))
    
    archivo_inventario = None
    archivo_ventas = None
    
    for archivo in archivos_xlsx:
        nombre = os.path.basename(archivo).lower()
        
        # Identificar por contenido del nombre
        if 'inventario' in nombre:
            archivo_inventario = archivo
        elif 'venta' in nombre:
            archivo_ventas = archivo
        # Si no tiene palabras clave especificas, usar el primero como inventario, segundo como ventas
        elif archivo_inventario is None:
            archivo_inventario = archivo
        elif archivo_ventas is None:
            archivo_ventas = archivo
    
    return archivo_inventario, archivo_ventas

def subir_archivo_gcs(bucket, ruta_local, ruta_destino):
    """Sube un archivo especifico al bucket"""
    try:
        blob = bucket.blob(ruta_destino)
        blob.upload_from_filename(ruta_local)
        
        # Verificar que se subio correctamente
        if blob.exists():
            tamaño = os.path.getsize(ruta_local)
            print(f"✅ Subido: {os.path.basename(ruta_local)} → {ruta_destino} ({tamaño:,} bytes)")
            return True
        else:
            print(f"❌ Error: El archivo no se subio correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error al subir {os.path.basename(ruta_local)}: {e}")
        return False

def subir_archivos_bucket():
    """Sube los archivos extraidos al bucket de Google Cloud Storage"""
    print("\n☁️ === SUBIENDO ARCHIVOS AL BUCKET ===")
    
    # Conectar con GCS
    client, bucket = conectar_gcs()
    if not bucket:
        return False
    
    # Clasificar archivos
    archivo_inventario, archivo_ventas = clasificar_archivos()
    
    if not archivo_inventario and not archivo_ventas:
        print("❌ No se encontraron archivos .xlsx para subir")
        return False
    
    exito_total = True
    
    # Procesar archivo de inventario
    if archivo_inventario:
        print(f"\n📊 Procesando inventario: {os.path.basename(archivo_inventario)}")
        
        # Limpiar ruta de inventario
        if limpiar_bucket_path(bucket, RUTA_INVENTARIO):
            # Subir nuevo archivo
            nombre_archivo = os.path.basename(archivo_inventario)
            ruta_destino = f"{RUTA_INVENTARIO}/{nombre_archivo}"
            if not subir_archivo_gcs(bucket, archivo_inventario, ruta_destino):
                exito_total = False
        else:
            exito_total = False
    
    # Procesar archivo de ventas
    if archivo_ventas:
        print(f"\n📈 Procesando ventas: {os.path.basename(archivo_ventas)}")
        
        # Limpiar ruta de ventas
        if limpiar_bucket_path(bucket, RUTA_VENTAS):
            # Subir nuevo archivo
            nombre_archivo = os.path.basename(archivo_ventas)
            ruta_destino = f"{RUTA_VENTAS}/{nombre_archivo}"
            if not subir_archivo_gcs(bucket, archivo_ventas, ruta_destino):
                exito_total = False
        else:
            exito_total = False
    
    if exito_total:
        print(f"\n🎉 Todos los archivos subidos exitosamente al bucket {BUCKET_NAME}")
    else:
        print(f"\n⚠️ Algunos archivos no se pudieron subir correctamente")
    
    return exito_total

def limpiar_archivos_locales():
    """Elimina todos los archivos ZIP y XLSX locales despues de la subida"""
    print("\n🧹 === LIMPIANDO ARCHIVOS LOCALES ===")
    
    archivos_eliminados = 0
    
    # Eliminar archivos ZIP
    archivos_zip = glob.glob(os.path.join(DIRECTORIO, "*.zip"))
    if archivos_zip:
        print(f"🗑️ Eliminando {len(archivos_zip)} archivo(s) ZIP:")
        for archivo in archivos_zip:
            try:
                nombre = os.path.basename(archivo)
                tamaño = os.path.getsize(archivo)
                os.remove(archivo)
                print(f"   ✅ {nombre} ({tamaño:,} bytes)")
                archivos_eliminados += 1
            except Exception as e:
                print(f"   ❌ Error al eliminar {os.path.basename(archivo)}: {e}")
    else:
        print("📂 No hay archivos ZIP para eliminar")
    
    # Eliminar archivos XLSX extraidos
    archivos_xlsx = glob.glob(os.path.join(DIRECTORIO_EXTRAIDOS, "*.xlsx"))
    if archivos_xlsx:
        print(f"\n🗑️ Eliminando {len(archivos_xlsx)} archivo(s) XLSX:")
        for archivo in archivos_xlsx:
            try:
                nombre = os.path.basename(archivo)
                tamaño = os.path.getsize(archivo)
                os.remove(archivo)
                print(f"   ✅ {nombre} ({tamaño:,} bytes)")
                archivos_eliminados += 1
            except Exception as e:
                print(f"   ❌ Error al eliminar {os.path.basename(archivo)}: {e}")
    else:
        print("📂 No hay archivos XLSX para eliminar")
    
    # Verificar si la carpeta extraidos esta vacia y mostrar resultado
    try:
        if os.path.exists(DIRECTORIO_EXTRAIDOS) and not os.listdir(DIRECTORIO_EXTRAIDOS):
            print(f"✨ Carpeta {os.path.basename(DIRECTORIO_EXTRAIDOS)} esta vacia")
    except:
        pass
    
    if archivos_eliminados > 0:
        print(f"\n🎉 Limpieza completada: {archivos_eliminados} archivo(s) eliminado(s)")
    else:
        print(f"\n📁 No habia archivos que limpiar")
    
    return archivos_eliminados

def main():
    """Funcion principal que ejecuta todo el proceso"""
    print("🚀 === INICIANDO PROCESO AUTOMATIZADO CENCOSUD ===")
    
    driver = None
    try:
        # 1. Configurar driver
        driver = setup_driver()
        if not driver:
            print("❌ Error: No se pudo crear el driver")
            return False
        
        print("Driver listo para usar")
        
        # 2. Proceso de login
        if not login_process(driver):
            print("❌ Error en el proceso de login")
            return False
        
        # 3. Descargar inventario
        if not descargar_inventario(driver):
            print("❌ Error descargando inventario")
            return False
        
        # 4. Descargar ventas
        if not descargar_ventas(driver):
            print("❌ Error descargando ventas")
            return False
        
        print("✅ Todas las descargas completadas")
        
    except Exception as e:
        print(f"❌ Error en el proceso principal: {e}")
        return False
    
    finally:
        # Cerrar driver
        if driver:
            driver.quit()
            print("🔒 Driver cerrado")
    
    # 5. Verificar descargas
    verificar_descargas()
    
    # 6. Extraer archivos ZIP
    archivos_extraidos = extraer_archivos_zip()
    if not archivos_extraidos:
        print("❌ No se extrajeron archivos")
        return False
    
    # 7. Subir al bucket
    if not subir_archivos_bucket():
        print("❌ Error subiendo archivos al bucket")
        return False
    
    # 8. Limpiar archivos locales
    limpiar_archivos_locales()
    
    print("\n🎉 === PROCESO COMPLETADO EXITOSAMENTE ===")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:

        print(f"\n❌ Error inesperado: {e}")
