"""
Script para extracción de datos del portal SICOE y carga a Google Cloud Storage.

Este script automatiza la extracción de reportes (detallados y de facturas) desde el sistema SICOE 
y los sube a buckets específicos en Google Cloud Storage. También gestiona la limpieza de archivos
locales y remotos.
"""

import os
import glob
import time
import sys
import logging
import calendar
import subprocess
from datetime import date, datetime
from typing import Tuple, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from google.cloud import storage
from google.oauth2 import service_account

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sicoe_automation.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SICOE_Automation")


def setup_requirements():
    """
    Instala los requerimientos necesarios para el script.
    Crea el archivo requirements.txt si no existe e instala las dependencias.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(current_dir, "requirements.txt")
    
    # Contenido del requirements.txt
    requirements_content = """selenium
beautifulsoup4
pandas
webdriver_manager
google-cloud-storage"""
    
    try:
        # Crear requirements.txt si no existe
        if not os.path.exists(requirements_path):
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            logger.info(f"Archivo requirements.txt creado en: {requirements_path}")
        
        # Instalar las librerías
        logger.info("Instalando dependencias...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_path
        ])
        logger.info("✅ Librerías instaladas correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error al instalar librerías: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado en setup_requirements: {e}")
        return False


def setup_credentials_directory():
    """
    Configura el directorio de credenciales y verifica que exista el archivo.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_dir = os.path.join(current_dir, "credentials")
    credentials_file = os.path.join(credentials_dir, "croc-454221-e1a3c2e02181.json")
    
    # Crear directorio si no existe
    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)
        logger.info(f"✅ Directorio de credenciales creado: {credentials_dir}")
    
    # Verificar archivo de credenciales
    if not os.path.exists(credentials_file):
        logger.error(f"❌ Archivo de credenciales no encontrado: {credentials_file}")
        logger.info("📋 Para solucionarlo:")
        logger.info("1. Descarga tu archivo de credenciales desde Google Cloud Console")
        logger.info("2. Renómbralo a: croc-454221-e1a3c2e02181.json")
        logger.info(f"3. Colócalo en: {credentials_dir}")
        return None
    
    # Configurar variable de entorno
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
    logger.info(f"✅ Credenciales configuradas: {credentials_file}")
    return credentials_file


class SicoeConfig:
    """
    Clase para la configuración del script de SICOE.
    
    Maneja todos los parámetros de configuración necesarios para la conexión con
    el portal SICOE y Google Cloud Storage.
    """
    
    def __init__(
        self, 
        login_url: str = "https://sicoe.com.co/sicoe/dist/#/login",
        nit: str = "8301256101",
        username: str = "analistadatos",
        password: str = "628473*****Se",
        bucket_name: str = "bucket-quickstart_croc_830",
        destination_prefix: str = "raw/Ventas/sicoe/",
        destination_prefix_facture: str = "raw/Ventas/sicoe_facture_diarias/",
        credentials_path: str = None,
        base_dir: str = None,
        file_pattern: str = "*detallado*",
        file_pattern_facture: str = "*LISTADO_FACTURAS*",
        wait_time_standard: int = 8,
        download_wait_time: int = 25
    ):
        """
        Inicializa la configuración para el script de SICOE.
        """
        self.login_url = login_url
        self.nit = nit
        self.username = username
        self.password = password
        self.bucket_name = bucket_name
        self.destination_prefix = destination_prefix
        self.destination_prefix_facture = destination_prefix_facture
        
        # Configurar rutas usando el directorio actual del script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Configurar credentials_path si no se proporciona
        if credentials_path is None:
            self.credentials_path = os.path.join(current_dir, "credentials", "croc-454221-e1a3c2e02181.json")
        else:
            self.credentials_path = credentials_path
        
        # Configurar base_dir si no se proporciona
        if base_dir is None:
            # Usar el directorio padre del directorio actual
            self.base_dir = os.path.dirname(current_dir)
        else:
            self.base_dir = base_dir
        
        self.file_pattern = file_pattern
        self.file_pattern_facture = file_pattern_facture
        self.wait_time_standard = wait_time_standard
        self.download_wait_time = download_wait_time
        
    def get_date_range(self) -> Tuple[str, str]:
        """
        Obtiene el rango de fechas del mes actual.
        
        Returns:
            Tupla con el primer y último día del mes en formato 'YYYY-MM-DD'
        """
        today = datetime.now()
        year, month = today.year, today.month
        first_day = date(year, month, 1)
        
        # Obtener el último día del mes usando calendar
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        
        return (
            first_day.strftime("%Y-%m-%d"), 
            last_day.strftime("%Y-%m-%d")
        )

    def load_from_env(self) -> None:
        """
        Carga la configuración desde variables de entorno si están disponibles.
        
        Permite sobreescribir la configuración por defecto con valores de entorno,
        útil para entornos de CI/CD y despliegues en contenedores.
        """
        # Valores de autenticación
        self.nit = os.environ.get('SICOE_NIT', self.nit)
        self.username = os.environ.get('SICOE_USERNAME', self.username)
        self.password = os.environ.get('SICOE_PASSWORD', self.password)
        
        # Configuración de GCS
        self.bucket_name = os.environ.get('GCS_BUCKET_NAME', self.bucket_name)
        credentials_from_env = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_from_env:
            self.credentials_path = credentials_from_env
        
        # Configuración adicional opcional
        self.login_url = os.environ.get('SICOE_LOGIN_URL', self.login_url)
        base_dir_from_env = os.environ.get('BASE_DIR')
        if base_dir_from_env:
            self.base_dir = base_dir_from_env
        
        logger.debug("Configuración cargada desde variables de entorno")


