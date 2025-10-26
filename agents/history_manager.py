"""
History Manager - Fixed ID System
"""
import json
import os
from datetime import datetime
from typing import List, Dict
import uuid

class HistoryManager:
    def __init__(self, history_file='analysis_history.json'):
        self.history_file = history_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def add_analysis(self, repo_url: str, summary: Dict):
        """Add new analysis to history with unique ID"""
        history = self.get_history()
        
        # Generate unique ID using timestamp + uuid
        unique_id = f"{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
        
        entry = {
            'id': unique_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'repo_url': repo_url,
            'repo_name': repo_url.split('/')[-1] if '/' in repo_url else repo_url,
            'health_score': summary.get('overall_health_score', 0),
            'total_issues': summary.get('total_issues_found', 0),
            'critical_issues': summary.get('critical_security_issues', 0)
        }
        
        history.insert(0, entry)  # Add to beginning
        history = history[:20]  # Keep only last 20
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return unique_id
    
    def get_history(self) -> List[Dict]:
        """Get all history entries"""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading history: {e}")
            return []
    
    def delete_entry(self, entry_id):
        """Delete specific entry"""
        history = self.get_history()
        history = [h for h in history if h.get('id') != entry_id]
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def clear_history(self):
        """Clear all history"""
        with open(self.history_file, 'w') as f:
            json.dump([], f)
