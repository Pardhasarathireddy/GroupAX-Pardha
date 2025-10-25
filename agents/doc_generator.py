"""
Documentation Generation Agent
"""
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.prompts import GENERATE_DOCSTRING_PROMPT, GENERATE_README_PROMPT
import re

class DocGenerator:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3  # Slightly higher for creative documentation
        )
    
    def generate_missing_docstrings(self, files: List[Dict], repo_context: str = "") -> Dict[str, str]:
        """
        Generate docstrings for functions missing them
        Returns dict of {file_path: updated_content}
        """
        updated_files = {}
        
        for file_info in files:
            if not file_info['path'].endswith('.py'):
                continue
                
            content = file_info['content']
            functions = self._extract_functions_without_docstrings(content)
            
            if not functions:
                continue
            
            # Generate docstrings for each function
            new_content = content
            for func in functions[:5]:  # Limit to 5 functions per file
                docstring = self._generate_docstring(
                    file_path=file_info['path'],
                    function_code=func['code'],
                    repo_context=repo_context
                )
                
                if docstring:
                    new_content = self._insert_docstring(new_content, func, docstring)
            
            if new_content != content:
                updated_files[file_info['path']] = new_content
        
        return updated_files
    
    def generate_readme(self, current_readme: str, repo_structure: str, main_files: List[str]) -> str:
        """
        Generate improved README.md
        """
        prompt = GENERATE_README_PROMPT.format(
            current_readme=current_readme or "No existing README",
            repo_structure=repo_structure,
            main_files="\n".join(main_files[:10])
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"README generation error: {e}")
            return current_readme
    
    def _extract_functions_without_docstrings(self, code: str) -> List[Dict]:
        """
        Extract Python functions that lack docstrings
        """
        functions = []
        
        # Pattern to match function definitions
        func_pattern = r'(def\s+(\w+)\s*\([^)]*\):(?:\s*\n)(?!\s*"""|\s*\'\'\'))'
        
        matches = re.finditer(func_pattern, code)
        
        for match in matches:
            func_start = match.start()
            func_name = match.group(2)
            
            # Extract full function (simple heuristic)
            lines = code[func_start:].split('\n')
            func_lines = [lines[0]]
            
            for i, line in enumerate(lines[1:], 1):
                if line and not line[0].isspace() and i > 1:
                    break
                func_lines.append(line)
            
            functions.append({
                'name': func_name,
                'code': '\n'.join(func_lines),
                'start_pos': func_start
            })
        
        return functions
    
    def _generate_docstring(self, file_path: str, function_code: str, repo_context: str) -> str:
        """
        Generate a docstring for a specific function
        """
        prompt = GENERATE_DOCSTRING_PROMPT.format(
            file_path=file_path,
            function_code=function_code,
            repo_context=repo_context[:500]  # Limit context
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Docstring generation error: {e}")
            return None
    
    def _insert_docstring(self, content: str, func: Dict, docstring: str) -> str:
        """
        Insert docstring into function
        """
        lines = content.split('\n')
        
        # Find function definition line
        for i, line in enumerate(lines):
            if f"def {func['name']}" in line:
                # Insert docstring after function definition
                indent = len(line) - len(line.lstrip())
                docstring_lines = [' ' * (indent + 4) + docstring]
                lines.insert(i + 1, '\n'.join(docstring_lines))
                break
        
        return '\n'.join(lines)
