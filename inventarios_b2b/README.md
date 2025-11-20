📄 Makro B2B Web Scraping - Documentación
markdown# Makro B2B Automation Script

Script automatizado orientado a objetos para extraer reportes de Stock, Purchase Orders y Sales desde el portal B2B de Makro y sincronizarlos con Google Cloud Storage.

## 📋 Descripción

Este script de Python utiliza Selenium y programación orientada a objetos para automatizar el proceso completo de:
- Login en el portal B2B de Makro
- Navegación por la interfaz iSupplier Vendor Commercial
- Configuración de parámetros del reporte (fechas, opciones de totalización)
- Generación y descarga del reporte "Stock and PO and Sales"
- Gestión de múltiples ventanas del navegador
- Subida automática a Google Cloud Storage con reemplazo de duplicados
- Limpieza de archivos locales post-sincronización

## ✨ Características

- ✅ **Carga de Credenciales desde Archivo**: Sistema seguro de gestión de credenciales
- ✅ **Arquitectura Orientada a Objetos**: Clase `MakroAutomation` encapsulada
- ✅ **Gestión de Ventanas Múltiples**: Manejo de popups de Oracle BI
- ✅ **Configuración Flexible de Fechas**: Parámetros ajustables de rango temporal
- ✅ **Dropdowns Dinámicos**: Múltiples estrategias de selección
- ✅ **Tiempos de Espera Optimizados**: Esperas específicas para generación de reportes (115s)
- ✅ **Reemplazo Inteligente en GCS**: Elimina duplicados antes de subir
- ✅ **Logging Descriptivo**: Indicadores visuales de progreso (-->)
- ✅ **Fallback de Credenciales**: Sistema de respaldo para desarrollo
- ✅ **Limpieza Automática**: Eliminación de archivos locales post-upload

## 🔧 Requisitos Previos

