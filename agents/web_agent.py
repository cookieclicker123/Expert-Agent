from agents.base_agent import BaseAgent
from tools.web_tools import SerperTool
from utils.prompts import WEB_AGENT_PROMPT

class WebAgent(BaseAgent):
    def __init__(self, callbacks=None):
        super().__init__("web", callbacks)
        self.search_tool = SerperTool()
        self.prompt = WEB_AGENT_PROMPT
        
    def process(self, query: str) -> str:
        """Process web-based queries with search and analysis"""
        try:
            # Get search results
            search_results = self.search_tool.search(query)
            
            # Format prompt with results
            prompt = self.prompt.format(
                search_results=search_results,
                query=query
            )
            
            # Use streaming invoke
            return self._invoke_llm(prompt)
            
        except Exception as e:
            return f"Error in web agent: {str(e)}" 