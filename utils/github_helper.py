"""
GitHub API helper functions
"""
import os
from github import Github
from typing import List, Dict, Optional
import base64

class GitHubHelper:
    def __init__(self, token: str):
        self.g = Github(token)
        
    def get_repo(self, repo_url: str):
        """Extract and return GitHub repo object"""
        # Handle different URL formats
        repo_name = repo_url.replace("https://github.com/", "")
        repo_name = repo_name.replace(".git", "")
        return self.g.get_repo(repo_name)
    
    def get_repo_files(self, repo_url: str, max_files: int = 50) -> List[Dict]:
        """
        Fetch files from repository
        Returns list of {path, content, type}
        """
        repo = self.get_repo(repo_url)
        files = []
        
        try:
            contents = repo.get_contents("")
            
            while contents and len(files) < max_files:
                file_content = contents.pop(0)
                
                if file_content.type == "dir":
                    # Skip certain directories
                    if file_content.path not in ['.git', 'node_modules', 'venv', '__pycache__', '.next']:
                        contents.extend(repo.get_contents(file_content.path))
                else:
                    # Get file content
                    try:
                        # Only analyze certain file types
                        if self._should_analyze_file(file_content.path):
                            content = file_content.decoded_content.decode('utf-8')
                            files.append({
                                'path': file_content.path,
                                'content': content,
                                'type': file_content.type,
                                'size': file_content.size
                            })
                    except Exception as e:
                        # Skip binary files or decode errors
                        pass
                        
        except Exception as e:
            print(f"Error fetching files: {e}")
            
        return files
    
    def _should_analyze_file(self, filepath: str) -> bool:
        """Determine if file should be analyzed"""
        analyzable_extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.cpp', '.c', '.h', '.cs',
            '.rb', '.go', '.rs', '.php',
            '.md', '.txt', '.json', '.yaml', '.yml'
        ]
        return any(filepath.endswith(ext) for ext in analyzable_extensions)
    
    def create_pull_request(
        self,
        repo_url: str,
        branch_name: str,
        files_to_update: Dict[str, str],
        pr_title: str,
        pr_body: str
    ) -> Optional[str]:
        """
        Create a pull request with file changes
        Returns PR URL if successful
        """
        try:
            repo = self.get_repo(repo_url)
            
            # Get base branch
            base_branch = repo.default_branch
            base_sha = repo.get_branch(base_branch).commit.sha
            
            # Create new branch
            ref = f"refs/heads/{branch_name}"
            repo.create_git_ref(ref, base_sha)
            
            # Update/create files
            for file_path, new_content in files_to_update.items():
                try:
                    # Try to get existing file
                    contents = repo.get_contents(file_path, ref=branch_name)
                    
                    # Update existing file
                    repo.update_file(
                        path=contents.path,
                        message=f"AI Agent: Update {file_path}",
                        content=new_content,
                        sha=contents.sha,
                        branch=branch_name
                    )
                except:
                    # Create new file
                    repo.create_file(
                        path=file_path,
                        message=f"AI Agent: Create {file_path}",
                        content=new_content,
                        branch=branch_name
                    )
            
            # Create pull request
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=base_branch
            )
            
            # Add labels
            try:
                pr.add_to_labels("ai-generated", "documentation")
            except:
                pass  # Labels might not exist
            
            return pr.html_url
            
        except Exception as e:
            print(f"Error creating PR: {e}")
            return None
    
    def get_repo_structure(self, repo_url: str) -> str:
        """Get repository structure as string"""
        repo = self.get_repo(repo_url)
        structure = []
        
        try:
            contents = repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                structure.append(f"{'  ' * file_content.path.count('/')}{file_content.path}")
                
                if file_content.type == "dir" and file_content.path not in ['.git', 'node_modules', 'venv']:
                    contents.extend(repo.get_contents(file_content.path))
        except:
            pass
            
        return "\n".join(structure[:100])  # Limit to 100 items
