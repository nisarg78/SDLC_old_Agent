"""
Supervisor Agent
Manages the overall workflow, state transitions, and agent coordination.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


class SupervisorAgent:
    """
    Orchestrates the multi-agent workflow.
    Decides when to trigger each agent and manages state transitions.
    """
    
    def __init__(self, state_manager, logger):
        self.state_manager = state_manager
        self.logger = logger
        self.workflow_stages = [
            "requirements_analysis",
            "architecture_design",
            "backend_development",
            "frontend_development",
            "testing",
            "healing",  # conditional
            "validation",
            "packaging"
        ]
        self.current_stage = 0
    
    def should_trigger_healing(self, test_results: Dict) -> bool:
        """
        Autonomous decision: Should we trigger the healer agent?
        """
        if not test_results.get("all_passed", True):
            self.logger.info("Supervisor: Test failures detected. Triggering Healer Agent.")
            return True
        
        if test_results.get("warnings", []):
            self.logger.warning("Supervisor: Warnings detected but tests passed. Proceeding without healing.")
        
        return False
    
    def should_retry_phase(self, phase: str, attempt: int, max_attempts: int = 3) -> bool:
        """
        Autonomous decision: Should we retry a failed phase?
        """
        if attempt >= max_attempts:
            self.logger.error(f"Supervisor: Max attempts ({max_attempts}) reached for phase '{phase}'")
            return False
        
        self.logger.info(f"Supervisor: Retrying phase '{phase}' (attempt {attempt + 1}/{max_attempts})")
        return True
    
    def get_next_agent(self) -> Optional[str]:
        """
        Autonomous transition to next agent.
        Returns the next agent to trigger or None if complete.
        """
        if self.current_stage >= len(self.workflow_stages):
            return None
        
        next_agent = self.workflow_stages[self.current_stage]
        self.current_stage += 1
        
        self.logger.info(f"Supervisor: Triggering next agent → {next_agent}")
        return next_agent
    
    def log_transition(self, from_agent: str, to_agent: str, reason: str = ""):
        """Log state transitions"""
        transition = {
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "reason": reason
        }
        
        self.state_manager.add_transition(transition)
        self.logger.info(f"Supervisor: Transition {from_agent} → {to_agent}")
    
    def make_architectural_decision(self, context: Dict, options: List[str]) -> str:
        """
        Make an autonomous architectural decision when requirements are ambiguous.
        """
        # Decision logic based on context
        if "database" in context and not context.get("database_specified"):
            # Default to PostgreSQL for relational data
            decision = "PostgreSQL"
            reason = "Robust, ACID-compliant, good for relational data"
            
        elif "frontend_framework" in context and not context.get("framework_specified"):
            # Default to React for modern UI
            decision = "React"
            reason = "Industry standard, large ecosystem, component-based"
            
        elif "backend_language" in context and not context.get("language_specified"):
            # Default to Node.js for full-stack JS
            decision = "Node.js"
            reason = "Full-stack JavaScript, fast, large ecosystem"
        
        else:
            # Pick the first option as default
            decision = options[0] if options else "default"
            reason = "First available option selected"
        
        self.logger.info(f"Supervisor: Autonomous decision made - {decision} ({reason})")
        
        return decision
    
    def assess_risk(self, operation: str) -> str:
        """
        Assess risk level of an operation.
        Returns: 'low', 'medium', 'high'
        """
        high_risk_operations = ["database_migration", "production_deployment", "data_deletion"]
        medium_risk_operations = ["schema_change", "api_breaking_change"]
        
        if operation in high_risk_operations:
            return "high"
        elif operation in medium_risk_operations:
            return "medium"
        else:
            return "low"
