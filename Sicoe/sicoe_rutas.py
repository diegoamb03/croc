#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para automatizar la descarga de rutas por vendedor desde SICOE
y subir el archivo a Google Cloud Storage.
"""

import os
import time
import tempfile
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import win32com.client as win32
from google.cloud import storage


def obtener_ruta_base():
    """Obtiene la ruta base del proyecto automáticamente"""
    return Path.cwd()


def descargar_rutas_sicoe(downloads_path):
    """Automatiza la descarga del archivo de rutas desde SICOE"""
    
    print(f"[INFO] Los archivos se descargarán en: {downloads_path}")
    
    # Crear la carpeta de descargas si no existe
    os.makedirs(downloads_path, exist_ok=True)
    
    # Configuración del navegador
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized") 
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Configurar la carpeta de descarga
    prefs = {
        "download.default_directory": str(downloads_path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Inicia el navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Carga la URL
        driver.get("https://sicoe.com.co/sicoe/dist/#/")
        
        # Espera a que cargue el botón "Iniciar sesión"
        boton_login = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Iniciar sesión")]'))
        )
        boton_login.click()
        print("[OK] Botón 'Iniciar sesión' clickeado")
        
        # Acceso de información a la página
        input_nit = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "nit"))
        )
        input_nit.send_keys("8301256101")
        print("[OK] NIT ingresado")
        
        # Espera a que cargue el campo de usuario
        input_usuario = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "login"))
        )
        input_usuario.send_keys("analistadatos")
        print("[OK] Usuario ingresado")
        
        # Espera a que cargue el campo de contraseña
        input_pass = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "passwd"))
        )
        input_pass.send_keys("628473*****Se")
        print("[OK] Contraseña ingresada")
        
        # Manejo de Checkbox 
        checkbox = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"]'))
        )
        checkbox.click()
        print("[OK] Checkbox seleccionado")
        
        # Darle Click al botón iniciar sesión
        boton_iniciar = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Iniciar")]'))
        )
        boton_iniciar.click()
        print("[OK] Sesión iniciada")
        
        # Click en el Botón de Informe 
        boton_informes = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/sam/menu1/menu/index.php"]'))
        )
        boton_informes.click()
        print("[OK] Botón informes clickeado")
        
        # Click en el botón siguiente 
        boton_next = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.buttonNext'))
        )
        boton_next.click()
        print("[OK] Botón siguiente clickeado")
        
        # Click en el botón de rutas 
        rutas_por_vendedor = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='tip' and contains(@href, \"ruta_x_asesor\")]"))
        )
        rutas_por_vendedor.click()
        print("[OK] Rutas por vendedor clickeado")
        
        # Click en exportar a excel 
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "sb-player"))
        )
        print("[OK] Cambiado al iframe con el informe.")
        
        boton_excel = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "excel"))
        )
        boton_excel.click()
        print("[OK] Descarga de Excel iniciada")
        
        # Espera para asegurarse de que la descarga se complete
        print("[ESPERA] Esperando a que se complete la descarga...")
        time.sleep(60)
        
        # Verificar si el archivo se descargó
        archivos_descargados = [f for f in os.listdir(downloads_path) if f.endswith(('.xlsx', '.xls'))]
        if archivos_descargados:
            print(f"[OK] Archivo(s) descargado(s): {archivos_descargados}")
            return True
        else:
            print("[ERROR] No se encontraron archivos de Excel descargados")
            return False
    
    except Exception as e:
        print(f"[ERROR] Error durante la ejecución: {str(e)}")
        return False
    
    finally:
        # Cierra el navegador y finaliza el WebDriver
        driver.quit()
        print("[OK] Navegador cerrado.")


def buscar_y_convertir_archivo(downloads_path):
    """Buscar archivo de rutas y convertirlo a xlsx"""
    
    # Buscar archivo
    archivos = [f for f in os.listdir(downloads_path) 
                if "rutas_x_asesor" in f and f.endswith(".xls")]
    
    if not archivos:
        print("[ERROR] No se encontró archivo de rutas")
        return None
    
    # Tomar el más reciente
    archivo = max(archivos, key=lambda f: os.path.getmtime(os.path.join(downloads_path, f)))
    ruta_xls = os.path.join(downloads_path, archivo)
    print(f"[OK] Archivo encontrado: {archivo}")
    
    # Limpiar cache win32com
    try:
        cache_dir = os.path.join(tempfile.gettempdir(), "gen_py")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
    except:
        pass
    
    # Convertir usando Excel
    try:
        excel = win32.Dispatch('Excel.Application')
        excel.Visible = False
        excel.DisplayAlerts = False
        
        wb = excel.Workbooks.Open(os.path.abspath(ruta_xls))
        ruta_xlsx = ruta_xls.replace('.xls', '.xlsx')
        wb.SaveAs(os.path.abspath(ruta_xlsx), FileFormat=51)
        wb.Close()
        excel.Quit()
        
        print(f"[OK] Convertido a: {os.path.basename(ruta_xlsx)}")
        return ruta_xlsx
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None


def buscar_credenciales(ruta_base):
    """Busca automáticamente el archivo de credenciales"""
    # Determinar la ruta correcta según desde dónde se ejecute
    if ruta_base.name == 'Sicoe':
        # Si estamos en la carpeta Sicoe
        ruta_credenciales = ruta_base / 'credentials' / 'croc-454221-e1a3c2e02181.json'
    else:
        # Si estamos en WEB SCAPING
        ruta_credenciales = ruta_base / 'Sicoe' / 'credentials' / 'croc-454221-e1a3c2e02181.json'
    
    if ruta_credenciales.exists():
        print(f"[OK] Credenciales encontradas: {ruta_credenciales}")
        return str(ruta_credenciales)
    
    # Buscar en posibles ubicaciones alternativas
    posibles_rutas = [
        ruta_base / 'credentials' / 'croc-454221-e1a3c2e02181.json',
        ruta_base / 'Sicoe' / 'credentials' / 'croc-454221-e1a3c2e02181.json',
    ]
    
    for ruta in posibles_rutas:
        if ruta.exists():
            print(f"[OK] Credenciales encontradas: {ruta}")
            return str(ruta)
    
    # Si no se encuentra, buscar cualquier archivo .json en credentials
    for base_path in [ruta_base, ruta_base / 'Sicoe']:
        credentials_dir = base_path / 'credentials'
        if credentials_dir.exists():
            json_files = list(credentials_dir.glob('*.json'))
            if json_files:
                print(f"[OK] Credenciales encontradas: {json_files[0]}")
                return str(json_files[0])
    
    raise FileNotFoundError(f"[ERROR] No se encontraron credenciales de Google Cloud")


def buscar_archivo_rutas(carpeta_descargas):
    """Busca el archivo de rutas más reciente en la carpeta de descargas"""
    carpeta_descargas = Path(carpeta_descargas)
    archivos = list(carpeta_descargas.glob("rutas_x_asesor*.xlsx"))
    
    if not archivos:
        print("[ERROR] No se encontró ningún archivo que coincida.")
        return None
    
    # Obtener el más reciente
    archivo_mas_reciente = max(archivos, key=lambda f: f.stat().st_mtime)
    print(f"[OK] Archivo encontrado: {archivo_mas_reciente.name}")
    return str(archivo_mas_reciente)


def subir_archivo_bucket(ruta_base, carpeta_descargas):
    """Función principal para subir archivo al bucket"""
    
    bucket_name = 'bucket-quickstart_croc_830'
    carpeta_destino = 'raw/Ventas/sicoe_rutas_vendedor'
    
    print(f"[INFO] Directorio base: {ruta_base}")
    print(f"[INFO] Carpeta de descargas: {carpeta_descargas}")
    
    # Buscar credenciales automáticamente
    try:
        ruta_credenciales = buscar_credenciales(ruta_base)
    except FileNotFoundError as e:
        print(e)
        return False
    
    # Buscar archivo de rutas en la carpeta de descargas
    archivo_local = buscar_archivo_rutas(carpeta_descargas)
    if not archivo_local:
        print("[ERROR] No se encontró el archivo .xlsx")
        return False
    
    # Autenticación
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ruta_credenciales
        cliente = storage.Client()
        bucket = cliente.bucket(bucket_name)
        print(f"[OK] Conectado al bucket: {bucket_name}")
    except Exception as e:
        print(f"[ERROR] Error de autenticación: {e}")
        return False
    
    # Eliminar archivos existentes en la carpeta
    try:
        print(f"[LIMPIEZA] Limpiando carpeta '{carpeta_destino}' en el bucket...")
        blobs = bucket.list_blobs(prefix=carpeta_destino)
        archivos_eliminados = 0
        for blob in blobs:
            print(f"[ELIMINANDO] {blob.name}")
            blob.delete()
            archivos_eliminados += 1
        
        if archivos_eliminados == 0:
            print("[INFO] No había archivos previos para eliminar")
        else:
            print(f"[OK] {archivos_eliminados} archivo(s) eliminado(s)")
            
    except Exception as e:
        print(f"[ADVERTENCIA] Error al limpiar carpeta: {e}")
    
    # Subir nuevo archivo
    try:
        nombre_archivo = os.path.basename(archivo_local)
        nombre_archivo_bucket = f"{carpeta_destino}/{nombre_archivo}"
        
        blob = bucket.blob(nombre_archivo_bucket)
        blob.upload_from_filename(archivo_local)
        
        print(f"[OK] Archivo subido exitosamente: {nombre_archivo_bucket}")
        print(f"[INFO] Tamaño del archivo: {os.path.getsize(archivo_local) / (1024*1024):.2f} MB")
        print(f"[INFO] Ruta en el bucket: gs://{bucket_name}/{nombre_archivo_bucket}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al subir archivo: {e}")
        return False


def limpiar_archivos_locales(downloads_path):
    """Elimina los archivos descargados localmente"""
    archivos_eliminados = 0
    for archivo in os.listdir(downloads_path):
        if "rutas_x_asesor" in archivo:
            ruta_completa = os.path.join(downloads_path, archivo)
            try:
                os.remove(ruta_completa)
                print(f"[ELIMINADO] {archivo}")
                archivos_eliminados += 1
            except Exception as e:
                print(f"[ERROR] Error al eliminar {archivo}: {e}")
    
    if archivos_eliminados == 0:
        print("[INFO] No se encontraron archivos para eliminar.")
    else:
        print(f"[OK] Eliminados {archivos_eliminados} archivos.")


def main():
    """Función principal del script"""
    print("=" * 60)
    print("INICIO DEL PROCESO DE DESCARGA Y CARGA DE RUTAS SICOE")
    print("=" * 60)
    
    # Obtener ruta base (debería ser la carpeta Sicoe)
    ruta_base = obtener_ruta_base()
    
    # Si el script se ejecuta desde dentro de Sicoe, usar descargas directamente
    # Si se ejecuta desde WEB SCAPING, navegar a Sicoe/descargas
    if ruta_base.name == 'Sicoe':
        downloads_path = ruta_base / 'descargas'
    else:
        # Si estamos en WEB SCAPING, ir a Sicoe/descargas
        downloads_path = ruta_base / 'Sicoe' / 'descargas'
    
    # Paso 1: Descargar archivo desde SICOE
    print("\n[PASO 1] Descargando archivo desde SICOE...")
    if not descargar_rutas_sicoe(str(downloads_path)):
        print("\n[ERROR] Error en la descarga. Proceso abortado.")
        return
    
    # Paso 2: Convertir archivo de .xls a .xlsx
    print("\n[PASO 2] Convirtiendo archivo a formato .xlsx...")
    ruta_xlsx = buscar_y_convertir_archivo(str(downloads_path))
    if not ruta_xlsx:
        print("\n[ERROR] Error en la conversión. Proceso abortado.")
        return
    
    # Verificar contenido
    df = pd.read_excel(ruta_xlsx)
    print(f"[OK] {len(df)} filas, {len(df.columns)} columnas")
    
    # Paso 3: Subir archivo a Google Cloud Storage
    print("\n[PASO 3] Subiendo archivo a Google Cloud Storage...")
    if not subir_archivo_bucket(ruta_base, str(downloads_path)):
        print("\n[ERROR] Error al subir a GCS. Proceso abortado.")
        return
    
    # Paso 4: Limpiar archivos locales
    print("\n[PASO 4] Limpiando archivos locales...")
    limpiar_archivos_locales(str(downloads_path))
    print("\n" + "=" * 60)
    print("[EXITO] PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 60)


if __name__ == "__main__":
    main()