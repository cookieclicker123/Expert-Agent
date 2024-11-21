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
            # Use the LLM to decide which agents to use
            analysis_prompt = self.prompt.format(
                query=query,
                available_agents=self.registry.list_agents()
            )
            response = self.llm.invoke(analysis_prompt)
            
            # Smart fallback based on query content
            if any(term in query.lower() for term in ["stock", "price", "market", "ticker", "ratio"]):
                return ["finance"]
            return ["pdf"]
            
        except Exception as e:
            # Simple fallback
            if any(term in query.lower() for term in ["stock", "price", "market", "ticker", "ratio"]):
                return ["finance"]
            return ["pdf"]
        
    def _synthesize_responses(self, query: str, responses: List[dict]) -> str:
        """Combine responses from multiple agents into coherent answer"""
        if not responses:
            return json.dumps({"error": "No agent responses to synthesize"})
            
        synthesis_prompt = self.synthesis_prompt.format(
            query=query,
            agent_responses=json.dumps(responses, indent=2)
        )

        return self.llm.invoke(synthesis_prompt) 