"""
Architect Agent
Designs the system architecture based on requirements analysis.
Makes autonomous decisions about tech stack, database, API design, etc.
"""

import json
from typing import Dict, List


class ArchitectAgent:
    """
    Creates technical architecture including:
    - Technology stack selection
    - Database schema design
    - API endpoint design
    - Component architecture
    - Deployment architecture
    """
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.claude_api_key = config.ANTHROPIC_API_KEY
    
    async def design(self, requirements: Dict) -> Dict:
        """
        Design system architecture based on requirements.
        Makes autonomous decisions for any ambiguous aspects.
        """
        self.logger.info("Architect: Designing system architecture...")
        
        # Autonomous tech stack selection
        tech_stack = self._select_tech_stack(requirements)
        
        # Design database schema
        database_schema = self._design_database_schema(requirements, tech_stack)
        
        # Design API endpoints
        api_endpoints = self._design_api_endpoints(requirements)
        
        # Create component architecture
        components = self._design_components(requirements, tech_stack)
        
        # Design deployment architecture
        deployment = self._design_deployment(tech_stack)
        
        architecture = {
            "overview": self._generate_overview(requirements),
            "tech_stack": tech_stack,
            "database": database_schema,
            "api_endpoints": api_endpoints,
            "components": components,
            "deployment": deployment,
            "backend": {
                "technology": tech_stack["backend"],
                "framework": tech_stack.get("backend_framework", "Express"),
                "entry_point": "server.js" if "node" in tech_stack["backend"].lower() else "main.py"
            },
            "frontend": {
                "technology": tech_stack["frontend"],
                "framework": tech_stack.get("frontend_framework", "React"),
                "entry_point": "index.html"
            },
            "key_decisions": self._log_decisions(tech_stack, database_schema),
            "cloud_provider": "aws"
        }
        
        self.logger.info(f"Architect: Architecture designed with {tech_stack['backend']} backend and {tech_stack['frontend']} frontend")
        
        return architecture
    
    def _select_tech_stack(self, requirements: Dict) -> Dict:
        """
        Autonomous tech stack selection.
        Makes decisions based on requirements complexity and type.
        """
        num_features = len(requirements.get("features", []))
        has_realtime = any("real-time" in str(f).lower() or "websocket" in str(f).lower() 
                          for f in requirements.get("features", []))
        has_auth = any("auth" in str(f).lower() or "login" in str(f).lower() 
                      for f in requirements.get("features", []))
        
        # Decision: Backend technology
        if has_realtime:
            backend = "Node.js"
            backend_framework = "Express + Socket.io"
            reason_backend = "Real-time features require WebSocket support"
        elif num_features > 10:
            backend = "Python"
            backend_framework = "FastAPI"
            reason_backend = "Complex business logic benefits from Python's libraries"
        else:
            backend = "Node.js"
            backend_framework = "Express"
            reason_backend = "Standard choice for web APIs, large ecosystem"
        
        # Decision: Frontend technology
        if num_features > 15:
            frontend = "React"
            frontend_framework = "React + TypeScript"
            reason_frontend = "Complex UI requires component-based architecture"
        else:
            frontend = "React"
            frontend_framework = "React"
            reason_frontend = "Industry standard, good developer experience"
        
        # Decision: Database
        has_complex_relations = num_features > 5
        if has_complex_relations:
            database = "PostgreSQL"
            reason_database = "Relational data with complex relationships"
        else:
            database = "PostgreSQL"
            reason_database = "Reliable, ACID-compliant, good default choice"
        
        stack = {
            "backend": backend,
            "backend_framework": backend_framework,
            "backend_reason": reason_backend,
            "frontend": frontend,
            "frontend_framework": frontend_framework,
            "frontend_reason": reason_frontend,
            "database": database,
            "database_reason": reason_database,
            "authentication": "JWT" if has_auth else "none",
            "caching": "Redis" if num_features > 10 else "none",
            "testing_framework": "Jest" if backend == "Node.js" else "pytest"
        }
        
        self.logger.info(f"Architect Decision: Backend={backend}, Frontend={frontend}, DB={database}")
        
        return stack
    
    def _design_database_schema(self, requirements: Dict, tech_stack: Dict) -> Dict:
        """
        Design database schema based on entities in requirements.
        """
        features = requirements.get("features", [])
        
        # Extract entities from features
        entities = self._extract_entities(features)
        
        # Create tables for each entity
        tables = []
        for entity in entities:
            table = {
                "name": entity["name"].lower() + "s",
                "columns": entity["fields"],
                "indexes": [f"idx_{entity['name'].lower()}_id"],
                "relationships": entity.get("relationships", [])
            }
            tables.append(table)
        
        # Add standard tables
        if tech_stack.get("authentication") == "JWT":
            tables.append({
                "name": "users",
                "columns": [
                    {"name": "id", "type": "UUID", "primary_key": True},
                    {"name": "email", "type": "VARCHAR(255)", "unique": True},
                    {"name": "password_hash", "type": "VARCHAR(255)"},
                    {"name": "created_at", "type": "TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP"}
                ],
                "indexes": ["idx_users_email"]
            })
        
        return {
            "type": tech_stack["database"],
            "tables": tables,
            "migrations_required": True
        }
    
    def _extract_entities(self, features: List[Dict]) -> List[Dict]:
        """Extract data entities from features"""
        entities = []
        
        # Common entities based on typical applications
        common_entities = ["user", "product", "order", "item", "post", "comment"]
        
        for feature in features:
            feature_text = str(feature).lower()
            
            for entity_name in common_entities:
                if entity_name in feature_text and entity_name not in [e["name"] for e in entities]:
                    entity = {
                        "name": entity_name.capitalize(),
                        "fields": [
                            {"name": "id", "type": "UUID", "primary_key": True},
                            {"name": "created_at", "type": "TIMESTAMP"},
                            {"name": "updated_at", "type": "TIMESTAMP"}
                        ]
                    }
                    
                    # Add entity-specific fields
                    if entity_name == "product":
                        entity["fields"].extend([
                            {"name": "name", "type": "VARCHAR(255)"},
                            {"name": "description", "type": "TEXT"},
                            {"name": "price", "type": "DECIMAL(10,2)"}
                        ])
                    elif entity_name == "post":
                        entity["fields"].extend([
                            {"name": "title", "type": "VARCHAR(255)"},
                            {"name": "content", "type": "TEXT"},
                            {"name": "user_id", "type": "UUID"}
                        ])
                    
                    entities.append(entity)
        
        # If no entities found, create a generic one
        if not entities:
            entities.append({
                "name": "Item",
                "fields": [
                    {"name": "id", "type": "UUID", "primary_key": True},
                    {"name": "name", "type": "VARCHAR(255)"},
                    {"name": "data", "type": "JSONB"},
                    {"name": "created_at", "type": "TIMESTAMP"}
                ]
            })
        
        return entities
    
    def _design_api_endpoints(self, requirements: Dict) -> List[Dict]:
        """Design RESTful API endpoints"""
        endpoints = []
        features = requirements.get("features", [])
        
        # Standard CRUD endpoints
        resource_types = ["items", "users", "posts", "products"]
        
        for resource in resource_types[:min(3, len(features))]:  # Limit based on features
            endpoints.extend([
                {"method": "GET", "path": f"/api/{resource}", "description": f"List all {resource}"},
                {"method": "GET", "path": f"/api/{resource}/:id", "description": f"Get {resource[:-1]} by ID"},
                {"method": "POST", "path": f"/api/{resource}", "description": f"Create new {resource[:-1]}"},
                {"method": "PUT", "path": f"/api/{resource}/:id", "description": f"Update {resource[:-1]}"},
                {"method": "DELETE", "path": f"/api/{resource}/:id", "description": f"Delete {resource[:-1]}"}
            ])
        
        # Health check endpoint
        endpoints.append({"method": "GET", "path": "/health", "description": "Health check"})
        
        return endpoints
    
    def _design_components(self, requirements: Dict, tech_stack: Dict) -> Dict:
        """Design application components"""
        return {
            "backend_components": [
                "API Server",
                "Database Layer",
                "Business Logic",
                "Authentication Middleware",
                "Error Handler"
            ],
            "frontend_components": [
                "App Container",
                "Routing",
                "State Management",
                "UI Components",
                "API Client"
            ],
            "shared": [
                "Types/Interfaces",
                "Validation Schemas"
            ]
        }
    
    def _design_deployment(self, tech_stack: Dict) -> Dict:
        """Design deployment architecture"""
        return {
            "backend_deployment": {
                "type": "AWS Lambda + API Gateway",
                "runtime": "nodejs18.x" if "Node" in tech_stack["backend"] else "python3.11",
                "memory": "512MB",
                "timeout": "30s"
            },
            "frontend_deployment": {
                "type": "S3 + CloudFront",
                "hosting": "Static site"
            },
            "database_deployment": {
                "type": "RDS PostgreSQL",
                "instance": "db.t3.micro"
            },
            "cicd": {
                "tool": "GitHub Actions",
                "stages": ["build", "test", "deploy"]
            }
        }
    
    def _generate_overview(self, requirements: Dict) -> str:
        """Generate architecture overview"""
        project_name = requirements.get("project_name", "Application")
        description = requirements.get("description", "")
        
        return f"{project_name} - {description[:200]}"
    
    def _log_decisions(self, tech_stack: Dict, database_schema: Dict) -> List[Dict]:
        """Log all architectural decisions"""
        decisions = []
        
        decisions.append({
            "decision": f"Backend: {tech_stack['backend']} with {tech_stack['backend_framework']}",
            "rationale": tech_stack["backend_reason"],
            "alternatives": ["Python/FastAPI", "Go/Gin", "Java/Spring Boot"]
        })
        
        decisions.append({
            "decision": f"Frontend: {tech_stack['frontend']} with {tech_stack['frontend_framework']}",
            "rationale": tech_stack["frontend_reason"],
            "alternatives": ["Vue.js", "Angular", "Svelte"]
        })
        
        decisions.append({
            "decision": f"Database: {tech_stack['database']}",
            "rationale": tech_stack["database_reason"],
            "alternatives": ["MySQL", "MongoDB", "DynamoDB"]
        })
        
        return decisions
