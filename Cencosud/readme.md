📄 Cencosud Web Scraping - Documentación
markdown# Cencosud Web Scraping Automation

Script automatizado para descargar archivos de inventario y ventas desde la plataforma Cencosud B2B y sincronizarlos con Google Cloud Storage.

## 📋 Descripción

Este script de Python utiliza Selenium para automatizar el proceso completo de:
- Login en la plataforma Cencosud B2B
- Descarga de reportes de inventario y ventas
- Extracción de archivos ZIP
- Subida automática a Google Cloud Storage
- Limpieza de archivos temporales

## ✨ Características

- ✅ Automatización completa sin intervención manual (excepto CAPTCHA)
- ✅ Gestión automática de versiones de ChromeDriver con WebDriverManager
- ✅ Clasificación inteligente de archivos (inventario vs ventas)
- ✅ Sincronización bidireccional con Google Cloud Storage
- ✅ Limpieza automática de archivos locales y en bucket
- ✅ Manejo robusto de errores y logging detallado
- ✅ Validación de descargas y uploads

## 🔧 Requisitos Previos

### Software Necesario
- Python 3.8 o superior
- Google Chrome (versión actualizada)
- Cuenta de Google Cloud Platform con permisos de Storage

### Dependencias Python
```bash
selenium>=4.0.0
webdriver-manager>=4.0.0
google-cloud-storage>=2.0.0
```

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone 
cd cencosud-scraping
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

### 4. Configurar credenciales de Google Cloud
- Descargar el archivo JSON de credenciales desde Google Cloud Console
- Colocar el archivo en el directorio del proyecto
- Actualizar la variable `CREDENTIALS_FILE` en el script

## ⚙️ Configuración

### Variables de Configuración Principal
```python
# Directorio de trabajo local
DIRECTORIO = r"C:\Users\dani\OneDrive\Web Scaping\Cencosud"

# Configuración de Google Cloud Storage
BUCKET_NAME = "bucket-quickstart_croc_830"
CREDENTIALS_FILE = "croc-454221-e1a3c2e02181.json"
RUTA_VENTAS = "raw/Ventas/moderno/cencosud/ventas"
RUTA_INVENTARIO = "raw/Ventas/moderno/cencosud/inventario"

# Credenciales de acceso (usar variables de entorno en producción)
EMAIL = "tu-email@ejemplo.com"
PASSWORD = "tu-contraseña"
```

### ⚠️ Seguridad - Variables de Entorno

**IMPORTANTE**: Para producción, usar variables de entorno en lugar de hardcodear credenciales:
```python
import os
EMAIL = os.getenv('CENCOSUD_EMAIL')
PASSWORD = os.getenv('CENCOSUD_PASSWORD')
```

## 🚀 Uso

### Ejecución Básica
```bash
python cencosud_scraper.py
```

### Interacción Manual Requerida
Durante el proceso de login, será necesario:
1. Resolver el CAPTCHA manualmente (interacción humana requerida)
2. El script continuará automáticamente después del CAPTCHA

## 📁 Estructura del Proyecto
```
cencosud-scraping/
├── cencosud_scraper.py          # Script principal
├── croc-454221-e1a3c2e02181.json  # Credenciales GCS (no incluir en git)
├── requirements.txt              # Dependencias Python
├── README.md                     # Esta documentación
├── .gitignore                    # Archivos a ignorar
└── extraidos/                    # Carpeta temporal (creada automáticamente)
```

## 🔄 Flujo del Proceso
```
1. Configuración del WebDriver
   ↓
2. Login en Plataforma Cencosud
   ├── Ingreso de credenciales
   ├── Resolución de CAPTCHA (manual)
   └── Selección de país (Colombia)
   ↓
3. Descarga de Inventario
   ├── Navegación a Abastecimiento → Detalle de Inventario
   ├── Generación de informe
   └── Descarga de archivo ZIP
   ↓
4. Descarga de Ventas
   ├── Navegación a Comercial → Ventas por Período
   ├── Generación de informe
   └── Descarga de archivo ZIP
   ↓
5. Procesamiento Local
   ├── Extracción de archivos XLSX de los ZIP
   └── Clasificación (inventario/ventas)
   ↓
6. Sincronización con GCS
   ├── Limpieza de archivos antiguos en bucket
   ├── Subida de nuevos archivos
   └── Verificación de integridad
   ↓
7. Limpieza Local
   ├── Eliminación de archivos ZIP
   └── Eliminación de archivos XLSX temporales
```

