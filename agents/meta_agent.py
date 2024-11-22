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
            
            self._stream_output("\nUsing agents: " + ", ".join(required_agents) + "\n\n")
            
            responses = []
            accumulated_text = ""
            
            for agent_name in required_agents:
                agent = self.registry.get_agent(agent_name)
                if agent:
                    if len(required_agents) > 1:
                        header = f"[{agent_name.upper()} AGENT]\n"
                        self._stream_output(header)
                        accumulated_text += header
                    
                    response = agent.process(query)
                    responses.append({"agent": agent_name, "response": response})
                    
                    if len(required_agents) > 1:
                        self._stream_output("\n")
                        accumulated_text += "\n"
                    
                    accumulated_text += response + "\n"
            
            if len(responses) == 1:
                return responses[0]["response"]
                
            # Now synthesize with the accumulated text
            synthesis = self._synthesize_responses(query, responses)
            self._stream_output("\n[SYNTHESIS]\n" + synthesis)
            return synthesis
                
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
            
            # Multi-agent scenarios
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
            
            # Use LLM for complex queries
            analysis_prompt = self.prompt.format(
                query=query,
                available_agents=self.registry.list_agents()
            )
            response = self.llm.invoke(analysis_prompt)
            
            # Extract agents from response
            if "REQUIRED_AGENTS:" in response:
                agents_section = response.split("REQUIRED_AGENTS:")[1].split("REASON:")[0].strip()
                agents = [a.strip() for a in agents_section.split("\n") if a.strip()]
                valid_agents = [a for a in agents if a in self.registry.list_agents()]
                if valid_agents:
                    return valid_agents
            
            # Default to PDF for general knowledge queries
            return ["pdf"]
                
        except Exception as e:
            print(f"Error in analyze_query: {str(e)}")
            # Smart fallback - prefer PDF for educational content
            if any(term in query_lower for term in knowledge_terms):
                return ["pdf"]
            return ["web"]
        
    def _synthesize_responses(self, query: str, responses: List[dict]) -> str:
        """Combine responses from multiple agents into coherent answer"""
        try:
            # Validate responses
            valid_responses = []
            agent_names = []
            
            for response in responses:
                if not response["response"] or "error" in response["response"].lower():
                    continue
                    
                valid_responses.append(response)
                agent_names.append(response["agent"])
                
            if not valid_responses:
                return json.dumps({"error": "No valid responses to synthesize"})
                
            if len(valid_responses) == 1:
                return valid_responses[0]["response"]
                
            # Format responses for better LLM processing
            formatted_responses = []
            for r in valid_responses:
                formatted_responses.append(f"""
    [{r['agent'].upper()} AGENT RESPONSE]
    {r['response']}
    """)
                
            synthesis_prompt = self.synthesis_prompt.format(
                query=query,
                agent_responses="\n".join(formatted_responses),
                agent_names=", ".join(agent_names)
            )

            # Use streaming for synthesis
            return self._invoke_llm(synthesis_prompt)
                
        except Exception as e:
            return json.dumps({
                "error": {
                    "message": f"Synthesis failed: {str(e)}",
                    "agent": "meta"
                }
            }, indent=2)