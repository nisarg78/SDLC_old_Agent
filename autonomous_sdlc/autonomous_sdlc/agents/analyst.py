"""
Analyst Agent
Parses requirements document and creates structured technical specifications.
"""

import json
import re
from typing import Dict, List


class AnalystAgent:
    """
    Analyzes requirements document and extracts:
    - Functional requirements
    - Non-functional requirements
    - User stories
    - Technical constraints
    - Success criteria
    """
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.claude_api_key = config.ANTHROPIC_API_KEY
    
    async def analyze(self, raw_requirements: str) -> Dict:
        """
        Analyze requirements document and structure it.
        Uses Claude API to understand and parse requirements.
        """
        self.logger.info("Analyst: Processing requirements document...")
        
        # Call Claude API to analyze requirements
        analysis_prompt = self._create_analysis_prompt(raw_requirements)
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_api_key)
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }]
            )
            
            # Parse Claude's response
            analysis_text = response.content[0].text
            
            # Extract structured data
            structured_analysis = self._parse_analysis(analysis_text)
            
            self.logger.info(f"Analyst: Identified {len(structured_analysis['features'])} features")
            self.logger.info(f"Analyst: Extracted {len(structured_analysis['user_stories'])} user stories")
            
            return structured_analysis
            
        except Exception as e:
            self.logger.error(f"Analyst: Error during analysis - {str(e)}")
            # Fallback to basic parsing
            return self._basic_parse(raw_requirements)
    
    def _create_analysis_prompt(self, requirements: str) -> str:
        """Create prompt for Claude to analyze requirements"""
        return f"""You are a senior business analyst. Analyze this requirements document and extract structured information.

Requirements Document:
{requirements}

Please provide a JSON response with the following structure:
{{
  "project_name": "...",
  "description": "...",
  "features": [
    {{"id": "F1", "name": "...", "description": "...", "priority": "high|medium|low"}}
  ],
  "user_stories": [
    {{"id": "US1", "as_a": "...", "i_want": "...", "so_that": "..."}}
  ],
  "functional_requirements": [
    {{"id": "FR1", "requirement": "...", "category": "..."}}
  ],
  "non_functional_requirements": [
    {{"id": "NFR1", "requirement": "...", "category": "performance|security|scalability|..."}}
  ],
  "technical_constraints": [
    "..."
  ],
  "success_criteria": [
    "..."
  ],
  "assumptions": [
    "..."
  ]
}}

If anything is not explicitly mentioned, make reasonable assumptions and note them in the assumptions array."""
    
    def _parse_analysis(self, analysis_text: str) -> Dict:
        """Parse Claude's analysis response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # Add metadata
                data["analysis_version"] = "1.0"
                data["analyzed_at"] = self._get_timestamp()
                
                return data
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            self.logger.warning(f"Analyst: Failed to parse JSON response - {str(e)}")
            return self._basic_parse(analysis_text)
    
    def _basic_parse(self, text: str) -> Dict:
        """Fallback basic parsing if Claude API fails"""
        self.logger.info("Analyst: Using basic parsing fallback")
        
        return {
            "project_name": "Generated Application",
            "description": text[:200] + "..." if len(text) > 200 else text,
            "features": self._extract_features(text),
            "user_stories": [],
            "functional_requirements": [],
            "non_functional_requirements": [
                {"id": "NFR1", "requirement": "System should be performant", "category": "performance"},
                {"id": "NFR2", "requirement": "System should be secure", "category": "security"}
            ],
            "technical_constraints": [],
            "success_criteria": ["Application builds and runs successfully"],
            "assumptions": [
                "Using modern web technologies",
                "Deploying to cloud infrastructure",
                "RESTful API architecture"
            ],
            "analysis_version": "1.0",
            "analyzed_at": self._get_timestamp()
        }
    
    def _extract_features(self, text: str) -> List[Dict]:
        """Extract features from text using basic pattern matching"""
        features = []
        
        # Look for numbered lists, bullet points, etc.
        patterns = [
            r'(?:^|\n)\s*[-*•]\s*(.+)',  # Bullet points
            r'(?:^|\n)\s*\d+\.\s*(.+)',  # Numbered lists
        ]
        
        feature_id = 1
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                features.append({
                    "id": f"F{feature_id}",
                    "name": match.strip()[:50],
                    "description": match.strip(),
                    "priority": "medium"
                })
                feature_id += 1
        
        # If no features found, create a default one
        if not features:
            features.append({
                "id": "F1",
                "name": "Core Application",
                "description": "Build the core application based on requirements",
                "priority": "high"
            })
        
        return features[:10]  # Limit to 10 features
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
