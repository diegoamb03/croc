📄 SICOE Web Scraping - Documentación
markdown# SICOE Web Scraping Automation

Script automatizado con arquitectura modular para extraer reportes desde el portal SICOE (Sistema de Información Comercial) y sincronizarlos con Google Cloud Storage.

## 📋 Descripción

Este script de Python utiliza Selenium y programación orientada a objetos con arquitectura modular para automatizar el proceso completo de:
- Login en el portal SICOE
- Generación de reportes detallados (Ventas normales y Cambios)
- Generación de reportes de facturas diarias
- Configuración automática de rangos de fecha (mes actual)
- Subida automática a Google Cloud Storage
- Limpieza de archivos locales y remotos
- Sistema de logging robusto con rotación de archivos

## ✨ Características

- ✅ **Arquitectura Modular**: 4 clases especializadas con responsabilidades únicas
- ✅ **Configuración Centralizada**: Clase `SicoeConfig` para toda la configuración
- ✅ **Logging Avanzado**: Sistema de logs con archivos y consola simultáneos
- ✅ **Variables de Entorno**: Soporte completo para configuración externa
- ✅ **Rango de Fechas Automático**: Selección del mes completo actual
- ✅ **Múltiples Tipos de Reporte**: Detallado (ventas/cambios) y Facturas
- ✅ **Manejo Robusto de Iframes**: Navegación en modales complejos
- ✅ **JavaScript Injection**: Manipulación de datepickers de solo lectura
- ✅ **Gestión Completa del Ciclo de Vida**: Limpieza automática local y remota
- ✅ **Manejo de Señales**: Terminación correcta con Ctrl+C
- ✅ **Códigos de Salida**: Integración con pipelines de CI/CD

## 🏗️ Arquitectura

### Diagrama de Clases
```
┌─────────────────┐
│  SicoeConfig    │ ← Configuración centralizada
└────────┬────────┘
         │
    ┌────▼────┐
    │  main() │ ← Función orquestadora
    └────┬────┘
         │
    ┌────▼──────────────────────────────────┐
    │                                        │
┌───▼────────────┐  ┌──────────────┐  ┌────▼──────┐
│ SicoeAutomation│  │ GCSManager   │  │WebDriver  │
│                │  │              │  │Manager    │
├────────────────┤  ├──────────────┤  ├───────────┤
│ • login()      │  │ • upload()   │  │ • init()  │
│ • navigate()   │  │ • delete()   │  │ • close() │
│ • download()   │  │ • verify()   │  │ • wait()  │
└────────────────┘  └──────────────┘  └───────────┘
```

### Flujo de Datos
```
Config → WebDriver → SICOE Login → Reportes → Descargas Locales
                                                      ↓
Config → GCS Manager ← Upload ← Archivos Clasificados
                ↓
          Clean Local + Remote Files
```

## 🔧 Requisitos Previos

### Software Necesario
- Python 3.8 o superior
- Google Chrome (versión actualizada)
- Cuenta de Google Cloud Platform con permisos de Storage
- Acceso al portal SICOE

### Dependencias Python
```bash
selenium>=4.0.0
webdriver-manager>=4.0.0
google-cloud-storage>=2.0.0
google-auth>=2.0.0
```

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone 
cd sicoe-scraping
```

### 2. Crear estructura de directorios
```bash
mkdir -p credentials
mkdir -p logs
mkdir -p "C:\Users\Diego Mendez\Documents\Web Scaping\Sicoe\descargas"  # Windows
# O para Linux/Mac:
# mkdir -p ~/Downloads/Sicoe/descargas
```

### 3. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar credenciales de Google Cloud
- Descargar el archivo JSON de credenciales desde Google Cloud Console
- Colocar el archivo en `credentials/`
- Actualizar la variable `credentials_path` si es necesario

## ⚙️ Configuración

### Clase SicoeConfig - Parámetros
```python
class SicoeConfig:
    def __init__(
        self,
        # Autenticación SICOE
        login_url: str = "https://sicoe.com.co/sicoe/dist/#/login",
        nit: str = "8301256101",
        username: str = "analistadatos",
        password: str = "tu_password",
        
        # Google Cloud Storage
        bucket_name: str = "bucket-quickstart_croc_830",
        credentials_path: str = "credentials/archivo.json",
        
        # Rutas en GCS
        destination_prefix: str = "raw/Ventas/sicoe/",
        destination_prefix_facture: str = "raw/Ventas/sicoe_facture_diarias/",
        
        # Directorio local
        download_dir: str = r"C:\Users\...\descargas",
        
        # Patrones de búsqueda
        file_pattern: str = "*detallado*",
        file_pattern_facture: str = "*LISTADO_FACTURAS*",
        
        # Tiempos de espera
        wait_time_standard: int = 8,
        download_wait_time: int = 25
    )
