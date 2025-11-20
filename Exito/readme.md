📄 Éxito Web Scraping - Documentación
markdown# Éxito Web Scraping Automation

Script automatizado orientado a objetos para descargar reportes de ventas e inventario desde la plataforma Prescriptiva Latam (Éxito) y sincronizarlos con Google Cloud Storage.

## 📋 Descripción

Este script de Python utiliza Selenium y programación orientada a objetos para automatizar el proceso completo de:
- Login en la plataforma Prescriptiva Latam
- Navegación por la interfaz de Cen Colaboración
- Descarga de reportes dinámicos (Ventas e Inventario)
- Selección automática de períodos (mes actual y anterior)
- Clasificación y renombrado inteligente de archivos
- Subida automática a Google Cloud Storage con limpieza previa
- Limpieza de archivos locales post-sincronización

## ✨ Características

- ✅ Arquitectura orientada a objetos para mejor mantenibilidad
- ✅ Selección automática de períodos (mes actual y anterior)
- ✅ Manejo de múltiples ventanas del navegador
- ✅ Clasificación automática de reportes (Ventas/Inventario)
- ✅ Renombrado inteligente de archivos descargados
- ✅ Limpieza automática del bucket antes de subir nuevos archivos
- ✅ Verificación de archivos en GCS post-upload
- ✅ Múltiples estrategias de selección de elementos (mayor robustez)
- ✅ Manejo robusto de modales y pop-ups
- ✅ Logging detallado en cada paso del proceso

## 🔧 Requisitos Previos

### Software Necesario
- Python 3.8 o superior
- Google Chrome (versión actualizada)
- Cuenta de Google Cloud Platform con permisos de Storage
- Acceso a Prescriptiva Latam

### Dependencias Python
```bash
selenium>=4.0.0
webdriver-manager>=4.0.0
google-cloud-storage>=2.0.0
pandas>=1.3.0
```

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone 
cd exito-scraping
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar estructura de carpetas
```bash
mkdir -p credentials
mkdir -p "C:\Users\dani\OneDrive\Web Scaping\Exito"  # O tu ruta preferida
```

### 5. Configurar credenciales de Google Cloud
- Descargar el archivo JSON de credenciales desde Google Cloud Console
- Colocar el archivo en la carpeta `credentials/`
- Actualizar la variable `credentials_path` en el script

## ⚙️ Configuración

### Variables de Configuración Principal
```python
# Ruta de descarga local (CAMBIAR SEGÚN NECESIDAD)
download_path = r"C:\Users\dani\OneDrive\Web Scaping\Exito"

# Configuración de Google Cloud Storage
credentials_path = "credentials/croc-454221-e1a3c2e02181.json"
bucket_name = "bucket-quickstart_croc_830"

# Rutas en el bucket
RUTA_INVENTARIO = "raw/Ventas/moderno/exito/inventario/"
RUTA_VENTAS = "raw/Ventas/moderno/exito/ventas/"

# Credenciales de acceso (usar variables de entorno en producción)
EMAIL = "tu-email@ejemplo.com"
PASSWORD = "tu-contraseña"
```

### ⚠️ Seguridad - Variables de Entorno

**CRÍTICO**: Para producción, usar variables de entorno:
```python
import os

EMAIL = os.getenv('EXITO_EMAIL')
PASSWORD = os.getenv('EXITO_PASSWORD')
CREDENTIALS_PATH = os.getenv('GCS_CREDENTIALS_PATH')
```

Crear archivo `.env`:
```bash
EXITO_EMAIL=grandessuperficies@ejemplo.com
EXITO_PASSWORD=tu_password_seguro
GCS_CREDENTIALS_PATH=credentials/tu-archivo.json
```

## 🚀 Uso

### Ejecución Básica
```bash
python exito_automation.py
```

### Uso Programático
```python
from exito_automation import ExitoAutomation

# Configurar parámetros
download_path = r"C:\ruta\de\descarga"
credentials_path = "credentials/archivo.json"
bucket_name = "mi-bucket"

# Crear instancia
automation = ExitoAutomation(download_path, credentials_path, bucket_name)

# Ejecutar proceso completo
automation.run_automation(email="tu@email.com", password="tu_password")

# O ejecutar pasos individuales
automation.setup_driver()
automation.login_to_site(email, password)
automation.click_cen_colaboracion()
# ... etc
```

### Interacción Manual Requerida
Durante el proceso de login:
1. **CAPTCHA reCAPTCHA**: Resolver manualmente en 20 segundos
2. El script automáticamente hace clic inicial en el checkbox
3. Esperar a completar el desafío visual si aparece
4. El script continúa automáticamente después