class WebDriverManager:
    """
    Clase para gestionar las operaciones del WebDriver.
    
    Maneja la inicialización, configuración y cierre del navegador,
    así como las esperas para elementos en la página.
    """
    
    def __init__(self, config: SicoeConfig):
        """
        Inicializa el gestor de WebDriver.
        
        Args:
            config: Objeto de configuración de SICOE
        """
        self.config = config
        self.driver = None
        
    def initialize_driver(self) -> webdriver.Chrome:
        """
        Inicializa y configura el navegador Chrome VISIBLE.
        
        Returns:
            Instancia del WebDriver de Chrome configurado
        """
        try:
            options = webdriver.ChromeOptions()
            
            # OPCIONES PARA CHROME VISIBLE
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # REMOVER estas líneas que ocultan Chrome:
            # options.add_argument("--disable-gpu")
            # options.add_argument("--no-sandbox") 
            # options.add_argument("--disable-dev-shm-usage")
            
            # Opcional: Mantener Chrome abierto después del script
            options.add_experimental_option("detach", True)
            
            # Configurar carpeta de descarga si es necesario
            download_dir = os.path.join(os.path.dirname(__file__), "downloads")
            os.makedirs(download_dir, exist_ok=True)
            
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            # Ejecutar script para ocultar que es automatizado
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("WebDriver de Chrome inicializado correctamente (MODO VISIBLE)")
            return self.driver
            
        except WebDriverException as e:
            logger.error(f"Error al inicializar el WebDriver: {e}")
            raise

            
    def close_driver(self) -> None:
        """
        Cierra el navegador y libera recursos.
        
        Este método debe llamarse siempre al finalizar las operaciones
        para liberar recursos del sistema.
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver cerrado correctamente")
            except Exception as e:
                logger.warning(f"Error al cerrar el WebDriver: {e}")
            finally:
                self.driver = None
                
    def wait_for_element(self, by: By, value: str, timeout: int = 10) -> bool:
        """
        Espera hasta que un elemento esté presente en la página.
        
        Args:
            by: Método de localización (By.ID, By.XPATH, etc.)
            value: Valor del localizador
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            bool: True si el elemento se encontró dentro del tiempo límite, False en caso contrario
        """
        try:
            if not self.driver:
                logger.error("WebDriver no inicializado")
                return False
                
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            logger.warning(f"Tiempo de espera agotado al buscar elemento {by}={value}")
            return False
        except Exception as e:
            logger.error(f"Error al esperar elemento {by}={value}: {e}")
            return False


class GCSManager:
    """
    Clase para gestionar las operaciones en Google Cloud Storage.
    
    Maneja la conexión con GCS, la eliminación y subida de archivos.
    """
    
    def __init__(self, config: SicoeConfig):
        """
        Inicializa el gestor de Google Cloud Storage.
        
        Args:
            config: Objeto de configuración de SICOE
            
        Raises:
            Exception: Si hay un problema con las credenciales o la inicialización del cliente
        """
        self.config = config
        self.credentials = self._get_credentials()
        self.client = None
        self._initialize_client()
        
    def _get_credentials(self) -> service_account.Credentials:
        """
        Obtiene las credenciales de Google Cloud Storage.
        
        Returns:
            Objeto de credenciales para la autenticación con GCS
            
        Raises:
            Exception: Si hay un problema al obtener las credenciales
        """
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.config.credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            logger.debug("Credenciales de GCS obtenidas correctamente")
            return credentials
        except Exception as e:
            logger.error(f"Error al obtener las credenciales de GCS: {e}")
            raise
            
    def _initialize_client(self) -> None:
        """
        Inicializa el cliente de Google Cloud Storage.
        
        Raises:
            Exception: Si hay un problema al inicializar el cliente
        """
        try:
            self.client = storage.Client(credentials=self.credentials)
            logger.debug("Cliente de GCS inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar el cliente de GCS: {e}")
            raise
    
    def eliminar_archivos(self, prefix: str) -> int:
        """
        Elimina todos los archivos en una ruta específica del bucket GCS.
        
        Args:
            prefix: Prefijo/ruta en el bucket donde se eliminarán los archivos
            
        Returns:
            int: Cantidad de archivos eliminados
            
        Raises:
            Exception: Si hay un problema al eliminar los archivos
        """
        try:
            bucket = self.client.bucket(self.config.bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            count = 0
            
            for blob in blobs:
                blob.delete()
                count += 1
                logger.info(f"Archivo eliminado: {blob.name}")
            
            logger.info(f"Total de archivos eliminados en {prefix}: {count}")
            return count
        except Exception as e:
            logger.error(f"Error al eliminar archivos de GCS en {prefix}: {e}")
            raise
            
    def eliminar_archivos_facture(self) -> int:
        """
        Elimina archivos de facturación del bucket.
        
        Returns:
            int: Cantidad de archivos eliminados
        """
        return self.eliminar_archivos(self.config.destination_prefix_facture)
        
    def eliminar_archivos_detallado(self) -> int:
        """
        Elimina archivos detallados del bucket.
        
        Returns:
            int: Cantidad de archivos eliminados
        """
        return self.eliminar_archivos(self.config.destination_prefix)

    def subir_archivos(self, file_pattern: str, destination_prefix: str) -> int:
        """
        Busca archivos que coincidan con un patrón y los sube a GCS.
        
        Args:
            file_pattern: Patrón para buscar archivos
            destination_prefix: Prefijo/ruta en el bucket donde se subirán los archivos
            
        Returns:
            int: Cantidad de archivos subidos
            
        Raises:
            Exception: Si hay un problema al subir los archivos
        """
        try:
            bucket = self.client.bucket(self.config.bucket_name)
            patron_path = os.path.join(self.config.base_dir, "**", file_pattern)
            archivos_encontrados = glob.glob(patron_path, recursive=True)
            
            if not archivos_encontrados:
                logger.warning(f"No se encontraron archivos que coincidan con el patrón: {file_pattern}")
                return 0
            
            count = 0
            for ruta_archivo in archivos_encontrados:
                if os.path.isfile(ruta_archivo):
                    nombre_archivo = os.path.basename(ruta_archivo)
                    destination_blob_name = f"{destination_prefix}{nombre_archivo}"
                    
                    blob = bucket.blob(destination_blob_name)
                    blob.upload_from_filename(ruta_archivo)
                    
                    count += 1
                    logger.info(f"Archivo subido: {ruta_archivo} -> gs://{self.config.bucket_name}/{destination_blob_name}")
            
            logger.info(f"Total de archivos subidos a {destination_prefix}: {count}")
            return count
        except Exception as e:
            logger.error(f"Error al subir archivos a GCS en {destination_prefix}: {e}")
            raise
            
    def subir_archivos_facture(self) -> int:
        """
        Sube archivos de facturación al bucket.
        
        Returns:
            int: Cantidad de archivos subidos
        """
        return self.subir_archivos(
            self.config.file_pattern_facture, 
            self.config.destination_prefix_facture
        )
        
    def subir_archivos_detallado(self) -> int:
        """
        Sube archivos detallados al bucket.
        
        Returns:
            int: Cantidad de archivos subidos
        """
        return self.subir_archivos(
            self.config.file_pattern, 
            self.config.destination_prefix
        )
    

class SicoeAutomation:
    """
    Clase principal para automatizar las operaciones en SICOE.
    
    Maneja el inicio de sesión, la navegación, la descarga de reportes
    y la gestión de archivos locales.
    """
    
    def __init__(self, config: SicoeConfig):
        """
        Inicializa la automatización de SICOE.
        
        Args:
            config: Objeto de configuración de SICOE
        """
        self.config = config
        self.driver_manager = WebDriverManager(config)
    
    def login(self, driver: webdriver.Chrome) -> bool:
        """
        Realiza el inicio de sesión en el portal SICOE.
        
        Args:
            driver: Instancia del WebDriver
            
        Returns:
            bool: True si el inicio de sesión fue exitoso, False en caso contrario
        """
        try:
            driver.get(self.config.login_url)
            
            # Esperar a que la página se cargue
            if not self.driver_manager.wait_for_element(By.ID, "nit", timeout=15):
                return False
            
            # Completar los campos de inicio de sesión
            driver.find_element(By.ID, "nit").send_keys(self.config.nit)
            driver.find_element(By.ID, "login").send_keys(self.config.username)
            driver.find_element(By.ID, "passwd").send_keys(self.config.password)
            
            # Marcar la casilla de verificación y hacer clic en el botón de inicio de sesión
            driver.find_element(By.XPATH, '//*[@id="form"]/div[3]/input').click()
            driver.find_element(By.XPATH, '//*[@id="form"]/div[4]/button').click()
            
            # Esperar a que la página cargue después del inicio de sesión
            if not self.driver_manager.wait_for_element(
                By.XPATH, '//*[@id="dock"]/ul/li[1]/a/img', timeout=30
            ):
                return False
            
            logger.info("Inicio de sesión exitoso")
            return True
        except Exception as e:
            logger.error(f"Error durante el inicio de sesión: {e}")
            return False
    
    def navigate_to_report(self, driver: webdriver.Chrome, report_type: str) -> bool:
        """
        Navega a la sección de reportes y selecciona el reporte deseado.
        
        Args:
            driver: Instancia del WebDriver
            report_type: Tipo de reporte ('detallado' o 'facturas')
            
        Returns:
            bool: True si la navegación fue exitosa, False en caso contrario
        """
        try:
            # Hacer clic en el botón de informes
            reports_button = driver.find_element(By.XPATH, '//*[@id="dock"]/ul/li[1]/a/img')
            
            reports_button.click()
            
            # Esperar a que se cargue la sección de informes
            if not self.driver_manager.wait_for_element(
                By.XPATH, '//*[@id="step-1"]/table/tbody/tr[2]/td[1]/a'
            ):
                return False
        
            # Seleccionar el informe según el tipo
            if report_type == 'facturas':
                xpath = '//*[@id="step-1"]/table/tbody/tr[1]/td[1]/a'
                logger.info("Seleccionando informe de listado de facturas")
            else:  # detallado
                xpath = '//*[@id="step-1"]/table/tbody/tr[2]/td[1]/a'
                logger.info("Seleccionando informe detallado por facturas")
            
            driver.find_element(By.XPATH, xpath).click()
            logger.info(f"Navegación a la sección de informes {report_type} exitosa")
            return True
        except Exception as e:
            logger.error(f"Error al navegar a la sección de informes {report_type}: {e}")
            return False
    
    def set_date_value(self, driver: webdriver.Chrome, field_id: str, date_value: str) -> bool:
        """
        Establece un valor de fecha en un campo de datepicker de solo lectura.
        
        Args:
            driver: Instancia del WebDriver
            field_id: ID del campo de fecha
            date_value: Valor de fecha a establecer (formato YYYY-MM-DD)
            
        Returns:
            bool: True si se estableció el valor correctamente, False en caso contrario
        """
        try:
            date_field = driver.find_element(By.ID, field_id)
            
            # Establecer el valor de fecha utilizando JavaScript
            js_script = """
                // Establecer el valor directamente
                arguments[0].value = arguments[1];
                
                // Disparar evento de cambio para asegurar que se actualice la validación
                var event = new Event('change', { bubbles: true });
                arguments[0].dispatchEvent(event);
                
                // También disparar el evento de cambio del datepicker si es necesario
                try {
                    if (typeof jQuery !== 'undefined') {
                        jQuery(arguments[0]).datepicker('setDate', arguments[1]);
                    }
                } catch (e) {
                    console.log('Error triggering datepicker:', e);
                }
            """
            driver.execute_script(js_script, date_field, date_value)
            
            logger.debug(f"Valor de fecha establecido para {field_id}: {date_value}")
            return True
        except Exception as e:
            logger.error(f"Error al establecer el valor de fecha para {field_id}: {e}")
            return False
    
    def click_excel_button(self, driver: webdriver.Chrome, wait_time: int = 3) -> bool:
        """
        Hace clic en el botón 'Imprimir Excel' en el formulario modal.
        
        Args:
            driver: Instancia del WebDriver
            wait_time: Tiempo de espera después del clic en segundos
            
        Returns:
            bool: True si se hizo clic correctamente, False en caso contrario
        """
        try:
            excel_button = driver.find_element(By.ID, "excel")
            excel_button.click()
            logger.info("Clic en el botón Excel realizado")
            time.sleep(wait_time)
            return True
        except Exception as e:
            logger.error(f"Error al hacer clic en el botón Excel: {e}")
            return False
    
    def handle_report_form(
        self, 
        driver: webdriver.Chrome, 
        form_type: str,
        report_type: Optional[str] = None
    ) -> bool:
        """
        Maneja el formulario modal de informe y establece los rangos de fechas.
        
        Args:
            driver: Instancia del WebDriver
            form_type: Tipo de formulario ('detallado' o 'facturas')
            report_type: Tipo de informe a generar ('cambio' o None para ventas normales)
            
        Returns:
            bool: True si se manejó el formulario correctamente, False en caso contrario
        """
        try:
            # Esperar y cambiar al iframe
            time.sleep(1)
            WebDriverWait(driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "sb-player"))
            )
            
            # Configurar campos de fecha según el tipo de formulario
            if form_type == 'facturas':
                fecha_ini = "fecha_ini"
                fecha_fin = "fecha_fin"
            else:  # detallado
                fecha_ini = "fecha_ini_factura"
                fecha_fin = "fecha_fin_factura"
            
            # Esperar a que los campos de fecha estén presentes
            if not self.driver_manager.wait_for_element(By.ID, fecha_ini):
                return False
            
            # Obtener rango de fechas del mes actual
            first_day_str, last_day_str = self.config.get_date_range()
            
            # Establecer los valores de fecha
            self.set_date_value(driver, fecha_ini, first_day_str)
            self.set_date_value(driver, fecha_fin, last_day_str)
            
            # Si es un informe de tipo "cambio", seleccionar la opción "C"
            if report_type == 'cambio' and form_type == 'detallado':
                logger.info("Configurando informe de tipo CAMBIO")
                select_element = driver.find_element(By.ID, "id_tipo_producto")
                select = Select(select_element)
                select.select_by_value("C")
                logger.info("Tipo de producto CAMBIO seleccionado correctamente")
            
            # Esperar a que se carguen los datos
            time.sleep(self.config.wait_time_standard)
            
            # Hacer clic en el botón Excel
            if not self.click_excel_button(driver):
                return False
            
            # Si es un informe de ventas normales, esperar más tiempo para la descarga
            if not report_type:
                time.sleep(self.config.download_wait_time)
            
            # Volver al contenido predeterminado
            driver.switch_to.default_content()
            
            logger.info(f"Manejo del formulario de informe {form_type} completado correctamente")
            return True
        except TimeoutException:
            logger.error(f"Tiempo de espera agotado al esperar el modal o los campos de fecha en {form_type}")
            return False
        except Exception as e:
            logger.error(f"Error al manejar el formulario de informe {form_type}: {e}")
            return False
    
    def run_process(self, report_form: str, report_type: Optional[str] = None) -> bool:
        """
        Ejecuta el proceso completo para generar un informe.
        
        Args:
            report_form: Tipo de formulario de informe ('detallado' o 'facturas')
            report_type: Tipo de informe a generar ('cambio' o None para ventas normales)
            
        Returns:
            bool: True si el proceso fue exitoso, False en caso contrario
        """
        driver = None
        try:
            # Inicializar el WebDriver
            driver = self.driver_manager.initialize_driver()
            
            # Realizar el inicio de sesión
            if not self.login(driver):
                logger.error("Fallo en el proceso de inicio de sesión")
                return False
            
            # Navegar a la sección de informes
            if not self.navigate_to_report(driver, report_form):
                logger.error(f"Fallo en la navegación al reporte {report_form}")
                return False
            
            # Manejar el formulario de informe
            if not self.handle_report_form(driver, report_form, report_type):
                logger.error(f"Fallo en el manejo del formulario {report_form}")
                return False
            
            logger.info(f"Proceso de informe {report_type or 'NORMAL'} de {report_form} completado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error en el proceso de informe {report_form}: {e}")
            return False
        finally:
            # Cerrar el navegador
            if driver:
                self.driver_manager.close_driver()

    def eliminar_archivos_locales(self, file_pattern: str) -> int:
        """
        Elimina todos los archivos locales que coinciden con el patrón especificado.
        
        Args:
            file_pattern: Patrón para buscar archivos
            
        Returns:
            int: Cantidad de archivos eliminados
            
        Raises:
            Exception: Si hay un problema al eliminar los archivos
        """
        try:
            # Buscar archivos que coincidan con el patrón
            patron_path = os.path.join(self.config.base_dir, "**", file_pattern)
            archivos_encontrados = glob.glob(patron_path, recursive=True)
            
            if not archivos_encontrados:
                logger.warning(f"No se encontraron archivos locales que coincidan con el patrón: {file_pattern}")
                return 0
            
            # Eliminar archivos encontrados
            count = 0
            for ruta_archivo in archivos_encontrados:
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
                    count += 1
                    logger.info(f"Archivo local eliminado: {ruta_archivo}")
            
            logger.info(f"Total de archivos locales eliminados: {count}")
            return count
        except Exception as e:
            logger.error(f"Error al eliminar archivos locales: {e}")
            raise

    def eliminar_archivos_locales_detallado(self) -> int:
        """
        Elimina todos los archivos locales de tipo detallado.
        
        Returns:
            int: Cantidad de archivos eliminados
        """
        return self.eliminar_archivos_locales(self.config.file_pattern)

    def eliminar_archivos_locales_facture(self) -> int:
        """
        Elimina todos los archivos locales de tipo factura.
        
        Returns:
            int: Cantidad de archivos eliminados
        """
        return self.eliminar_archivos_locales(self.config.file_pattern_facture)


def main():
    """
    Función principal del script.
    
    Ejecuta la secuencia completa de operaciones para la extracción
    y carga de datos.
    
    Returns:
        int: 0 si el proceso fue exitoso, 1 en caso de error
    """
    try:
        logger.info("=== Iniciando proceso de automatización SICOE ===")
        
        # Configurar dependencias y credenciales
        logger.info("📦 Configurando dependencias...")
        # Comentar temporalmente si las librerías ya están instaladas
        # if not setup_requirements():
        #     logger.error("No se pudieron instalar las dependencias")
        #     return 1
        
        # Verificar imports críticos
        try:
            from selenium import webdriver
            from google.cloud import storage
            logger.info("✅ Dependencias principales verificadas")
        except ImportError as e:
            logger.error(f"❌ Falta una dependencia crítica: {e}")
            logger.info("Ejecuta: pip install selenium webdriver_manager google-cloud-storage pandas beautifulsoup4")
            return 1
        
        logger.info("🔐 Configurando credenciales...")
        credentials_path = setup_credentials_directory()
        if not credentials_path:
            logger.error("No se pudieron configurar las credenciales")
            return 1
        
        # Crear configuración
        config = SicoeConfig()
        # Cargar configuración desde variables de entorno si están disponibles
        config.load_from_env()
        
        # Crear instancias
        sicoe = SicoeAutomation(config)
        gcs_manager = GCSManager(config)
        
        # Ejecutar procesos de informe detallado
        logger.info("=== Iniciando proceso de informe de CAMBIOS ===")
        sicoe.run_process(report_form='detallado', report_type='cambio')
        
        logger.info("=== Iniciando proceso de informe de VENTAS NORMALES ===")
        sicoe.run_process(report_form='detallado', report_type=None)

        # Ejecutar proceso de informe de facturas
        logger.info("=== Iniciando proceso de informe de listado de facturas ===")
        sicoe.run_process(report_form='facturas', report_type=None)
        
        # Gestionar archivos en GCS - Informes detallados
        logger.info("=== Iniciando eliminación de archivos detallados en GCS ===")
        gcs_manager.eliminar_archivos_detallado()
        
        logger.info("=== Iniciando subida de archivos detallados a GCS ===")
        gcs_manager.subir_archivos_detallado()

        # Gestionar archivos en GCS - Informes de facturas
        logger.info("=== Iniciando eliminación de archivos de facturas en GCS ===")
        gcs_manager.eliminar_archivos_facture()

        logger.info("=== Iniciando subida de archivos de facturas a GCS ===")
        gcs_manager.subir_archivos_facture()
        
        # Eliminar archivos locales después de subirlos a GCS
        logger.info("=== Eliminando archivos locales detallados ===")
        sicoe.eliminar_archivos_locales_detallado()
        
        logger.info("=== Eliminando archivos locales de facturas ===")
        sicoe.eliminar_archivos_locales_facture()

        logger.info("=== Proceso de automatización SICOE completado exitosamente ===")
        return 0  # Código de salida exitoso
    except Exception as e:
        logger.error(f"Error crítico en el proceso principal: {e}", exc_info=True)
        return 1  # Código de salida con error
    finally:
        logger.info("=== Finalizando proceso de automatización SICOE ===")
        


if __name__ == "__main__":
    # Configurar nivel de log desde variables de entorno
    if os.environ.get('DEBUG_MODE') == 'true':
        logging.getLogger("SICOE_Automation").setLevel(logging.DEBUG)
        
    # Añadir manejo de señales para terminar correctamente
    try:
        import signal
        def signal_handler(sig, frame):
            logger.info("Proceso interrumpido por el usuario. Finalizando...")
            return 1
        signal.signal(signal.SIGINT, signal_handler)
    except (ImportError, AttributeError):
        # En algunos sistemas puede no estar disponible
        pass
        
    try:
        # Ejecutar el proceso principal
        result = main()
        
        # Mostrar resultado final
        if result == 0:
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        else:
            print("❌ PROCESO TERMINÓ CON ERRORES")
            
    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por el usuario")
        print("❌ Proceso interrumpido por el usuario")
    except Exception as e:
        logger.critical(f"Error no manejado: {e}", exc_info=True)
        print("❌ Error crítico en el proceso")