```

### ⚠️ Configuración con Variables de Entorno

**RECOMENDADO**: Usar variables de entorno para credenciales:

#### Crear archivo `.env`
```bash
# Autenticación SICOE
SICOE_NIT=8301256101
SICOE_USERNAME=analistadatos
SICOE_PASSWORD=tu_password_seguro

# Google Cloud Storage
GCS_BUCKET_NAME=tu-bucket
GOOGLE_APPLICATION_CREDENTIALS=credentials/tu-archivo.json

# Configuración adicional
SICOE_LOGIN_URL=https://sicoe.com.co/sicoe/dist/#/login
DOWNLOAD_DIR=C:\ruta\descargas

# Modo debug
DEBUG_MODE=false
```

#### Uso Programático
```python
from sicoe_automation import SicoeConfig

# Crear configuración con valores por defecto
config = SicoeConfig()

# Cargar desde variables de entorno
config.load_from_env()

# O sobreescribir valores específicos
config.nit = os.getenv('SICOE_NIT')
config.password = os.getenv('SICOE_PASSWORD')
```

### Configuración de Logging
```python
import logging

# Nivel de logging por defecto: INFO
# Para debugging, usar variable de entorno:
# DEBUG_MODE=true python sicoe_automation.py

# Archivos de log se crean en:
# - sicoe_automation.log (archivo persistente)
# - Consola (output en tiempo real)
```

## 🚀 Uso

### Ejecución Básica
```bash
python sicoe_automation.py
```

### Ejecución con Debug
```bash
DEBUG_MODE=true python sicoe_automation.py
```

### Uso Programático
```python
from sicoe_automation import (
    SicoeConfig, 
    SicoeAutomation, 
    GCSManager, 
    WebDriverManager
)

# 1. Configuración
config = SicoeConfig(
    nit="tu_nit",
    username="tu_usuario",
    password="tu_password",
    download_dir="/ruta/descargas"
)

# 2. Crear instancias
sicoe = SicoeAutomation(config)
gcs_manager = GCSManager(config)

# 3. Ejecutar procesos individuales
sicoe.run_process(report_form='detallado', report_type='cambio')
sicoe.run_process(report_form='detallado', report_type=None)  # Ventas normales
sicoe.run_process(report_form='facturas', report_type=None)

# 4. Gestionar archivos en GCS
gcs_manager.eliminar_archivos_detallado()
gcs_manager.subir_archivos_detallado()

# 5. Limpiar archivos locales
sicoe.eliminar_archivos_locales_detallado()
```

### Ejecución en Contenedor Docker
```dockerfile
FROM python:3.9-slim

# Instalar Chrome y dependencias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "sicoe_automation.py"]
```

## 📁 Estructura del Proyecto
```
sicoe-scraping/
├── sicoe_automation.py           # Script principal
├── credentials/
│   └── archivo-credenciales.json   # Credenciales GCS (no incluir en git)
├── logs/
│   └── sicoe_automation.log        # Archivo de logs
├── descargas/                      # Archivos temporales (auto-limpiado)
├── requirements.txt                # Dependencias Python
├── .env                            # Variables de entorno (no incluir en git)
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore                      # Archivos a ignorar
├── README.md                       # Esta documentación
├── CHANGELOG.md                    # Historial de cambios
└── docker-compose.yml              # Configuración Docker (opcional)
```

## 🔄 Flujo del Proceso
```
1. Inicialización
   ├── Crear SicoeConfig
   ├── Cargar variables de entorno
   └── Inicializar logging
   
