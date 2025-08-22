#!/usr/bin/env python3
"""
Robust Ingestion Manager for VPS Deployment
Handles session timeouts, provides monitoring, and ensures reliable ingestion completion.
"""

import os
import sys
import json
import time
import signal
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psutil
import requests
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class RobustIngestionManager:
    def __init__(self, 
                 collection_name: str = None,
                 data_folder: str = "data/test",
                 output_dir: str = "src/output/rag",
                 max_retries: int = 3,
                 session_timeout: int = 3600):  # 1 hour
        
        # Get collection name from environment if not provided
        if collection_name is None:
            collection_name = os.getenv("QDRANT_COLLECTION_NAME", "default-collection")
        
        # Set project root for proper working directory
        self.project_root = Path(__file__).parent.parent
        
        self.collection_name = collection_name
        self.data_folder = Path(data_folder)
        self.output_dir = Path(output_dir)
        self.max_retries = max_retries
        self.session_timeout = session_timeout
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Session tracking
        self.session_start = datetime.now()
        self.ingestion_status = {}
        self.current_process = None
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_file = self.output_dir / f"ingestion_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"🚀 Robust Ingestion Manager Started")
        self.logger.info(f"📁 Data folder: {self.data_folder}")
        self.logger.info(f"🗄️ Collection: {self.collection_name}")
        self.logger.info(f"📊 Output directory: {self.output_dir}")
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)
        
    def check_vps_health(self) -> Dict[str, Any]:
        """Check VPS system health"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network connectivity
            network_ok = self.check_network_connectivity()
            
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_ok': network_ok,
                'session_duration': (datetime.now() - self.session_start).total_seconds(),
                'healthy': (
                    cpu_percent < 90 and 
                    memory_percent < 85 and 
                    disk_percent < 90 and 
                    network_ok
                )
            }
            
            self.logger.info(f"🏥 VPS Health Check: CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent}%, Network: {'✅' if network_ok else '❌'}")
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Error checking VPS health: {e}")
            return {'healthy': False, 'error': str(e)}
            
    def check_network_connectivity(self) -> bool:
        """Check network connectivity to external services"""
        try:
            # Test internet connectivity
            response = requests.get("https://httpbin.org/get", timeout=10)
            return response.status_code == 200
        except:
            return False
            
    def check_qdrant_status(self) -> Dict[str, Any]:
        """Check Qdrant service status"""
        try:
            response = requests.get("http://localhost:6333/collections", timeout=10)
            if response.status_code == 200:
                collections = response.json()["result"]["collections"]
                collection_info = next((col for col in collections if col["name"] == self.collection_name), None)
                
                if collection_info:
                    return {
                        'status': 'running',
                        'collection_exists': True,
                        'points_count': collection_info.get('points_count', 0),
                        'vectors_count': collection_info.get('indexed_vectors_count', 0)
                    }
                else:
                    return {
                        'status': 'running',
                        'collection_exists': False,
                        'points_count': 0,
                        'vectors_count': 0
                    }
            else:
                return {'status': 'error', 'http_code': response.status_code}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
            
    def get_pending_files(self) -> List[Path]:
        """Get list of PDF files that haven't been processed yet"""
        try:
            # Get all PDF files in data folder
            pdf_files = list(self.data_folder.glob("*.pdf"))
            
            # Check which ones haven't been processed by looking at output files
            processed_files = set()
            for output_file in self.output_dir.glob("enhanced_chunks_v2_*.json"):
                # Extract filename from output
                filename = output_file.name.replace("enhanced_chunks_v2_", "").replace(".json", "")
                processed_files.add(filename)
            
            # Return unprocessed files
            pending_files = [f for f in pdf_files if f.stem not in processed_files]
            
            self.logger.info(f"📋 Found {len(pdf_files)} total PDF files, {len(pending_files)} pending processing")
            
            return pending_files
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pending files: {e}")
            return []
            
    def run_ingestion_for_all_files(self, retry_count: int = 0) -> bool:
        """Run ingestion for all PDF files in the folder with retry logic"""
        try:
            self.logger.info(f"🔄 Processing all files in folder (attempt {retry_count + 1})")
            
            # Check VPS health before processing
            health = self.check_vps_health()
            if not health['healthy']:
                self.logger.warning(f"⚠️ VPS health check failed, skipping processing")
                return False
            
            # Run ingestion command - process all files in the folder
            cmd = [
                sys.executable, 
                "src/ingestion_manual_mistral.py"
            ]
            
            # Start process with timeout and correct working directory
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_root)  # Set working directory to project root
            )
            
            self.current_process = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=self.session_timeout)
                
                if process.returncode == 0:
                    self.logger.info(f"✅ Successfully processed all files")
                    return True
                else:
                    self.logger.error(f"❌ Process failed: {stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"⏰ Timeout processing files")
                process.kill()
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error running ingestion: {e}")
            return False
            
    def run_batch_ingestion(self) -> Dict[str, Any]:
        """Run batch ingestion with monitoring and recovery"""
        self.logger.info("🚀 Starting batch ingestion process")
        
        # Initial health check
        initial_health = self.check_vps_health()
        if not initial_health['healthy']:
            self.logger.error("❌ VPS health check failed, cannot start ingestion")
            return {'success': False, 'error': 'VPS health check failed'}
        
        # Check Qdrant status
        qdrant_status = self.check_qdrant_status()
        if qdrant_status['status'] != 'running':
            self.logger.error(f"❌ Qdrant not running: {qdrant_status}")
            return {'success': False, 'error': 'Qdrant service not available'}
        
        # Get pending files
        pending_files = self.get_pending_files()
        if not pending_files:
            self.logger.info("✅ No pending files to process")
            return {'success': True, 'message': 'No pending files'}
        
        # Process files with monitoring
        results = {
            'start_time': datetime.now().isoformat(),
            'total_files': len(pending_files),
            'processed_files': [],
            'failed_files': [],
            'health_checks': []
        }
        
        # Process all files at once with retries
        self.logger.info(f"📄 Processing all {len(pending_files)} files in batch")
        
        # Health check before processing
        health = self.check_vps_health()
        results['health_checks'].append(health)
        
        if not health['healthy']:
            self.logger.warning(f"⚠️ VPS health degraded, pausing for 30 seconds...")
            time.sleep(30)
        
        # Process all files with retries
        success = False
        for retry in range(self.max_retries):
            if self.run_ingestion_for_all_files(retry):
                success = True
                break
            elif retry < self.max_retries - 1:
                self.logger.info(f"🔄 Retrying all files in 10 seconds...")
                time.sleep(10)
        
        if success:
            results['processed_files'] = [str(f) for f in pending_files]
            self.logger.info(f"✅ Successfully processed all {len(pending_files)} files")
        else:
            results['failed_files'] = [str(f) for f in pending_files]
            self.logger.error(f"❌ Failed to process files after {self.max_retries} attempts")
        
        # Final status
        results['end_time'] = datetime.now().isoformat()
        results['duration'] = (datetime.now() - datetime.fromisoformat(results['start_time'])).total_seconds()
        results['success_rate'] = len(results['processed_files']) / len(pending_files) if pending_files else 1.0
        
        # Save results
        self.save_ingestion_results(results)
        
        # Log summary
        self.logger.info(f"🎯 Batch ingestion completed:")
        self.logger.info(f"   📁 Total files: {len(pending_files)}")
        self.logger.info(f"   ✅ Processed: {len(results['processed_files'])}")
        self.logger.info(f"   ❌ Failed: {len(results['failed_files'])}")
        self.logger.info(f"   📊 Success rate: {results['success_rate']:.1%}")
        self.logger.info(f"   ⏱️ Duration: {results['duration']:.1f} seconds")
        
        return results
        
    def save_ingestion_results(self, results: Dict[str, Any]):
        """Save ingestion results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.output_dir / f"ingestion_results_{timestamp}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Results saved to: {results_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving results: {e}")
            
    def create_session_script(self):
        """Create a tmux/screen session script for VPS deployment"""
        script_content = f"""#!/bin/bash
# Robust Ingestion Session Script
# Run this in tmux or screen to prevent session timeouts

echo "🚀 Starting robust ingestion session..."

# Create tmux session
tmux new-session -d -s ingestion_session
tmux send-keys -t ingestion_session "cd {project_root}" Enter
tmux send-keys -t ingestion_session "source .venv/bin/activate" Enter
tmux send-keys -t ingestion_session "python3 scripts/robust_ingestion_manager.py" Enter

echo "✅ Ingestion session started in tmux session 'ingestion_session'"
echo "📋 To attach to session: tmux attach -t ingestion_session"
echo "📋 To detach from session: Ctrl+B, then D"
echo "📋 To kill session: tmux kill-session -t ingestion_session"
"""
        
        script_path = project_root / "start_ingestion_session.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        self.logger.info(f"📜 Session script created: {script_path}")
        
    def cleanup(self):
        """Cleanup resources"""
        if self.current_process and self.current_process.poll() is None:
            self.logger.info("🛑 Terminating current process...")
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
        
        self.logger.info("🧹 Cleanup completed")

def main():
    """Main function"""
    print("🔧 ROBUST INGESTION MANAGER FOR VPS")
    print("=" * 50)
    
    # Load environment variables from .env file
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Robust ingestion manager for VPS deployment")
    parser.add_argument("--collection", default=os.getenv("QDRANT_COLLECTION_NAME"), help="Qdrant collection name (from .env or specify)")
    parser.add_argument("--data-folder", default="data/test", help="Data folder path")
    parser.add_argument("--output-dir", default="src/output/rag", help="Output directory")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum retry attempts")
    parser.add_argument("--session-timeout", type=int, default=3600, help="Session timeout in seconds")
    parser.add_argument("--create-session-script", action="store_true", help="Create tmux session script")
    
    args = parser.parse_args()
    
    # Create manager
    manager = RobustIngestionManager(
        collection_name=args.collection,
        data_folder=args.data_folder,
        output_dir=args.output_dir,
        max_retries=args.max_retries,
        session_timeout=args.session_timeout
    )
    
    try:
        if args.create_session_script:
            manager.create_session_script()
            print("✅ Session script created successfully!")
        else:
            # Run batch ingestion
            results = manager.run_batch_ingestion()
            if results.get('success', False):
                print("🎉 Ingestion completed successfully!")
            else:
                print(f"❌ Ingestion failed: {results.get('error', 'Unknown error')}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()
