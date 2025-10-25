"""
Optimized prompts for Gemini Flash 2.5
"""

ANALYZE_CODE_PROMPT = """
You are an expert code reviewer analyzing a GitHub repository.

Analyze the following files and identify issues:

{files_content}

Provide a structured analysis in JSON format:
{{
  "documentation_issues": [
    {{
      "file": "filename",
      "issue": "description",
      "severity": "high/medium/low"
    }}
  ],
  "code_quality_issues": [...],
  "security_issues": [...],
  "performance_issues": [...]
}}

Focus on:
1. Missing or incomplete documentation
2. Functions without docstrings
3. Complex code without comments
4. Security vulnerabilities (hardcoded secrets, SQL injection risks)
5. Performance bottlenecks

Be specific and actionable.
"""

GENERATE_DOCSTRING_PROMPT = """
You are a documentation expert. Generate a comprehensive docstring for this function:

File: {file_path}
Function code:
{function_code}

Context from repository: {repo_context}

Generate a Python docstring following Google style guide:
- Brief description (one line)
- Detailed explanation
- Args: parameter descriptions with types
- Returns: return value description with type
- Raises: exceptions that may be raised
- Example usage

Return ONLY the docstring (including triple quotes).
"""

GENERATE_README_PROMPT = """
Generate an improved README.md for this repository.

Current README:
{current_readme}

Repository structure:
{repo_structure}

Main files analyzed:
{main_files}

Create a comprehensive README with:
1. Project title and badges
2. Description
3. Features
4. Installation instructions
5. Usage examples
6. API documentation (if applicable)
7. Contributing guidelines
8. License

Make it professional and user-friendly.
Return ONLY the markdown content.
"""

FIX_CODE_ISSUE_PROMPT = """
Fix this code issue:

File: {file_path}
Issue: {issue_description}
Current code:
{current_code}

Provide:
1. Fixed code
2. Explanation of changes

Return in JSON format:
{{
  "fixed_code": "...",
  "explanation": "..."
}}
"""
