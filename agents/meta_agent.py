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
            
            responses = []
            for agent_name in required_agents:
                agent = self.registry.get_agent(agent_name)
                if agent:
                    response = agent.process(query)
                    responses.append({"agent": agent_name, "response": response})
            
            if len(responses) == 1:
                return responses[0]["response"]
                
            return self._synthesize_responses(query, responses)
            
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
            
            # Web-specific terms
            web_terms = [
                "latest", "news", "recent", "current", "today", "update",
                "happening", "announced", "report", "shortage", "supply",
                "trend", "development", "analysis", "analyst", "sentiment"
            ]
            
            # Finance-specific terms
            finance_terms = [
                "stock", "price", "market cap", "ticker", "trading",
                "dividend", "earnings", "revenue", "profit", "eps",
                "pe ratio", "valuation"
            ]
            
            # Document-specific terms
            doc_terms = [
                "document", "pdf", "report", "filing", "historical",
                "past", "previous", "old", "archive", "documentation",
                "manual", "guide", "presentation"
            ]
            
            # Company and sector terms (these could trigger web or finance depending on context)
            company_terms = [
                "nvidia", "apple", "microsoft", "amd", "intel",
                "semiconductor", "chip", "tech", "technology",
                "ai", "artificial intelligence"
            ]
            
            # First, check for explicit agent indicators
            if any(term in query_lower for term in web_terms):
                if any(term in query_lower for term in finance_terms):
                    return ["web", "finance"]
                return ["web"]
                
            if any(term in query_lower for term in finance_terms):
                if any(term in query_lower for term in web_terms):
                    return ["finance", "web"]
                return ["finance"]
                
            if any(term in query_lower for term in doc_terms):
                return ["pdf"]
                
            # If query contains company/sector terms but no specific agent indicators,
            # default to web for real-time information
            if any(term in query_lower for term in company_terms):
                return ["web"]
                
            # Use LLM for complex queries
            analysis_prompt = self.prompt.format(
                query=query,
                available_agents=self.registry.list_agents()
            )
            response = self.llm.invoke(analysis_prompt)
            
            if "REQUIRED_AGENTS:" in response:
                agents_str = response.split("REQUIRED_AGENTS:")[1].split("\n")[0]
                agents = [a.strip() for a in agents_str.strip("[]").split(",")]
                return [a for a in agents if a in self.registry.list_agents()]
                
            # Default to web for general queries about current events/information
            return ["web"]
                
        except Exception as e:
            # Smart fallback - prefer web for general queries
            return ["web"]
        
    def _synthesize_responses(self, query: str, responses: List[dict]) -> str:
        """Combine responses from multiple agents into coherent answer"""
        if not responses:
            return json.dumps({"error": "No agent responses to synthesize"})
            
        synthesis_prompt = self.synthesis_prompt.format(
            query=query,
            agent_responses=json.dumps(responses, indent=2)
        )

        return self.llm.invoke(synthesis_prompt) 