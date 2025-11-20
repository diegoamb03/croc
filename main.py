#!/usr/bin/env python3
"""
Scheduler MULTI-SCRIPTS - Versión sin emojis para Windows
Compatible con todas las consolas de Windows
"""

import schedule
import subprocess
import sys
import time
import logging
from datetime import datetime
import os
from pathlib import Path

# CONFIGURACION DE SCRIPTS
SCRIPTS = {
    "Cencosud": {
        "ruta": r"C:\Users\Diego Mendez\Documents\Web Scaping\Cencosud\main_cencosud.py",
        "descripcion": "Script de Cencosud",
        "timeout": 300
    },
    "Exito": {
        "ruta": r"C:\Users\Diego Mendez\Documents\Web Scaping\Exito\Main_exito.py",
        "descripcion": "Script de Exito",
        "timeout": 300
    },
    "Inventarios_b2b": {
        "ruta": r"C:\Users\Diego Mendez\Documents\Web Scaping\inventarios_b2b\main_b2b.py",
        "descripcion": "Script de inventarios B2B",
        "timeout": 300
    },
    "Sicoe": {
        "ruta": r"C:\Users\Diego Mendez\Documents\Web Scaping\Sicoe\sicoe_detail_sales.py",
        "descripcion": "Script de Sicoe",
        "timeout": 300
    },
    "Sicoe_Rutas": {
    "ruta": r"C:\Users\Diego Mendez\Documents\Web Scaping\Sicoe\sicoe_rutas.py",
    "descripcion": "Script de Rutas por Vendedor SICOE",
    "timeout": 300
}
    
}