### Software Necesario
- Python 3.8 o superior
- Google Chrome (versión actualizada)
- Cuenta de Google Cloud Platform con permisos de Storage
- Acceso al portal B2B de Makro (https://b2b.makro.com/)

### Dependencias Python
```bash
selenium>=4.0.0
webdriver-manager>=4.0.0
google-cloud-storage>=2.0.0
google-auth>=2.0.0
beautifulsoup4>=4.9.0
pandas>=1.3.0
```

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone 
cd makro-scraping
```

### 2. Crear estructura de directorios
```bash
mkdir -p credentials
mkdir -p "C:\Users\dani\OneDrive\Web Scaping\inventarios_b2b"  # Windows
# O para Linux/Mac:
# mkdir -p ~/Downloads/Makro/inventarios_b2b
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

### 5. Configurar credenciales

#### Archivo de credenciales (Recomendado)
Crear archivo `credentials.txt` en el directorio raíz:
```txt
username=grandessuperficies@donchicharron.com.co
password=tu_password_seguro
```

#### Credenciales de Google Cloud
- Descargar el archivo JSON desde Google Cloud Console
- Colocar en `credentials/croc-454221-e1a3c2e02181.json`
- Actualizar `credentials_path` si es necesario

## ⚙️ Configuración

### Variables de Configuración Global
```python
# Directorio de descargas local
directorio = r"C:\Users\dani\OneDrive\Web Scaping\inventarios_b2b"

# Nombre del archivo generado por Makro
nombre_archivo_makro = "Stock and PO and Sales Report_Stock and PO and Sales Report.xlsx"

# Configuración de Google Cloud Storage
bucket_name = "bucket-quickstart_croc_830"
destino = "raw/Ventas/moderno/makro/"
credentials_path = "credentials/croc-454221-e1a3c2e02181.json"
```

### Clase MakroAutomation - Parámetros
```python
class MakroAutomation:
    def __init__(self, credentials_file="credentials.txt"):
        """
        Args:
            credentials_file: Ruta al archivo de credenciales.
                             Formato requerido:
                             username=email@ejemplo.com
                             password=contraseña_segura
        """
```

### ⚠️ Sistema de Credenciales

#### Formato del Archivo credentials.txt
```txt
# Credenciales de Makro B2B
username=tu_email@ejemplo.com
password=tu_password_seguro
```

#### Jerarquía de Carga de Credenciales
1. **Archivo credentials.txt** (Primario)
2. **Valores hardcodeados** (Fallback solo para desarrollo)

#### Mejores Prácticas
```python
# ✅ Correcto - Usar archivo de credenciales
automation = MakroAutomation(credentials_file="credentials.txt")

# ✅ Correcto - Variables de entorno (para producción)
import os
username = os.getenv('MAKRO_USERNAME')
password = os.getenv('MAKRO_PASSWORD')

# ❌ Evitar - Hardcodear credenciales en código
username = "usuario@ejemplo.com"  # NO HACER ESTO
```

### Configuración de Fechas del Reporte
```python
# En configure_report_parameters()
start_date = "01/08/2025"  # Formato: DD/MM/YYYY
end_date = "20/08/2025"    # Formato: DD/MM/YYYY

# Llamada personalizada:
automation.configure_report_parameters(
    start_date="01/11/2024",
    end_date="30/11/2024"
)
```

## 🚀 Uso

### Ejecución Básica
```bash
python makro_automation.py
```

### Ejecución con Credenciales Personalizadas
```bash
# Crear archivo de credenciales alternativo
cat > credentials_prod.txt << EOF
username=produccion@empresa.com
password=password_produccion
EOF

# Modificar el script para usar el archivo alternativo
# En main() o al crear la instancia:
automation = MakroAutomation(credentials_file="credentials_prod.txt")
```

### Uso Programático
```python
from makro_automation import MakroAutomation, subir_archivos, borrar_archivos

# 1. Crear instancia (ejecuta automáticamente la secuencia)
automation = MakroAutomation(credentials_file="credentials.txt")

# 2. Subir archivos a GCS
archivos_subidos = subir_archivos()

# 3. Limpiar archivos locales
borrar_archivos(archivos_subidos)
```

### Uso Programático Avanzado (Sin Auto-ejecución)

Para mayor control, modificar la clase:
```python
class MakroAutomation:
    def __init__(self, credentials_file="credentials.txt", auto_run=True):
        self.credentials_file = credentials_file
        self.username, self.password = self._load_credentials()
        self.driver = None
        self.main_window = None
        
        if auto_run:
            self.run_automation()

# Uso con control manual
automation = MakroAutomation(auto_run=False)
automation.initialize_driver()
automation.login()
automation.configure_report_parameters(start_date="01/01/2025", end_date="31/01/2025")
automation.download_excel_report()
```

## 📁 Estructura del Proyecto
```
makro-scraping/
├── makro_automation.py           # Script principal
├── credentials.txt                # Credenciales Makro (no incluir en git)
├── credentials/
│   └── croc-454221-e1a3c2e02181.json  # Credenciales GCS (no incluir en git)
├── inventarios_b2b/               # Descargas temporales (auto-limpiado)
│   └── Stock and PO and Sales Report_*.xlsx
├── requirements.txt               # Dependencias Python
├── .env                           # Variables de entorno (no incluir en git)
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore                     # Archivos a ignorar
├── README.md                      # Esta documentación
└── CHANGELOG.md                   # Historial de cambios
```

## 🔄 Flujo del Proceso
```
1. Inicialización
   ├── Crear instancia de MakroAutomation
   ├── Cargar credenciales desde credentials.txt
   ├── Inicializar WebDriver con directorio de descarga
   └── Configurar opciones de Chrome
   
2. Login en Makro B2B
   ├── Navegar a https://b2b.makro.com/
   ├── Completar campo username
   ├── Completar campo password
   ├── Click en botón de login
   └── Esperar carga del dashboard (3 segundos)
   
3. Navegación a iSupplier
   ├── Buscar botón "ISUPPLIER VENDOR COMMERCIAL"
   ├── Click en el botón
   └── Esperar carga (3 segundos)
   
4. Navegación a Commercial
   ├── Buscar botón "Commercial" (ID: MAKRO_POS_COMMERCIAL)
   ├── Click en el botón
   └── Esperar carga (5 segundos)
   
5. Navegación a Stock PO Sales Report
   ├── Buscar botón "Stock and PO and Sales report" (ID: STOCKPOSALES)
   ├── Click en el botón
   ├── Esperar apertura de nueva ventana (10 segundos)
   └── Guardar referencia a ventana principal
   
6. Cambiar a Ventana del Reporte
   ├── Listar todas las ventanas abiertas
   ├── Identificar nueva ventana (popup)
   ├── Cambiar foco a la ventana del reporte
   └── Mantener referencia a ventana principal
   
7. Configuración de Parámetros
   ├── Campo "BEGIN_DATE": Ingresar fecha inicio (DD/MM/YYYY)
   ├── Campo "END_DATE": Ingresar fecha fin (DD/MM/YYYY)
   ├── Dropdown "Totalizar tiendas": Seleccionar "No"
   │   ├── Abrir dropdown
   │   ├── Esperar opciones (1 segundo)
   │   └── Click en "No"
   ├── Dropdown "Mostrar total empresa": Seleccionar "No"
   │   ├── Abrir dropdown
   │   ├── Esperar opciones (1 segundo)
   │   └── Click en "No"
   ├── Click en botón "Aplicar"
   └── Esperar generación del reporte
   
8. Descarga del Reporte
   ├── Click en enlace "Ver Informe"
   ├── Esperar generación completa (115 segundos) ⏳
   ├── Buscar opción "Excel (*.xlsx)" en menú flotante
   │   ├── Método 1: Buscar por texto exacto
   │   └── Método 2 (fallback): Buscar por fmid='3' o fmid='102'
   ├── Click en opción Excel
   ├── Iniciar descarga automática
   └── Archivo guardado en directorio configurado
   
9. Subida a Google Cloud Storage
   ├── Conectar a GCS con credenciales de servicio
   ├── Buscar archivos en directorio local
   │   └── Patrón: "Stock and PO and Sales Report_*.xlsx"
   ├── Para cada archivo:
   │   ├── Verificar si ya existe en bucket
   │   ├── Si existe: Eliminar versión anterior
   │   └── Subir nueva versión
   └── Ruta destino: raw/Ventas/moderno/makro/
   
10. Limpieza Local
    ├── Para cada archivo subido:
    │   ├── Verificar existencia local
    │   ├── Eliminar archivo
    │   └── Registrar eliminación
    └── Liberar espacio en disco
    
11. Finalización
    ├── Mantener driver abierto (no se cierra automáticamente)
    └── Mostrar resumen del proceso
```

## 🛠️ Clase MakroAutomation - Métodos

### Inicialización y Configuración

#### `__init__(credentials_file="credentials.txt")`
Inicializa la automatización y ejecuta la secuencia completa.
```python
automation = MakroAutomation(credentials_file="credentials.txt")
# La automatización se ejecuta automáticamente al crear la instancia
```

#### `_load_credentials() -> Tuple[str, str]`
Carga credenciales desde archivo de texto (método privado).
```python
# Formato del archivo:
# username=usuario@ejemplo.com
# password=contraseña

# Retorna: (username, password)
```

**Manejo de Errores**:
- `FileNotFoundError`: Usa credenciales de fallback
- `ValueError`: Formato incorrecto, usa credenciales de fallback
- Cualquier otra excepción: Usa credenciales de fallback

#### `initialize_driver() -> webdriver.Chrome`
Inicializa y configura Chrome WebDriver con directorio de descarga.
```python
driver = automation.initialize_driver()
```

**Configuraciones aplicadas**:
- Directorio de descarga personalizado
- Descargas automáticas sin prompt
- No sandbox mode para estabilidad
- Deshabilitación de controles de automatización
- Implicit wait de 10 segundos
- Creación automática de directorio si no existe

---

### Autenticación

#### `login() -> bool`
Realiza el inicio de sesión en el portal B2B de Makro.
```python
if automation.login():
    print("Login exitoso")
else:
    print("Login falló")
```

**Pasos**:
1. Navegar a https://b2b.makro.com/
2. Esperar campo username (timeout: 10s)
3. Ingresar credenciales
4. Click en botón de login
5. Esperar carga (3s)

**Retorna**: `True` si exitoso, `False` si falla

---

### Navegación

#### `navigate_to_isupplier() -> bool`
Navega a la sección "ISUPPLIER VENDOR COMMERCIAL".
```python
if automation.navigate_to_isupplier():
    print("Navegación exitosa")
```

**Selector**: XPath por texto exacto
```python
By.XPATH, "//div[@class='textdivresp' and text()='ISUPPLIER VENDOR COMMERCIAL']"
```

#### `navigate_to_commercial() -> bool`
Navega a la sección "Commercial".
```python
automation.navigate_to_commercial()
```

**Selector**: Por ID
```python
By.ID, "MAKRO_POS_COMMERCIAL"
```

**Tiempo de espera**: 5 segundos

#### `navigate_to_stock_po_sales() -> bool`
Navega al reporte "Stock and PO and Sales".
```python
automation.navigate_to_stock_po_sales()
```

**Selector**: Por ID
```python
By.ID, "STOCKPOSALES"
```

**Tiempo de espera**: 10 segundos (apertura de nueva ventana)

#### `switch_to_report_window() -> bool`
Cambia el foco a la ventana del reporte (popup).
```python
if automation.switch_to_report_window():
    print("Ventana del reporte activa")
```

**Lógica**:
1. Guardar referencia a ventana principal
2. Listar todas las ventanas abiertas
3. Cambiar a la ventana que no es la principal
4. Mantener referencia para posible regreso

---

### Configuración del Reporte

#### `configure_report_parameters(start_date="01/08/2025", end_date="20/08/2025") -> bool`
Configura los parámetros del reporte.
```python
# Usar fechas por defecto
automation.configure_report_parameters()

# Usar fechas personalizadas
automation.configure_report_parameters(
    start_date="01/01/2025",
    end_date="31/01/2025"
)
```

**Parámetros configurados**:
1. **BEGIN_DATE**: Fecha inicio (DD/MM/YYYY)
2. **END_DATE**: Fecha fin (DD/MM/YYYY)
3. **Totalizar tiendas**: "No"
4. **Mostrar total empresa**: "No"

**Importante**: Las fechas deben estar en formato DD/MM/YYYY

#### `_select_dropdown_option(dropdown_id, option_xpath, dropdown_name) -> None`
Selecciona una opción de un dropdown (método privado).
```python
# Uso interno en configure_report_parameters()
self._select_dropdown_option(
    dropdown_id="xdo:xdo:_paramsPM_SUM_LOCATIONS_div_input",
    option_xpath="//li[contains(@id, '_paramsPM_SUM_LOCATIONS_div_li') and .//div[text()='No']]",
    dropdown_name="Totalizar tiendas"
)
```

**Pasos**:
1. Click en dropdown para abrir
2. Esperar 1 segundo (animación)
3. Click en opción especificada
4. Logging descriptivo

---

### Descarga del Reporte

#### `download_excel_report() -> bool`
Descarga el reporte en formato Excel.
```python
if automation.download_excel_report():
    print("Descarga iniciada")
```

**Pasos críticos**:
1. Click en "Ver Informe" (ID: xdo:viewFormatLink)
2. **Esperar 115 segundos** ⏳ (generación del reporte)
3. Buscar opción "Excel (*.xlsx)" en menú flotante
4. Click en la opción Excel
5. Descarga automática inicia

**Métodos de Selección de Excel**:
- **Método 1** (Primario): Buscar por texto "Excel (*.xlsx)"
- **Método 2** (Fallback): Buscar por atributo fmid='3' o fmid='102'

---

### Orquestación

#### `run_automation() -> None`
Ejecuta la secuencia completa de automatización.
```python
# Llamado automáticamente en __init__
automation = MakroAutomation()

# O manualmente si se deshabilita auto_run
automation.run_automation()
```

**Flujo de ejecución**:
```python
try:
    initialize_driver()
    login()
    navigate_to_isupplier()
    navigate_to_commercial()
    navigate_to_stock_po_sales()
    switch_to_report_window()
    configure_report_parameters()
    download_excel_report()
    print("Automatización completada exitosamente")
except Exception as e:
    print(f"Error durante la automatización: {e}")
finally:
    # Driver NO se cierra automáticamente
    pass
```

---

## 🌐 Funciones Auxiliares

### `subir_archivos() -> List[str]`
Sube archivos al bucket eliminando duplicados existentes.
```python
archivos_subidos = subir_archivos()
# Retorna: Lista de rutas de archivos subidos
```

**Proceso**:
1. Conectar a GCS con credenciales de servicio
2. Buscar archivos que coincidan con `nombre_archivo_makro`
3. Para cada archivo:
   - Verificar si existe en bucket
   - Si existe: Eliminar (🗑️)
   - Subir nuevo archivo (✅)
4. Retornar lista de archivos procesados

**Logging**:
- 🗑️ Eliminado del bucket
- ✅ Subido exitosamente

### `borrar_archivos(archivos: List[str]) -> None`
Elimina archivos locales.
```python
archivos = ["archivo1.xlsx", "archivo2.xlsx"]
borrar_archivos(archivos)
```

**Proceso**:
1. Para cada archivo en la lista:
   - Verificar existencia
   - Eliminar si existe (🗑️)
   - Advertir si no existe (⚠️)

### `main() -> None`
Función principal que orquesta todo el proceso.
```python
if __name__ == "__main__":
    main()
```

**Secuencia completa**:
1. Banner de inicio
2. Crear instancia de `MakroAutomation`
3. Subir archivos a GCS
4. Limpiar archivos locales
5. Banner de finalización

---

## 🐛 Troubleshooting

### Error: Archivo credentials.txt no encontrado
```bash
ERROR: Archivo de credenciales 'credentials.txt' no encontrado.
Usando credenciales predeterminadas para propósitos de desarrollo.

✅ Solución:
# Crear archivo credentials.txt
cat > credentials.txt << EOF
username=tu_email@makro.com
password=tu_password
EOF
```

### Error: Formato incorrecto en credentials.txt
```bash
ERROR al cargar credenciales: Formato incorrecto
Usando credenciales predeterminadas

✅ Solución:
# Verificar formato del archivo
# Debe contener exactamente:
username=email@ejemplo.com
password=contraseña
# Sin espacios alrededor del signo =
```

### Error: Login falla constantemente
```bash
✅ Verificar:
- Credenciales correctas en credentials.txt
- URL de Makro B2B no ha cambiado
- No hay mantenimiento en el portal
- Selectores de campos no han cambiado:
  * usernameField
  * passwordField
  * //button[@message='FND_SSO_LOGIN']
```

### Error: No se encuentra "ISUPPLIER VENDOR COMMERCIAL"
```bash
❌ Error común: Elemento no visible o cambió el texto

✅ Solución:
1. Verificar login exitoso
2. Inspeccionar elemento en navegador manual
3. Actualizar XPath si cambió:
   //div[@class='textdivresp' and text()='NUEVO_TEXTO']
4. Aumentar tiempo de espera después del login
```

### Error: No se abre la ventana del reporte
```bash
❌ Problema: Bloqueador de pop-ups activo

✅ Solución:
1. Desactivar bloqueador de pop-ups para b2b.makro.com
2. Verificar que se hace click correctamente en STOCKPOSALES
3. Aumentar tiempo de espera:
   time.sleep(15)  # En lugar de 10
```

### Error: No se puede cambiar a ventana del reporte
```bash
✅ Solución:
# Agregar logging para debug
all_windows = self.driver.window_handles
print(f"Ventanas abiertas: {len(all_windows)}")
for i, window in enumerate(all_windows):
    print(f"Ventana {i}: {window}")
```

### Error: Campos de fecha no aceptan valores
```bash
❌ Error común: IDs de campos cambiaron

✅ Verificar IDs actuales:
- BEGIN_DATE: _paramsPM_BEGIN_DATE
- END_DATE: _paramsPM_END_DATE

# Si cambiaron, actualizar en el código
begin_date_field = driver.find_element(By.ID, "NUEVO_ID")
```

### Error: Dropdowns no se despliegan
```bash
✅ Solución:
1. Aumentar tiempo de espera antes de click:
   time.sleep(7)  # En lugar de 5
2. Usar JavaScript para click forzado:
   driver.execute_script("arguments[0].click();", dropdown)
3. Verificar que el dropdown no esté oculto o deshabilitado
```

### Error: Opción Excel no se encuentra
```bash
❌ Error: Menú flotante no visible o cambió estructura

✅ Solución 1 - Aumentar tiempo de espera:
time.sleep(120)  # En lugar de 115 segundos

✅ Solución 2 - Verificar atributos del menú:
# Inspeccionar en navegador:
# - fmid puede haber cambiado
# - Texto puede ser diferente: "Excel 2007+" vs "Excel (*.xlsx)"

✅ Solución 3 - Capturar screenshot para debug:
driver.save_screenshot("debug_menu.png")
```

### Error: Archivo no se descarga
```bash
✅ Verificar:
- Directorio de descargas existe y tiene permisos
- Chrome permite descargas automáticas
- No hay descargas previas bloqueadas

# Test manual del directorio:
import os
print(os.path.exists(directorio))
print(os.access(directorio, os.W_OK))
```

### Error: Credenciales GCS inválidas
```bash
✅ Verificar:
- Archivo JSON en credentials/
- Permisos: Storage Object Admin
- credentials_path apunta al archivo correcto

# Test rápido:
from google.cloud import storage
client = storage.Client.from_service_account_json(credentials_path)
print(client.list_buckets())
```

### Error: Archivos no se suben a GCS
```bash
✅ Verificar:
- nombre_archivo_makro coincide con archivo descargado
- Bucket existe y es accesible
- Ruta de destino es válida

# Listar archivos locales:
import glob
archivos = glob.glob(os.path.join(directorio, nombre_archivo_makro))
print(f"Archivos encontrados: {archivos}")
```

### Error: Timeout en "Ver Informe" (115 segundos)
```bash
❌ Problema: Reporte tarda más de 115 segundos en generarse

✅ Solución:
# Aumentar timeout en download_excel_report():
time.sleep(180)  # 3 minutos

# O verificar tamaño del rango de fechas
# Rangos muy amplios tardan más en procesarse
```

---

## 📊 Logs y Monitoreo

### Sistema de Logging

El script usa un sistema de logging simple con el prefijo `-->`:
```python
print("-->Operación exitosa")
print("-->Esperando que el reporte se genere")
print("-->Botón 'Excel' presionado")
```

### Indicadores Visuales
```
✅ Operación exitosa
🗑️ Eliminación de archivo
⚠️ Advertencia
❌ Error
= Separadores de secciones
```

### Ejemplo de Salida
```
============================================================
MAKRO B2B AUTOMATION - INICIANDO PROCESO
============================================================
-->Credenciales cargadas exitosamente desde credentials.txt
-->Directorio creado: C:\Users\...\inventarios_b2b
-->Driver configurado para descargar en: C:\Users\...\inventarios_b2b
-->Inicio de sesion
-->Botón 'ISUPPLIER VENDOR COMMERCIAL' encontrado
-->Botón 'ISUPPLIER VENDOR COMMERCIAL' clickeado
-->Botón 'Commercial' encontrado por ID
-->Botón 'Stock and PO and Sales report' encontrado por ID
-->Cambiado a la nueva ventana del reporte
-->Campo de fecha de inicio encontrado
-->Fecha de inicio ingresada: 01/08/2025
-->Fecha final ingresada: 20/08/2025
-->Dropdown 'Totalizar tiendas' abierto
-->Opción 'No' seleccionada para 'Totalizar tiendas'
-->Dropdown 'Mostrar total empresa' abierto
-->Opción 'No' seleccionada para 'Mostrar total empresa'
-->Botón 'Aplicar' presionado
-->Esperando que el reporte se genere
-->Enlace 'Ver Informe' presionado
-->Opción 'Excel (*.xlsx)' seleccionada mediante texto
-->Descarga del archivo Excel iniciada
-->Automatización completada exitosamente

========================================
SUBIENDO ARCHIVOS A GOOGLE CLOUD STORAGE
========================================
🗑️ Eliminado del bucket: gs://bucket-quickstart_croc_830/raw/Ventas/moderno/makro/Stock and PO and Sales Report_Stock and PO and Sales Report.xlsx
✅ Subido: C:\Users\...\Stock and PO and Sales Report_Stock and PO and Sales Report.xlsx → gs://bucket-quickstart_croc_830/raw/Ventas/moderno/makro/...

==============================
LIMPIANDO ARCHIVOS LOCALES
==============================
🗑️ Eliminado local: C:\Users\...\Stock and PO and Sales Report_Stock and PO and Sales Report.xlsx

==================================================
PROCESO COMPLETADO EXITOSAMENTE
==================================================
```

### Monitoreo en Producción

Para monitoreo avanzado, implementar logging a archivo:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('makro_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Proceso iniciado")
```

---

## 🔐 Seguridad

### Buenas Prácticas Implementadas

- ✅ **Credenciales en Archivo Externo**: No hardcodeadas en código
- ✅ **Sistema de Fallback**: Desarrollo vs Producción
- ✅ **Archivo .gitignore**: Credenciales excluidas del control de versiones
- ✅ **Limpieza Automática**: Archivos sensibles eliminados post-proceso
- ✅ **Permisos de GCS Limitados**: Solo los necesarios

### Checklist de Seguridad

#### Antes de Producción
- [ ] Eliminar credenciales hardcodeadas de fallback
- [ ] Migrar a variables de entorno o secrets manager
- [ ] Implementar rotación de credenciales periódica
- [ ] Configurar alertas de fallos
- [ ] Encriptar archivo credentials.txt en reposo
- [ ] Limitar acceso al archivo de credenciales (chmod 600)
- [ ] Implementar auditoría de accesos
- [ ] Configurar firewall para acceso a Makro B2B

#### Hardening de Producción
```bash
# 1. Permisos restrictivos para credenciales
chmod 600 credentials.txt
chmod 600 credentials/*.json

# 2. Variables de entorno seguras
export MAKRO_USERNAME=$(vault read -field=username secret/makro)
export MAKRO_PASSWORD=$(vault read -field=password secret/makro)

# 3. Encriptar credenciales
gpg --encrypt credentials.txt

# 4. Usar secrets manager
aws secretsmanager create-secret \
    --name makro-credentials \
    --secret-string file://credentials.txt
```

#### Eliminar Fallback de Producción
```python
# En _load_credentials(), eliminar el fallback:
except FileNotFoundError:
    raise FileNotFoundError(f"Archivo de credenciales '{self.credentials_file}' no encontrado. Proceso abortado.")
except Exception as e:
    raise Exception(f"Error al cargar credenciales: {e}. Proceso abortado.")
```

---

## 📝 Notas Importantes

1. **Ventana del Driver**: El driver NO se cierra automáticamente al finalizar. Esto es intencional para inspección manual si es necesario.

2. **Tiempo de Generación del Reporte**: El reporte tarda **115 segundos** en generarse. Este tiempo es crítico y no debe reducirse.

3. **Formato de Fechas**: Las fechas DEBEN estar en formato **DD/MM/YYYY** (diferente a otros scripts que usan YYYY-MM-DD).

4. **Nombre del Archivo**: El archivo descargado siempre tiene el mismo nombre fijo: `Stock and PO and Sales Report_Stock and PO and Sales Report.xlsx`

5. **Reemplazo de Archivos en GCS**: Los archivos existentes en el bucket se eliminan antes de subir nuevos (no versionado).

6. **Múltiples Ventanas**: El script maneja un popup de Oracle BI. La ventana principal se mantiene abierta.

7. **Dropdowns Complejos**: Los dropdowns son elementos dinámicos de Oracle que requieren esperas específicas.

8. **Auto-ejecución**: La clase ejecuta automáticamente la secuencia completa en `__init__()`. Para control manual, modificar el código.

---

## 🔄 Mantenimiento

### Actualizar Selectores

Si Makro cambia su interfaz:
```python
# Login
username_field = driver.find_element(By.ID, "nuevo_id_username")

# Navegación
isupplier_button = driver.find_element(By.XPATH, "//div[text()='NUEVO TEXTO']")

# Parámetros del reporte
begin_date_field = driver.find_element(By.ID, "nuevo_id_fecha_inicio")
```

### Cambiar Rango de Fechas por Defecto
```python
# En configure_report_parameters():
def configure_report_parameters(self, start_date="01/01/2025", end_date="31/01/2025"):
    # Nuevos valores por defecto
```

### Agregar Nuevos Parámetros del Reporte
```python
# En configure_report_parameters(), después de las fechas:

# Nuevo parámetro: Filtro por categoría
category_field = WebDriverWait(self.driver, 10).until(
    EC.element_to_be_clickable((By.ID, "_paramsPM_CATEGORY"))
)
category_field.send_keys("CATEGORIA_DESEADA")
print("-->Categoría configurada")
```

### Configurar Tiempo de Generación Dinámico

Para reportes con rangos de fechas variables:
```python
def download_excel_report(self, wait_time=115):
    """
    Args:
        wait_time: Tiempo de espera en segundos para generación del reporte
    """
    # ...código existente...
    time.sleep(wait_time)  # En lugar de 115 hardcodeado
```

### Deshabilitar Auto-ejecución

Para más control sobre el flujo:
```python
class MakroAutomation:
    def __init__(self, credentials_file="credentials.txt", auto_run=False):
        self.credentials_file = credentials_file
        self.username, self.password = self._load_credentials()
        self.driver = None
        self.main_window = None
        
        if auto_run:
            self.run_automation()

# Uso:
automation = MakroAutomation(auto_run=False)
automation.initialize_driver()
# ...ejecutar métodos manualmente...
```

---

## 🎯 Casos de Uso

### 1. Extracción Mensual Automatizada
```python
from datetime import datetime, timedelta
from makro_automation import MakroAutomation

# Calcular primer y último día del mes anterior
today = datetime.now()
first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
last_day_last_month = today.replace(day=1) - timedelta(days=1)

# Formatear fechas
start = first_day_last_month.strftime("%d/%m/%Y")
end = last_day_last_month.strftime("%d/%m/%Y")

# Modificar la configuración
automation = MakroAutomation(auto_run=False)
automation.initialize_driver()
automation.login()
# ... navegación ...
automation.configure_report_parameters(start_date=start, end_date=end)
automation.download_excel_report()
```

### 2. Programar con Cron (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Ejecutar el primer día de cada mes a las 2 AM
0 2 1 * * cd /ruta/proyecto && /ruta/venv/bin/python makro_automation.py >> /var/log/makro.log 2>&1
```

### 3. Programar con Task Scheduler (Windows)
```powershell
# Crear tarea programada
$action = New-ScheduledTaskAction -Execute "C:\ruta\venv\Scripts\python.exe" -Argument "C:\ruta\makro_automation.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 2AM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "MakroExtraction" -Description "Extracción automática de Makro B2B"
```

### 4. Integración con Airflow
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def run_makro_extraction():
    from makro_automation import main
    main()

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'makro_b2b_extraction',
    default_args=default_args,
    description='Extracción diaria de reportes Makro B2B',
    schedule_interval='0 2 * * *',  # Diario a las 2 AM
    catchup=False
) as dag:
    
    extract_task = PythonOperator(
        task_id='extract_makro_reports',
        python_callable=run_makro_extraction
    )
```

### 5. Notificaciones por Email
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_notification(subject, body):
    msg = MIMEMultipart()
    msg['From'] = 'automation@company.com'
    msg['To'] = 'team@company.com'
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.company.com', 587)
    server.starttls()
    server.login('user', 'password')
    server.send_message(msg)
    server.quit()

# En main():
try:
    main()
    send_notification(
        "Makro B2B - Éxito",
        "Extracción completada exitosamente"
    )
except Exception as e:
    send_notification(
        "Makro B2B - Error",
        f"La extracción falló: {e}"
    )
```

### 6. Procesamiento Post-descarga
```python
from makro_automation import MakroAutomation, subir_archivos
import pandas as pd

def process_report(filepath):
    """Procesar y transformar el reporte antes de subir"""
    df = pd.read_excel(filepath)
    
    # Limpiar datos
    df = df.dropna(subset=['SKU'])
    df['Stock'] = df['Stock'].fillna(0)
    
    # Agregar metadatos
    df['fecha_extraccion'] = pd.Timestamp.now()
    df['fuente'] = 'Makro B2B'
    
    # Guardar versión procesada
    processed_path = filepath.replace('.xlsx', '_processed.xlsx')
    df.to_excel(processed_path, index=False)
    
    return processed_path

# Uso
automation = MakroAutomation()
# ... el archivo se descarga ...

# Procesar antes de subir
import glob
archivos = glob.glob(os.path.join(directorio, nombre_archivo_makro))
for archivo in archivos:
    archivo_procesado = process_report(archivo)
    # Subir archivo procesado en lugar del original
```

---

## 🤝 Contribuciones

### Guía de Contribución

1. **Fork** del repositorio
2. **Crear branch** de feature (`git checkout -b feature/MejoraMakro`)
3. **Seguir convenciones**:
   - PEP 8 para estilo
   - Docstrings en formato Google
   - Logging con prefijo `-->`
   - Manejo de excepciones robusto
4. **Agregar tests** si es posible
5. **Actualizar documentación** relevante
6. **Commit con mensajes descriptivos**:
```bash
   git commit -m "Add: Soporte para múltiples rangos de fechas"
   git commit -m "Fix: Error en selección de dropdown"
   git commit -m "Docs: Actualizar troubleshooting"
```
7. **Push** al branch (`git push origin feature/MejoraMakro`)
8. **Abrir Pull Request** con descripción detallada

### Estándares de Código
```python
# ✅ Correcto
def configure_report_parameters(
    self, 
    start_date: str = "01/08/2025", 
    end_date: str = "20/08/2025"
) -> bool:
    """
    Configura los parámetros del reporte.
    
    Args:
        start_date: Fecha de inicio en formato DD/MM/YYYY
        end_date: Fecha de fin en formato DD/MM/YYYY
        
    Returns:
        True si la configuración fue exitosa, False en caso contrario
    """
    print(f"-->Configurando reporte: {start_date} a {end_date}")
    # ... implementación
    return True

# ❌ Incorrecto (sin type hints, sin docstring, sin logging)
def configure_report_parameters(self, start_date="01/08/2025", end_date="20/08/2025"):
    # Implementación
    return True
```

---

## 📦 Despliegue

### Docker

#### Dockerfile
```dockerfile
FROM python:3.9-slim

# Instalar Chrome y dependencias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY makro_automation.py .
COPY credentials.txt .
COPY credentials/ credentials/

# Crear directorio de descargas
RUN mkdir -p /app/inventarios_b2b

# Ejecutar script
CMD ["python", "makro_automation.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  makro-automation:
    build: .
    container_name: makro-scraper
    volumes:
      - ./credentials:/app/credentials:ro
      - ./inventarios_b2b:/app/inventarios_b2b
      - /dev/shm:/dev/shm  # Para Chrome
    environment:
      - DISPLAY=:99
    restart: on-failure
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Kubernetes CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: makro-extraction
spec:
  schedule: "0 2 1 * *"  # Primer día de cada mes a las 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: makro-scraper
            image: tu-registry/makro-automation:latest
            volumeMounts:
            - name: credentials
              mountPath: /app/credentials.txt
              subPath: credentials.txt
              readOnly: true
            - name: gcs-key
              mountPath: /app/credentials
              readOnly: true
          volumes:
          - name: credentials
            secret:
              secretName: makro-credentials
          - name: gcs-key
            secret:
              secretName: gcs-credentials
          restartPolicy: OnFailure
```

---

## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

## 👤 Autor

**Creator**: Diego Mendez  
**Version**: 1.0 - Creación de Código Makro-Extracción Oracle

**Contacto**: Data Engineering Team

## 📞 Soporte

Para problemas o consultas:
- **Issues**: Crear issue en el repositorio
- **Email**: soporte-data@company.com
- **Slack**: #data-engineering
- **Documentación**: Confluence Wiki

---

## 📚 Referencias

- [Makro B2B Portal](https://b2b.makro.com/)
- [Oracle BI Publisher](https://docs.oracle.com/en/cloud/saas/analytics-cloud/analytics-desktop/bidvd.html)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Google Cloud Storage Python](https://cloud.google.com/python/docs/reference/storage/latest)

---

**Última actualización**: 2024  
**Versión**: 1.0  
**Plataforma**: Makro B2B (Oracle BI Publisher)  
**Tecnología**: Selenium + Python 3.8+ + GCS  
**Tipo de Reporte**: Stock and Purchase Orders and Sales

Archivos Adicionales Recomendados
requirements.txt
txtselenium>=4.0.0
webdriver-manager>=4.0.0
google-cloud-storage>=2.0.0
google-auth>=2.0.0
beautifulsoup4>=4.9.0
pandas>=1.3.0
openpyxl>=3.0.0
.gitignore
gitignore# Credenciales
credentials.txt
credentials/
*.json
!requirements.json

# Archivos descargados
inventarios_b2b/
Stock and PO and Sales Report*.xlsx

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

# Logs
*.log

# Temporal
temp/
tmp/
*.tmp
credentials.txt.example
txt# Credenciales de Makro B2B
# Renombrar este archivo a 'credentials.txt' y completar con tus credenciales reales
username=tu_email@ejemplo.com
password=tu_password_seguro
.env.example
bash# =====================================
# Makro B2B Automation - Configuración
# =====================================

# Credenciales Makro (alternativa a credentials.txt)
MAKRO_USERNAME=tu_email@ejemplo.com
MAKRO_PASSWORD=tu_password

# Google Cloud Storage
GCS_BUCKET_NAME=bucket-quickstart_croc_830
GCS_CREDENTIALS_PATH=credentials/tu-archivo.json

# Configuración de directorios
DOWNLOAD_DIR=C:\Users\Usuario\Downloads\Makro

# Configuración de reportes
REPORT_START_DATE=01/01/2025
REPORT_END_DATE=31/01/2025
CHANGELOG.md
markdown# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [1.0.0] - 2024-11-20

### Added
- Implementación inicial del script de automatización Makro B2B
- Clase `MakroAutomation` con métodos encapsulados
- Sistema de carga de credenciales desde archivo externo
- Navegación completa por portal B2B de Makro
- Configuración de parámetros de reporte:
  - Rango de fechas (BEGIN_DATE, END_DATE)
  - Totalizar tiendas (configuración: No)
  - Mostrar total empresa (configuración: No)
- Descarga de reporte "Stock and PO and Sales" en formato Excel
- Gestión de múltiples ventanas del navegador
- Múltiples estrategias de selección de dropdown
- Subida automática a Google Cloud Storage
- Eliminación de duplicados en bucket antes de subir
- Limpieza automática de archivos locales
- Sistema de logging con prefijo `-->`
- Indicadores visuales (✅, 🗑️, ⚠️)
- Manejo robusto de excepciones

### Features
- Auto-ejecución en `__init__()`
- Fallback de credenciales para desarrollo
- Configuración de directorio de descargas personalizado
- Espera de 115 segundos para generación de reporte
- WebDriver no se cierra automáticamente para inspección

### Security
- Credenciales en archivo externo (credentials.txt)
- Sistema de fallback solo para desarrollo
- Archivo .gitignore configurado
- No se registran credenciales en logs

## [Future]

### Planned
- Migrar a variables de entorno
- Implementar logging a archivo
- Agregar tests unitarios
- Soporte para múltiples configuraciones de reporte
- Notificaciones por email en caso de fallo
- Retry automático en caso de errores transitorios
- Monitoreo de métricas del proceso
README_QUICK_START.md
markdown# Makro B2B Automation - Quick Start

## Inicio Rápido

### 1. Configuración Inicial (5 minutos)
```bash
# Clonar repositorio
git clone 
cd makro-scraping

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# O: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Credenciales
```bash
# Crear archivo de credenciales
cat > credentials.txt << EOF
username=tu_email@makro.com
password=tu_password
EOF

# Configurar GCS
# Colocar archivo JSON en credentials/
```

### 3. Ejecutar
```bash
python makro_automation.py
```

### 4. Verificar
```bash
# Verificar archivo descargado
ls inventarios_b2b/

# Verificar en GCS
gsutil ls gs://bucket-quickstart_croc_830/raw/Ventas/moderno/makro/
```

## Troubleshooting Rápido

- **No encuentra credentials.txt**: Crear el archivo en el directorio raíz
- **Login falla**: Verificar credenciales en credentials.txt
- **No se descarga**: Esperar los 115 segundos completos
- **Error en GCS**: Verificar credentials/archivo.json

## Ayuda

Ver README.md completo para documentación detallada.
Esta documentación es completa y cubre todos los aspectos del script de Makro B2B, incluyendo el sistema único de credenciales desde archivo, el manejo de ventanas múltiples, los tiempos de espera específicos (115 segundos), y todas las particularidades del portal Oracle BI Publisher. 