2. Reporte de CAMBIOS
   ├── Inicializar WebDriver
   ├── Login en SICOE
   ├── Navegar a "Informe detallado por facturas"
   ├── Cambiar a iframe modal
   ├── Configurar rango de fechas (mes actual)
   ├── Seleccionar tipo producto: "C" (Cambio)
   ├── Click en "Imprimir Excel"
   └── Cerrar driver
   
3. Reporte de VENTAS NORMALES
   ├── Inicializar WebDriver
   ├── Login en SICOE
   ├── Navegar a "Informe detallado por facturas"
   ├── Cambiar a iframe modal
   ├── Configurar rango de fechas (mes actual)
   ├── Tipo producto: Default (Ventas)
   ├── Click en "Imprimir Excel"
   ├── Esperar descarga (25 segundos)
   └── Cerrar driver
   
4. Reporte de FACTURAS
   ├── Inicializar WebDriver
   ├── Login en SICOE
   ├── Navegar a "Listado de facturas"
   ├── Cambiar a iframe modal
   ├── Configurar rango de fechas (mes actual)
   ├── Click en "Imprimir Excel"
   └── Cerrar driver
   
5. Sincronización GCS - Archivos Detallados
   ├── Conectar a Google Cloud Storage
   ├── Eliminar archivos existentes en raw/Ventas/sicoe/
   ├── Buscar archivos "*detallado*" en directorio local
   ├── Subir archivos a raw/Ventas/sicoe/
   └── Verificar integridad
   
6. Sincronización GCS - Archivos de Facturas
   ├── Eliminar archivos existentes en raw/Ventas/sicoe_facture_diarias/
   ├── Buscar archivos "*LISTADO_FACTURAS*" en directorio local
   ├── Subir archivos a raw/Ventas/sicoe_facture_diarias/
   └── Verificar integridad
   
7. Limpieza Local
   ├── Eliminar archivos "*detallado*" del directorio local
   ├── Eliminar archivos "*LISTADO_FACTURAS*" del directorio local
   └── Liberar espacio en disco
   
8. Finalización
   ├── Cerrar conexiones
   ├── Escribir logs finales
   └── Retornar código de salida (0=éxito, 1=error)
```

## 🛠️ Clases y Métodos

### Clase SicoeConfig

Gestiona toda la configuración del script.

#### Métodos Principales

##### `__init__(**kwargs)`
Inicializa la configuración con valores por defecto o personalizados.

##### `load_from_env() -> None`
Carga configuración desde variables de entorno.
```python
config = SicoeConfig()
config.load_from_env()  # Sobrescribe con valores de entorno
```

##### `get_date_range() -> Tuple[str, str]`
Obtiene el primer y último día del mes actual.
```python
config = SicoeConfig()
first_day, last_day = config.get_date_range()
# Retorna: ('2024-11-01', '2024-11-30')
```

##### `_create_download_directory() -> None`
Crea el directorio de descargas si no existe (método privado).

---

### Clase WebDriverManager

Gestiona el ciclo de vida del WebDriver.

#### Métodos Principales

##### `__init__(config: SicoeConfig)`
Inicializa el gestor con la configuración.

##### `initialize_driver() -> webdriver.Chrome`
Crea y configura una instancia de Chrome WebDriver.
```python
wdm = WebDriverManager(config)
driver = wdm.initialize_driver()
```

**Opciones configuradas**:
- Directorio de descargas personalizado
- Descargas automáticas sin prompt
- Deshabilitación de GPU para estabilidad
- Ventana maximizada
- No-sandbox mode

##### `close_driver() -> None`
Cierra el navegador y libera recursos.
```python
wdm.close_driver()  # Siempre llamar al finalizar
```

##### `wait_for_element(by: By, value: str, timeout: int = 10) -> bool`
Espera hasta que un elemento esté presente en la página.
```python
if wdm.wait_for_element(By.ID, "login", timeout=15):
    # Elemento encontrado
    pass
