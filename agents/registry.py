from typing import Dict, Type
from agents.base_agent import BaseAgent

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._purposes: Dict[str, str] = {
            "pdf": "For educational and background knowledge",
            "finance": "For market data and financial analysis",
            "web": "For current context and news"
        }
        
    def register(self, name: str, agent: BaseAgent) -> None:
        """Register a new agent"""
        self._agents[name] = agent
        
    def get_agent(self, name: str) -> BaseAgent:
        """Get an agent by name"""
        return self._agents.get(name)
        
    def list_agents(self) -> list[str]:
        """List all registered agents"""
        return list(self._agents.keys())
        
    def get_agent_purpose(self, name: str) -> str:
        """Get the purpose description for an agent"""
        return self._purposes.get(name, "Purpose not specified")