def configurar_logging():
    """Configura el sistema de logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'scheduler.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def ejecutar_script(nombre_script):
    """Ejecuta un script específico"""
    if nombre_script not in SCRIPTS:
        logger.error(f"[ERROR] Script '{nombre_script}' no configurado")
        return False
    
    script_info = SCRIPTS[nombre_script]
    ruta = script_info["ruta"]
    descripcion = script_info["descripcion"]
    timeout = script_info.get("timeout", 300)
    
    logger.info("="*60)
    logger.info(f"[INICIO] Ejecutando: {descripcion}")
    logger.info(f"[ARCHIVO] {os.path.basename(ruta)}")
    logger.info(f"[TIMEOUT] {timeout} segundos")
    logger.info("="*60)
    
    if not os.path.exists(ruta):
        logger.error(f"[ERROR] Archivo no encontrado: {ruta}")
        return False
    
    try:
        inicio = time.time()
        
        resultado = subprocess.run(
            [sys.executable, ruta], 
            cwd=os.path.dirname(ruta),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        duracion = time.time() - inicio
        
        if resultado.returncode == 0:
            logger.info(f"[EXITO] Script completado exitosamente en {duracion:.1f}s")
            if resultado.stdout.strip():
                logger.info(f"[OUTPUT] {resultado.stdout.strip()}")
            return True
        else:
            logger.error(f"[FALLO] Script falló (código: {resultado.returncode}) en {duracion:.1f}s")
            if resultado.stderr.strip():
                logger.error(f"[ERROR] {resultado.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"[TIMEOUT] Script excedió timeout de {timeout}s")
        return False
    except Exception as e:
        logger.error(f"[EXCEPCION] Error ejecutando script: {e}")
        return False
    finally:
        logger.info("="*60)

def ejecutar_todos_los_scripts():
    """Ejecuta todos los scripts configurados"""
    logger.info("[INICIO GRUPAL] Ejecutando todos los scripts")
    
    exitosos = 0
    fallidos = 0
    
    for nombre in SCRIPTS.keys():
        if ejecutar_script(nombre):
            exitosos += 1
        else:
            fallidos += 1
    
    logger.info(f"[FIN GRUPAL] Completado: {exitosos} exitosos, {fallidos} fallidos")
    return exitosos, fallidos

def configurar_horarios():
    """Configura todos los horarios de ejecución"""
    
    # Horarios individuales espaciados
    schedule.every().day.at("18:00").do(ejecutar_script, "Cencosud")     
    schedule.every().day.at("18:10").do(ejecutar_script, "Exito")         
    schedule.every().day.at("18:20").do(ejecutar_script, "Inventarios_b2b")
    schedule.every().day.at("18:30").do(ejecutar_script, "Sicoe")  
    schedule.every().day.at("18:40").do(ejecutar_script, "Sicoe_Rutas")        

    # Ejecución grupal al final del día
    schedule.every().day.at("10:37").do(ejecutar_todos_los_scripts)       
    schedule.every().day.at("23:00").do(ejecutar_todos_los_scripts) 

def verificar_scripts():
    """Verifica que todos los scripts configurados existan"""
    logger.info("[VERIFICACION] Checking scripts configurados...")
    scripts_validos = {}
    
    for nombre, info in SCRIPTS.items():
        ruta = info["ruta"]
        if os.path.exists(ruta):
            logger.info(f"[OK] {info['descripcion']}: {os.path.basename(ruta)}")
            scripts_validos[nombre] = info
        else:
            logger.error(f"[FALTA] {info['descripcion']}: {ruta}")
    
    return scripts_validos

def mostrar_configuracion_horarios():
    """Muestra los horarios configurados"""
    logger.info("\n[HORARIOS CONFIGURADOS]")
    logger.info("-" * 50)
    
    for job in schedule.jobs:
        next_run = job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else "No programado"
        logger.info(f"   {next_run} - {job.job_func.__name__}")
    
    logger.info("-" * 50)

def mostrar_proximas_ejecuciones():
    """Muestra las próximas ejecuciones programadas"""
    if not schedule.jobs:
        logger.info("[INFO] No hay trabajos programados")
        return
    
    logger.info("\n[PROXIMAS EJECUCIONES]")
    logger.info("-" * 60)
    
    jobs_ordenados = sorted(schedule.jobs, key=lambda x: x.next_run)
    
    for job in jobs_ordenados:
        next_run = job.next_run.strftime('%Y-%m-%d %H:%M:%S')
        time_until = job.next_run - datetime.now()
        hours_until = time_until.total_seconds() / 3600
        
        func_name = getattr(job.job_func, '__name__', str(job.job_func))
        logger.info(f"   {next_run} (en {hours_until:.1f}h) - {func_name}")
    
    logger.info("-" * 60)

def mostrar_menu():
    """Muestra un menú interactivo"""
    print("\n" + "="*50)
    print("MENU DE TESTING")
    print("="*50)
    print("1. Ejecutar script específico")
    print("2. Ejecutar todos los scripts")
    print("3. Ver scripts configurados")
    print("4. Ver próximas ejecuciones")
    print("5. Iniciar scheduler automático")
    print("0. Salir")
    print("="*50)

def menu_interactivo():
    """Ejecuta el menú interactivo"""
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (0-5): ").strip()
        
        if opcion == "0":
            logger.info("[SALIDA] Hasta luego!")
            break
        elif opcion == "1":
            print("\nScripts disponibles:")
            for i, (nombre, info) in enumerate(SCRIPTS.items(), 1):
                print(f"{i}. {info['descripcion']} ({nombre})")
            
            try:
                num = int(input("Número de script: ")) - 1
                nombres = list(SCRIPTS.keys())
                if 0 <= num < len(nombres):
                    ejecutar_script(nombres[num])
                else:
                    logger.error("[ERROR] Número inválido")
            except ValueError:
                logger.error("[ERROR] Ingresa un número válido")
                
        elif opcion == "2":
            ejecutar_todos_los_scripts()
            
        elif opcion == "3":
            verificar_scripts()
            
        elif opcion == "4":
            mostrar_proximas_ejecuciones()
            
        elif opcion == "5":
            logger.info("[INICIO] Iniciando scheduler automático...")
            break
        else:
            logger.error("[ERROR] Opción inválida")

if __name__ == "__main__":
    logger = configurar_logging()
    
    logger.info("[INICIO] SCHEDULER MULTI-SCRIPTS v2.0")
    logger.info("=" * 50)
    
    # Verificar scripts
    scripts_validos = verificar_scripts()
    
    if not scripts_validos:
        logger.error("[ERROR] No hay scripts válidos configurados")
        input("Presiona Enter para salir...")
        exit()
    
    # Configurar horarios
    configurar_horarios()
    mostrar_configuracion_horarios()
    
    # Menú principal
    print(f"\n¿Qué quieres hacer?")
    print("1. Iniciar scheduler automático")
    print("2. Menú interactivo de testing")
    
    opcion = input("Opción (1-2): ").strip()
    
    if opcion == "2":
        menu_interactivo()
    
    # Iniciar scheduler
    logger.info("\n[SCHEDULER] Iniciado correctamente")
    logger.info("[INFO] Presiona Ctrl+C para detener")
    mostrar_proximas_ejecuciones()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Revisa cada 30 segundos
    except KeyboardInterrupt:
        logger.info("\n[DETENIDO] Scheduler detenido por usuario")
        logger.info("[SALIDA] Hasta luego!")