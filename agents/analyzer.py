"""
Code Analysis Agent using Gemini Flash 2.5
"""
import json
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.prompts import ANALYZE_CODE_PROMPT

class CodeAnalyzer:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1  # Lower for more consistent analysis
        )
    
    def analyze_repository(self, files: List[Dict]) -> Dict:
        """
        Analyze repository files and return structured issues
        """
        # Prepare files content (limit to avoid token limits)
        files_content = self._prepare_files_for_analysis(files)
        
        # Create prompt
        prompt = ANALYZE_CODE_PROMPT.format(files_content=files_content)
        
        # Get analysis from Gemini
        try:
            response = self.llm.invoke(prompt)
            
            # Parse JSON response
            analysis = json.loads(response.content)
            
            # Add file references
            analysis['total_files_analyzed'] = len(files)
            analysis['analyzed_at'] = self._get_timestamp()
            
            return analysis
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._create_fallback_analysis(response.content)
        except Exception as e:
            print(f"Analysis error: {e}")
            return self._create_error_response(str(e))
    
    def _prepare_files_for_analysis(self, files: List[Dict], max_tokens: int = 50000) -> str:
        """
        Prepare files content for analysis, respecting token limits
        """
        content_parts = []
        current_tokens = 0
        
        for file_info in files[:30]:  # Limit to 30 files
            file_str = f"\n{'='*60}\nFile: {file_info['path']}\n{'='*60}\n{file_info['content']}\n"
            
            # Rough token estimation (1 token ≈ 4 chars)
            estimated_tokens = len(file_str) // 4
            
            if current_tokens + estimated_tokens > max_tokens:
                break
                
            content_parts.append(file_str)
            current_tokens += estimated_tokens
        
        return "\n".join(content_parts)
    
    def _create_fallback_analysis(self, raw_response: str) -> Dict:
        """Create structured analysis from non-JSON response"""
        return {
            "documentation_issues": [],
            "code_quality_issues": [],
            "security_issues": [],
            "performance_issues": [],
            "raw_analysis": raw_response,
            "total_files_analyzed": 0
        }
    
    def _create_error_response(self, error: str) -> Dict:
        """Create error response"""
        return {
            "error": error,
            "documentation_issues": [],
            "code_quality_issues": [],
            "security_issues": [],
            "performance_issues": []
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
