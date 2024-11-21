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
            # Determine which agents to use based on query
            required_agents = self._analyze_query(query)
            
            # Collect responses from required agents
            responses = []
            for agent_name in required_agents:
                agent = self.registry.get_agent(agent_name)
                if agent:
                    response = agent.process(query)
                    responses.append({
                        "agent": agent_name,
                        "response": response
                    })
            
            # If only one agent responded, return its response directly
            if len(responses) == 1:
                return responses[0]["response"]
                
            # Otherwise, synthesize responses
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
            # For now, since we only have PDF agent, skip prompt creation
            return ["pdf"]  # Temporary direct routing to PDF agent
            
            # When we add more agents, we'll uncomment this:
            # analysis_prompt = self.prompt.format(
            #     query=query,
            #     available_agents=self.registry.list_agents()
            # )
            # response = self.llm.invoke(analysis_prompt)
            # return self._parse_agent_requirements(response)
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            return ["pdf"]  # Fallback to PDF agent
        
    def _parse_agent_requirements(self, response: str) -> List[str]:
        """Parse the LLM's response to get required agents"""
        try:
            # Parse JSON response
            parsed = json.loads(response)
            
            # Extract agent names in order
            agents = []
            if "required_agents" in parsed:
                sorted_agents = sorted(
                    parsed["required_agents"],
                    key=lambda x: x.get("execution_order", 0)
                )
                agents = [agent["agent_name"] for agent in sorted_agents]
            
            # Fallback to PDF agent if no valid agents specified
            if not agents and "pdf" in self.registry.list_agents():
                agents = ["pdf"]
                
            return agents
            
        except json.JSONDecodeError:
            # Fallback to PDF agent if JSON parsing fails
            if "pdf" in self.registry.list_agents():
                return ["pdf"]
            return []
        
    def _synthesize_responses(self, query: str, responses: List[dict]) -> str:
        """Combine responses from multiple agents into coherent answer"""
        if not responses:
            return json.dumps({"error": "No agent responses to synthesize"})
            
        synthesis_prompt = self.synthesis_prompt.format(
            query=query,
            agent_responses=json.dumps(responses, indent=2)
        )

        return self.llm.invoke(synthesis_prompt) 