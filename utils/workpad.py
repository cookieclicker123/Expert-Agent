from typing import Dict, Optional
import json

class Workpad:
    def __init__(self):
        self.content: Dict[str, str] = {}
        self.metadata: Dict[str, dict] = {}
        
    def write(self, agent: str, content: str, metadata: Optional[dict] = None):
        """Write agent output to workpad"""
        self.content[agent] = content
        if metadata:
            self.metadata[agent] = metadata
            
    def get_content(self, agent: str) -> Optional[str]:
        """Get specific agent's content"""
        return self.content.get(agent)
        
    def get_all_content(self) -> Dict[str, str]:
        """Get all content"""
        return self.content
        
    def clear(self):
        """Clear workpad"""
        self.content.clear()
        self.metadata.clear() 