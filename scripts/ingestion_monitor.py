#!/usr/bin/env python3
"""
Ingestion Monitor Script
Simple script to monitor ingestion status and detect VPS session issues.
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

def check_qdrant_status(collection_name: str = None) -> Dict[str, Any]:
    """Check Qdrant collection status"""
    # Get collection name from environment if not provided
    if collection_name is None:
        collection_name = os.getenv("QDRANT_COLLECTION_NAME", "default-collection")
    try:
        # First check if collections endpoint is available
        response = requests.get("http://localhost:6333/collections", timeout=10)
        if response.status_code == 200:
            collections = response.json()["result"]["collections"]
            collection_info = next((col for col in collections if col["name"] == collection_name), None)
            
            if collection_info:
                # Get detailed collection info with points count
                detail_response = requests.get(f"http://localhost:6333/collections/{collection_name}", timeout=10)
                if detail_response.status_code == 200:
                    detail_info = detail_response.json()["result"]
                    return {
                        'status': 'running',
                        'collection_exists': True,
                        'points_count': detail_info.get('points_count', 0),
                        'vectors_count': detail_info.get('indexed_vectors_count', 0),
                        'collection_name': collection_name
                    }
                else:
                    # Fallback to basic info if detail call fails
                    return {
                        'status': 'running',
                        'collection_exists': True,
                        'points_count': 0,
                        'vectors_count': 0,
                        'collection_name': collection_name
                    }
            else:
                return {
                    'status': 'running',
                    'collection_exists': False,
                    'points_count': 0,
                    'vectors_count': 0,
                    'collection_name': collection_name
                }
        else:
            return {'status': 'error', 'http_code': response.status_code}
            
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_output_files(output_dir: str = "src/output/rag") -> Dict[str, Any]:
    """Check output files to see what has been processed"""
    try:
        output_path = Path(output_dir)
        if not output_path.exists():
            return {'status': 'error', 'error': 'Output directory does not exist'}
        
        # Count processed files
        processed_files = list(output_path.glob("enhanced_chunks_mistral_*.json"))
        contextualized_files = list(output_path.glob("contextualized_content.json"))
        
        # Get file details
        file_details = []
        for file_path in processed_files:
            try:
                stat = file_path.stat()
                file_details.append({
                    'name': file_path.name,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'age_hours': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 3600
                })
            except Exception as e:
                file_details.append({'name': file_path.name, 'error': str(e)})
        
        return {
            'status': 'success',
            'processed_files_count': len(processed_files),
            'contextualized_files_count': len(contextualized_files),
            'file_details': file_details,
            'output_directory': str(output_path)
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_data_folder(data_folder: str = "data/test") -> Dict[str, Any]:
    """Check data folder for PDF files"""
    try:
        data_path = Path(data_folder)
        if not data_path.exists():
            return {'status': 'error', 'error': 'Data directory does not exist'}
        
        pdf_files = list(data_path.glob("*.pdf"))
        
        file_info = []
        for pdf_file in pdf_files:
            try:
                stat = pdf_file.stat()
                file_info.append({
                    'name': pdf_file.name,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                file_info.append({'name': pdf_file.name, 'error': str(e)})
        
        return {
            'status': 'success',
            'total_pdf_files': len(pdf_files),
            'file_info': file_info,
            'data_directory': str(data_path)
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_chunks_integrity(collection_name: str = None) -> Dict[str, Any]:
    """Verifica la integridad de chunks entre archivos generados y Qdrant"""
    if collection_name is None:
        collection_name = os.getenv("QDRANT_COLLECTION_NAME", "default-collection")
    
    try:
        # Contar chunks en archivos generados
        output_path = Path("src/output/rag")
        generated_chunks = {}
        
        if output_path.exists():
            enhanced_files = list(output_path.glob("enhanced_chunks_mistral_*.json"))
            for file_path in enhanced_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        file_name = file_path.name.replace('enhanced_chunks_mistral_', '').replace('.json', '')
                        generated_chunks[file_name] = len(data)
                except Exception:
                    continue
        
        total_generated = sum(generated_chunks.values())
        
        # Obtener info de Qdrant
        collection_response = requests.get(f"http://localhost:6333/collections/{collection_name}", timeout=10)
        qdrant_points = 0
        
        if collection_response.status_code == 200:
            qdrant_points = collection_response.json()["result"]["points_count"]
        
        # Verificar integridad
        integrity_match = (total_generated == qdrant_points) if total_generated > 0 else False
        
        return {
            'status': 'success',
            'generated_chunks': generated_chunks,
            'total_generated': total_generated,
            'qdrant_points': qdrant_points,
            'integrity_match': integrity_match,
            'files_processed': len(generated_chunks)
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def check_ingestion_completeness() -> Dict[str, Any]:
    """Check if ingestion is complete by comparing data vs output"""
    data_status = check_data_folder()
    output_status = check_output_files()
    
    if data_status['status'] != 'success' or output_status['status'] != 'success':
        return {
            'status': 'error',
            'data_status': data_status,
            'output_status': output_status
        }
    
    # Calculate completion
    total_pdfs = data_status['total_pdf_files']
    processed_pdfs = output_status['processed_files_count']
    
    completion_percentage = (processed_pdfs / total_pdfs * 100) if total_pdfs > 0 else 0
    
    # Check for recent activity (files modified in last 2 hours)
    recent_files = [f for f in output_status['file_details'] 
                    if f.get('age_hours', 999) < 2]
    
    # Verificar integridad de chunks
    chunks_integrity = check_chunks_integrity()
    
    return {
        'status': 'success',
        'total_pdf_files': total_pdfs,
        'processed_pdf_files': processed_pdfs,
        'completion_percentage': round(completion_percentage, 1),
        'recent_activity': len(recent_files) > 0,
        'recent_files_count': len(recent_files),
        'is_complete': processed_pdfs >= total_pdfs,
        'missing_files': max(0, total_pdfs - processed_pdfs),
        'chunks_integrity': chunks_integrity
    }

def check_system_health() -> Dict[str, Any]:
    """Check basic system health indicators"""
    try:
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Check if any processes are using high resources
        high_cpu_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > 80:
                    high_cpu_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {
            'status': 'success',
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent,
            'high_cpu_processes': high_cpu_processes,
            'healthy': (
                cpu_percent < 90 and 
                memory_percent < 85 and 
                disk_percent < 90
            )
        }
        
    except ImportError:
        return {'status': 'error', 'error': 'psutil not available'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def generate_status_report() -> str:
    """Generate a comprehensive status report"""
    print("🔍 INGESTION STATUS MONITOR")
    print("=" * 50)
    print(f"📅 Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check Qdrant
    print("🗄️ Checking Qdrant status...")
    qdrant_status = check_qdrant_status(os.getenv("QDRANT_COLLECTION_NAME"))
    if qdrant_status['status'] == 'running':
        print(f"   ✅ Qdrant is running")
        if qdrant_status['collection_exists']:
            print(f"   📊 Collection: {qdrant_status['collection_name']}")
            print(f"   📈 Points: {qdrant_status['points_count']}")
            print(f"   🔢 Vectors: {qdrant_status['vectors_count']}")
        else:
            print(f"   ⚠️ Collection '{qdrant_status['collection_name']}' not found")
    else:
        print(f"   ❌ Qdrant error: {qdrant_status.get('error', 'Unknown error')}")
    print()
    
    # Check data folder
    print("📁 Checking data folder...")
    data_status = check_data_folder()
    if data_status['status'] == 'success':
        print(f"   ✅ Data folder: {data_status['data_directory']}")
        print(f"   📄 Total PDF files: {data_status['total_pdf_files']}")
    else:
        print(f"   ❌ Data folder error: {data_status.get('error', 'Unknown error')}")
    print()
    
    # Check output files
    print("📊 Checking output files...")
    output_status = check_output_files()
    if output_status['status'] == 'success':
        print(f"   ✅ Output directory: {output_status['output_directory']}")
        print(f"   📦 Processed files: {output_status['processed_files_count']}")
        print(f"   📋 Contextualized files: {output_status['contextualized_files_count']}")
    else:
        print(f"   ❌ Output error: {output_status.get('error', 'Unknown error')}")
    print()
    
    # Check completion
    print("🎯 Checking ingestion completion...")
    completion_status = check_ingestion_completeness()
    if completion_status['status'] == 'success':
        print(f"   📊 Completion: {completion_status['completion_percentage']}%")
        print(f"   ✅ Complete: {'Yes' if completion_status['is_complete'] else 'No'}")
        print(f"   📄 Missing files: {completion_status['missing_files']}")
        print(f"   🔄 Recent activity: {'Yes' if completion_status['recent_activity'] else 'No'}")
        
        # Mostrar información de integridad de chunks
        chunks_info = completion_status.get('chunks_integrity', {})
        if chunks_info.get('status') == 'success':
            print(f"   📋 Chunks generated: {chunks_info['total_generated']}")
            print(f"   🗄️ Chunks in Qdrant: {chunks_info['qdrant_points']}")
            integrity_status = "✅ Match" if chunks_info['integrity_match'] else "❌ Mismatch"
            print(f"   🔍 Integrity: {integrity_status}")
            
            # Mostrar distribución por archivo si hay discrepancias
            if not chunks_info['integrity_match'] and chunks_info['generated_chunks']:
                print(f"   📄 File breakdown:")
                for file_name, count in chunks_info['generated_chunks'].items():
                    print(f"      • {file_name}: {count} chunks")
        
        if not completion_status['is_complete'] or not chunks_info.get('integrity_match', True):
            print(f"   ⚠️ Issues detected!")
            print(f"   💡 Run detailed validation: python3 scripts/validate_ingestion_integrity.py")
            print(f"   💡 Consider re-running: python3 scripts/robust_ingestion_manager.py")
    else:
        print(f"   ❌ Completion check error: {completion_status.get('error', 'Unknown error')}")
    print()
    
    # Check system health
    print("🏥 Checking system health...")
    health_status = check_system_health()
    if health_status['status'] == 'success':
        print(f"   💻 CPU: {health_status['cpu_percent']}%")
        print(f"   🧠 Memory: {health_status['memory_percent']}%")
        print(f"   💾 Disk: {health_status['disk_percent']}%")
        print(f"   ✅ Healthy: {'Yes' if health_status['healthy'] else 'No'}")
        
        if health_status['high_cpu_processes']:
            print(f"   ⚠️ High CPU processes detected:")
            for proc in health_status['high_cpu_processes'][:3]:  # Show top 3
                print(f"      • PID {proc['pid']} ({proc['name']}): {proc['cpu_percent']}%")
    else:
        print(f"   ❌ Health check error: {health_status.get('error', 'Unknown error')}")
    print()
    
    # Summary and recommendations
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("=" * 50)
    
    issues = []
    
    if qdrant_status['status'] != 'running':
        issues.append("Qdrant service is not running")
    
    if completion_status.get('status') == 'success' and not completion_status.get('is_complete', True):
        issues.append("Ingestion is incomplete")
    
    if health_status.get('status') == 'success' and not health_status.get('healthy', True):
        issues.append("System resources are constrained")
    
    if not completion_status.get('recent_activity', False):
        issues.append("No recent ingestion activity detected")
    
    if issues:
        print("❌ Issues detected:")
        for issue in issues:
            print(f"   • {issue}")
        print()
        print("🔧 Recommended actions:")
        print("   1. Check Qdrant container: docker ps | grep qdrant")
        print("   2. Restart ingestion: python3 scripts/robust_ingestion_manager.py")
        print("   3. Use tmux session: bash start_ingestion_session.sh")
        print("   4. Monitor logs: tail -f src/output/rag/ingestion_manager_*.log")
    else:
        print("✅ All systems operational")
        print("   🎉 Ingestion appears to be working correctly")
    
    return "Status check completed"

def main():
    """Main function"""
    # Load environment variables from .env file
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
    
    try:
        report = generate_status_report()
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
