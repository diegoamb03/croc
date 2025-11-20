import requests
import json
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from datetime import datetime
import traceback
import os
import sys
import logging
import time
import google.cloud.logging
import config
from typing import Dict, List, Any, Optional
import uuid

# Configuración mejorada del logging
logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cliente de Google Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

class AccountingLogger:
    """Clase para manejar logs estructurados en Cloud Run"""
    
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.start_time = datetime.now()
    
    def log_operation(self, operation: str, status: str, details: Dict[str, Any] = None, level: str = "INFO"):
        """Log estructurado para cada operación"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "execution_id": self.execution_id,
            "operation": operation,
            "status": status,
            "details": details or {},
            "severity": level
        }
        
        if level == "ERROR":
            print(json.dumps(log_entry, ensure_ascii=False))
            logger.error(f"[{operation}] {status}: {details}")
        elif level == "WARNING":
            print(json.dumps(log_entry, ensure_ascii=False))
            logger.warning(f"[{operation}] {status}: {details}")
        else:
            print(json.dumps(log_entry, ensure_ascii=False))
            logger.info(f"[{operation}] {status}: {details}")
    
    def log_performance(self, operation: str, duration_seconds: float, additional_metrics: Dict = None):
        """Log específico para métricas de performance"""
        metrics = {
            "duration_seconds": round(duration_seconds, 3),
            "duration_ms": round(duration_seconds * 1000, 1)
        }
        if additional_metrics:
            metrics.update(additional_metrics)
        
        self.log_operation(
            operation=f"PERFORMANCE_{operation}",
            status="MEASURED",
            details=metrics
        )

def get_time_post():
    """Genera timestamp para logs y auditoría"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

def get_data_bq(project, dataset, table, partition, acc_logger: AccountingLogger):
    """
    Extrae datos contables desde BigQuery con logging detallado
    """
    operation_start = time.time()
    acc_logger.log_operation("BIGQUERY_EXTRACTION", "STARTING", {
        "project": project,
        "dataset": dataset, 
        "table": table,
        "partition": partition
    })
    
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project)
        
        acc_logger.log_operation("BIGQUERY_CLIENT", "INITIALIZED", {
            "project": project
        })
        
        # Lee la consulta SQL
        sql_file_path = f"/app/sql/get_data_bq_send.sql"
        acc_logger.log_operation("SQL_FILE", "READING", {
            "file_path": sql_file_path
        })
        
        with open(sql_file_path, "r") as f:
            query = f.read().format(
                project=project,
                dataset=dataset,
                table=table,
                partition=partition
            )
        
        acc_logger.log_operation("SQL_QUERY", "PREPARED", {
            "query_length": len(query),
            "query_preview": query[:200] + "..." if len(query) > 200 else query
        })
        
        # Ejecuta la consulta
        query_start = time.time()
        acc_logger.log_operation("BIGQUERY_QUERY", "EXECUTING", {})
        
        query_job = client.query(query)
        results = query_job.result()
        
        query_duration = time.time() - query_start
        acc_logger.log_performance("BIGQUERY_QUERY", query_duration, {
            "total_rows": results.total_rows,
            "bytes_processed": getattr(query_job, 'total_bytes_processed', 0),
            "cache_hit": getattr(query_job, 'cache_hit', False)
        })
        
        acc_logger.log_operation("BIGQUERY_EXTRACTION", "COMPLETED", {
            "total_rows": results.total_rows,
            "duration_seconds": round(query_duration, 3)
        })
        
        return results
        
    except Exception as e:
        acc_logger.log_operation("BIGQUERY_EXTRACTION", "FAILED", {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }, level="ERROR")
        raise