```

---

### Clase GCSManager

Gestiona operaciones con Google Cloud Storage.

#### Métodos Principales

##### `__init__(config: SicoeConfig)`
Inicializa el cliente GCS con credenciales.

##### `eliminar_archivos(prefix: str) -> int`
Elimina archivos en una ruta específica del bucket.
```python
gcs = GCSManager(config)
count = gcs.eliminar_archivos("raw/Ventas/sicoe/")
print(f"Eliminados {count} archivos")
```

##### `eliminar_archivos_detallado() -> int`
Elimina archivos detallados del bucket.
```python
count = gcs.eliminar_archivos_detallado()
```

##### `eliminar_archivos_facture() -> int`
Elimina archivos de facturas del bucket.
```python
count = gcs.eliminar_archivos_facture()
```

##### `subir_archivos(file_pattern: str, destination_prefix: str) -> int`
Sube archivos que coincidan con un patrón al bucket.
```python
count = gcs.subir_archivos(
    file_pattern="*detallado*",
    destination_prefix="raw/Ventas/sicoe/"
)
```

##### `subir_archivos_detallado() -> int`
Sube archivos detallados al bucket.

##### `subir_archivos_facture() -> int`
Sube archivos de facturas al bucket.

##### `_get_credentials() -> service_account.Credentials`
Obtiene credenciales de GCS (método privado).

##### `_initialize_client() -> None`
Inicializa el cliente de Storage (método privado).

---

### Clase SicoeAutomation

Automatiza las operaciones en el portal SICOE.

#### Métodos Principales

##### `__init__(config: SicoeConfig)`
Inicializa la automatización con configuración.

##### `login(driver: webdriver.Chrome) -> bool`
Realiza el inicio de sesión en SICOE.
```python
sicoe = SicoeAutomation(config)
driver = wdm.initialize_driver()
if sicoe.login(driver):
    print("Login exitoso")
```

**Pasos**:
1. Navegar a login_url
2. Completar campos: NIT, usuario, contraseña
3. Marcar checkbox de términos
4. Click en botón de login
5. Esperar carga del dashboard

##### `navigate_to_report(driver: webdriver.Chrome, report_type: str) -> bool`
Navega a la sección de reportes.
```python
sicoe.navigate_to_report(driver, 'detallado')
# O
sicoe.navigate_to_report(driver, 'facturas')
```

##### `set_date_value(driver: webdriver.Chrome, field_id: str, date_value: str) -> bool`
Establece valor de fecha en datepicker de solo lectura usando JavaScript.
```python
sicoe.set_date_value(driver, "fecha_ini_factura", "2024-11-01")
```

**Técnica especial**: Inyección de JavaScript para manipular datepickers bloqueados.

##### `click_excel_button(driver: webdriver.Chrome, wait_time: int = 3) -> bool`
Hace clic en el botón "Imprimir Excel".

##### `handle_report_form(driver: webdriver.Chrome, form_type: str, report_type: Optional[str] = None) -> bool`
Maneja el formulario modal completo.
```python
# Para ventas normales
sicoe.handle_report_form(driver, 'detallado', report_type=None)

# Para cambios
sicoe.handle_report_form(driver, 'detallado', report_type='cambio')

# Para facturas
sicoe.handle_report_form(driver, 'facturas', report_type=None)
```

**Pasos**:
1. Cambiar a iframe modal
2. Esperar campos de fecha
3. Obtener rango del mes actual
4. Establecer fechas inicio y fin
5. Seleccionar tipo de producto si es 'cambio'
6. Click en botón Excel
7. Esperar descarga
8. Volver al contenido principal

##### `run_process(report_form: str, report_type: Optional[str] = None) -> bool`
Ejecuta el proceso completo para un reporte.
```python
# Reporte de cambios
sicoe.run_process(report_form='detallado', report_type='cambio')

# Reporte de ventas normales
sicoe.run_process(report_form='detallado', report_type=None)

# Reporte de facturas
sicoe.run_process(report_form='facturas', report_type=None)
```

**Flujo completo**:
- Inicializar WebDriver
- Login
- Navegar al reporte
- Manejar formulario
- Cerrar driver

##### `eliminar_archivos_locales(file_pattern: str) -> int`
Elimina archivos locales que coincidan con el patrón.

##### `eliminar_archivos_locales_detallado() -> int`
Elimina archivos detallados locales.

##### `eliminar_archivos_locales_facture() -> int`
Elimina archivos de facturas locales.

---

### Función main()

Orquesta todo el proceso de automatización.
```python
def main() -> int:
    """
    Retorna:
        0 si exitoso
        1 si hay error
    """