## 📁 Estructura del Proyecto
```
exito-scraping/
├── exito_automation.py          # Script principal (clase ExitoAutomation)
├── credentials/
│   └── archivo-credenciales.json  # Credenciales GCS (no incluir en git)
├── requirements.txt              # Dependencias Python
├── README.md                     # Esta documentación
├── .env                          # Variables de entorno (no incluir en git)
├── .gitignore                    # Archivos a ignorar
└── logs/                         # Carpeta de logs (opcional)
```

## 🔄 Flujo del Proceso
```
1. Limpieza Inicial
   └── Eliminar archivos Excel existentes en carpeta local
   
2. Setup del WebDriver
   └── Configurar Chrome con opciones de descarga
   
3. Login en Prescriptiva Latam
   ├── Navegar a https://prescriptivalatam.com/
   ├── Ingresar credenciales
   ├── Resolver CAPTCHA (manual - 20 segundos)
   ├── Hacer clic en login
   └── Manejar modal si aparece
   
4. Navegación a Reportes
   ├── Clic en "Cen Colaboración"
   ├── Expandir accordion "Reporte dinámico"
   └── Clic en "Reporte en línea"
   
5. Cambiar a Nueva Ventana
   └── Switch al popup de Qlik Sense
   
6. Descargar Reporte de Ventas
   ├── Clic en marcadores (bookmarks)
   ├── Seleccionar "Ventas"
   ├── Aceptar términos
   ├── Seleccionar mes actual y anterior
   ├── Seleccionar año 2025
   ├── Descargar reporte
   └── Cerrar modal de descarga
   
7. Descargar Reporte de Inventario
   ├── Clic en marcadores
   ├── Seleccionar "Inventario1"
   ├── Limpiar filtros existentes
   ├── Seleccionar mes actual
   ├── Seleccionar año 2025
   └── Descargar reporte
   
8. Cerrar Navegador
   └── Quit driver
   
9. Procesamiento de Archivos
   ├── Identificar archivos descargados
   └── Renombrar según tipo:
       ├── (con "(1)") → Inventario
       └── (sin "(1)") → Ventas Mensuales
   
10. Sincronización con GCS
    ├── Limpiar archivos existentes en bucket
    ├── Subir archivo de Inventario → raw/Ventas/moderno/exito/inventario/
    ├── Subir archivo de Ventas → raw/Ventas/moderno/exito/ventas/
    └── Verificar integridad de archivos
    
11. Limpieza Local
    └── Eliminar archivos Excel descargados
```

## 🛠️ Métodos de la Clase ExitoAutomation

### Configuración y Setup

#### `__init__(download_path, credentials_path, bucket_name)`
Inicializa la clase con las rutas y configuraciones necesarias.

#### `setup_driver()`
Configura y retorna el driver de Chrome con opciones de descarga.

#### `clean_existing_files()`
Elimina archivos Excel existentes antes de iniciar el proceso.

### Autenticación

#### `login_to_site(email, password)`
Automatiza el proceso completo de login en Prescriptiva Latam.

#### `wait_captcha()`
Proporciona 20 segundos para resolver CAPTCHA manualmente.

### Navegación

#### `click_cen_colaboracion()`
Hace clic en el menú "Cen Colaboración".

#### `click_reporte_dinamico_accordion()`
Expande el accordion de "Reporte dinámico".

#### `click_reporte_en_linea()`
Hace clic en "Reporte en línea" para abrir nueva ventana.

#### `switch_to_new_window()`
Cambia el contexto a la nueva ventana de Qlik Sense.

### Gestión de Reportes

#### `click_bookmarks_button()`
Hace clic en el botón de marcadores.

#### `click_ventas_button()`
Selecciona el marcador de Ventas.

#### `process_inventory_report()`
Procesa y descarga el reporte de inventario completo.

### Filtros y Selección

#### `select_month_filter()`
Abre el selector de meses.

#### `select_current_and_previous_months()`
Selecciona automáticamente mes actual y anterior.
- Retorna: `(bool, list)` - Success y lista de meses seleccionados

#### `select_year_filter()`
Abre el selector de años.

#### `select_year_2025()`
Selecciona el año 2025.

#### `confirm_selection()`
Confirma las selecciones de filtros.

#### `accept_terms()`
Acepta los términos de uso.

### Descarga

#### `download_report(report_name="Reporte en línea")`
Descarga el reporte mediante menú contextual.

#### `close_download_modal()`
Cierra el modal de descarga.

### Procesamiento de Archivos

#### `rename_downloaded_files()`
Identifica y renombra archivos descargados:
- Con "(1)" → Inventario
- Sin "(1)" → Ventas Mensuales

### Google Cloud Storage

