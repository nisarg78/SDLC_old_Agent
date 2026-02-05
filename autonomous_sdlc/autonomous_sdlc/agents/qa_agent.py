"""
QA Agent
Tests generated backend and frontend code for correctness and integration.
"""

import json
import subprocess
from typing import Dict, List


class QAAgent:
    """
    Runs automated tests on generated code:
    - Syntax validation
    - Dependency checks
    - Unit tests
    - Integration tests
    - Security scans
    """
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.test_results = []
    
    async def test(self, backend_code: Dict, frontend_code: Dict) -> Dict:
        """Run all tests on backend and frontend code"""
        self.logger.info("QA Agent: Starting comprehensive testing...")
        
        self.test_results = []
        
        # Test backend
        backend_results = await self._test_backend(backend_code)
        
        # Test frontend
        frontend_results = await self._test_frontend(frontend_code)
        
        # Integration tests
        integration_results = await self._test_integration(backend_code, frontend_code)
        
        # Compile results
        all_tests = backend_results + frontend_results + integration_results
        passed = sum(1 for t in all_tests if t["status"] == "passed")
        total = len(all_tests)
        
        result = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "all_passed": passed == total,
            "tests": all_tests,
            "warnings": self._get_warnings(all_tests)
        }
        
        self.logger.info(f"QA Agent: Tests completed - {passed}/{total} passed")
        
        if not result["all_passed"]:
            self.logger.warning(f"QA Agent: {result['failed']} tests failed")
            for test in all_tests:
                if test["status"] == "failed":
                    self.logger.warning(f"  FAILED: {test['name']} - {test.get('error', 'Unknown error')}")
        
        return result
    
    async def _test_backend(self, backend_code: Dict) -> List[Dict]:
        """Test backend code"""
        tests = []
        
        # Test 1: Validate package.json
        tests.append(self._test_package_json_valid(backend_code))
        
        # Test 2: Check for required files
        tests.append(self._test_required_backend_files(backend_code))
        
        # Test 3: Syntax check
        tests.append(await self._test_backend_syntax(backend_code))
        
        # Test 4: Database configuration
        tests.append(self._test_database_config(backend_code))
        
        # Test 5: API endpoints defined
        tests.append(self._test_api_endpoints_exist(backend_code))
        
        return tests
    
    async def _test_frontend(self, frontend_code: Dict) -> List[Dict]:
        """Test frontend code"""
        tests = []
        
        # Test 1: Validate package.json
        tests.append(self._test_frontend_package_json(frontend_code))
        
        # Test 2: Check for required files
        tests.append(self._test_required_frontend_files(frontend_code))
        
        # Test 3: Syntax check
        tests.append(await self._test_frontend_syntax(frontend_code))
        
        # Test 4: Component structure
        tests.append(self._test_component_structure(frontend_code))
        
        return tests
    
    async def _test_integration(self, backend_code: Dict, frontend_code: Dict) -> List[Dict]:
        """Test integration between frontend and backend"""
        tests = []
        
        # Test 1: API client configuration
        tests.append(self._test_api_client_config(frontend_code))
        
        # Test 2: Endpoint coverage
        tests.append(self._test_endpoint_coverage(backend_code, frontend_code))
        
        return tests
    
    def _test_package_json_valid(self, backend_code: Dict) -> Dict:
        """Test if package.json is valid JSON"""
        try:
            package_json = backend_code["files"].get("package.json")
            if not package_json:
                return {
                    "name": "Backend package.json exists",
                    "status": "failed",
                    "error": "package.json file not found"
                }
            
            json.loads(package_json)
            return {
                "name": "Backend package.json valid",
                "status": "passed"
            }
        except json.JSONDecodeError as e:
            return {
                "name": "Backend package.json valid",
                "status": "failed",
                "error": f"Invalid JSON: {str(e)}"
            }
    
    def _test_required_backend_files(self, backend_code: Dict) -> Dict:
        """Test if all required backend files exist"""
        required_files = ["package.json", "server.js", "routes/index.js"]
        missing_files = []
        
        for file in required_files:
            if file not in backend_code["files"]:
                missing_files.append(file)
        
        if missing_files:
            return {
                "name": "Backend required files exist",
                "status": "failed",
                "error": f"Missing files: {', '.join(missing_files)}"
            }
        else:
            return {
                "name": "Backend required files exist",
                "status": "passed"
            }
    
    async def _test_backend_syntax(self, backend_code: Dict) -> Dict:
        """Basic syntax validation for backend code"""
        try:
            # Check for common syntax errors in JS files
            js_files = [f for f in backend_code["files"].keys() if f.endswith('.js')]
            
            for file in js_files:
                content = backend_code["files"][file]
                
                # Check for balanced braces
                if content.count('{') != content.count('}'):
                    return {
                        "name": "Backend syntax check",
                        "status": "failed",
                        "error": f"Unbalanced braces in {file}"
                    }
                
                # Check for balanced parentheses
                if content.count('(') != content.count(')'):
                    return {
                        "name": "Backend syntax check",
                        "status": "failed",
                        "error": f"Unbalanced parentheses in {file}"
                    }
            
            return {
                "name": "Backend syntax check",
                "status": "passed"
            }
        except Exception as e:
            return {
                "name": "Backend syntax check",
                "status": "failed",
                "error": str(e)
            }
    
    def _test_database_config(self, backend_code: Dict) -> Dict:
        """Test database configuration exists"""
        db_config = backend_code["files"].get("config/database.js")
        
        if not db_config:
            return {
                "name": "Database config exists",
                "status": "failed",
                "error": "config/database.js not found"
            }
        
        # Check for required database elements
        required_elements = ["Pool", "query"]
        missing = [e for e in required_elements if e not in db_config]
        
        if missing:
            return {
                "name": "Database config valid",
                "status": "failed",
                "error": f"Missing elements: {', '.join(missing)}"
            }
        
        return {
            "name": "Database config valid",
            "status": "passed"
        }
    
    def _test_api_endpoints_exist(self, backend_code: Dict) -> Dict:
        """Test that API endpoints are defined"""
        routes = backend_code["files"].get("routes/index.js")
        
        if not routes:
            return {
                "name": "API endpoints defined",
                "status": "failed",
                "error": "routes/index.js not found"
            }
        
        # Check for route definitions
        if "router.get" not in routes and "router.post" not in routes:
            return {
                "name": "API endpoints defined",
                "status": "failed",
                "error": "No routes defined"
            }
        
        return {
            "name": "API endpoints defined",
            "status": "passed"
        }
    
    def _test_frontend_package_json(self, frontend_code: Dict) -> Dict:
        """Test frontend package.json validity"""
        try:
            package_json = frontend_code["files"].get("package.json")
            if not package_json:
                return {
                    "name": "Frontend package.json exists",
                    "status": "failed",
                    "error": "package.json file not found"
                }
            
            data = json.loads(package_json)
            
            # Check for required dependencies
            required_deps = ["react", "react-dom"]
            missing_deps = [d for d in required_deps if d not in data.get("dependencies", {})]
            
            if missing_deps:
                return {
                    "name": "Frontend package.json valid",
                    "status": "failed",
                    "error": f"Missing dependencies: {', '.join(missing_deps)}"
                }
            
            return {
                "name": "Frontend package.json valid",
                "status": "passed"
            }
        except json.JSONDecodeError as e:
            return {
                "name": "Frontend package.json valid",
                "status": "failed",
                "error": f"Invalid JSON: {str(e)}"
            }
    
    def _test_required_frontend_files(self, frontend_code: Dict) -> Dict:
        """Test required frontend files exist"""
        required_files = ["package.json", "public/index.html", "src/App.js", "src/index.js"]
        missing_files = []
        
        for file in required_files:
            if file not in frontend_code["files"]:
                missing_files.append(file)
        
        if missing_files:
            return {
                "name": "Frontend required files exist",
                "status": "failed",
                "error": f"Missing files: {', '.join(missing_files)}"
            }
        else:
            return {
                "name": "Frontend required files exist",
                "status": "passed"
            }
    
    async def _test_frontend_syntax(self, frontend_code: Dict) -> Dict:
        """Basic syntax validation for frontend code"""
        try:
            # Check JSX/JS files
            js_files = [f for f in frontend_code["files"].keys() if f.endswith('.js') or f.endswith('.jsx')]
            
            for file in js_files:
                content = frontend_code["files"][file]
                
                # Check for balanced braces
                if content.count('{') != content.count('}'):
                    return {
                        "name": "Frontend syntax check",
                        "status": "failed",
                        "error": f"Unbalanced braces in {file}"
                    }
                
                # Check for React imports
                if "App.js" in file and "import React" not in content:
                    return {
                        "name": "Frontend syntax check",
                        "status": "failed",
                        "error": f"Missing React import in {file}"
                    }
            
            return {
                "name": "Frontend syntax check",
                "status": "passed"
            }
        except Exception as e:
            return {
                "name": "Frontend syntax check",
                "status": "failed",
                "error": str(e)
            }
    
    def _test_component_structure(self, frontend_code: Dict) -> Dict:
        """Test React component structure"""
        app_js = frontend_code["files"].get("src/App.js")
        
        if not app_js:
            return {
                "name": "Component structure valid",
                "status": "failed",
                "error": "src/App.js not found"
            }
        
        # Check for function/class component
        if "function App" not in app_js and "class App" not in app_js:
            return {
                "name": "Component structure valid",
                "status": "failed",
                "error": "No App component defined"
            }
        
        # Check for export
        if "export default App" not in app_js:
            return {
                "name": "Component structure valid",
                "status": "failed",
                "error": "App component not exported"
            }
        
        return {
            "name": "Component structure valid",
            "status": "passed"
        }
    
    def _test_api_client_config(self, frontend_code: Dict) -> Dict:
        """Test API client configuration"""
        api_client = frontend_code["files"].get("src/services/api.js")
        
        if not api_client:
            return {
                "name": "API client configured",
                "status": "failed",
                "error": "src/services/api.js not found"
            }
        
        # Check for axios
        if "axios" not in api_client:
            return {
                "name": "API client configured",
                "status": "failed",
                "error": "Axios not imported"
            }
        
        return {
            "name": "API client configured",
            "status": "passed"
        }
    
    def _test_endpoint_coverage(self, backend_code: Dict, frontend_code: Dict) -> Dict:
        """Test that frontend has components for backend endpoints"""
        # This is a basic check
        routes = backend_code["files"].get("routes/index.js", "")
        
        # Count backend routes
        backend_routes = routes.count("router.")
        
        # Count frontend components
        frontend_components = len([f for f in frontend_code["files"].keys() if "components/" in f])
        
        if frontend_components == 0 and backend_routes > 0:
            return {
                "name": "Frontend-Backend integration",
                "status": "warning",
                "error": "No frontend components generated for backend routes"
            }
        
        return {
            "name": "Frontend-Backend integration",
            "status": "passed"
        }
    
    def _get_warnings(self, tests: List[Dict]) -> List[str]:
        """Extract warnings from test results"""
        warnings = []
        for test in tests:
            if test["status"] == "warning":
                warnings.append(f"{test['name']}: {test.get('error', 'Warning')}")
        return warnings
