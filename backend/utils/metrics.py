# backend/utils/metrics.py
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, Any

class MetricsCollector:
    """Tracks agent performance and system health."""
    
    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.agent_latencies = defaultdict(list)  # agent_name -> [latency_ms]
        self.hourly_requests = defaultdict(int)  # hour -> count
        
    def record_request(self, agent_name: str, success: bool, latency_ms: float):
        """Record a single agent invocation."""
        self.request_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
            
        self.agent_latencies[agent_name].append(latency_ms)
        current_hour = datetime.now().hour
        self.hourly_requests[current_hour] += 1
        
    def get_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        success_rate = (self.success_count / self.request_count * 100) if self.request_count > 0 else 0
        
        avg_latencies = {
            agent: sum(latencies) / len(latencies)
            for agent, latencies in self.agent_latencies.items()
        }
        
        return {
            "total_requests": self.request_count,
            "success_rate": f"{success_rate:.1f}%",
            "average_latencies_ms": avg_latencies,
            "hourly_distribution": dict(self.hourly_requests)
        }

# Singleton instance
metrics = MetricsCollector()