"""
State Manager
Tracks the state of the SDLC process across all phases.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List


class StateManager:
    """
    Manages persistent state for the autonomous SDLC process.
    Tracks phase completion, errors, and transitions.
    """
    
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load state from file or create new"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Initialize new state
        return {
            "version": "1.0",
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "current_phase": "not_started",
            "phases": {},
            "transitions": [],
            "errors": [],
            "metadata": {}
        }
    
    def _save_state(self):
        """Persist state to file"""
        self.state["last_updated"] = datetime.now().isoformat()
        
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def update_phase(self, phase_name: str, status: str, data: Any = None):
        """
        Update phase status.
        
        Args:
            phase_name: Name of the phase (e.g., 'requirements_analysis')
            status: Status ('in_progress', 'completed', 'failed')
            data: Optional data associated with the phase
        """
        if phase_name not in self.state["phases"]:
            self.state["phases"][phase_name] = {
                "started_at": datetime.now().isoformat(),
                "status": "not_started",
                "attempts": 0,
                "data": None
            }
        
        phase = self.state["phases"][phase_name]
        
        if status == "in_progress" and phase["status"] == "not_started":
            phase["started_at"] = datetime.now().isoformat()
        
        if status == "completed":
            phase["completed_at"] = datetime.now().isoformat()
        
        phase["status"] = status
        phase["attempts"] += 1
        
        if data is not None:
            phase["data"] = data
        
        self.state["current_phase"] = phase_name
        self._save_state()
    
    def add_transition(self, transition: Dict):
        """Add a state transition record"""
        self.state["transitions"].append({
            **transition,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state()
    
    def add_error(self, phase: str, error: str, recoverable: bool = True):
        """Record an error"""
        self.state["errors"].append({
            "phase": phase,
            "error": error,
            "recoverable": recoverable,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state()
    
    def get_phase_status(self, phase_name: str) -> str:
        """Get status of a specific phase"""
        return self.state["phases"].get(phase_name, {}).get("status", "not_started")
    
    def get_phase_data(self, phase_name: str) -> Any:
        """Get data associated with a phase"""
        return self.state["phases"].get(phase_name, {}).get("data")
    
    def is_phase_complete(self, phase_name: str) -> bool:
        """Check if a phase is completed"""
        return self.get_phase_status(phase_name) == "completed"
    
    def get_all_phases(self) -> Dict:
        """Get all phases and their status"""
        return self.state["phases"]
    
    def get_current_phase(self) -> str:
        """Get the current phase name"""
        return self.state["current_phase"]
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.state["metadata"][key] = value
        self._save_state()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.state["metadata"].get(key, default)
    
    def get_state_summary(self) -> Dict:
        """Get summary of current state"""
        completed_phases = sum(1 for p in self.state["phases"].values() if p["status"] == "completed")
        total_phases = len(self.state["phases"])
        
        return {
            "started_at": self.state["started_at"],
            "current_phase": self.state["current_phase"],
            "progress": f"{completed_phases}/{total_phases}",
            "errors_count": len(self.state["errors"]),
            "has_errors": len(self.state["errors"]) > 0
        }
    
    def reset(self):
        """Reset state to initial"""
        self.state = {
            "version": "1.0",
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "current_phase": "not_started",
            "phases": {},
            "transitions": [],
            "errors": [],
            "metadata": {}
        }
        self._save_state()
