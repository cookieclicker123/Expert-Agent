from typing import List
import json
from agents.base_agent import BaseAgent
from agents.registry import AgentRegistry
from utils.prompts import META_AGENT_PROMPT, SYNTHESIS_PROMPT
from utils.workpad import Workpad

class MetaAgent(BaseAgent):
    def __init__(self):
        super().__init__("meta")
        self.registry = AgentRegistry()
        self.prompt = META_AGENT_PROMPT
        self.synthesis_prompt = SYNTHESIS_PROMPT
        self.workpad = Workpad()
        
    def process(self, query: str) -> str:
        try:
            print("\nProcessing query...")
            
            # Get workflow analysis
            workflow = self._analyze_workflow(query)
            
            # Execute agents
            self.workpad.clear()
            for step in workflow:
                agent = self.registry.get_agent(step["agent"])
                if agent:
                    result = agent.process(query)
                    if result and "error" not in str(result).lower():
                        self.workpad.write(
                            agent=step["agent"],
                            content=result
                        )
            
            # Get synthesis
            return self._synthesize_from_workpad(query)
            
        except Exception as e:
            return json.dumps({
                "error": {
                    "message": str(e),
                    "agent": "meta"
                }
            }, indent=2)

    def _synthesize_from_workpad(self, query: str) -> str:
        """Synthesize final response from workpad content"""
        try:
            content = self.workpad.get_all_content()
            if not content:
                return "No valid information gathered from agents."
                
            # Format content for synthesis
            formatted_content = []
            for agent, response in content.items():
                formatted_content.append(f"""
Information from {agent}:
{response}
""")
            
            # Create synthesis prompt
            synthesis_prompt = self.synthesis_prompt.format(
                query=query,
                agent_responses="\n".join(formatted_content)
            )
            
            # Get synthesis
            return self._invoke_llm(synthesis_prompt)
            
        except Exception as e:
            return f"Synthesis failed: {str(e)}"
        
    def _analyze_workflow(self, query: str) -> List[dict]:
        """Build dynamic workflow based on query analysis"""
        try:
            analysis_prompt = self.prompt.format(
                query=query,
                available_agents=self.registry.list_agents()
            )
            
            # Get LLM's workflow analysis
            response = self._invoke_llm(analysis_prompt)
            
            # Parse workflow steps - More robust parsing
            workflow = []
            if "WORKFLOW:" in response:
                workflow_text = response.split("WORKFLOW:")[1]
                # Handle both formats (with or without REASON:)
                if "REASON:" in workflow_text:
                    workflow_text = workflow_text.split("REASON:")[0]
                
                # Split into lines and process each
                lines = [line.strip() for line in workflow_text.split('\n') if line.strip()]
                for line in lines:
                    if "->" in line:
                        parts = line.split("->")
                        agent = parts[0].strip()
                        reason = parts[1].split("-")[0].strip()  # Remove any trailing comments
                        if agent in self.registry.list_agents():
                            workflow.append({
                                "agent": agent,
                                "reason": reason
                            })
            
            return workflow or [{"agent": "web", "reason": "fallback"}]
            
        except Exception as e:
            print(f"Workflow analysis failed: {str(e)}")
            return [{"agent": "web", "reason": "error fallback"}]