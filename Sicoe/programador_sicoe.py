import schedule
import time
import subprocess
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def ejecutar_sicoe():
    logger.info("Iniciando ejecución de SICOE...")
    try:
        result = subprocess.run([
            "python", "sicoe_detail_sales.py"
        ], cwd=r"C:\Users\Lenovo\Downloads\scripts\Sicoe")
        
        if result.returncode == 0:
            logger.info("Script SICOE completado exitosamente")
        else:
            logger.error("Error en la ejecución del script")
    except Exception as e:
        logger.error(f"Error: {e}")

# Programar ejecución diaria
schedule.every().day.at("14:47").do(ejecutar_sicoe)

# Para pruebas: cada 5 minutos
# schedule.every(5).minutes.do(ejecutar_sicoe)

print("Programador iniciado. Ejecución programada diariamente a las 02:47 PM")
print("Presiona Ctrl+C para detener")

while True:
    schedule.run_pending()
    time.sleep(60)