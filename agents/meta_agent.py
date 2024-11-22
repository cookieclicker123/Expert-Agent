from typing import List
import json
from agents.base_agent import BaseAgent
from agents.registry import AgentRegistry
from utils.prompts import META_AGENT_PROMPT, SYNTHESIS_PROMPT

class MetaAgent(BaseAgent):
    def __init__(self):
        super().__init__("meta")
        self.registry = AgentRegistry()
        self.prompt = META_AGENT_PROMPT
        self.synthesis_prompt = SYNTHESIS_PROMPT
        
    def process(self, query: str) -> str:
        """Process query and delegate to appropriate agents"""
        try:
            required_agents = self._analyze_query(query)
            required_agents = list(dict.fromkeys(required_agents))
            
            # Only show agents being used if more than one
            if len(required_agents) > 1:
                self._stream_output("\nUsing agents: " + ", ".join(required_agents) + "\n\n")
            
            responses = []
            for agent_name in required_agents:
                agent = self.registry.get_agent(agent_name)
                if agent:
                    response = agent.process(query)
                    if response and "error" not in response.lower():
                        responses.append({"agent": agent_name, "response": response})
            
            # For single agent, return direct response
            if len(responses) == 1:
                return responses[0]["response"]
            
            # For multiple agents, synthesize and return
            if len(responses) > 1:
                synthesis = self._synthesize_responses(query, responses)
                return synthesis
                
            return json.dumps({
                "error": {
                    "message": "No valid responses received from agents",
                    "agent": "meta"
                }
            }, indent=2)
                
        except Exception as e:
            return json.dumps({
                "error": {
                    "message": str(e),
                    "agent": "meta"
                }
            }, indent=2)
        
    def _analyze_query(self, query: str) -> List[str]:
        """Determine which agents are needed for this query"""
        try:
            query_lower = query.lower()
            
            # Educational/Knowledge terms (PDF priority)
            knowledge_terms = [
                "how to", "explain", "what is", "strategy", "guide",
                "tutorial", "understand", "learn", "concept", "theory",
                "principle", "method", "technique", "approach", "framework",
                "process", "steps", "advanced", "basic", "intermediate"
            ]
            
            # Current events terms (Web priority)
            current_terms = [
                "latest", "current", "now", "today", "recent",
                "breaking", "update", "news", "announced", "happening"
            ]
            
            # Market data terms (Finance priority)
            market_terms = [
                "price", "stock", "ticker", "trading", "market cap",
                "volume", "dividend", "earnings", "ratio"
            ]
            
            # First try keyword-based multi-agent scenarios
            if any(term in query_lower for term in knowledge_terms):
                if any(term in query_lower for term in current_terms):
                    return ["pdf", "web"]  # Knowledge base first, then current context
                return ["pdf"]  # Pure educational query
                
            if any(term in query_lower for term in market_terms):
                if any(term in query_lower for term in current_terms):
                    return ["finance", "web"]  # Market data first, then news
                return ["finance"]  # Pure market query
                
            if any(term in query_lower for term in current_terms):
                return ["web"]  # Pure current events query
            
            # Then try LLM analysis for complex queries
            try:
                analysis_prompt = self.prompt.format(
                    query=query,
                    available_agents=self.registry.list_agents()
                )
                response = self.llm.invoke(analysis_prompt)
                
                if "REQUIRED_AGENTS:" in response:
                    agents_section = response.split("REQUIRED_AGENTS:")[1].split("REASON:")[0].strip()
                    agents = [a.strip() for a in agents_section.split("\n") if a.strip()]
                    valid_agents = [a for a in agents if a in self.registry.list_agents()]
                    if valid_agents:
                        return valid_agents[:2]  # Limit to max 2 agents for better synthesis
            except:
                pass  # If LLM analysis fails, continue to fallback
            
            # Smart fallback based on query content
            if any(term in query_lower for term in knowledge_terms):
                return ["pdf"]
            if any(term in query_lower for term in market_terms):
                return ["finance"]
            return ["web"]
                
        except Exception as e:
            print(f"Error in analyze_query: {str(e)}")