#!/usr/bin/env python3
"""
Script to set up the new Pinecone index for Mistral OCR testing.
Creates the 'asistente_normativa_mocr_test' index with proper configuration.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pinecone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv(project_root / '.env')

def setup_pinecone_index():
    """Set up the new Pinecone index for Mistral OCR testing."""
    
    # Get API key
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        print("❌ Error: PINECONE_API_KEY no está configurada en el archivo .env")
        return False
    
    # Initialize Pinecone
    try:
        pinecone.init(api_key=pinecone_api_key, environment="gcp-starter")
        print("✅ Pinecone inicializado correctamente")
    except Exception as e:
        print(f"❌ Error inicializando Pinecone: {e}")
        return False
    
    # Index configuration
    index_name = "asistente-normativa-mocr-test"
    dimension = 768  # For nomic-embed-text model
    metric = "cosine"
    
    print(f"\n🔧 Configurando índice Pinecone:")
    print(f"   - Nombre: {index_name}")
    print(f"   - Dimensión: {dimension}")
    print(f"   - Métrica: {metric}")
    print(f"   - Entorno: gcp-starter")
    
    try:
        # Check if index already exists
        existing_indexes = pinecone.list_indexes()
        print(f"📋 Índices existentes: {existing_indexes}")
        
        if index_name in existing_indexes:
            print(f"⚠️  El índice '{index_name}' ya existe")
            
            # Get index info
            index = pinecone.Index(index_name)
            stats = index.describe_index_stats()
            print(f"📊 Estadísticas del índice existente:")
            print(f"   - Total de vectores: {stats.get('total_vector_count', 0)}")
            print(f"   - Dimensiones: {stats.get('dimension', 'N/A')}")
            print(f"   - Métrica: {stats.get('metric', 'N/A')}")
            
            response = input("\n¿Desea continuar usando el índice existente? (y/n): ")
            if response.lower() != 'y':
                print("❌ Operación cancelada")
                return False
            
            print("✅ Usando índice existente")
            return True
        
        # Create new index
        print(f"\n🔄 Creando nuevo índice '{index_name}'...")
        
        pinecone.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=pinecone.Spec(
                serverless=pinecone.ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        )
        
        print("✅ Índice creado exitosamente")
        
        # Wait for index to be ready
        print("⏳ Esperando que el índice esté listo...")
        import time
        time.sleep(10)  # Wait 10 seconds for index to be ready
        
        # Verify index
        index = pinecone.Index(index_name)
        stats = index.describe_index_stats()
        print(f"📊 Estadísticas del nuevo índice:")
        print(f"   - Total de vectores: {stats.get('total_vector_count', 0)}")
        print(f"   - Dimensiones: {stats.get('dimension', 'N/A')}")
        print(f"   - Métrica: {stats.get('metric', 'N/A')}")
        
        print(f"\n🎉 Índice '{index_name}' configurado y listo para usar!")
        return True
        
    except Exception as e:
        print(f"❌ Error configurando índice: {e}")
        return False

def update_env_file():
    """Update .env file with the new index name."""
    env_file = project_root / '.env'
    
    if not env_file.exists():
        print("⚠️  Archivo .env no encontrado, creando uno nuevo...")
        env_content = f"""# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=asistente-normativa-mocr-test

# Mistral Configuration
MISTRAL_API_KEY=your_mistral_api_key_here
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
    else:
        print("📝 Actualizando archivo .env...")
        
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update PINECONE_INDEX
        if 'PINECONE_INDEX=' in content:
            # Replace existing PINECONE_INDEX
            lines = content.split('\n')
            updated_lines = []
            for line in lines:
                if line.startswith('PINECONE_INDEX='):
                    updated_lines.append('PINECONE_INDEX=asistente-normativa-mocr-test')
                else:
                    updated_lines.append(line)
            content = '\n'.join(updated_lines)
        else:
            # Add PINECONE_INDEX if not present
            content += '\nPINECONE_INDEX=asistente-normativa-mocr-test\n'
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Archivo .env actualizado")

def main():
    """Main function to set up Pinecone index."""
    print("🚀 Configurando índice Pinecone para Mistral OCR")
    print("=" * 60)
    
    # Update .env file
    update_env_file()
    
    # Set up index
    success = setup_pinecone_index()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Configuración completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("1. Asegúrate de que PINECONE_API_KEY esté configurada en .env")
        print("2. Ejecuta el script de ingesta: python src/ingestion_manual_mistral_enhanced.py")
        print("3. Los embeddings se almacenarán en el nuevo índice")
    else:
        print("\n" + "=" * 60)
        print("❌ Configuración falló")
        print("\n🔧 Solución de problemas:")
        print("1. Verifica que PINECONE_API_KEY sea válida")
        print("2. Asegúrate de tener permisos para crear índices")
        print("3. Verifica la conexión a internet")

if __name__ == "__main__":
    main() 