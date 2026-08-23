# backend/utils/logger.py
import logging
import json
import os
from datetime import datetime
from typing import Any, Dict

# --- Configuration ---
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "agent_activity.jsonl") # JSON Lines format for easy parsing

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs as structured JSON."""
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Attach extra fields if they exist (like agent_name, tool_name, etc.)
        if hasattr(record, "agent_name"):
            log_entry["agent_name"] = record.agent_name
        if hasattr(record, "action"):
            log_entry["action"] = record.action
        if hasattr(record, "details"):
            log_entry["details"] = record.details
            
        return json.dumps(log_entry)

def setup_logger(name: str) -> logging.Logger:
    """Sets up a logger that outputs to both console and a JSON file."""
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Console Handler (Human readable for the dev terminal)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler (Structured JSON for the UI/Observability)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger

# --- Pre-configured Loggers for the Hackathon ---
orchestrator_logger = setup_logger("PantryPilot.Orchestrator")
intake_logger = setup_logger("PantryPilot.IntakeAgent")
dispatch_logger = setup_logger("PantryPilot.DispatchAgent")
logistics_logger = setup_logger("PantryPilot.LogisticsAgent") # <-- ADDED THIS!
guardrail_logger = setup_logger("PantryPilot.Guardrails")

# --- Helper Functions for Clean Logging ---
def log_agent_action(logger: logging.Logger, action: str, details: Dict[str, Any]):
    """Logs a standard agent action."""
    extra = {"action": action, "details": details}
    logger.info(f"Agent executed action: {action}", extra=extra)

def log_hitl_event(logger: logging.Logger, action: str, status: str, details: Dict[str, Any]):
    """Crucial for judging: Logs when the agent pauses for Human-in-the-Loop."""
    extra = {"action": action, "status": status, "details": details}
    logger.info(f"HITL Event: {status} for action {action}", extra=extra)

def log_tool_execution(logger: logging.Logger, tool_name: str, input_data: Any, output_data: Any):
    """Logs the exact inputs and outputs of MCP tools for transparency."""
    extra = {"tool": tool_name, "input": str(input_data)[:200], "output": str(output_data)[:200]} # Truncate to avoid massive logs
    logger.info(f"Tool executed: {tool_name}", extra=extra)