## 🛠️ Funciones Principales

### `setup_driver()`
Configura y crea la instancia de Selenium WebDriver con Chrome.

### `login_process(driver)`
Automatiza el proceso de login en la plataforma Cencosud.

### `descargar_inventario(driver)`
Navega y descarga el reporte de inventario.

### `descargar_ventas(driver)`
Navega y descarga el reporte de ventas.

### `extraer_archivos_zip()`
Extrae archivos XLSX de los ZIP descargados.

### `subir_archivos_bucket()`
Sube archivos procesados a Google Cloud Storage.

### `limpiar_archivos_locales()`
Elimina archivos temporales del sistema local.

## 🐛 Troubleshooting

### Error: ChromeDriver no compatible
```
✅ Solución: El script usa webdriver-manager que descarga automáticamente 
la versión correcta. Si falla, actualizar Chrome browser.
```

### Error: No se puede resolver CAPTCHA
```
⚠️ El CAPTCHA requiere interacción humana. Esperar a que aparezca 
la casilla de verificación y hacer clic manualmente.
```

### Error: Timeout en elementos
```
✅ Solución: Aumentar los tiempos de espera en las funciones:
WebDriverWait(driver, 20)  # Incrementar de 10 a 20 segundos
```

### Error: Credenciales GCS inválidas
```
✅ Verificar:
- Archivo JSON en el directorio correcto
- Permisos de Storage Object Admin en GCP
- Nombre del bucket correcto
```

### Error: Archivos no se descargan
```
✅ Verificar:
- DIRECTORIO existe y tiene permisos de escritura
- No hay descargas previas pendientes
- Navegador permite descargas automáticas
```

## 📊 Logs y Monitoreo

El script proporciona logging detallado en consola:
- ✅ Operaciones exitosas
- ⚠️ Advertencias
- ❌ Errores críticos
- 📊 Información de archivos procesados

## 🔐 Seguridad

### Buenas Prácticas Implementadas
- ✅ Uso de variables para credenciales (migrar a env vars)
- ✅ Eliminación automática de archivos temporales
- ✅ Validación de permisos GCS

### Mejoras Recomendadas
- [ ] Migrar credenciales a variables de entorno
- [ ] Implementar encriptación de credenciales locales
- [ ] Agregar autenticación de dos factores si está disponible
- [ ] Implementar rotación de credenciales

## 📝 Notas Importantes

1. **CAPTCHA**: Requiere interacción humana durante el login
2. **Límite de Ejecución**: No ejecutar más de una vez por hora para evitar bloqueos
3. **Archivos Temporales**: Se limpian automáticamente después de cada ejecución
4. **Bucket GCS**: Los archivos antiguos se sobrescriben automáticamente

## 🔄 Actualizaciones y Mantenimiento

### Actualizar Dependencias
```bash
pip install --upgrade -r requirements.txt
```

### Verificar Compatibilidad
```bash
python --version  # Debe ser >= 3.8
google-chrome --version  # Verificar versión de Chrome
```

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

## 👤 Autor

Desarrollado para automatización de procesos de descarga Cencosud.

## 📞 Soporte

Para problemas o consultas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

---

**Última actualización**: 2024
**Versión**: 1.0.0

También te recomiendo crear estos archivos adicionales:
requirements.txt
txtselenium>=4.0.0
webdriver-manager>=4.0.0
google-cloud-storage>=2.0.0
.gitignore
gitignore# Credenciales
*.json
!requirements.json

# Archivos descargados
*.zip
*.xlsx
extraidos/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Sistema
.DS_Store
Thumbs.db