def upload_blob(bucket_name, object_str, destination_blob_name, acc_logger: AccountingLogger):
    """
    Sube logs al Google Cloud Storage con logging detallado
    """
    operation_start = time.time()
    acc_logger.log_operation("GCS_UPLOAD", "STARTING", {
        "bucket": bucket_name,
        "destination": destination_blob_name,
        "content_size_bytes": len(object_str.encode('utf-8'))
    })
    
    try:
        from google.cloud import storage
        
        # Validación JSON
        acc_logger.log_operation("JSON_VALIDATION", "STARTING", {})
        json.loads(object_str)
        acc_logger.log_operation("JSON_VALIDATION", "PASSED", {})
        
        # Inicialización del cliente
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        acc_logger.log_operation("GCS_CLIENT", "INITIALIZED", {
            "bucket": bucket_name
        })
        
        # Verificar archivo existente
        existing_content = ''
        if blob.exists():
            acc_logger.log_operation("GCS_EXISTING_FILE", "FOUND", {
                "destination": destination_blob_name
            })
            existing_content = blob.download_as_text()
            acc_logger.log_operation("GCS_EXISTING_CONTENT", "DOWNLOADED", {
                "existing_size_bytes": len(existing_content.encode('utf-8'))
            })
        else:
            acc_logger.log_operation("GCS_EXISTING_FILE", "NOT_FOUND", {
                "destination": destination_blob_name
            })
        
        # Combinar contenido
        combined_content = existing_content + object_str
        final_size = len(combined_content.encode('utf-8'))
        
        acc_logger.log_operation("GCS_CONTENT", "COMBINED", {
            "final_size_bytes": final_size,
            "new_content_size": len(object_str.encode('utf-8')),
            "existing_content_size": len(existing_content.encode('utf-8'))
        })
        
        # Subir contenido
        upload_start = time.time()
        blob.upload_from_string(
            combined_content,
            content_type="application/json"
        )
        upload_duration = time.time() - upload_start
        
        acc_logger.log_performance("GCS_UPLOAD", upload_duration, {
            "bytes_uploaded": final_size,
            "throughput_mbps": round((final_size / 1024 / 1024) / upload_duration, 2) if upload_duration > 0 else 0
        })
        
        acc_logger.log_operation("GCS_UPLOAD", "COMPLETED", {
            "destination": destination_blob_name,
            "final_size_bytes": final_size
        })
        
    except json.JSONDecodeError as e:
        acc_logger.log_operation("JSON_VALIDATION", "FAILED", {
            "error": str(e),
            "content_preview": object_str[:500]
        }, level="ERROR")
        raise
        
    except Exception as e:
        acc_logger.log_operation("GCS_UPLOAD", "FAILED", {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }, level="ERROR")
        raise

def insert_bq(tabla_insert, obj_json, acc_logger: AccountingLogger):
    """
    Inserta logs de auditoría en BigQuery con logging detallado
    """
    operation_start = time.time()
    acc_logger.log_operation("BIGQUERY_INSERT_LOG", "STARTING", {
        "table": tabla_insert,
        "transaction_id": obj_json.get("transaction_id", "unknown")
    })
    
    try:
        from google.cloud import bigquery
        client = bigquery.Client()
        
        # Preparar datos para inserción
        obj_json_copy = obj_json.copy()
        obj_json_copy["json_send"] = json.dumps(obj_json_copy["json_send"])
        obj_json_copy["json_response"] = json.dumps(obj_json_copy["json_response"])
        
        acc_logger.log_operation("BIGQUERY_DATA", "PREPARED", {
            "json_send_size": len(obj_json_copy["json_send"]),
            "json_response_size": len(obj_json_copy["json_response"])
        })
        
        # Insertar datos
        insert_start = time.time()
        errores = client.insert_rows_json(
            tabla_insert, [obj_json_copy], ignore_unknown_values=True
        )
        insert_duration = time.time() - insert_start
        
        if errores == []:
            acc_logger.log_performance("BIGQUERY_INSERT_LOG", insert_duration)
            acc_logger.log_operation("BIGQUERY_INSERT_LOG", "COMPLETED", {
                "table": tabla_insert,
                "transaction_id": obj_json.get("transaction_id", "unknown")
            })
        else:
            acc_logger.log_operation("BIGQUERY_INSERT_LOG", "FAILED", {
                "errors": errores,
                "table": tabla_insert,
                "transaction_id": obj_json.get("transaction_id", "unknown")
            }, level="ERROR")
        
        return errores
        
    except Exception as e:
        acc_logger.log_operation("BIGQUERY_INSERT_LOG", "FAILED", {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "table": tabla_insert
        }, level="ERROR")
        raise

