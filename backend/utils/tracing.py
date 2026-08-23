# backend/utils/tracing.py
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any
from utils.logger import orchestrator_logger

class TraceSpan:
    """Represents a single operation in a trace."""
    def __init__(self, operation: str, agent: str):
        self.trace_id = str(uuid.uuid4())[:8]
        self.operation = operation
        self.agent = agent
        self.start_time = time.time()
        self.end_time = None
        self.status = "running"
        self.metadata = {}
        
    def finish(self, status: str = "success", metadata: Dict = None):
        self.end_time = time.time()
        self.status = status
        if metadata:
            self.metadata = metadata
            
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000

class TraceCollector:
    """Collects and stores traces for visualization."""
    
    def __init__(self):
        self.traces: List[TraceSpan] = []
        self.max_traces = 100  # Keep last 100 traces
        
    def start_span(self, operation: str, agent: str) -> TraceSpan:
        span = TraceSpan(operation, agent)
        self.traces.append(span)
        if len(self.traces) > self.max_traces:
            self.traces = self.traces[-self.max_traces:]
        return span
        
    def get_recent_traces(self, limit: int = 20) -> List[Dict]:
        """Get recent traces for the UI."""
        return [
            {
                "trace_id": span.trace_id,
                "operation": span.operation,
                "agent": span.agent,
                "duration_ms": f"{span.duration_ms:.1f}",
                "status": span.status,
                "timestamp": datetime.fromtimestamp(span.start_time).strftime("%H:%M:%S")
            }
            for span in self.traces[-limit:]
        ]

# Singleton
tracer = TraceCollector()