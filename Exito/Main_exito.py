#!/usr/bin/env python3
#Cambiar la ruta de descarga en download_path (Linea 800)
"""
Proceso automatización Exito
Script para automatizar la descarga de reportes de Exito y subirlos a Google Cloud Storage
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from google.oauth2 import service_account
from google.cloud import storage
import time
import datetime
import os
import glob
import pandas as pd
import re
import shutil


class ExitoAutomation:
    def __init__(self, download_path, credentials_path, bucket_name):
        self.download_path = download_path
        self.credentials_path = credentials_path
        self.bucket_name = bucket_name
        self.driver = None
        self.ventana_original = None
        
    def setup_driver(self):
        """Configura y retorna el driver de Chrome"""
        chrome_options = Options()
        prefs = {
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        return self.driver

    def clean_existing_files(self):
        """Elimina archivos Excel existentes en la carpeta de descarga"""
        archivos_excel = glob.glob(os.path.join(self.download_path, "*.xlsx")) + glob.glob(os.path.join(self.download_path, "*.xls"))
        
        for archivo in archivos_excel:
            try:
                os.remove(archivo)
                print(f"Archivo eliminado: {archivo}")
            except Exception as e:
                print(f"No se pudo eliminar {archivo}: {e}")

    def wait_captcha(self):
        """Espera para resolver CAPTCHA manualmente"""
        print("Resuelve el CAPTCHA manualmente (20 segundos)...")
        for i in range(20, 0, -1):
            print(f"Tiempo: {i}s", end="\r")
            time.sleep(1)
        print("\nContinuando...")

    def login_to_site(self, email, password):
        """Función principal para hacer login automático"""
        print("INICIANDO LOGIN AUTOMÁTICO")
        print("=" * 40)
        
        self.setup_driver()
        
        try:
            # 1. Navegar a la página
            print("Navegando a la página...")
            self.driver.get("https://prescriptivalatam.com/")
            
            # 2. Llenar credenciales
            print("Llenando credenciales...")
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            email_field.clear()
            email_field.send_keys(email)
            password_field.clear()
            password_field.send_keys(password)
            
            # 3. Manejar reCAPTCHA
            print("Clickeando CAPTCHA...")
            recaptcha_iframe = WebDriverWait(self.driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
            )
            checkbox = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "recaptcha-checkbox-border"))
            )
            checkbox.click()
            self.driver.switch_to.default_content()
            
            # 4. Esperar resolución manual del CAPTCHA
            self.wait_captcha()
            
            # 5. Hacer login
            print("Ejecutando login...")
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            login_button.click()
            time.sleep(3)
            
            # 6. Manejar modal si aparece
            print("Verificando modal...")
            try:
                continuar_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btn__applyFilter"))
                )
                continuar_btn.click()
                print("Modal cerrado")
                time.sleep(2)
                
                # Segundo login después del modal
                login_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                )
                login_button.click()
                time.sleep(2)
                
            except:
                print("No hay modal - continuando...")
            
            print("LOGIN COMPLETADO EXITOSAMENTE")
            print("=" * 40)
            print(f"URL: {self.driver.current_url}")
            print("Driver listo para scraping")
            
            return True
            
        except Exception as e:
            print(f"ERROR: {e}")
            if self.driver:
                self.driver.quit()
            return False

    def click_cen_colaboracion(self):
        """Hace clic en 'Cen Colaboración' del menú"""
        print("Clickeando 'Cen Colaboración'...")
        
        selectors = [
            (By.ID, "menu-options-1"),
            (By.XPATH, "//button[@aria-label='Cen Colaboración']"),
            (By.XPATH, "//button[.//img[@alt='Cen Colaboración']]")
        ]
        
        for selector_type, selector_value in selectors:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(1)
                element.click()
                print("Cen Colaboración activado")
                time.sleep(2)
                return True
            except:
                continue
        
        print("No se pudo activar Cen Colaboración")
        return False

    def click_reporte_dinamico_accordion(self):
        """Hace clic en el accordion de Reporte dinámico"""
        Reporte_dinamico = [
            (By.XPATH, "//button[text()='Reporte dinámico']"),
            (By.XPATH, "//button[contains(text(), 'Reporte dinámico')]"),
            (By.XPATH, "//button[contains(text(), 'Reporte')]"),
            (By.XPATH, "//button[contains(text(), 'dinámico')]"),
            (By.XPATH, "//button[contains(@class, 'sideBar__button__options') and contains(text(), 'Reporte')]"),
        ]
        
        for selector_type, selector_value in Reporte_dinamico:
            try:
                print(f"Intentando selector: {selector_value}")
                
                accordion_element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                
                print(f"Accordion encontrado: {accordion_element.tag_name}")
                
                # Hacer scroll al elemento
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", accordion_element)
                time.sleep(2)
                
                # Intentar click normal
                try:
                    accordion_element.click()
                    print("Click normal exitoso en accordion")
                    break
                except Exception as click_error:
                    print(f"Click normal falló: {str(click_error)[:50]}...")
                    print("Intentando con JavaScript...")
                    
                    # Si el click normal falla, usar JavaScript
                    self.driver.execute_script("arguments[0].click();", accordion_element)
                    print("Click con JavaScript exitoso en accordion")
                    break
                    
            except Exception as e:
                print(f"Selector falló: {str(e)[:60]}...")
                continue
        
        print("Esperando animación del accordion...")
        time.sleep(3)

    def click_reporte_en_linea(self):
        """Hace clic en 'Reporte en línea'"""
        print("Intentando hacer clic en 'Reporte en línea'...")
        
        selectors = [
            (By.XPATH, "//button[text()='Reporte en línea']"),
            (By.XPATH, "//button[contains(text(), 'Reporte en línea')]"),
            (By.XPATH, "//button[contains(@class, 'MuiButton-root') and text()='Reporte en línea']"),
        ]
        
        wait = WebDriverWait(self.driver, 15)
        current_url = self.driver.current_url
        
        for i, (selector_type, selector_value) in enumerate(selectors, 1):
            try:
                print(f"Estrategia {i}: {selector_value[:50]}...")
                
                element = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                print(f"Elemento encontrado y clickeable")

                element.click()
                print("Click realizado")
                
                time.sleep(3)
                
                if self.driver.current_url != current_url:
                    print("URL cambió - Click exitoso confirmado")
                    return True
                
                try:
                    element.is_enabled()
                except StaleElementReferenceException:
                    print("Elemento stale - Click exitoso confirmado")
                    return True
                    
                print("Click procesado correctamente")
                return True
                    
            except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
                if isinstance(e, StaleElementReferenceException):
                    print("Stale element - Click anterior exitoso")
                    return True
                print(f"Estrategia {i} falló: {str(e)[:50]}...")
                continue
                
            except Exception as e:
                print(f"Estrategia {i} falló: {str(e)[:50]}...")
                continue
        
        print("Todas las estrategias fallaron")
        return False

    def switch_to_new_window(self):
        """Cambia a la nueva ventana"""
        self.ventana_original = self.driver.current_window_handle
        self.driver.implicitly_wait(4)
        todas_las_ventanas = self.driver.window_handles
        for ventana in todas_las_ventanas:
            if ventana != self.ventana_original:
                self.driver.switch_to.window(ventana)
                break

    def click_bookmarks_button(self):
        """Hace clic en el botón de marcadores"""
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-tid="assets-button-bookmarks"]'))
        )
        element.click()

    def click_ventas_button(self):
        """Hace clic en el botón de ventas"""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-testid="privateList-list-item-button-7cf8658b-22b6-476c-8a67-aa90c13fc026"]'))
            )
            element.click()
        except:
            print("No se encontró el botón de ventas")

    def accept_terms(self):
        """Acepta los términos"""
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.lui-button.ng-scope.ng-isolate-scope'))
        )
        element.click()

    def select_month_filter(self):
        """Selecciona el filtro de mes"""
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'h6[aria-label="Mes"]'))
        )
        element.click()
        time.sleep(2)

    def select_current_and_previous_months(self):
        """Selecciona automáticamente el mes actual y el mes anterior"""
        # Diccionario de meses en español
        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        
        # Obtener fecha actual
        fecha_actual = datetime.datetime.now()
        mes_actual = fecha_actual.month
        
        # Calcular mes anterior
        if mes_actual == 1:
            mes_anterior = 12
            año_anterior = fecha_actual.year - 1
        else:
            mes_anterior = mes_actual - 1
            año_anterior = fecha_actual.year
        
        # Nombres de los meses
        nombre_mes_actual = meses[mes_actual]
        nombre_mes_anterior = meses[mes_anterior]
        
        print(f"Seleccionando: {nombre_mes_actual} (actual) y {nombre_mes_anterior} (anterior)")
        
        try:
            # Seleccionar mes actual
            element_actual = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[text()="{nombre_mes_actual}"]'))
            )
            element_actual.click()
            print(f"Seleccionado mes actual: {nombre_mes_actual}")
            time.sleep(1)
            
            # Seleccionar mes anterior
            element_anterior = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[text()="{nombre_mes_anterior}"]'))
            )
            element_anterior.click()
            print(f"Seleccionado mes anterior: {nombre_mes_anterior}")
            time.sleep(2)
            
            return True, [nombre_mes_actual, nombre_mes_anterior]
            
        except Exception as e:
            print(f"Error seleccionando los meses: {e}")
            return False, []

    def confirm_selection(self):
        """Confirma la selección"""
        boton = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="actions-toolbar-confirm"]'))
        )
        boton.click()
        time.sleep(2)

    def select_year_filter(self):
        """Selecciona el filtro de año"""
        elemento = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'h6[aria-label="Año"]'))
        )
        elemento.click()
        time.sleep(3)

    def select_year_2025(self):
        """Selecciona el año 2025"""
        elemento = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="2025"]'))
        )
        elemento.click()
        time.sleep(3)

    def download_report(self, report_name="Reporte en línea"):
        """Descarga el reporte"""
        # Esperar hasta que el elemento sea visible
        elemento = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f'//div[text()="{report_name}"]'))
        )

        # Hacer clic derecho (context click)
        acciones = ActionChains(self.driver)
        acciones.context_click(elemento).perform()

        # Esperar a que aparezca la opción del menú contextual "Descargar"
        descargar_opcion = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//li[@id="download" or @tid="download" or .//span[text()="Descargar"]]'))
        )

        # Hacer clic en esa opción
        descargar_opcion.click()
        time.sleep(2)

        # Hacer clic en el botón de descarga final
        boton_descarga_final = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="download-dialog-download-button"]'))
        )
        boton_descarga_final.click()

    def close_download_modal(self):
        """Cierra el modal de descarga"""
        try:
            cerrar_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="download-dialog-close" or @tid="download-cancel"]'))
            )
            cerrar_btn.click()
            print("Modal de descarga cerrado")
        except:
            print("No se pudo cerrar el modal de descarga")

    def process_inventory_report(self):
        """Procesa el reporte de inventario"""
        print("Procesando reporte de inventario...")
        
        # Hacer clic en marcadores
        self.click_bookmarks_button()
        
        # Esperar y hacer clic en "Inventario1"
        inventario_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Inventario1"]'))
        )
        inventario_btn.click()
        print("Clic en Inventario1")
        
        # Aceptar términos
        self.accept_terms()
        
        # Limpiar selección de month_name
        clear_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="clear-month_name"]'))
        )
        clear_btn.click()
        print("Clic en limpiar selección de month_name")
        
        # Limpiar selección de year_number
        print("Limpiando selección de year_number...")
        year_clear_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="clear-year_number"]'))
        )
        year_clear_btn.click()
        print("Clic en limpiar selección de year_number")
        time.sleep(3)
        
        # Buscar selector de Mes con múltiples estrategias
        print("Buscando selector de Mes...")
        month_selectors = [
            (By.CSS_SELECTOR, 'h6[aria-label="Mes"]'),
            (By.XPATH, '//h6[text()="Mes"]'),
            (By.XPATH, '//h6[contains(text(), "Mes")]'),
        ]
        
        element_found = False
        for i, (selector_type, selector_value) in enumerate(month_selectors, 1):
            try:
                print(f"Estrategia {i}: {selector_value}")
                
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                
                if element.is_displayed() and element.is_enabled():
                    print(f"Elemento encontrado con estrategia {i}")
                    
                    # Hacer scroll al elemento
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(1)
                    
                    # Hacer click
                    try:
                        element.click()
                        print("Click exitoso en selector de Mes")
                        element_found = True
                        break
                    except Exception as click_error:
                        print(f"Click normal falló: {click_error}")
                        self.driver.execute_script("arguments[0].click();", element)
                        print("Click con JavaScript exitoso")
                        element_found = True
                        break
                        
            except Exception as e:
                print(f"Estrategia {i} falló: {str(e)[:50]}...")
                continue
        
        if element_found:
            # Obtener mes actual para selección
            fecha_actual = datetime.datetime.now()
            meses = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            nombre_mes = meses[fecha_actual.month]
            
            # Hacer clic en el mes actual
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[text()="{nombre_mes}"]'))
            )
            element.click()
            
            # Confirmar selección
            self.confirm_selection()
            
            # Seleccionar año
            self.select_year_filter()
            
            # Seleccionar año 2025 con XPath específico
            try:
                wait = WebDriverWait(self.driver, 10)
                elemento = wait.until(EC.element_to_be_clickable((By.XPATH, 
                    '//span[@class="njs-1ecc-Typography-root njs-1ecc-Typography-body2 njs-1ecc-Typography-alignRight RowColumn-labelText css-78lweu"]//span[text()="2025"]')))
                
                if elemento.is_displayed() and elemento.is_enabled():
                    print("Elemento encontrado y visible")
                    
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemento)
                    time.sleep(1)
                    
                    try:
                        elemento.click()
                        print("Click normal exitoso")
                    except ElementClickInterceptedException:
                        self.driver.execute_script("arguments[0].click();", elemento)
                        print("Click JavaScript exitoso")
                        
            except Exception as e:
                print(f"Error seleccionando año 2025: {e}")
            
            # Confirmar selección
            self.confirm_selection()
            
            # Descargar reporte
            self.download_report()

    def rename_downloaded_files(self):
        """Identifica y renombra los archivos descargados"""
        # Esperar a que existan ambos archivos
        while True:
            archivos = glob.glob(os.path.join(self.download_path, "Qlik Sense - Reporte en línea*.xlsx"))
            archivos = [f for f in archivos if not f.endswith(".crdownload")]
            if len(archivos) >= 2:
                break
            time.sleep(1)

        # Identificar el que tiene (1) → Inventario, y el que no → Ventas Mensuales
        for archivo in archivos:
            fecha = archivo.split("Qlik Sense - Reporte en línea - ")[1].replace(".xlsx", "").replace(" (1)", "")
            if "(1)" in archivo:
                nuevo_nombre = f"Qlik Sense - Reporte en línea - {fecha} Inventario.xlsx"
            else:
                nuevo_nombre = f"Qlik Sense - Reporte en línea - {fecha} Ventas Mensuales.xlsx"
            
            nuevo_path = os.path.join(self.download_path, nuevo_nombre)
            shutil.move(archivo, nuevo_path)
            print(f"Renombrado: {os.path.basename(archivo)} → {os.path.basename(nuevo_path)}")

    def clean_bucket(self):
        """Función para eliminar archivos existentes en el bucket antes de subir nuevos"""
        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            
            # Rutas a limpiar
            rutas_a_limpiar = [
                "raw/Ventas/moderno/exito/inventario/",
                "raw/Ventas/moderno/exito/ventas/"
            ]
            
            print("Limpiando archivos existentes en el bucket...")
            
            for ruta in rutas_a_limpiar:
                blobs = list(bucket.list_blobs(prefix=ruta))
                archivos_xlsx = [blob for blob in blobs if blob.name.endswith('.xlsx')]
                
                if archivos_xlsx:
                    print(f"Limpiando {len(archivos_xlsx)} archivos en {ruta}")
                    for blob in archivos_xlsx:
                        try:
                            blob.delete()
                            print(f"Eliminado: {blob.name.split('/')[-1]}")
                        except Exception as e:
                            print(f"Error eliminando {blob.name}: {e}")
                else:
                    print(f"No hay archivos .xlsx en {ruta}")
            
            print("Limpieza del bucket completada")
            return True
            
        except Exception as e:
            print(f"Error limpiando el bucket: {e}")
            return False

    def upload_files_to_bucket(self):
        """Función para subir los archivos descargados al bucket de Google Cloud Storage"""
        try:
            # Configurar las credenciales
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            
            # Inicializar el cliente de Storage
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            
            # Buscar los archivos descargados
            archivos_excel = glob.glob(os.path.join(self.download_path, "Qlik Sense - Reporte en línea*.xlsx"))
            
            if not archivos_excel:
                print("No se encontraron archivos para subir")
                return False
            
            print(f"Encontrados {len(archivos_excel)} archivos para subir")
            
            # Procesar cada archivo
            for archivo_local in archivos_excel:
                nombre_archivo = os.path.basename(archivo_local)
                print(f"\nProcesando: {nombre_archivo}")
                
                # Determinar la ruta de destino según el tipo de archivo
                if "Inventario" in nombre_archivo:
                    ruta_destino = f"raw/Ventas/moderno/exito/inventario/{nombre_archivo}"
                    print(f"Tipo: Inventario")
                elif "Ventas Mensuales" in nombre_archivo:
                    ruta_destino = f"raw/Ventas/moderno/exito/ventas/{nombre_archivo}"
                    print(f"Tipo: Ventas Mensuales")
                else:
                    print(f"Tipo de archivo no reconocido: {nombre_archivo}")
                    continue
                
                # Crear el blob y subir el archivo
                blob = bucket.blob(ruta_destino)
                
                try:
                    print(f"Subiendo a: gs://{self.bucket_name}/{ruta_destino}")
                    blob.upload_from_filename(archivo_local)
                    
                    # Verificar que se subió correctamente
                    if blob.exists():
                        print(f"Archivo subido exitosamente")
                        print(f"Tamaño: {blob.size} bytes")
                        print(f"Fecha de subida: {blob.time_created}")
                    else:
                        print(f"Error: El archivo no se encuentra en el bucket")
                        
                except Exception as upload_error:
                    print(f"Error subiendo {nombre_archivo}: {upload_error}")
                    continue
            
            print(f"\nProceso de subida completado")
            return True
            
        except Exception as e:
            print(f"Error crítico en la subida al bucket: {e}")
            return False

    def verify_bucket_files(self):
        """Función para verificar que los archivos están en el bucket"""
        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            
            # Verificar archivos en inventario
            inventario_blobs = list(bucket.list_blobs(prefix="raw/Ventas/moderno/exito/inventario/"))
            ventas_blobs = list(bucket.list_blobs(prefix="raw/Ventas/moderno/exito/ventas/"))
            
            print("\nArchivos en inventario:")
            for blob in inventario_blobs:
                if blob.name.endswith('.xlsx'):
                    print(f"  {blob.name.split('/')[-1]} - {blob.size} bytes")
            
            print("\nArchivos en ventas:")
            for blob in ventas_blobs:
                if blob.name.endswith('.xlsx'):
                    print(f"  {blob.name.split('/')[-1]} - {blob.size} bytes")
                    
        except Exception as e:
            print(f"Error verificando archivos en bucket: {e}")

    def clean_local_files(self):
        """Función para limpiar los archivos locales después de subirlos"""
        try:
            archivos_excel = glob.glob(os.path.join(self.download_path, "Qlik Sense - Reporte en línea*.xlsx"))
            
            for archivo in archivos_excel:
                try:
                    os.remove(archivo)
                    print(f"Archivo local eliminado: {os.path.basename(archivo)}")
                except Exception as e:
                    print(f"No se pudo eliminar {archivo}: {e}")
                    
        except Exception as e:
            print(f"Error limpiando archivos locales: {e}")

    def run_automation(self, email, password):
        """Ejecuta todo el proceso de automatización"""
        print("INICIANDO PROCESO DE AUTOMATIZACIÓN EXITO")
        print("=" * 50)
        
        # Paso 1: Limpiar archivos existentes
        print("Paso 1: Limpiando archivos existentes...")
        self.clean_existing_files()
        
        # Paso 2: Login
        print("\nPaso 2: Iniciando sesión...")
        if not self.login_to_site(email, password):
            print("Error en el login. Abortando proceso.")
            return False
        
        # Paso 3: Activar Cen Colaboración
        print("\nPaso 3: Activando Cen Colaboración...")
        if not self.click_cen_colaboracion():
            print("Error activando Cen Colaboración. Abortando proceso.")
            return False
        
        # Paso 4: Expandir accordion Reporte dinámico
        print("\nPaso 4: Expandiendo accordion Reporte dinámico...")
        self.click_reporte_dinamico_accordion()
        
        # Paso 5: Hacer clic en Reporte en línea
        print("\nPaso 5: Haciendo clic en Reporte en línea...")
        if not self.click_reporte_en_linea():
            print("Error haciendo clic en Reporte en línea. Abortando proceso.")
            return False
        
        # Paso 6: Cambiar a nueva ventana
        print("\nPaso 6: Cambiando a nueva ventana...")
        self.switch_to_new_window()
        
        # Paso 7: Procesar reporte de ventas
        print("\nPaso 7: Procesando reporte de ventas...")
        self.click_bookmarks_button()
        self.click_ventas_button()
        self.accept_terms()
        
        # Seleccionar mes y año para ventas
        self.select_month_filter()
        success, meses_seleccionados = self.select_current_and_previous_months()
        if success:
            print(f"Meses seleccionados correctamente: {', '.join(meses_seleccionados)}")
        
        self.confirm_selection()
        self.select_year_filter()
        self.select_year_2025()
        self.confirm_selection()
        
        # Descargar reporte de ventas
        print("Descargando reporte de ventas...")
        self.download_report()
        time.sleep(7)  # Esperar descarga
        self.close_download_modal()
        
        # Paso 8: Procesar reporte de inventario
        print("\nPaso 8: Procesando reporte de inventario...")
        self.process_inventory_report()
        time.sleep(10)  # Esperar descarga
        
        # Paso 9: Cerrar navegador
        print("\nPaso 9: Cerrando navegador...")
        if self.driver:
            self.driver.quit()
        
        # Paso 10: Renombrar archivos
        print("\nPaso 10: Renombrando archivos...")
        self.rename_downloaded_files()
        
        # Paso 11: Subir al bucket
        print("\nPaso 11: Subiendo archivos al bucket...")
        if self.clean_bucket():
            if self.upload_files_to_bucket():
                print("\nVerificando archivos en el bucket...")
                self.verify_bucket_files()

                print("\nLimpiando archivos locales automáticamente...")
                self.clean_local_files()
        
        print("\nPROCESO COMPLETADO EXITOSAMENTE")
        return True


def main():
    """Función principal"""
    # Configuración
    download_path = r"C:\Users\dani\OneDrive\Web Scaping\Exito"  # Cambiar por tu ruta
    credentials_path = "credentials/croc-454221-e1a3c2e02181.json"
    bucket_name = "bucket-quickstart_croc_830"
    
    # Credenciales
    EMAIL = "grandessuperficies@donchicharron.com.co"
    PASSWORD = "Mar2cazaz123*"
    
    # Crear instancia de automatización
    automation = ExitoAutomation(download_path, credentials_path, bucket_name)
    
    # Ejecutar proceso
    try:
        automation.run_automation(EMAIL, PASSWORD)
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario")
        if automation.driver:
            automation.driver.quit()
    except Exception as e:
        print(f"Error crítico en el proceso: {e}")
        if automation.driver:
            automation.driver.quit()


if __name__ == "__main__":
    main()