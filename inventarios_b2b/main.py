pip install selenium beautifulsoup4 pandas webdriver_manager

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import os
import re
import glob
import pandas as pd
from google.oauth2 import service_account


class MakroAutomation:
    """Clase para automatizar el proceso de obtención de reportes desde el portal B2B de Makro."""
    
    def __init__(self, credentials_file="credentials.txt"):
        """Inicializa la automatización de Makro.
        
        Args:
            credentials_file (str): Ruta al archivo que contiene las credenciales.
                                   El archivo debe tener el formato:
                                   username=usuario@ejemplo.com
                                   password=contraseña
        """
        self.credentials_file = credentials_file
        self.username, self.password = self._load_credentials()
        self.driver = None
        self.main_window = None
        
        # Ejecutar la secuencia de automatización
        self.run_automation()
        
    def _load_credentials(self):
        """Carga las credenciales desde un archivo de texto.
        
        Returns:
            tuple: (username, password) leídos del archivo.
            
        Raises:
            FileNotFoundError: Si el archivo de credenciales no existe.
            ValueError: Si el formato del archivo es incorrecto.
        """
        try:
            username = None
            password = None
            
            with open(self.credentials_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('username='):
                        username = line.split('=', 1)[1]
                    elif line.startswith('password='):
                        password = line.split('=', 1)[1]
            
            if not username or not password:
                raise ValueError(f"Formato incorrecto en el archivo {self.credentials_file}. " 
                                "Debe contener líneas con 'username=' y 'password='")
                
            print(f"-->Credenciales cargadas exitosamente desde {self.credentials_file}")
            return username, password
            
        except FileNotFoundError:
            print(f"ERROR: Archivo de credenciales '{self.credentials_file}' no encontrado.")
            print("Usando credenciales predeterminadas para propósitos de desarrollo.")
            # Valores predeterminados como fallback (solo para desarrollo)
            return "grandessuperficies@donchicharron.com.co", "Pilar2025"
        except Exception as e:
            print(f"ERROR al cargar credenciales: {e}")
            print("Usando credenciales predeterminadas para propósitos de desarrollo.")
            # Valores predeterminados como fallback (solo para desarrollo)
            return "grandessuperficies@donchicharron.com.co", "Pilar2025"
        
    def initialize_driver(self):
        """Initialize and configure the Edge webdriver."""
        self.driver = webdriver.Chrome()  # O Firefox, Edge, etc.
        self.driver.implicitly_wait(10)
        return self.driver
    
    def login(self):
        """Realiza el inicio de sesión en el portal B2B de Makro."""
        try:
            self.driver.get("https://b2b.makro.com/")
            
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "usernameField"))
            )
            
            username_field.click()
            username_field.clear()
            print("-->Inicio de sesion")
            username_field.send_keys(self.username)
            
            pass_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "passwordField"))
            )
            pass_field.click()
            pass_field.send_keys(self.password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@message='FND_SSO_LOGIN']")
            login_button.click()
            
            # Esperar a que la página cargue después del login
            time.sleep(3)
            return True
            
        except TimeoutException:
            print("Tiempo de espera agotado durante el inicio de sesión.")
            return False
        except Exception as e:
            print(f"Error durante el inicio de sesión: {e}")
            return False
    
    def navigate_to_isupplier(self):
        """Navega a la sección ISUPPLIER VENDOR COMMERCIAL."""
        try:
            isupplier_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='textdivresp' and text()='ISUPPLIER VENDOR COMMERCIAL']"))
            )
            print("-->Botón 'ISUPPLIER VENDOR COMMERCIAL' encontrado por texto exacto")
            isupplier_button.click()
            print("-->Botón 'ISUPPLIER VENDOR COMMERCIAL' clickeado1")
            
            # Esperar a que la página cargue
            time.sleep(3)
            return True
            
        except TimeoutException:
            print("Tiempo de espera agotado al buscar ISUPPLIER VENDOR COMMERCIAL.")
            return False
        except Exception as e:
            print(f"Error al navegar a ISUPPLIER: {e}")
            return False
    
    def navigate_to_commercial(self):
        """Navega a la sección Commercial."""
        try:
            commercial_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "MAKRO_POS_COMMERCIAL"))
            )
            print("-->Botón 'Commercial' encontrado por ID")
            commercial_button.click()
            
            # Esperar a que la página cargue
            time.sleep(5)
            return True
            
        except TimeoutException:
            print("No se pudo encontrar el botón 'Commercial'")
            return False
        except Exception as e:
            print(f"Error al navegar a Commercial: {e}")
            return False
    
    def navigate_to_stock_po_sales(self):
        """Navega al reporte de Stock and PO and Sales."""
        try:
            stock_po_sales_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "STOCKPOSALES"))
            )
            print("-->Botón 'Stock and PO and Sales report' encontrado por ID")
            stock_po_sales_button.click()
            
            # Esperar a que la nueva ventana se abra
            time.sleep(10)
            return True
            
        except TimeoutException:
            print("No se pudo encontrar el botón 'Stock and PO and Sales report'")
            return False
        except Exception as e:
            print(f"Error al navegar a Stock PO Sales: {e}")
            return False
    
    def switch_to_report_window(self):
        """Cambia el foco a la ventana del reporte."""
        try:
            self.main_window = self.driver.current_window_handle
            
            all_windows = self.driver.window_handles
            for window in all_windows:
                if window != self.main_window:
                    self.driver.switch_to.window(window)
                    print("-->Cambiado a la nueva ventana del reporte")
                    return True
            
            print("No se encontró una nueva ventana.")
            return False
            
        except Exception as e:
            print(f"Error al cambiar a la ventana del reporte: {e}")
            return False
    
    def configure_report_parameters(self, start_date="01/04/2025", end_date="30/04/2025"):
        """Configura los parámetros del reporte.
        
        Args:
            start_date (str): Fecha de inicio en formato DD/MM/YYYY.
            end_date (str): Fecha de fin en formato DD/MM/YYYY.
        """
        try:
            # Configurar fecha de inicio
            begin_date_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "_paramsPM_BEGIN_DATE"))
            )
            print("-->Campo de fecha de inicio encontrado")
            
            begin_date_field.clear()
            begin_date_field.send_keys(start_date)
            print(f"-->Fecha de inicio ingresada: {start_date}")
            
            # Configurar fecha de fin
            end_date_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "_paramsPM_END_DATE"))
            )
            end_date_field.clear()
            end_date_field.send_keys(end_date)
            print(f"-->Fecha final ingresada: {end_date}")
            
            # Configurar "Totalizar tiendas"
            self._select_dropdown_option(
                dropdown_id="xdo:xdo:_paramsPM_SUM_LOCATIONS_div_input",
                option_xpath="//li[contains(@id, '_paramsPM_SUM_LOCATIONS_div_li') and .//div[text()='No']]",
                dropdown_name="Totalizar tiendas"
            )
            
            # Configurar "Mostrar total empresa"
            self._select_dropdown_option(
                dropdown_id="xdo:xdo:_paramsPM_SHOW_TOTAL_COMPANY_div_input",
                option_xpath="//li[contains(@id, '_paramsPM_SHOW_TOTAL_COMPANY_div_li') and .//div[text()='No']]",
                dropdown_name="Mostrar total empresa"
            )
            
            # Aplicar cambios
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "reportViewApply"))
            )
            apply_button.click()
            print("-->Botón 'Aplicar' presionado")
            
            # Esperar a que el reporte se genere
            return True
            
        except TimeoutException as e:
            print(f"Error al interactuar con el formulario de fechas: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado en configuración de parámetros: {e}")
            return False
    
    def _select_dropdown_option(self, dropdown_id, option_xpath, dropdown_name):
        """Selecciona una opción de un dropdown.
        
        Args:
            dropdown_id (str): ID del elemento dropdown.
            option_xpath (str): XPath de la opción a seleccionar.
            dropdown_name (str): Nombre descriptivo del dropdown (para logs).
        """
        time.sleep(25)
        dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, dropdown_id))
        )
        dropdown.click()
        print(f"-->Dropdown '{dropdown_name}' abierto")
        
        # Pequeña pausa para que se despliegue el dropdown
        time.sleep(1)
        
        no_option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        no_option.click()
        print(f"-->Opción 'No' seleccionada para '{dropdown_name}'")
    
    def download_excel_report(self):
        """Descarga el reporte en formato Excel."""
        try:
            print("-->Esperando que el reporte se genere")
            time.sleep(45)
            # Hacer clic en "Ver Informe"
            view_report_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "xdo:viewFormatLink"))
            )
            view_report_link.click()
            print("-->Enlace 'Ver Informe' presionado")
            time.sleep(5)
            
            # Intentar seleccionar la opción Excel por texto
            try:
                excel_option = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'floatMenu') and contains(@style, 'display: block')]//div[contains(@class, 'itemTxt') and text()='Excel (*.xlsx)']"))
                )
                excel_option.click()
                print("-->Opción 'Excel (*.xlsx)' seleccionada mediante texto")
            except TimeoutException:
                # Método alternativo si el primero falla
                visible_menu = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'floatMenu') and contains(@style, 'display: block')]"))
                )
                excel_menu_item = visible_menu.find_element(By.XPATH, ".//li[@fmid='3' or @fmid='102']")
                excel_link = excel_menu_item.find_element(By.TAG_NAME, "a")
                excel_link.click()
                print("Opción 'Excel (*.xlsx)' seleccionada mediante fmid")
            
            print("-->Esperando que el archivo empiece a cargar en pantalla")   
            time.sleep(25)
            print("-->Descarga del archivo Excel iniciada")
            return True
            
        except Exception as e:
            print(f"Error al seleccionar la opción de descarga: {e}")
            return False
    
    def run_automation(self):
        """Ejecuta la secuencia completa de automatización."""
        try:
            self.initialize_driver()
    
            if not self.login():
                raise Exception("Fallo en el inicio de sesión")
            
            if not self.navigate_to_isupplier():
                raise Exception("Fallo en la navegación a ISUPPLIER")
            
            if not self.navigate_to_commercial():
                raise Exception("Fallo en la navegación a Commercial")
            
            if not self.navigate_to_stock_po_sales():
                raise Exception("Fallo en la navegación a Stock PO Sales")
            
            if not self.switch_to_report_window():
                raise Exception("Fallo al cambiar a la ventana del reporte")
            
            # Configurar parámetros del reporte
            if not self.configure_report_parameters():
                raise Exception("Fallo en la configuración de parámetros")
            
            # Descargar reporte en Excel
            if not self.download_excel_report():
                raise Exception("Fallo en la descarga del reporte")
            
            print("-->Automatización completada exitosamente")
            
        except Exception as e:
            print(f"Error durante la automatización: {e}")
        finally:
            # No cerramos el driver automáticamente para mantener el comportamiento original
            pass
    
    def close(self):
        if __name__ == "__main__":
            automation = MakroAutomation()
            automation.close()