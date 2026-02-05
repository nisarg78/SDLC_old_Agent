"""
Healer Agent
Self-corrects code based on test failures and errors.
Uses recursion with maximum attempt limits.
"""

import json
import re
from typing import Dict, List, Tuple


class HealerAgent:
    """
    Analyzes test failures and applies fixes autonomously.
    Has a recursion limit to prevent infinite loops.
    """
    
    def __init__(self, config, logger, max_attempts: int = 5):
        self.config = config
        self.logger = logger
        self.max_attempts = max_attempts
        self.claude_api_key = config.ANTHROPIC_API_KEY
        self.applied_fixes = []
        self.attempt_count = 0
    
    async def heal(
        self,
        test_results: Dict,
        backend_code: Dict,
        frontend_code: Dict,
        architecture: Dict
    ) -> Tuple[Dict, Dict]:
        """
        Heal code based on test failures.
        Returns healed backend and frontend code.
        """
        self.logger.info("Healer Agent: Initiating self-healing process...")
        self.applied_fixes = []
        self.attempt_count = 0
        
        failed_tests = [t for t in test_results["tests"] if t["status"] == "failed"]
        
        self.logger.info(f"Healer Agent: Found {len(failed_tests)} failed tests")
        
        healed_backend = backend_code.copy()
        healed_frontend = frontend_code.copy()
        
        for test in failed_tests:
            if self.attempt_count >= self.max_attempts:
                self.logger.warning(f"Healer Agent: Max attempts ({self.max_attempts}) reached")
                break
            
            self.attempt_count += 1
            
            self.logger.info(f"Healer Agent: Fixing test '{test['name']}' (attempt {self.attempt_count})")
            
            # Determine which code needs fixing
            if "backend" in test["name"].lower():
                healed_backend = await self._fix_backend(test, healed_backend, architecture)
            elif "frontend" in test["name"].lower():
                healed_frontend = await self._fix_frontend(test, healed_frontend, architecture)
            else:
                # Try to fix both
                healed_backend = await self._fix_backend(test, healed_backend, architecture)
                healed_frontend = await self._fix_frontend(test, healed_frontend, architecture)
        
        self.logger.info(f"Healer Agent: Applied {len(self.applied_fixes)} fixes")
        
        return healed_backend, healed_frontend
    
    async def _fix_backend(self, test: Dict, backend_code: Dict, architecture: Dict) -> Dict:
        """Fix backend code based on test failure"""
        test_name = test["name"]
        error = test.get("error", "Unknown error")
        
        self.logger.info(f"Healer Agent: Diagnosing backend issue - {error}")
        
        # Apply specific fixes based on error type
        if "package.json" in test_name.lower():
            backend_code = self._fix_package_json(backend_code, error, "backend")
        
        elif "missing files" in error.lower():
            backend_code = self._fix_missing_files(backend_code, error, architecture, "backend")
        
        elif "syntax" in error.lower():
            backend_code = await self._fix_syntax_errors(backend_code, error, "backend")
        
        elif "database" in error.lower():
            backend_code = self._fix_database_config(backend_code, error)
        
        elif "endpoints" in error.lower():
            backend_code = self._fix_api_endpoints(backend_code, error)
        
        else:
            # Generic fix attempt
            backend_code = await self._generic_fix(backend_code, test, "backend")
        
        return backend_code
    
    async def _fix_frontend(self, test: Dict, frontend_code: Dict, architecture: Dict) -> Dict:
        """Fix frontend code based on test failure"""
        test_name = test["name"]
        error = test.get("error", "Unknown error")
        
        self.logger.info(f"Healer Agent: Diagnosing frontend issue - {error}")
        
        # Apply specific fixes based on error type
        if "package.json" in test_name.lower():
            frontend_code = self._fix_package_json(frontend_code, error, "frontend")
        
        elif "missing files" in error.lower():
            frontend_code = self._fix_missing_files(frontend_code, error, architecture, "frontend")
        
        elif "syntax" in error.lower():
            frontend_code = await self._fix_syntax_errors(frontend_code, error, "frontend")
        
        elif "component" in error.lower():
            frontend_code = self._fix_component_structure(frontend_code, error)
        
        elif "api client" in error.lower():
            frontend_code = self._fix_api_client(frontend_code, error)
        
        else:
            # Generic fix attempt
            frontend_code = await self._generic_fix(frontend_code, test, "frontend")
        
        return frontend_code
    
    def _fix_package_json(self, code: Dict, error: str, code_type: str) -> Dict:
        """Fix package.json issues"""
        try:
            package_json = code["files"].get("package.json", "{}")
            data = json.loads(package_json)
            
            # Fix missing dependencies
            if "missing dependencies" in error.lower():
                missing_deps = re.findall(r"'([^']+)'", error)
                
                if "dependencies" not in data:
                    data["dependencies"] = {}
                
                for dep in missing_deps:
                    if dep == "react":
                        data["dependencies"]["react"] = "^18.2.0"
                    elif dep == "react-dom":
                        data["dependencies"]["react-dom"] = "^18.2.0"
                    elif dep == "express":
                        data["dependencies"]["express"] = "^4.18.2"
                    else:
                        data["dependencies"][dep] = "latest"
                
                code["files"]["package.json"] = json.dumps(data, indent=2)
                
                self.applied_fixes.append({
                    "description": f"Added missing dependencies to package.json: {', '.join(missing_deps)}",
                    "changes": f"Updated {code_type}/package.json"
                })
            
            return code
            
        except Exception as e:
            self.logger.error(f"Healer Agent: Error fixing package.json - {str(e)}")
            return code
    
    def _fix_missing_files(self, code: Dict, error: str, architecture: Dict, code_type: str) -> Dict:
        """Create missing required files"""
        missing_files = re.findall(r"([a-zA-Z0-9/_.-]+\.[a-z]+)", error)
        
        for file in missing_files:
            if file not in code["files"]:
                # Create basic file content
                if file.endswith(".js"):
                    code["files"][file] = self._generate_placeholder_js(file)
                elif file.endswith(".html"):
                    code["files"][file] = self._generate_placeholder_html()
                elif file.endswith(".css"):
                    code["files"][file] = "/* Auto-generated styles */\n"
                
                self.applied_fixes.append({
                    "description": f"Created missing file: {file}",
                    "changes": f"Added {code_type}/{file}"
                })
        
        return code
    
    async def _fix_syntax_errors(self, code: Dict, error: str, code_type: str) -> Dict:
        """Fix syntax errors in code"""
        # Extract file name from error
        file_match = re.search(r"in ([a-zA-Z0-9/_.-]+\.[a-z]+)", error)
        
        if file_match:
            file_name = file_match.group(1)
            
            if file_name in code["files"]:
                content = code["files"][file_name]
                
                # Fix unbalanced braces
                if "unbalanced braces" in error.lower():
                    open_count = content.count('{')
                    close_count = content.count('}')
                    
                    if open_count > close_count:
                        content += '\n' + '}' * (open_count - close_count)
                    
                    code["files"][file_name] = content
                    
                    self.applied_fixes.append({
                        "description": f"Fixed unbalanced braces in {file_name}",
                        "changes": f"Added {open_count - close_count} closing braces"
                    })
                
                # Fix unbalanced parentheses
                elif "unbalanced parentheses" in error.lower():
                    open_count = content.count('(')
                    close_count = content.count(')')
                    
                    if open_count > close_count:
                        content += ')' * (open_count - close_count)
                    
                    code["files"][file_name] = content
                    
                    self.applied_fixes.append({
                        "description": f"Fixed unbalanced parentheses in {file_name}",
                        "changes": f"Added {open_count - close_count} closing parentheses"
                    })
        
        return code
    
    def _fix_database_config(self, backend_code: Dict, error: str) -> Dict:
        """Fix database configuration issues"""
        db_config_file = "config/database.js"
        
        if db_config_file not in backend_code["files"]:
            # Create basic database config
            backend_code["files"][db_config_file] = """const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://localhost/app_db'
});

module.exports = {
  query: (text, params) => pool.query(text, params)
};
"""
            
            self.applied_fixes.append({
                "description": "Created database configuration file",
                "changes": f"Added {db_config_file}"
            })
        
        return backend_code
    
    def _fix_api_endpoints(self, backend_code: Dict, error: str) -> Dict:
        """Fix API endpoint definition issues"""
        routes_file = "routes/index.js"
        
        if routes_file in backend_code["files"]:
            content = backend_code["files"][routes_file]
            
            if "no routes defined" in error.lower():
                # Add a default health check route
                if "router.get" not in content:
                    content += "\n\nrouter.get('/health', (req, res) => res.json({ status: 'ok' }));\n"
                    backend_code["files"][routes_file] = content
                    
                    self.applied_fixes.append({
                        "description": "Added default health check route",
                        "changes": f"Updated {routes_file}"
                    })
        
        return backend_code
    
    def _fix_component_structure(self, frontend_code: Dict, error: str) -> Dict:
        """Fix React component structure issues"""
        app_file = "src/App.js"
        
        if app_file in frontend_code["files"]:
            content = frontend_code["files"][app_file]
            
            # Fix missing component definition
            if "no app component defined" in error.lower():
                if "function App" not in content and "class App" not in content:
                    # Add basic component
                    content += "\n\nfunction App() {\n  return <div>App</div>;\n}\n"
                    frontend_code["files"][app_file] = content
            
            # Fix missing export
            if "not exported" in error.lower():
                if "export default App" not in content:
                    content += "\nexport default App;\n"
                    frontend_code["files"][app_file] = content
            
            self.applied_fixes.append({
                "description": "Fixed App component structure",
                "changes": f"Updated {app_file}"
            })
        
        return frontend_code
    
    def _fix_api_client(self, frontend_code: Dict, error: str) -> Dict:
        """Fix API client issues"""
        api_file = "src/services/api.js"
        
        if api_file not in frontend_code["files"]:
            # Create basic API client
            frontend_code["files"][api_file] = """import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3000/api'
});

export const apiService = {
  get: (endpoint) => api.get(endpoint),
  post: (endpoint, data) => api.post(endpoint, data),
  put: (endpoint, data) => api.put(endpoint, data),
  delete: (endpoint) => api.delete(endpoint)
};

export default api;
"""
            
            self.applied_fixes.append({
                "description": "Created API client",
                "changes": f"Added {api_file}"
            })
        
        return frontend_code
    
    async def _generic_fix(self, code: Dict, test: Dict, code_type: str) -> Dict:
        """Attempt a generic fix using Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_api_key)
            
            prompt = f"""A test failed with the following error:

Test: {test['name']}
Error: {test.get('error', 'Unknown error')}

Please suggest a specific fix for this error. Respond with just the fix description, no code.
"""
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggestion = response.content[0].text
            
            self.logger.info(f"Healer Agent: Generic fix suggestion - {suggestion[:100]}...")
            
            self.applied_fixes.append({
                "description": f"Generic fix attempt: {suggestion[:100]}",
                "changes": "Analyzed but no automatic fix applied"
            })
            
        except Exception as e:
            self.logger.error(f"Healer Agent: Error in generic fix - {str(e)}")
        
        return code
    
    def _generate_placeholder_js(self, file_name: str) -> str:
        """Generate placeholder JS file"""
        return f"""// Auto-generated placeholder for {file_name}
// TODO: Implement functionality

module.exports = {{}};
"""
    
    def _generate_placeholder_html(self) -> str:
        """Generate placeholder HTML"""
        return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>App</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
"""
    
    def get_applied_fixes(self) -> List[Dict]:
        """Get list of all fixes applied"""
        return self.applied_fixes
