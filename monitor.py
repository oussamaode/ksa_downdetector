#!/usr/bin/env python3
import json
import ssl
import time
import warnings
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.ssl_ import create_urllib3_context
from requests.exceptions import (
    RequestException,
    ConnectionError,
    Timeout,
    HTTPError,
    TooManyRedirects,
)

warnings.simplefilter("ignore", InsecureRequestWarning)

# User-Agent realista que simula un navegador moderno para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

TIMEOUT_SECONDS = 10.0

# Codigos que indican proteccion anti-bot: el servidor responde, no esta caido
ANTI_BOT_CODES = {401, 403, 405, 429, 999}


class TLSAdapter(HTTPAdapter):
    """
    Adaptador TLS para sitios con cadena de certificados incompleta
    o suites cifradas que OpenSSL 3 rechaza por defecto (ej. alahli.com).
    """

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)


def build_session(verify_ssl: bool) -> requests.Session:
    session = requests.Session()
    if not verify_ssl:
        session.mount("https://", TLSAdapter())
    return session


def check_platform(platform: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprueba el estado de salud de una plataforma individual.
    
    Args:
        platform: Diccionario con los campos 'id', 'nombre_en', 'nombre_ar', 'url'
                  y opcionalmente 'verify_ssl' (default True)
    
    Returns:
        Diccionario con 'id', 'nombre_en', 'nombre_ar', 'url', 'status', 'response_time'
    """
    platform_id = platform.get("id", "")
    nombre_en = platform.get("nombre_en", "")
    nombre_ar = platform.get("nombre_ar", "")
    url = platform.get("url", "")
    verify_ssl = platform.get("verify_ssl", True)
    
    result = {
        "id": platform_id,
        "nombre_en": nombre_en,
        "nombre_ar": nombre_ar,
        "url": url,
        "status": "OFFLINE",
        "response_time": None,
    }
    
    session = build_session(verify_ssl)
    
    try:
        start_time = time.perf_counter()
        last_error: Optional[Exception] = None
        response = None
        
        # Hasta 2 intentos: algunos sitios cierran la conexion de forma intermitente
        for attempt in range(2):
            try:
                response = session.get(
                    url,
                    headers=HEADERS,
                    timeout=TIMEOUT_SECONDS,
                    allow_redirects=True,
                    verify=verify_ssl,
                )
                break
            except (ConnectionError, Timeout) as e:
                last_error = e
                if attempt == 0:
                    time.sleep(1.0)
        
        if response is None:
            raise last_error if last_error else RequestException("Sin respuesta")
        
        elapsed_time = time.perf_counter() - start_time
        response_time = round(elapsed_time, 3)
        
        # Clasifica segun el codigo de estado
        if 200 <= response.status_code < 300:
            result["status"] = "ONLINE"
            result["response_time"] = response_time
        elif 300 <= response.status_code < 400:
            # Redirigio sin destino claro: el servidor responde, no esta caido
            result["status"] = "ONLINE"
            result["response_time"] = response_time
        elif response.status_code in ANTI_BOT_CODES:
            # El servidor responde pero bloquea bots: sigue en pie
            result["status"] = "ONLINE"
            result["response_time"] = response_time
        else:
            result["status"] = "ISSUE"
            result["response_time"] = response_time
        
    except (ConnectionError, Timeout, TooManyRedirects, HTTPError) as e:
        # Errores de conexión, timeout, redirecciones, etc.
        result["status"] = "OFFLINE"
        result["response_time"] = None
    except RequestException as e:
        # Cualquier otra excepción de requests
        result["status"] = "OFFLINE"
        result["response_time"] = None
    except Exception as e:
        # Excepciones inesperadas para garantizar que el script nunca falle
        result["status"] = "OFFLINE"
        result["response_time"] = None
    finally:
        session.close()
    
    return result


def load_platforms(file_path: str) -> List[Dict[str, Any]]:
    """
    Carga las plataformas desde el archivo JSON.
    
    Args:
        file_path: Ruta al archivo plataformas_ksa.json
    
    Returns:
        Lista de todas las plataformas
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    plataformas = []
    categorias = data.get("categorias", {})
    for categoria, items in categorias.items():
        plataformas.extend(items)
    
    return plataformas


def monitor_platforms(platforms: List[Dict[str, Any]], max_workers: int = 10) -> List[Dict[str, Any]]:
    """
    Monitorea todas las plataformas de forma concurrente.
    
    Args:
        platforms: Lista de plataformas a comprobar
        max_workers: Número máximo de hilos concurrentes
    
    Returns:
        Lista con los resultados de cada plataforma
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_platform = {
            executor.submit(check_platform, platform): platform["id"]
            for platform in platforms
        }
        for future in as_completed(future_to_platform):
            platform_id = future_to_platform[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # Garantiza que aunque algo inesperado ocurra, no se pierda la plataforma
                platform = next(
                    (p for p in platforms if p["id"] == platform_id), 
                    {"id": platform_id, "nombre_en": "", "nombre_ar": "", "url": ""}
                )
                results.append({
                    "id": platform["id"],
                    "nombre_en": platform["nombre_en"],
                    "nombre_ar": platform["nombre_ar"],
                    "url": platform["url"],
                    "status": "OFFLINE",
                    "response_time": None,
                })
    
    return results


def save_results(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Guarda los resultados en formato JSON con fecha/hora UTC.
    
    Args:
        results: Lista de resultados de cada plataforma
        output_path: Ruta del archivo de salida
    """
    # Crear estructura indexada por id para facilitar el acceso
    results_by_id = {}
    for result in results:
        results_by_id[result["id"]] = {
            "status": result["status"],
            "response_time": result["response_time"],
        }
    
    status_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_platforms": len(results),
        "platforms": results_by_id,
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)


def main() -> None:
    input_file = "plataformas_ksa.json"
    output_file = "status.json"
    
    try:
        # Cargar plataformas
        platforms = load_platforms(input_file)
        print(f"Cargadas {len(platforms)} plataformas")
        
        # Monitorear todas las plataformas
        print(f"Iniciando comprobación con timeout de {TIMEOUT_SECONDS}s...")
        results = monitor_platforms(platforms)
        
        # Guardar resultados
        save_results(results, output_file)
        print(f"Resultados guardados en {output_file}")
        
        # Mostrar resumen
        online_count = sum(1 for r in results if r["status"] == "ONLINE")
        issue_count = sum(1 for r in results if r["status"] == "ISSUE")
        offline_count = sum(1 for r in results if r["status"] == "OFFLINE")
        
        print(f"\nResumen:")
        print(f"  ONLINE: {online_count}")
        print(f"  ISSUE: {issue_count}")
        print(f"  OFFLINE: {offline_count}")
        print(f"  Total: {len(results)}")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {input_file}")
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()