#### `clean_bucket()`
Elimina archivos existentes en rutas del bucket antes de subir nuevos.

#### `upload_files_to_bucket()`
Sube archivos clasificados al bucket de GCS.

#### `verify_bucket_files()`
Verifica que los archivos se subieron correctamente.

#### `clean_local_files()`
Elimina archivos locales después de subirlos al bucket.

### Orquestación

#### `run_automation(email, password)`
Ejecuta todo el proceso de automatización de principio a fin.

## 🐛 Troubleshooting

### Error: ChromeDriver incompatible
```bash
✅ Solución: 
- Actualizar Chrome a la última versión
- webdriver-manager descarga automáticamente la versión correcta
- Si falla: pip install --upgrade webdriver-manager
```

### Error: Timeout en CAPTCHA
```bash
⚠️ El CAPTCHA tiene 20 segundos para resolverse
✅ Solución: 
- Estar atento cuando aparezca el CAPTCHA
- Resolver rápidamente el desafío visual
- Si se agota el tiempo, reiniciar el script
```

### Error: No se encuentra elemento "Cen Colaboración"
```bash
✅ Solución: 
- Verificar que el login fue exitoso
- La página puede tardar en cargar completamente
- Aumentar tiempo de espera: WebDriverWait(driver, 15)
```

### Error: No se encuentra botón de Ventas
```bash
❌ Error común: data-testid cambió
✅ Solución: 
- Inspeccionar elemento en el navegador
- Actualizar selector en click_ventas_button()
- Usar XPath alternativo: //span[text()='Ventas']
```

### Error: Archivos no se renombran correctamente
```bash
✅ Verificar: 
- Ambos archivos se descargaron completamente
- No hay archivos .crdownload en la carpeta
- Los nombres contienen "Qlik Sense - Reporte en línea"
```

### Error: Credenciales GCS inválidas
```bash
✅ Verificar:
- Archivo JSON en carpeta credentials/
- Permisos de Storage Object Admin en GCP
- Variable credentials_path apunta al archivo correcto
- export GOOGLE_APPLICATION_CREDENTIALS="/ruta/completa"
```

### Error: No se puede cambiar a nueva ventana
```bash
✅ Solución:
- Verificar que se abrió popup de Qlik Sense
- Desactivar bloqueador de pop-ups para prescriptivalatam.com
- Aumentar implicitly_wait en switch_to_new_window()
```

### Error: Elementos Stale Element Reference
```bash
✅ Solución implementada:
- El script detecta automáticamente stale elements
- Re-busca elementos si es necesario
- Usa try/except para manejar estas excepciones
```

## 📊 Logs y Monitoreo

El script proporciona logging detallado:
```
✅ Operaciones exitosas
⚠️ Advertencias
❌ Errores críticos
📄 Información de archivos
🔄 Progreso del proceso
```

### Ejemplo de salida:
```
INICIANDO PROCESO DE AUTOMATIZACIÓN EXITO
==================================================
Paso 1: Limpiando archivos existentes...
Archivo eliminado: reporte_anterior.xlsx

Paso 2: Iniciando sesión...
INICIANDO LOGIN AUTOMÁTICO
========================================
Navegando a la página...
Llenando credenciales...
Clickeando CAPTCHA...
Esperando interacción con captcha...
Resuelve el CAPTCHA manualmente (20 segundos)...
Tiempo: 20s... 19s... 18s...
```

## 🔐 Seguridad

### Buenas Prácticas Implementadas
- ✅ Clase encapsulada con atributos privados
- ✅ Manejo seguro de credenciales
- ✅ Eliminación automática de archivos sensibles
- ✅ Validación de operaciones GCS

### Mejoras Recomendadas
- [ ] Migrar credenciales a AWS Secrets Manager o similar
- [ ] Implementar logging en archivos con rotación
- [ ] Agregar encriptación de credenciales en reposo
- [ ] Implementar rate limiting para evitar bloqueos
- [ ] Agregar monitoreo y alertas de fallos

## 📝 Notas Importantes

1. **CAPTCHA Manual**: Requiere intervención humana (20 segundos)
2. **Períodos Automáticos**: Selecciona mes actual y anterior automáticamente
3. **Múltiples Estrategias**: Usa varios selectores para mayor robustez
4. **Limpieza Automática**: Archivos locales y bucket se limpian automáticamente
5. **Verificación Post-Upload**: Valida integridad de archivos en GCS
6. **Nombres Dinámicos**: Archivos incluyen fecha de descarga en el nombre
7. **No Ejecutar en Paralelo**: Un solo proceso a la vez

## 🔄 Mantenimiento

