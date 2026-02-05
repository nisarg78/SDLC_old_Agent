"""
Validator Agent
Performs final validation on the complete generated project.
"""

import json
import re
from typing import Dict, List


class ValidatorAgent:
    """
    Final validation checks:
    - Code completeness
    - Best practices
    - Security checks
    - Performance considerations
    - Documentation quality
    """
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    async def validate(self, backend_code: Dict, frontend_code: Dict) -> Dict:
        """Perform comprehensive validation"""
        self.logger.info("Validator Agent: Starting final validation...")
        
        issues = []
        warnings = []
        
        # Validate backend
        backend_issues, backend_warnings = self._validate_backend(backend_code)
        issues.extend(backend_issues)
        warnings.extend(backend_warnings)
        
        # Validate frontend
        frontend_issues, frontend_warnings = self._validate_frontend(frontend_code)
        issues.extend(frontend_issues)
        warnings.extend(frontend_warnings)
        
        # Cross-cutting concerns
        security_issues = self._validate_security(backend_code, frontend_code)
        issues.extend(security_issues)
        
        # Performance checks
        perf_warnings = self._validate_performance(backend_code, frontend_code)
        warnings.extend(perf_warnings)
        
        # Documentation quality
        doc_warnings = self._validate_documentation(backend_code, frontend_code)
        warnings.extend(doc_warnings)
        
        is_valid = len(issues) == 0
        
        result = {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "critical_count": len(issues),
            "warning_count": len(warnings),
            "summary": self._generate_summary(is_valid, issues, warnings)
        }
        
        if is_valid:
            self.logger.info("Validator Agent: ✓ All validation checks passed")
        else:
            self.logger.warning(f"Validator Agent: ✗ Found {len(issues)} critical issues")
        
        if warnings:
            self.logger.info(f"Validator Agent: Found {len(warnings)} warnings")
        
        return result
    
    def _validate_backend(self, backend_code: Dict) -> tuple:
        """Validate backend code"""
        issues = []
        warnings = []
        
        # Check for error handling
        has_error_handler = any("errorHandler" in f or "error" in content.lower() 
                               for f, content in backend_code["files"].items())
        
        if not has_error_handler:
            warnings.append("No centralized error handling middleware found")
        
        # Check for environment configuration
        has_env_example = ".env.example" in backend_code["files"]
        if not has_env_example:
            warnings.append("No .env.example file for environment configuration")
        
        # Check for database connection handling
        db_config = backend_code["files"].get("config/database.js", "")
        if db_config and "error" not in db_config.lower():
            warnings.append("Database config missing error handling")
        
        # Check for input validation
        has_validation = any("validate" in content.lower() or "joi" in content.lower() or "yup" in content.lower()
                            for content in backend_code["files"].values())
        
        if not has_validation:
            warnings.append("No input validation library detected (consider adding Joi or Yup)")
        
        # Check for proper HTTP status codes
        server_js = backend_code["files"].get("server.js", "")
        controllers = {f: c for f, c in backend_code["files"].items() if "controller" in f.lower()}
        
        uses_status_codes = any("201" in content or "404" in content or "400" in content 
                               for content in controllers.values())
        
        if not uses_status_codes:
            warnings.append("Controllers should use appropriate HTTP status codes")
        
        return issues, warnings
    
    def _validate_frontend(self, frontend_code: Dict) -> tuple:
        """Validate frontend code"""
        issues = []
        warnings = []
        
        # Check for error handling in components
        components = {f: c for f, c in frontend_code["files"].items() if "components/" in f}
        
        has_error_handling = any("try" in content and "catch" in content 
                                for content in components.values())
        
        if not has_error_handling:
            warnings.append("Components should include error handling for API calls")
        
        # Check for loading states
        has_loading_states = any("loading" in content.lower() or "isLoading" in content 
                                for content in components.values())
        
        if not has_loading_states:
            warnings.append("Components should implement loading states")
        
        # Check for environment variables
        has_env_config = any("process.env" in content for content in frontend_code["files"].values())
        
        if not has_env_config:
            warnings.append("Frontend should use environment variables for API endpoints")
        
        # Check for accessibility
        html_file = frontend_code["files"].get("public/index.html", "")
        
        if html_file and "lang=" not in html_file:
            warnings.append("HTML should specify language attribute")
        
        # Check for proper component structure
        app_js = frontend_code["files"].get("src/App.js", "")
        
        if app_js and "export default" not in app_js:
            issues.append("App.js must export default component")
        
        return issues, warnings
    
    def _validate_security(self, backend_code: Dict, frontend_code: Dict) -> List[str]:
        """Validate security aspects"""
        issues = []
        
        # Check for hardcoded credentials
        all_code = " ".join(backend_code["files"].values()) + " ".join(frontend_code["files"].values())
        
        if re.search(r"password\s*[:=]\s*['\"][^'\"]+['\"]", all_code, re.IGNORECASE):
            issues.append("CRITICAL: Possible hardcoded password detected")
        
        # Check for SQL injection prevention
        has_parameterized_queries = "$1" in all_code or "?" in all_code
        
        if not has_parameterized_queries:
            issues.append("CRITICAL: Use parameterized queries to prevent SQL injection")
        
        # Check for CORS configuration
        server_js = backend_code["files"].get("server.js", "")
        
        if "cors" not in server_js.lower():
            issues.append("Backend should configure CORS properly")
        
        # Check for Helmet.js usage
        if "helmet" not in server_js.lower():
            issues.append("Backend should use Helmet.js for security headers")
        
        # Check for authentication
        has_auth = any("auth" in f.lower() or "jwt" in content.lower() 
                      for f, content in backend_code["files"].items())
        
        if not has_auth:
            # This is a warning, not critical
            pass  # Already handled in warnings
        
        return issues
    
    def _validate_performance(self, backend_code: Dict, frontend_code: Dict) -> List[str]:
        """Validate performance considerations"""
        warnings = []
        
        # Check for database indexing
        has_indexes = any("index" in content.lower() for content in backend_code["files"].values())
        
        if not has_indexes:
            warnings.append("Consider adding database indexes for better query performance")
        
        # Check for pagination
        has_pagination = any("limit" in content.lower() or "offset" in content.lower() 
                            for content in backend_code["files"].values())
        
        if not has_pagination:
            warnings.append("API endpoints should implement pagination for list operations")
        
        # Check for caching headers
        server_js = backend_code["files"].get("server.js", "")
        
        if "cache" not in server_js.lower():
            warnings.append("Consider adding cache-control headers for static assets")
        
        # Check for lazy loading in frontend
        has_lazy_loading = any("React.lazy" in content or "lazy" in content 
                              for content in frontend_code["files"].values())
        
        if not has_lazy_loading and len(frontend_code["files"]) > 10:
            warnings.append("Consider implementing lazy loading for better initial load time")
        
        return warnings
    
    def _validate_documentation(self, backend_code: Dict, frontend_code: Dict) -> List[str]:
        """Validate documentation quality"""
        warnings = []
        
        # Check for README files
        has_backend_readme = "README.md" in backend_code["files"]
        has_frontend_readme = "README.md" in frontend_code["files"]
        
        if not has_backend_readme:
            warnings.append("Backend should include README.md with setup instructions")
        
        if not has_frontend_readme:
            warnings.append("Frontend should include README.md with setup instructions")
        
        # Check for code comments
        backend_comment_ratio = self._calculate_comment_ratio(backend_code["files"])
        frontend_comment_ratio = self._calculate_comment_ratio(frontend_code["files"])
        
        if backend_comment_ratio < 0.05:  # Less than 5% comments
            warnings.append("Backend code should include more comments for maintainability")
        
        if frontend_comment_ratio < 0.05:
            warnings.append("Frontend code should include more comments for maintainability")
        
        # Check for API documentation
        has_api_docs = any("swagger" in content.lower() or "openapi" in content.lower() 
                          for content in backend_code["files"].values())
        
        if not has_api_docs:
            warnings.append("Consider adding API documentation (Swagger/OpenAPI)")
        
        return warnings
    
    def _calculate_comment_ratio(self, files: Dict[str, str]) -> float:
        """Calculate ratio of comments to code"""
        total_lines = 0
        comment_lines = 0
        
        for filename, content in files.items():
            if filename.endswith(('.js', '.jsx', '.ts', '.tsx')):
                lines = content.split('\n')
                total_lines += len(lines)
                
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                        comment_lines += 1
        
        if total_lines == 0:
            return 0.0
        
        return comment_lines / total_lines
    
    def _generate_summary(self, is_valid: bool, issues: List[str], warnings: List[str]) -> str:
        """Generate validation summary"""
        if is_valid and len(warnings) == 0:
            return "✓ All validation checks passed with no warnings"
        elif is_valid:
            return f"✓ Validation passed with {len(warnings)} warnings to address"
        else:
            return f"✗ Validation failed with {len(issues)} critical issues and {len(warnings)} warnings"
