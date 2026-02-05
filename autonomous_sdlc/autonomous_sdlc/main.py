#!/usr/bin/env python3
"""
Autonomous SDLC Multi-Agent System
Takes a requirements document and generates a complete full-stack application
with zero human intervention.
"""

import os
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from agents.supervisor import SupervisorAgent
from agents.analyst import AnalystAgent
from agents.architect import ArchitectAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.qa_agent import QAAgent
from agents.healer_agent import HealerAgent
from agents.validator import ValidatorAgent
from utils.state_manager import StateManager
from utils.logger import setup_logger
from config.settings import Config


class AutonomousSDLCFactory:
    """
    Main orchestrator for the autonomous SDLC system.
    Coordinates all agents to build a complete application from requirements.
    """
    
    def __init__(self, requirements_file: str, output_dir: str = "./output"):
        self.requirements_file = requirements_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = setup_logger("SDLC_Factory", self.output_dir / "factory.log")
        
        # Initialize state manager
        self.state_manager = StateManager(self.output_dir / "state.json")
        
        # Initialize configuration
        self.config = Config()
        
        # Initialize agents
        self.supervisor = SupervisorAgent(self.state_manager, self.logger)
        self.analyst = AnalystAgent(self.config, self.logger)
        self.architect = ArchitectAgent(self.config, self.logger)
        self.backend_agent = BackendAgent(self.config, self.logger)
        self.frontend_agent = FrontendAgent(self.config, self.logger)
        self.qa_agent = QAAgent(self.config, self.logger)
        self.healer = HealerAgent(self.config, self.logger, max_attempts=5)
        self.validator = ValidatorAgent(self.config, self.logger)
        
        # Decisions log
        self.decisions_log = []
        
        self.logger.info("=" * 80)
        self.logger.info("AUTONOMOUS SDLC FACTORY INITIALIZED")
        self.logger.info("=" * 80)
    
    async def execute(self) -> Dict:
        """
        Main execution flow - fully autonomous.
        Returns the final project structure and URLs.
        """
        try:
            self.logger.info("Starting autonomous SDLC process...")
            
            # Phase 1: Requirements Analysis
            self.logger.info("\n[PHASE 1] REQUIREMENTS ANALYSIS")
            requirements = await self._phase_requirements_analysis()
            self.state_manager.update_phase("requirements_analysis", "completed", requirements)
            
            # Phase 2: Architecture Design
            self.logger.info("\n[PHASE 2] ARCHITECTURE DESIGN")
            architecture = await self._phase_architecture_design(requirements)
            self.state_manager.update_phase("architecture_design", "completed", architecture)
            
            # Phase 3: Backend Development
            self.logger.info("\n[PHASE 3] BACKEND DEVELOPMENT")
            backend_code = await self._phase_backend_development(architecture)
            self.state_manager.update_phase("backend_development", "completed", {"status": "generated"})
            
            # Phase 4: Frontend Development
            self.logger.info("\n[PHASE 4] FRONTEND DEVELOPMENT")
            frontend_code = await self._phase_frontend_development(architecture, backend_code)
            self.state_manager.update_phase("frontend_development", "completed", {"status": "generated"})
            
            # Phase 5: Integration & Testing
            self.logger.info("\n[PHASE 5] INTEGRATION & TESTING")
            test_results = await self._phase_testing(backend_code, frontend_code)
            
            # Phase 6: Self-Healing (if needed)
            if not test_results["all_passed"]:
                self.logger.info("\n[PHASE 6] SELF-HEALING INITIATED")
                backend_code, frontend_code = await self._phase_healing(
                    test_results, backend_code, frontend_code, architecture
                )
                
                # Re-test after healing
                test_results = await self._phase_testing(backend_code, frontend_code)
            
            self.state_manager.update_phase("testing", "completed", test_results)
            
            # Phase 7: Final Validation
            self.logger.info("\n[PHASE 7] FINAL VALIDATION")
            validation_result = await self._phase_validation(backend_code, frontend_code)
            self.state_manager.update_phase("validation", "completed", validation_result)
            
            # Phase 8: Package & Deploy Prep
            self.logger.info("\n[PHASE 8] PACKAGING")
            final_output = await self._phase_packaging(
                requirements, architecture, backend_code, frontend_code, validation_result
            )
            
            # Save decisions log
            self._save_decisions_log()
            
            self.logger.info("\n" + "=" * 80)
            self.logger.info("AUTONOMOUS SDLC PROCESS COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 80)
            
            return final_output
            
        except Exception as e:
            self.logger.error(f"Critical error in SDLC process: {str(e)}", exc_info=True)
            self.state_manager.update_phase("error", "failed", {"error": str(e)})
            raise
    
    async def _phase_requirements_analysis(self) -> Dict:
        """Phase 1: Analyze requirements document"""
        self.logger.info("Reading requirements document...")
        
        with open(self.requirements_file, 'r') as f:
            raw_requirements = f.read()
        
        self.logger.info("Analyst Agent processing requirements...")
        analysis = await self.analyst.analyze(raw_requirements)
        
        # Log decision
        self.decisions_log.append({
            "phase": "requirements_analysis",
            "timestamp": datetime.now().isoformat(),
            "decision": "Requirements analyzed and structured",
            "details": analysis.get("summary", "")
        })
        
        return analysis
    
    async def _phase_architecture_design(self, requirements: Dict) -> Dict:
        """Phase 2: Design system architecture"""
        self.logger.info("Architect Agent designing system architecture...")
        
        architecture = await self.architect.design(requirements)
        
        # Log architectural decisions
        for decision in architecture.get("key_decisions", []):
            self.decisions_log.append({
                "phase": "architecture_design",
                "timestamp": datetime.now().isoformat(),
                "decision": decision["decision"],
                "rationale": decision.get("rationale", ""),
                "alternatives_considered": decision.get("alternatives", [])
            })
        
        return architecture
    
    async def _phase_backend_development(self, architecture: Dict) -> Dict:
        """Phase 3: Generate backend code"""
        self.logger.info("Backend Agent generating code...")
        
        backend_code = await self.backend_agent.generate(architecture)
        
        # Save backend files
        backend_dir = self.output_dir / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        for file_path, content in backend_code["files"].items():
            full_path = backend_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
        
        self.logger.info(f"Backend code generated: {len(backend_code['files'])} files")
        
        return backend_code
    
    async def _phase_frontend_development(self, architecture: Dict, backend_code: Dict) -> Dict:
        """Phase 4: Generate frontend code"""
        self.logger.info("Frontend Agent generating code...")
        
        frontend_code = await self.frontend_agent.generate(architecture, backend_code)
        
        # Save frontend files
        frontend_dir = self.output_dir / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        for file_path, content in frontend_code["files"].items():
            full_path = frontend_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
        
        self.logger.info(f"Frontend code generated: {len(frontend_code['files'])} files")
        
        return frontend_code
    
    async def _phase_testing(self, backend_code: Dict, frontend_code: Dict) -> Dict:
        """Phase 5: Run QA tests"""
        self.logger.info("QA Agent running tests...")
        
        test_results = await self.qa_agent.test(backend_code, frontend_code)
        
        self.logger.info(f"Tests completed: {test_results['passed']}/{test_results['total']} passed")
        
        return test_results
    
    async def _phase_healing(
        self, 
        test_results: Dict, 
        backend_code: Dict, 
        frontend_code: Dict,
        architecture: Dict
    ) -> tuple:
        """Phase 6: Self-healing process"""
        self.logger.info("Healer Agent initiating self-correction...")
        
        healed_backend, healed_frontend = await self.healer.heal(
            test_results=test_results,
            backend_code=backend_code,
            frontend_code=frontend_code,
            architecture=architecture
        )
        
        # Update files with healed code
        for file_path, content in healed_backend["files"].items():
            full_path = self.output_dir / "backend" / file_path
            with open(full_path, 'w') as f:
                f.write(content)
        
        for file_path, content in healed_frontend["files"].items():
            full_path = self.output_dir / "frontend" / file_path
            with open(full_path, 'w') as f:
                f.write(content)
        
        self.logger.info("Self-healing completed")
        
        # Log healing decisions
        for fix in self.healer.get_applied_fixes():
            self.decisions_log.append({
                "phase": "self_healing",
                "timestamp": datetime.now().isoformat(),
                "decision": f"Applied fix: {fix['description']}",
                "details": fix.get("changes", "")
            })
        
        return healed_backend, healed_frontend
    
    async def _phase_validation(self, backend_code: Dict, frontend_code: Dict) -> Dict:
        """Phase 7: Final validation"""
        self.logger.info("Validator Agent performing final checks...")
        
        validation_result = await self.validator.validate(backend_code, frontend_code)
        
        if validation_result["valid"]:
            self.logger.info("✓ Validation PASSED")
        else:
            self.logger.warning("✗ Validation issues detected")
            for issue in validation_result.get("issues", []):
                self.logger.warning(f"  - {issue}")
        
        return validation_result
    
    async def _phase_packaging(
        self,
        requirements: Dict,
        architecture: Dict,
        backend_code: Dict,
        frontend_code: Dict,
        validation_result: Dict
    ) -> Dict:
        """Phase 8: Package everything for deployment"""
        self.logger.info("Packaging final deliverables...")
        
        # Generate deployment scripts
        await self._generate_deployment_scripts(architecture)
        
        # Generate documentation
        await self._generate_documentation(requirements, architecture)
        
        # Generate README
        await self._generate_readme(requirements, architecture)
        
        final_output = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "output_directory": str(self.output_dir.absolute()),
            "backend": {
                "files_count": len(backend_code["files"]),
                "entry_point": backend_code.get("entry_point", "server.js"),
                "technology": architecture["backend"]["technology"]
            },
            "frontend": {
                "files_count": len(frontend_code["files"]),
                "entry_point": frontend_code.get("entry_point", "index.html"),
                "technology": architecture["frontend"]["technology"]
            },
            "validation": validation_result,
            "next_steps": [
                "Review the generated code in the output directory",
                "Run 'cd output/backend && npm install' (or pip install -r requirements.txt)",
                "Run 'cd output/frontend && npm install'",
                "Execute deployment scripts in output/deployment/",
                "Review decisions.log for all autonomous decisions made"
            ]
        }
        
        # Save final report
        with open(self.output_dir / "final_report.json", 'w') as f:
            json.dump(final_output, f, indent=2)
        
        return final_output
    
    async def _generate_deployment_scripts(self, architecture: Dict):
        """Generate AWS CDK/Terraform deployment scripts"""
        deployment_dir = self.output_dir / "deployment"
        deployment_dir.mkdir(exist_ok=True)
        
        # This would be expanded based on architecture choices
        # For now, creating basic structure
        
        if architecture.get("cloud_provider") == "aws":
            # Generate CDK code
            cdk_code = self._generate_aws_cdk(architecture)
            with open(deployment_dir / "cdk_app.py", 'w') as f:
                f.write(cdk_code)
            
            # Generate deploy script
            deploy_script = """#!/bin/bash
set -e

echo "Deploying to AWS..."
cd deployment
cdk deploy --require-approval never

echo "Deployment complete!"
"""
            with open(deployment_dir / "deploy.sh", 'w') as f:
                f.write(deploy_script)
            
            os.chmod(deployment_dir / "deploy.sh", 0o755)
    
    def _generate_aws_cdk(self, architecture: Dict) -> str:
        """Generate AWS CDK deployment code"""
        return """#!/usr/bin/env python3
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_rds as rds,
    Duration,
    RemovalPolicy
)
from constructs import Construct

class ApplicationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Backend Lambda
        backend_lambda = lambda_.Function(
            self, "BackendFunction",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_asset("../backend"),
            timeout=Duration.seconds(30)
        )
        
        # API Gateway
        api = apigateway.RestApi(
            self, "API",
            rest_api_name="GeneratedAPI",
            deploy_options=apigateway.StageOptions(stage_name="prod")
        )
        
        integration = apigateway.LambdaIntegration(backend_lambda)
        api.root.add_proxy(default_integration=integration)
        
        # Frontend S3 + CloudFront
        frontend_bucket = s3.Bucket(
            self, "FrontendBucket",
            website_index_document="index.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        distribution = cloudfront.CloudFrontWebDistribution(
            self, "CDN",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=frontend_bucket
                    ),
                    behaviors=[cloudfront.Behavior(is_default_behavior=True)]
                )
            ]
        )
"""
    
    async def _generate_documentation(self, requirements: Dict, architecture: Dict):
        """Generate technical documentation"""
        docs_dir = self.output_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Architecture documentation
        arch_doc = f"""# System Architecture

## Overview
{architecture.get('overview', '')}

## Technology Stack
- **Backend**: {architecture['backend']['technology']}
- **Frontend**: {architecture['frontend']['technology']}
- **Database**: {architecture.get('database', {}).get('type', 'N/A')}

## Components
{json.dumps(architecture.get('components', {}), indent=2)}

## API Endpoints
{json.dumps(architecture.get('api_endpoints', []), indent=2)}
"""
        
        with open(docs_dir / "ARCHITECTURE.md", 'w') as f:
            f.write(arch_doc)
    
    async def _generate_readme(self, requirements: Dict, architecture: Dict):
        """Generate project README"""
        readme = f"""# Auto-Generated Application

**Generated by Autonomous SDLC Factory**  
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Project Overview
{requirements.get('description', 'Auto-generated full-stack application')}

## Quick Start

### Backend
```bash
cd backend
npm install  # or: pip install -r requirements.txt
npm start    # or: python main.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Deployment
```bash
cd deployment
./deploy.sh
```

## Project Structure
```
output/
├── backend/          # Backend application code
├── frontend/         # Frontend application code
├── deployment/       # AWS CDK/Terraform scripts
├── docs/            # Technical documentation
├── decisions.log    # All autonomous decisions made
├── state.json       # Build state tracker
└── final_report.json # Summary report
```

## Technology Stack
- **Backend**: {architecture['backend']['technology']}
- **Frontend**: {architecture['frontend']['technology']}
- **Cloud**: {architecture.get('cloud_provider', 'AWS')}

## Generated Files
- Backend files: {len(architecture.get('backend_files', []))}
- Frontend files: {len(architecture.get('frontend_files', []))}

## Review Points
Please review `decisions.log` to see all architectural and implementation decisions made autonomously.

---
*This project was generated with zero human intervention by the Autonomous SDLC Multi-Agent System.*
"""
        
        with open(self.output_dir / "README.md", 'w') as f:
            f.write(readme)
    
    def _save_decisions_log(self):
        """Save all autonomous decisions to log file"""
        log_file = self.output_dir / "decisions.log"
        
        with open(log_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("AUTONOMOUS DECISIONS LOG\n")
            f.write("=" * 80 + "\n\n")
            
            for decision in self.decisions_log:
                f.write(f"[{decision['timestamp']}] {decision['phase'].upper()}\n")
                f.write(f"Decision: {decision['decision']}\n")
                
                if 'rationale' in decision:
                    f.write(f"Rationale: {decision['rationale']}\n")
                
                if 'details' in decision:
                    f.write(f"Details: {decision['details']}\n")
                
                if 'alternatives_considered' in decision:
                    f.write(f"Alternatives: {', '.join(decision['alternatives_considered'])}\n")
                
                f.write("\n" + "-" * 80 + "\n\n")


async def main():
    """Entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <requirements_document.md>")
        sys.exit(1)
    
    requirements_file = sys.argv[1]
    
    if not os.path.exists(requirements_file):
        print(f"Error: Requirements file '{requirements_file}' not found")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("AUTONOMOUS SDLC MULTI-AGENT FACTORY")
    print("=" * 80)
    print(f"\nRequirements: {requirements_file}")
    print("Output directory: ./output")
    print("\nStarting autonomous build process...")
    print("No human intervention required.\n")
    
    factory = AutonomousSDLCFactory(requirements_file)
    result = await factory.execute()
    
    print("\n" + "=" * 80)
    print("BUILD COMPLETE!")
    print("=" * 80)
    print(f"\nOutput directory: {result['output_directory']}")
    print(f"Backend files: {result['backend']['files_count']}")
    print(f"Frontend files: {result['frontend']['files_count']}")
    print("\nNext steps:")
    for step in result['next_steps']:
        print(f"  • {step}")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