### Actualizar Selectores
Si la interfaz de Prescriptiva Latam cambia:
```python
# Método: click_ventas_button()
# Actualizar el data-testid:
new_selector = 'div[data-testid="nuevo-id-aqui"]'
```

### Actualizar Períodos
Para cambiar la lógica de selección de meses:
```python
# Método: select_current_and_previous_months()
# Modificar el cálculo de mes_anterior
```

### Debugging Mode
Para ejecutar con navegador visible:
```python
# En setup_driver(), comentar:
# chrome_options.add_argument("--headless")
```

## 🎯 Casos de Uso

### 1. Ejecución Manual Diaria
```bash
# Programar tarea en Windows Task Scheduler o cron
0 8 * * * /path/to/venv/bin/python /path/to/exito_automation.py
```

### 2. Integración en Pipeline de Datos
```python
from exito_automation import ExitoAutomation

def daily_etl():
    # Descargar datos
    automation = ExitoAutomation(...)
    automation.run_automation(email, password)
    
    # Procesar datos
    process_sales_data()
    process_inventory_data()
```

### 3. Monitoreo y Alertas
```python
import logging

logging.basicConfig(filename='exito_automation.log', level=logging.INFO)

try:
    automation.run_automation(email, password)
    send_success_notification()
except Exception as e:
    logging.error(f"Error: {e}")
    send_alert_email(error=e)
```

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/NuevaFuncionalidad`)
3. Documentar cambios en código
4. Actualizar README si es necesario
5. Commit con mensajes descriptivos (`git commit -m 'Add: Nueva funcionalidad X'`)
6. Push al branch (`git push origin feature/NuevaFuncionalidad`)
7. Abrir Pull Request con descripción detallada

### Convenciones de Código
- Seguir PEP 8
- Documentar métodos con docstrings
- Usar type hints donde sea posible
- Mantener métodos < 50 líneas
- Agregar tests para nuevas funcionalidades

## 🔧 Configuración Avanzada

### Cambiar Año de Selección
```python
# En los métodos select_year_2025() y process_inventory_report()
# Cambiar el año según necesidad:
elemento = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="2026"]')))
```

### Personalizar Rutas de Bucket
```python
# Modificar en upload_files_to_bucket()
ruta_inventario = "tu/ruta/personalizada/inventario/"
ruta_ventas = "tu/ruta/personalizada/ventas/"
```

### Ajustar Timeouts
```python
# En cada WebDriverWait, ajustar el timeout:
WebDriverWait(self.driver, 30)  # Aumentar de 10 a 30 segundos
```

## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

## 👤 Autor

Desarrollado para automatización de procesos de descarga Éxito/Prescriptiva Latam.

## 📞 Soporte

Para problemas o consultas:
- Crear un issue en el repositorio
- Contactar al equipo de Data Engineering
- Email: soporte@tuempresa.com

---

**Última actualización**: 2024  
**Versión**: 1.0.0  
**Plataforma**: Prescriptiva Latam (Éxito)  
**Tecnología**: Selenium + Python 3.8+ + GCS

Archivos Adicionales Recomendados
requirements.txt
txtselenium>=4.0.0
webdriver-manager>=4.0.0
google-cloud-storage>=2.0.0
pandas>=1.3.0
python-dotenv>=0.19.0
.gitignore
gitignore# Credenciales
credentials/
*.json
!requirements.json

# Variables de entorno
.env
.env.local

# Archivos descargados
*.xlsx
*.xls
Qlik Sense*

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
.DS_Store

# Logs
*.log
logs/

# Sistema
Thumbs.db
desktop.ini
.env.example
bash# Credenciales de Éxito/Prescriptiva Latam
EXITO_EMAIL=tu-email@ejemplo.com
EXITO_PASSWORD=tu-password-seguro

# Google Cloud Storage
GCS_CREDENTIALS_PATH=credentials/tu-archivo.json
GCS_BUCKET_NAME=tu-bucket-name

# Rutas locales
DOWNLOAD_PATH=C:\Users\tu-usuario\Downloads\Exito
CHANGELOG.md
markdown# Changelog

## [1.0.0] - 2024-11-20

### Added
- Implementación inicial de ExitoAutomation class
- Login automatizado con manejo de CAPTCHA
- Descarga automática de reportes de Ventas e Inventario
- Selección automática de períodos (mes actual y anterior)
- Renombrado inteligente de archivos
- Integración completa con Google Cloud Storage
- Limpieza automática de archivos locales y bucket
- Verificación de integridad post-upload
- Logging detallado en cada paso
- Múltiples estrategias de selección de elementos
- Manejo robusto de errores y excepciones

### Security
- Soporte para variables de entorno
- Encapsulación de credenciales en clase