```

**Flujo**:
1. Crear configuración
2. Cargar variables de entorno
3. Crear instancias (SicoeAutomation, GCSManager)
4. Ejecutar reportes
5. Sincronizar con GCS
6. Limpiar archivos locales
7. Retornar código de salida

## 🐛 Troubleshooting

### Error: ChromeDriver incompatible
```bash
✅ Solución:
- Actualizar Chrome: chrome://settings/help
- webdriver-manager descarga automáticamente la versión correcta
- Si persiste: pip install --upgrade webdriver-manager
```

### Error: Login falla constantemente
```bash
✅ Verificar:
- Credenciales correctas en SicoeConfig
- URL de login no ha cambiado
- SICOE no tiene mantenimiento programado
- No hay captcha adicional
- Aumentar timeout en login(): timeout=30
```

### Error: No se encuentra iframe "sb-player"
```bash
❌ Error común: El modal tarda en cargar
✅ Solución:
- Aumentar wait_time_standard en config
- Verificar en navegador manual que el iframe existe
- Revisar XPath del iframe si cambió la estructura
```

### Error: Datepicker no acepta valor
```bash
✅ Implementado: JavaScript injection
- El script usa execute_script para forzar valores
- Si falla, revisar que field_id sea correcto
- Verificar formato de fecha: "YYYY-MM-DD"
```

### Error: Archivos no se descargan
```bash
✅ Verificar:
- download_dir existe y tiene permisos de escritura
- Chrome permite descargas automáticas
- No hay descargas pendientes bloqueadas
- Aumentar download_wait_time a 30-40 segundos
```

### Error: Credenciales GCS inválidas
```bash
✅ Verificar:
- Archivo JSON en credentials/
- Permisos: Storage Object Admin
- GOOGLE_APPLICATION_CREDENTIALS apunta al archivo correcto
- Bucket existe y es accesible

# Test manual:
python -c "from google.cloud import storage; print(storage.Client().list_buckets())"
```

### Error: No se suben archivos a GCS
```bash
✅ Verificar:
- file_pattern coincide con archivos descargados
- Archivos existen en download_dir
- Bucket name es correcto
- Prefijo de destino es válido

