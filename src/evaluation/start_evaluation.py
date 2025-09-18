#!/usr/bin/env python3
"""
Script de inicio para la evaluación RAG con RAGAS
================================================

Este script facilita el inicio de la evaluación completa:
1. Verifica que todos los servicios estén funcionando
2. Inicia la API RAG si es necesario
3. Ejecuta la evaluación completa
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def check_services():
    """Verifica que todos los servicios necesarios estén funcionando"""
    print("🔍 Verificando servicios...")
    
    services = {
        "Qdrant": "http://localhost:6333",
        "Ollama": "http://localhost:11434",
        "API RAG": "http://localhost:8001"
    }
    
    import requests
    
    for service_name, url in services.items():
        try:
            if service_name == "Qdrant":
                response = requests.get(f"{url}/collections", timeout=5)
            elif service_name == "Ollama":
                response = requests.get(f"{url}/api/tags", timeout=5)
            else:  # API RAG
                response = requests.get(f"{url}/docs", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {service_name} está funcionando")
            else:
                print(f"⚠️  {service_name} respondió con código {response.status_code}")
                return False
                
        except requests.exceptions.RequestException:
            print(f"❌ {service_name} no está disponible en {url}")
            return False
    
    return True

def start_api_rag():
    """Inicia la API RAG en segundo plano"""
    print("🚀 Iniciando API RAG...")
    
    try:
        # Cambiar al directorio de evaluación
        eval_dir = Path(__file__).parent
        
        # Iniciar API en segundo plano
        process = subprocess.Popen(
            [sys.executable, "api_rag.py"],
            cwd=eval_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Esperar un poco para que inicie
        time.sleep(3)
        
        # Verificar que esté funcionando
        import requests
        try:
            response = requests.get("http://localhost:8001/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API RAG iniciada correctamente")
                return process
            else:
                print("❌ API RAG no respondió correctamente")
                process.terminate()
                return None
        except requests.exceptions.RequestException:
            print("❌ No se pudo conectar a la API RAG")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando API RAG: {e}")
        return None

def run_evaluation():
    """Ejecuta la evaluación completa"""
    print("🎯 Ejecutando evaluación RAG con RAGAS...")
    
    try:
        eval_dir = Path(__file__).parent
        result = subprocess.run(
            [sys.executable, "evaluate_ragas.py"],
            cwd=eval_dir,
            capture_output=False
        )
        
        if result.returncode == 0:
            print("✅ Evaluación completada exitosamente")
            return True
        else:
            print(f"❌ Evaluación falló con código {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando evaluación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIADOR DE EVALUACIÓN RAG CON RAGAS")
    print("=" * 50)
    
    # Verificar variables de entorno
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ Error: MISTRAL_API_KEY no está configurada")
        print("Por favor, configura tu API key de Mistral en el archivo .env")
        return False
    
    # Verificar servicios
    if not check_services():
        print("\n⚠️  Algunos servicios no están disponibles")
        print("Asegúrate de que Qdrant y Ollama estén funcionando")
        
        # Intentar iniciar API RAG
        api_process = start_api_rag()
        if not api_process:
            print("❌ No se pudo iniciar la API RAG")
            return False
        
        # Esperar un poco más
        time.sleep(2)
        
        # Verificar nuevamente
        if not check_services():
            print("❌ Los servicios siguen sin estar disponibles")
            if api_process:
                api_process.terminate()
            return False
    
    # Ejecutar evaluación
    print("\n" + "=" * 50)
    success = run_evaluation()
    
    if success:
        print("\n🎉 ¡Evaluación completada exitosamente!")
        print("📁 Revisa los archivos en evaluation_results/ para ver los resultados")
    else:
        print("\n❌ La evaluación falló")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