def publishMessageSend(data, nro_total_rows, transaction_id, acc_logger: AccountingLogger):
    """
    Envía datos contables a la API externa con logging detallado
    """
    operation_start = time.time()
    request_id = str(uuid.uuid4())[:8]  # ID único para esta petición
    
    acc_logger.log_operation("API_REQUEST", "STARTING", {
        "transaction_id": transaction_id,
        "request_id": request_id,
        "total_rows_in_batch": nro_total_rows,
        "journal_rows": len(data['GLJournal']['Journal']['Row'])
    })
    
    log_str = ""
    time_init = get_time_post()
    
    # Estructura base del log
    log_dict = {
        "country": "", "entity": "", "execution_date": "", "nro_total_rows": 0, "transaction_id": "",
        "executionRecordId": 0, "description": "", "date_partition": "", "email": "", "category_name": "",
        "api_url": "", "status_code": "", "status": "Error", "type_send": "", 
        "ts_execution_start": "", "ts_execution_end": "", "json_send": "", "json_response": "",
        "error": "", "error_detail": "", "execution_id": "", "request_id": request_id
    }
    
    try:
        # Preparar datos JSON
        json_data_str = json.dumps(data)
        accounting_date = data['GLJournal']['Journal']['Row'][0]['AccountingDate']
        
        acc_logger.log_operation("JSON_PREPARATION", "COMPLETED", {
            "transaction_id": transaction_id,
            "request_id": request_id,
            "accounting_date": accounting_date,
            "json_size_bytes": len(json_data_str.encode('utf-8')),
            "journal_rows": len(data['GLJournal']['Journal']['Row'])
        })
        
        # Llenar log_dict con información básica
        log_dict.update({
            "country": country,
            "entity": entity,
            "execution_date": time_init[:10],
            "nro_total_rows": nro_total_rows,
            "transaction_id": transaction_id,
            "description": data['GLJournal']['Journal']['Row'][0]['Reference10'],
            "date_partition": accounting_date,
            "email": email,
            "category_name": data['GLJournal']['Journal']['Row'][0]['UserJeCategoryName'],
            "api_url": config.api_url_send,
            "type_send": type_send,
            "ts_execution_start": time_init,
            "json_send": json_data_str,
            "execution_id": execution_id,
            "request_id": request_id
        })
        
        acc_logger.log_operation("HTTP_REQUEST", "PREPARING", {
            "transaction_id": transaction_id,
            "request_id": request_id,
            "url": config.api_url_send,
            "timeout": post_timeout,
            "content_type": "application/json"
        })
        
        # Realizar petición HTTP
        http_start = time.time()
        response = requests.post(
            config.api_url_send, 
            auth=(config.username_send, config.password_send), 
            data=json_data_str, 
            headers={'Content-Type': 'application/json'}, 
            timeout=post_timeout
        )
        http_duration = time.time() - http_start
        
        log_dict["status_code"] = response.status_code
        
        acc_logger.log_performance("HTTP_REQUEST", http_duration, {
            "transaction_id": transaction_id,
            "request_id": request_id,
            "status_code": response.status_code,
            "response_size_bytes": len(response.content),
            "request_size_bytes": len(json_data_str.encode('utf-8'))
        })
        
        # Procesar respuesta
        if response.status_code == 200:
            acc_logger.log_operation("HTTP_RESPONSE", "SUCCESS_200", {
                "transaction_id": transaction_id,
                "request_id": request_id,
                "response_size": len(response.content)
            })
            
            try:
                response_json = response.json()
                log_dict["status"] = response_json['GLJournalResponse']['Status']
                log_dict["executionRecordId"] = response_json['GLJournalResponse']['ExecutionRecordId']
                log_dict["json_response"] = response_json
                
                if log_dict["status"] == "S":
                    acc_logger.log_operation("ACCOUNTING_ENTRY", "SUCCESS", {
                        "transaction_id": transaction_id,
                        "request_id": request_id,
                        "execution_record_id": log_dict["executionRecordId"],
                        "api_status": log_dict["status"]
                    })
                else:
                    acc_logger.log_operation("ACCOUNTING_ENTRY", "BUSINESS_ERROR", {
                        "transaction_id": transaction_id,
                        "request_id": request_id,
                        "api_status": log_dict["status"],
                        "api_message": response_json['GLJournalResponse'].get('Message', 'No message')
                    }, level="WARNING")
                    log_dict["error"] = response_json['GLJournalResponse']['Message']
                    
            except json.JSONDecodeError as e:
                acc_logger.log_operation("JSON_RESPONSE", "PARSE_ERROR", {
                    "transaction_id": transaction_id,
                    "request_id": request_id,
                    "error": str(e),
                    "response_preview": response.text[:500]
                }, level="ERROR")
                log_dict["json_response"] = response.text
                log_dict["error"] = f"JSON parse error: {str(e)}"
                
        else:
            # Errores HTTP
            http_error_status_dict = {
                "400": "Bad Request", "401": "Unauthorized", "403": "Forbidden", 
                "404": "Not Found", "500": "Internal Server Error", "502": "Bad Gateway",
                "503": "Service Unavailable", "504": "Gateway Timeout"
            }
            
            error_status = http_error_status_dict.get(str(response.status_code), "Unknown Error")
            log_dict["status"] = error_status
            
            acc_logger.log_operation("HTTP_RESPONSE", f"ERROR_{response.status_code}", {
                "transaction_id": transaction_id,
                "request_id": request_id,
                "status_code": response.status_code,
                "error_status": error_status,
                "response_preview": response.text[:500]
            }, level="ERROR")
            
            try:
                log_dict["json_response"] = response.json()
            except:
                log_dict["json_response"] = response.text
            
            log_dict["error_detail"] = str(traceback.format_exc())
            
    except requests.exceptions.Timeout as e:
        acc_logger.log_operation("HTTP_REQUEST", "TIMEOUT", {
            "transaction_id": transaction_id,
            "request_id": request_id,
            "timeout_seconds": post_timeout,
            "error": str(e)
        }, level="ERROR")
        log_dict["status_code"] = 408
        log_dict["error"] = f"Request timeout after {post_timeout} seconds"
        log_dict["error_detail"] = str(traceback.format_exc())
        
    except requests.exceptions.ConnectionError as e:
        acc_logger.log_operation("HTTP_REQUEST", "CONNECTION_ERROR", {
            "transaction_id": transaction_id,
            "request_id": request_id,
            "error": str(e)
        }, level="ERROR")
        log_dict["status_code"] = 503
        log_dict["error"] = f"Connection error: {str(e)}"
        log_dict["error_detail"] = str(traceback.format_exc())
        
    except Exception as e:
        acc_logger.log_operation("API_REQUEST", "UNEXPECTED_ERROR", {
            "transaction_id": transaction_id,
            "request_id": request_id,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }, level="ERROR")
        log_dict["status_code"] = 999
        log_dict["error"] = str(e)
        log_dict["error_detail"] = str(traceback.format_exc())
    
    # Finalizar log
    time_fin = get_time_post()
    log_dict["ts_execution_end"] = time_fin
    total_duration = time.time() - operation_start
    
    acc_logger.log_performance("API_REQUEST_COMPLETE", total_duration, {
        "transaction_id": transaction_id,
        "request_id": request_id,
        "final_status": log_dict["status"],
        "status_code": log_dict["status_code"]
    })
    
    log_str += json.dumps(log_dict, ensure_ascii=False) + "\n"
    
    # Insertar en BigQuery
    try:
        insert_bq(table_log_send, log_dict, acc_logger)
    except Exception as e:
        acc_logger.log_operation("LOG_PERSISTENCE", "FAILED", {
            "transaction_id": transaction_id,
            "request_id": request_id,
            "error": str(e)
        }, level="ERROR")
    
    # Preparar archivo para GCS (si está habilitado)
    name_file = f"{file_name}_{accounting_date.replace('-','')}{config.entity_code}0000.json"
    path_file = f"{entity}/{accounting_date}/{name_file}"
    
    acc_logger.log_operation("API_REQUEST", "COMPLETED", {
        "transaction_id": transaction_id,
        "request_id": request_id,
        "total_duration_seconds": round(total_duration, 3),
        "final_status": log_dict["status"],
        "log_file_path": path_file
    })
    
    return log_str