# Listar archivos locales:
ls -la /ruta/descargas/*detallado*
```

### Error: Proceso interrumpido sin mensaje
```bash
✅ Revisar:
- sicoe_automation.log para detalles
- Memoria RAM suficiente (Chrome consume ~500MB)
- Timeout en proceso largo (reporte de ventas: 25s)
- Ejecutar con DEBUG_MODE=true
```

### Error: Stale Element Reference
```bash
✅ El script ya maneja esto
- WebDriverManager.wait_for_element re-busca elementos
- Si persiste, agregar más time.sleep() antes de interacciones
```

## 📊 Logs y Monitoreo

### Niveles de Log
```python
# INFO (default): Operaciones principales
2024-11-20 10:15:32 - SICOE_Automation - INFO - Login exitoso

# DEBUG: Información detallada
2024-11-20 10:15:33 - SICOE_Automation - DEBUG - Valor de fecha establecido

# WARNING: Advertencias
2024-11-20 10:15:34 - SICOE_Automation - WARNING - No se encontraron archivos

# ERROR: Errores recuperables
2024-11-20 10:15:35 - SICOE_Automation - ERROR - Error al eliminar archivo

# CRITICAL: Errores críticos
2024-11-20 10:15:36 - SICOE_Automation - CRITICAL - Error no manejado
```

### Archivo de Log
```bash
# Ubicación
./sicoe_automation.log

# Rotar logs manualmente si crece mucho
mv sicoe_automation.log sicoe_automation.log.$(date +%Y%m%d)
```

### Monitoreo en Tiempo Real
```bash
# Ver logs en tiempo real
tail -f sicoe_automation.log

# Filtrar solo errores
tail -f sicoe_automation.log | grep ERROR

# Contar operaciones exitosas
grep "completado exitosamente" sicoe_automation.log | wc -l
```

## 🔐 Seguridad

### Buenas Prácticas Implementadas

- ✅ **Credenciales Externas**: Soporte de variables de entorno
- ✅ **Logging Seguro**: No registra contraseñas en logs
- ✅ **Manejo de Excepciones**: Evita exponer información sensible
- ✅ **Limpieza Automática**: Archivos temporales se eliminan
- ✅ **Credenciales GCS Separadas**: No hardcodeadas en código
- ✅ **Scopes Limitados**: Solo permisos necesarios para GCS

### Checklist de Seguridad

#### Antes de Producción
- [ ] Migrar todas las credenciales a variables de entorno
- [ ] Rotar credenciales de SICOE periódicamente
- [ ] Implementar secrets manager (AWS Secrets, HashiCorp Vault)
- [ ] Agregar autenticación adicional si está disponible
- [ ] Configurar alertas de fallos
- [ ] Limitar acceso al archivo de logs
- [ ] Encriptar credenciales en reposo
- [ ] Implementar rate limiting para evitar bloqueos

#### Hardening de Producción
```bash
# 1. Encriptar archivo de credenciales
gpg --encrypt credentials/archivo.json

# 2. Usar secrets manager
aws secretsmanager get-secret-value --secret-id sicoe-credentials

# 3. Variables de entorno seguras
export SICOE_PASSWORD=$(aws secretsmanager get-secret-value ...)

# 4. Permisos restrictivos
chmod 600 credentials/*.json
chmod 600 .env
```

## 📝 Notas Importantes

1. **Reportes de Cambio vs Ventas**: Los reportes "detallados" se generan dos veces:
   - Primera vez: tipo_producto="C" (Cambios/devoluciones)
   - Segunda vez: tipo_producto=default (Ventas normales)

2. **Rango de Fechas**: Automáticamente selecciona el mes completo actual (del 1 al último día)

3. **Tiempos de Espera**: 
   - Descargas normales: 8 segundos
   - Reporte de ventas (más pesado): 25 segundos

4. **Iframe Navigation**: El formulario modal está en un iframe llamado "sb-player"

5. **Datepickers de Solo Lectura**: Se usa JavaScript injection para establecer valores

6. **Archivos Locales**: Se eliminan automáticamente después de subirlos a GCS

7. **Gestión de Errores**: La función main() retorna códigos de salida para integración con CI/CD

8. **Logging**: Archivo persistente + consola simultáneamente

## 🔄 Mantenimiento

### Actualizar Selectores

Si SICOE cambia su interfaz:
```python
# En login():
driver.find_element(By.ID, "nuevo_id_campo_nit")

# En navigate_to_report():
xpath = '//*[@id="nuevo_xpath_reportes"]'

# En handle_report_form():
fecha_ini = "nuevo_id_fecha_inicial"
```

### Agregar Nuevo Tipo de Reporte
```python
# 1. Agregar configuración
config.destination_prefix_nuevo = "raw/Ventas/sicoe_nuevo/"
config.file_pattern_nuevo = "*nuevo_reporte*"

# 2. Agregar en navigate_to_report()
if report_type == 'nuevo':
    xpath = '//*[@id="nuevo_reporte_xpath"]'

# 3. Agregar en main()
sicoe.run_process(report_form='nuevo', report_type=None)
gcs_manager.eliminar_archivos("raw/Ventas/sicoe_nuevo/")
gcs_manager.subir_archivos("*nuevo_reporte*", "raw/Ventas/sicoe_nuevo/")
```

### Actualizar Rango de Fechas

Para usar un rango diferente al mes actual:
```python
# Modificar en SicoeConfig:
def get_date_range(self) -> Tuple[str, str]:
    # Para los últimos 7 días:
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    return (
        seven_days_ago.strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d")
    )
```

### Debugging Mode Detallado
```python
# Ejecutar con debug completo
DEBUG_MODE=true python sicoe_automation.py 2>&1 | tee debug_output.txt

# Agregar breakpoints para debugging interactivo
import pdb; pdb.set_trace()

# Capturar screenshots en errores
driver.save_screenshot(f"error_{timestamp}.png")
```

## 🎯 Casos de Uso

### 1. Cron Job Diario
```bash
# Agregar a crontab
0 2 * * * cd /ruta/proyecto && /ruta/venv/bin/python sicoe_automation.py >> /var/log/sicoe.log 2>&1
```

### 2. Integración con Airflow
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from sicoe_automation import main

def run_sicoe_extraction():
    result = main()
    if result != 0:
        raise Exception("SICOE extraction failed")

with DAG('sicoe_daily', schedule_interval='@daily') as dag:
    extract = PythonOperator(
        task_id='extract_sicoe',
        python_callable=run_sicoe_extraction
    )
```

### 3. Ejecución Paralela (Múltiples Entornos)
```python
import concurrent.futures

configs = [
    SicoeConfig(nit="nit1", username="user1", download_dir="/dir1"),
    SicoeConfig(nit="nit2", username="user2", download_dir="/dir2"),
]

def process_config(config):
    sicoe = SicoeAutomation(config)
    return sicoe.run_process('detallado', None)

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    results = executor.map(process_config, configs)
```

### 4. Notificaciones por Email
```python
import smtplib
from email.mime.text import MIMEText

def send_notification(success: bool, message: str):
    msg = MIMEText(message)
    msg['Subject'] = f"SICOE Report {'Success' if success else 'Failed'}"
    msg['From'] = 'alerts@company.com'
    msg['To'] = 'team@company.com'
    
    with smtplib.SMTP('smtp.company.com') as server:
        server.send_message(msg)

# En main():
try:
    result = main()
    if result == 0:
        send_notification(True, "SICOE extraction completed successfully")
except Exception as e:
    send_notification(False, f"SICOE extraction failed: {e}")
```

## 🤝 Contribuciones

### Guía de Contribución

1. **Fork** del repositorio
2. **Crear branch** de feature (`git checkout -b feature/MejoraNombre`)
3. **Seguir convenciones**:
   - PEP 8 para estilo de código
   - Docstrings en formato Google
   - Type hints en funciones públicas
   - Logging apropiado (INFO para operaciones, DEBUG para detalles)
4. **Agregar tests** si es posible
5. **Actualizar documentación** si cambia funcionalidad
6. **Commit con mensajes descriptivos**:
```bash
   git commit -m "Add: Soporte para reportes de inventario"
   git commit -m "Fix: Error en manejo de datepicker"
   git commit -m "Docs: Actualizar sección de troubleshooting"
```
7. **Push** al branch (`git push origin feature/MejoraNombre`)
8. **Abrir Pull Request** con descripción detallada

### Convenciones de Código
```python
# ✅ Correcto
def process_report(driver: webdriver.Chrome, report_type: str) -> bool:
    """
    Procesa un reporte específico.
    
    Args:
        driver: Instancia del WebDriver
        report_type: Tipo de reporte ('detallado' o 'facturas')
        
    Returns:
        True si el proceso fue exitoso, False en caso contrario
    """
    logger.info(f"Procesando reporte: {report_type}")
    # ... implementación
    return True

# ❌ Incorrecto (sin type hints, sin docstring, sin logging)
def process_report(driver, report_type):
    # Implementación
    return True
```

## 📦 Despliegue

### Docker Compose
```yaml
version: '3.8'

services:
  sicoe-automation:
    build: .
    environment:
      - SICOE_NIT=${SICOE_NIT}
      - SICOE_USERNAME=${SICOE_USERNAME}
      - SICOE_PASSWORD=${SICOE_PASSWORD}
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcs.json
    volumes:
      - ./credentials:/app/credentials:ro
      - ./logs:/app/logs
      - ./descargas:/app/descargas
    restart: on-failure
```

### Kubernetes CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: sicoe-extraction
spec:
  schedule: "0 2 * * *"  # Diario a las 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: sicoe
            image: tu-registry/sicoe-automation:latest
            envFrom:
            - secretRef:
                name: sicoe-credentials
            volumeMounts:
            - name: gcs-credentials
              mountPath: /app/credentials
              readOnly: true
          volumes:
          - name: gcs-credentials
            secret:
              secretName: gcs-key
          restartPolicy: OnFailure
```

## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

## 👤 Autor

Desarrollado para automatización de procesos de extracción SICOE.

**Contacto**: Data Engineering Team

## 📞 Soporte

Para problemas o consultas:
- **Issues**: Crear issue en repositorio con etiquetas apropiadas
- **Email**: soporte-data@company.com
- **Slack**: #data-engineering
- **Wiki**: Documentación extendida en Confluence

---

## 📚 Referencias

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Google Cloud Storage Python](https://cloud.google.com/python/docs/reference/storage/latest)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)

---

**Última actualización**: 2024  
**Versión**: 2.0.0  
**Plataforma**: SICOE  
**Tecnología**: Selenium + Python 3.8+ + GCS + Logging  
**Arquitectura**: Modular OOP con 4 clases especializadas

Archivos Adicionales Recomendados
requirements.txt
txtselenium>=4.0.0
webdriver-manager>=4.0.0
google-cloud-storage>=2.0.0
google-auth>=2.0.0
python-dotenv>=0.19.0
.gitignore
gitignore# Credenciales
credentials/
*.json
!requirements.json

# Variables de entorno
.env
.env.local
.env.*.local

# Archivos descargados
descargas/
*detallado*
*LISTADO_FACTURAS*
*.xlsx
*.xls
*.csv

# Logs
*.log
logs/
sicoe_automation.log*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Sistema
.DS_Store
Thumbs.db
desktop.ini

# Screenshots de debug
error_*.png
debug_*.png
.env.example
bash# =====================================
# SICOE Web Scraping - Configuración
# =====================================

# Autenticación SICOE
SICOE_NIT=8301256101
SICOE_USERNAME=analistadatos
SICOE_PASSWORD=tu_password_seguro
SICOE_LOGIN_URL=https://sicoe.com.co/sicoe/dist/#/login

# Google Cloud Storage
GCS_BUCKET_NAME=bucket-quickstart_croc_830
GOOGLE_APPLICATION_CREDENTIALS=credentials/tu-archivo.json

# Configuración de directorios
DOWNLOAD_DIR=C:\Users\Usuario\Downloads\Sicoe\descargas

# Debugging
DEBUG_MODE=false

# Configuración avanzada (opcional)
WAIT_TIME_STANDARD=8
DOWNLOAD_WAIT_TIME=25
docker-compose.yml
yamlversion: '3.8'

services:
  sicoe-automation:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sicoe-scraper
    environment:
      - SICOE_NIT=${SICOE_NIT}
      - SICOE_USERNAME=${SICOE_USERNAME}
      - SICOE_PASSWORD=${SICOE_PASSWORD}
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcs.json
      - DEBUG_MODE=${DEBUG_MODE:-false}
    volumes:
      - ./credentials:/app/credentials:ro
      - ./logs:/app/logs
      - ./descargas:/app/descargas
      - /dev/shm:/dev/shm  # Para Chrome
    restart: on-failure
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
CHANGELOG.md
markdown# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [2.0.0] - 2024-11-20

### Added
- Arquitectura modular con 4 clases especializadas
  - `SicoeConfig`: Gestión centralizada de configuración
  - `WebDriverManager`: Gestión del ciclo de vida del WebDriver
  - `GCSManager`: Operaciones con Google Cloud Storage
  - `SicoeAutomation`: Automatización del portal SICOE
- Sistema de logging robusto con archivo + consola
- Soporte completo para variables de entorno
- Método `get_date_range()` para obtener rango del mes actual
- Generación de reportes de CAMBIOS y VENTAS NORMALES
- Generación de reportes de FACTURAS DIARIAS
- JavaScript injection para manipular datepickers de solo lectura
- Limpieza automática de archivos locales post-sincronización
- Códigos de salida para integración con CI/CD
- Manejo de señales (SIGINT) para terminación correcta
- Type hints en todos los métodos públicos
- Docstrings en formato Google
- Creación automática de directorio de descargas

### Changed
- Migrado de Edge a Chrome WebDriver
- Refactorizado de script monolítico a arquitectura modular
- Mejorado manejo de errores con logging detallado
- Optimizados tiempos de espera por tipo de operación

### Fixed
- Problema con datepickers de solo lectura
- Race condition en espera de elementos
- Gestión de recursos del WebDriver

### Security
- Soporte para variables de entorno en todas las credenciales
- No se registran contraseñas en logs
- Credenciales GCS separadas del código

## [1.0.0] - 2024-XX-XX

### Added
- Implementación inicial del script
- Login básico en SICOE
- Descarga de reportes detallados
- Subida a Google Cloud Storage
Esta documentación es la más completa de las tres porque el script de SICOE tiene la arquitectura más sofisticada con múltiples clases, mejor manejo de errores, logging avanzado y soporte para variables de entorno. ¿Necesitas que agregue alguna sección adicional o que profundice en algún aspecto específico?ReintentarClaude puede cometer errores. Por favor, verifique las respuestas. Sonnet 4.5
