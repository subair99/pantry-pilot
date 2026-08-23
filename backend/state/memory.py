# backend/state/memory.py
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.logger import orchestrator_logger

class AgentMemory:
    """
    Manages conversational and episodic memory for PantryPilot agents.
    In this hackathon version, it uses an in-memory store for instant reliability.
    In production, this would be backed by Redis or a Vector Database (e.g., Pinecone).
    """
    
    def __init__(self):
        # Format: { donor_identifier: [ { "timestamp": "...", "message": "...", "action": "..." } ] }
        self.donor_history: Dict[str, List[Dict[str, Any]]] = {}
        self.global_context: Dict[str, Any] = {
            "total_donations_processed": 0,
            "last_system_restart": datetime.now().isoformat()
        }
        orchestrator_logger.info("Agent Memory initialized.")

    def save_interaction(self, donor_name: str, raw_message: str, action_taken: str):
        """Records a new interaction for a specific donor."""
        if donor_name not in self.donor_history:
            self.donor_history[donor_name] = []
            
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "message": raw_message,
            "action_taken": action_taken
        }
        
        self.donor_history[donor_name].append(interaction)
        self.global_context["total_donations_processed"] += 1
        
        orchestrator_logger.info(f"Memory updated: Saved interaction for '{donor_name}'")

    def get_donor_history(self, donor_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieves the most recent interactions for a specific donor."""
        history = self.donor_history.get(donor_name, [])
        return history[-limit:] # Return the last 'limit' interactions

    def generate_context_prompt(self, donor_name: str) -> str:
        """
        Generates a dynamic system prompt snippet based on past memory.
        This is injected into the Agent's system prompt to give it "memory".
        """
        history = self.get_donor_history(donor_name, limit=2)
        
        if not history:
            return f"This is the first time we are interacting with {donor_name}."
            
        last_donation = history[-1]
        return (
            f"CONTEXT MEMORY: You have interacted with {donor_name} before. "
            f"Their last recorded action was: '{last_donation['action_taken']}' "
            f"based on the message: '{last_donation['message']}'. "
            f"Acknowledge their return warmly."
        )

    def get_system_stats(self) -> Dict[str, Any]:
        """Returns high-level stats for the dashboard or logging."""
        return {
            "unique_donors": len(self.donor_history),
            "total_interactions": self.global_context["total_donations_processed"]
        }

# Singleton instance for the app to share state across agents
memory = AgentMemory()