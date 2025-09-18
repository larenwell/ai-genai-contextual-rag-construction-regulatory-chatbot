#!/usr/bin/env python3
"""
Script de prueba para la evaluación RAG con RAGAS
================================================

Este script verifica que todos los componentes estén funcionando correctamente
antes de ejecutar la evaluación completa.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent.parent))

# Agregar directorio global para langchain_mistralai
sys.path.append('/usr/local/lib/python3.12/dist-packages')

# Cargar variables de entorno
load_dotenv(Path(__file__).parent.parent.parent / '.env')

def test_imports():
    """Prueba que todas las dependencias estén disponibles"""
    print("🔍 Verificando dependencias...")
    
    try:
        import ragas
        print("✅ RAGAS importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando RAGAS: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando requests: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando pandas: {e}")
        return False
    
    try:
        from langchain_community.llms import Ollama
        print("✅ LangChain Ollama importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando LangChain Ollama: {e}")
        return False
    
    return True

def test_environment():
    """Verifica las variables de entorno necesarias"""
    print("\n🔍 Verificando variables de entorno...")
    
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key:
        print("✅ MISTRAL_API_KEY configurada")
    else:
        print("❌ MISTRAL_API_KEY no configurada")
        return False
    
    return True

def test_dataset():
    """Verifica que el dataset esté disponible"""
    print("\n🔍 Verificando dataset...")
    
    dataset_path = Path(__file__).parent / "data" / "evaluation_dataset.jsonl"
    
    if dataset_path.exists():
        print(f"✅ Dataset encontrado: {dataset_path}")
        
        # Contar líneas
        with open(dataset_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"✅ Dataset contiene {len(lines)} preguntas")
        return True
    else:
        print(f"❌ Dataset no encontrado: {dataset_path}")
        return False

def test_api_connection():
    """Prueba la conexión a la API"""
    print("\n🔍 Verificando conexión a API...")
    
    try:
        import requests
        response = requests.get("http://localhost:8001/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API RAG está disponible")
            return True
        else:
            print(f"❌ API respondió con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API no disponible: {e}")
        print("💡 Inicia la API con: cd src/evaluation && python api_rag.py")
        return False

def test_ragas_config():
    """Prueba la configuración de RAGAS"""
    print("\n🔍 Verificando configuración RAGAS...")
    
    try:
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_mistralai import ChatMistralAI as LangChainMistralAI
        from langchain_community.embeddings import OllamaEmbeddings as LangChainOllamaEmbeddings
        
        # Verificar que se pueden crear las instancias
        mistral_key = os.getenv("MISTRAL_API_KEY")
        if mistral_key:
            mistral_langchain = LangChainMistralAI(api_key=mistral_key, model="mistral-large-latest")
            llm = LangchainLLMWrapper(mistral_langchain)
            print("✅ MistralAI configurado correctamente")
        
        ollama_langchain = LangChainOllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        embeddings = LangchainEmbeddingsWrapper(ollama_langchain)
        print("✅ OllamaEmbeddings configurado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando RAGAS: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 PRUEBA DE EVALUACIÓN RAG CON RAGAS")
    print("=" * 50)
    
    tests = [
        ("Dependencias", test_imports),
        ("Variables de entorno", test_environment),
        ("Dataset", test_dataset),
        ("Conexión API", test_api_connection),
        ("Configuración RAGAS", test_ragas_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"⚠️  {test_name} falló")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo para la evaluación.")
        print("\n💡 Para ejecutar la evaluación completa:")
        print("   cd src/evaluation")
        print("   python evaluate_ragas.py")
    else:
        print("❌ Algunas pruebas fallaron. Revisa los errores antes de continuar.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
