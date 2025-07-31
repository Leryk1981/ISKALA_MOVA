"""
ISKALA Health Check System
Based on Agent Zero monitoring patterns
"""

import json
import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

class ISKALAHealthMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            "intentions_processed": 0,
            "trees_created": 0,
            "errors": 0,
            "uptime": 0
        }
        self.log_file = Path("/a0/instruments/custom/iskala/monitoring/health.log")
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ISKALA.Health")

    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # ISKALA specific metrics
            uptime = (datetime.now() - self.start_time).total_seconds()

            health_status = {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "uptime_seconds": uptime,
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                },
                "iskala": {
                    "intentions_processed": self.metrics["intentions_processed"],
                    "trees_created": self.metrics["trees_created"],
                    "errors": self.metrics["errors"],
                    "uptime": uptime
                }
            }

            # Log health status
            self.logger.info(f"Health check: {json.dumps(health_status, indent=2)}")

            return health_status

        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }

    def record_intention(self, intention: str, success: bool = True):
        """Record intention processing"""
        self.metrics["intentions_processed"] += 1
        if not success:
            self.metrics["errors"] += 1

        self.logger.info(f"Intention processed: {intention[:50]}... Success: {success}")

    def record_tree_creation(self, tree_id: str):
        """Record tree creation"""
        self.metrics["trees_created"] += 1
        self.logger.info(f"Tree created: {tree_id}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics.copy(),
            "uptime": (datetime.now() - self.start_time).total_seconds()
        }

# Global monitor instance
monitor = ISKALAHealthMonitor()