def publish_concurrency_send(acc_logger: AccountingLogger):
    """
    Función principal mejorada con logging detallado
    """
    overall_start = time.time()
    acc_logger.log_operation("BATCH_PROCESSING", "STARTING", {
        "partition": partition,
        "max_threads": n_max_threads
    })
    
    try:
        # Extraer datos
        data = list(get_data_bq(project, dataset, table_send, partition, acc_logger))
        nro_total_rows = len(data)
        
        acc_logger.log_operation("DATA_EXTRACTION", "COMPLETED", {
            "total_rows": nro_total_rows,
            "partition": partition
        })
        
        if nro_total_rows == 0:
            acc_logger.log_operation("BATCH_PROCESSING", "NO_DATA", {
                "partition": partition
            })
            return {"status": 204, "message": "No data to process"}
        
        # Determinar workers
        max_works = min(n_max_threads, nro_total_rows)
        acc_logger.log_operation("THREAD_POOL", "CONFIGURED", {
            "max_threads_config": n_max_threads,
            "total_rows": nro_total_rows,
            "actual_workers": max_works
        })
        
        # Agrupar por transaction_id
        grouping_start = time.time()
        grouped_results = {}
        
        for row in data:
            transaction_id = row["TRANSACTION_ID"]
            if transaction_id not in grouped_results:
                grouped_results[transaction_id] = []
            grouped_results[transaction_id].append({
                "Status": row["Status"],
                "LedgerId": row["LedgerId"],
                "AccountingDate": row["AccountingDate"],
                "UserJeSourceName": row["UserJeSourceName"],
                "UserJeCategoryName": row["UserJeCategoryName"],
                "CurrencyCode": row["CurrencyCode"],
                "BalanceType": row["BalanceType"],
                "Segment1": row["Segment1"], "Segment2": row["Segment2"],
                "Segment3": row["Segment3"], "Segment4": row["Segment4"],
                "Segment5": row["Segment5"], "Segment6": row["Segment6"],
                "Segment7": row["Segment7"], "Segment8": row["Segment8"],
                "Segment9": row["Segment9"], "Segment10": row["Segment10"],
                "EnteredDrAmount": row["EnteredDrAmount"],
                "EnteredCrAmount": row["EnteredCrAmount"],
                "Reference10": row["Reference10"],
                "CurrencyConversionDate": row["CurrencyConversionDate"],
                "UserCurrencyConversionType": row["UserCurrencyConversionType"],
                "CurrencyConversionRate": row["CurrencyConversionRate"]
            })
        
        grouping_duration = time.time() - grouping_start
        unique_transactions = len(grouped_results)
        
        acc_logger.log_performance("DATA_GROUPING", grouping_duration, {
            "total_rows": nro_total_rows,
            "unique_transactions": unique_transactions,
            "avg_rows_per_transaction": round(nro_total_rows / unique_transactions, 2) if unique_transactions > 0 else 0
        })
        
        # Procesamiento concurrente
        processing_start = time.time()
        total_log_str = ""
        successful_transactions = 0
        failed_transactions = 0
        
        acc_logger.log_operation("CONCURRENT_PROCESSING", "STARTING", {
            "unique_transactions": unique_transactions,
            "workers": max_works
        })
        
        with PoolExecutor(max_works) as executor:
            futures = []
            
            for transaction_id, rows in grouped_results.items():
                data_json = {
                    "GLJournal": {
                        "Email": email,
                        "Language": language,
                        "AppName": app_name,
                        "Country": country.upper(),
                        "TransactionId": str(transaction_id),
                        "Journal": {"Row": rows}
                    }
                }
                
                acc_logger.log_operation("TRANSACTION_SUBMIT", "QUEUED", {
                    "transaction_id": transaction_id,
                    "journal_rows": len(rows),
                    "accounting_date": rows[0]['AccountingDate'] if rows else 'unknown'
                })
                
                future = executor.submit(publishMessageSend, data_json, nro_total_rows, transaction_id, acc_logger)
                futures.append((future, transaction_id))
            
            # Recopilar resultados
            for future, transaction_id in futures:
                try:
                    result = future.result()
                    total_log_str += result
                    successful_transactions += 1
                    
                    acc_logger.log_operation("TRANSACTION_RESULT", "SUCCESS", {
                        "transaction_id": transaction_id
                    })
                    
                except Exception as e:
                    failed_transactions += 1
                    acc_logger.log_operation("TRANSACTION_RESULT", "FAILED", {
                        "transaction_id": transaction_id,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }, level="ERROR")
        
        processing_duration = time.time() - processing_start
        overall_duration = time.time() - overall_start
        
        acc_logger.log_performance("CONCURRENT_PROCESSING", processing_duration, {
            "unique_transactions": unique_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "success_rate_percent": round((successful_transactions / unique_transactions) * 100, 2) if unique_transactions > 0 else 0,
            "avg_transaction_time": round(processing_duration / unique_transactions, 3) if unique_transactions > 0 else 0
        })
        
        acc_logger.log_operation("BATCH_PROCESSING", "COMPLETED", {
            "total_duration_seconds": round(overall_duration, 3),
            "total_rows_processed": nro_total_rows,
            "unique_transactions": unique_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "throughput_transactions_per_second": round(unique_transactions / overall_duration, 2) if overall_duration > 0 else 0
        })
        
        return {
            "status": 200 if failed_transactions == 0 else 206,
            "message": "Processing completed",
            "stats": {
                "total_rows": nro_total_rows,
                "unique_transactions": unique_transactions,
                "successful": successful_transactions,
                "failed": failed_transactions,
                "duration_seconds": round(overall_duration, 3)
            }
        }
        
    except Exception as e:
        acc_logger.log_operation("BATCH_PROCESSING", "FAILED", {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }, level="ERROR")
        raise