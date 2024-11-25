from typing import List
import json
from agents.base_agent import BaseAgent
from agents.registry import AgentRegistry
from utils.prompts import META_AGENT_PROMPT, SYNTHESIS_PROMPT
from utils.workpad import Workpad
from utils.config import Config

class MetaAgent(BaseAgent):
    def __init__(self, callbacks=None):
        super().__init__("meta", callbacks)
        self.registry = AgentRegistry()
        self.prompt = META_AGENT_PROMPT
        self.synthesis_prompt = SYNTHESIS_PROMPT
        self.workpad = Workpad()
        
    def process(self, query: str) -> str:
        """Process query through appropriate agents"""
        try:
            print("\nAnalyzing workflow...")
            required_agents = self._analyze_query(query)
            
            print("\nGathering information...")
            self.workpad.clear()
            
            # Process each agent
            for agent_name in required_agents:
                agent = self.registry.get_agent(agent_name)
                if agent:
                    print(f"\nProcessing {agent_name} agent...")
                    response = agent.process(query)
                    print(f"Got response from {agent_name}: {response[:100]}...")
                    self.workpad.write(agent_name, response)
            
            # Synthesize once
            print("\nSynthesizing response...")
            content = self.workpad.get_all_content()
            
            # Add separator
            print("\n" + "-" * 100)
            
            # Generate final response - stream only, don't return
            synthesis_prompt = self.synthesis_prompt.format(
                query=query,
                agent_responses=json.dumps(content, indent=2)
            )
            
            self._invoke_llm(synthesis_prompt)
            return ""  # Return empty string since we're streaming
            
        except Exception as e:
            print(f"Error in workflow: {str(e)}")
            return str(e)

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
            
            response = self._invoke_llm(analysis_prompt)
            workflow = []
            
            if "WORKFLOW:" in response:
                workflow_text = response.split("WORKFLOW:")[1]
                if "REASON:" in workflow_text:
                    workflow_text = workflow_text.split("REASON:")[0]
                
                lines = [line.strip() for line in workflow_text.split('\n') if line.strip()]
                for line in lines:
                    if "->" in line:
                        parts = line.split("->")
                        agent = parts[0].strip().lstrip('-')
                        reason = parts[1].split("-")[0].strip()
                        if agent in self.registry.list_agents():
                            workflow.append({
                                "agent": agent,
                                "reason": reason
                            })
            
            return workflow or [{"agent": "web", "reason": "fallback"}]
                
        except Exception as e:
            print(f"Workflow analysis failed: {str(e)}")
            return [{"agent": "web", "reason": "error fallback"}]

    def _analyze_query(self, query: str) -> List[str]:
        """Extract required agents from workflow analysis"""
        try:
            workflow = self._analyze_workflow(query)
            required_agents = []
            
            # Extract agents from workflow and validate them
            for step in workflow:
                agent = step.get("agent")
                if agent and agent in self.registry.list_agents():
                    if agent not in required_agents:
                        required_agents.append(agent)
            
            # If no valid agents found, use web as fallback
            if not required_agents:
                print("No valid agents found in workflow, falling back to web")
                return ["web"]
            
            print(f"Selected agents from workflow: {required_agents}")
            return required_agents
            
        except Exception as e:
            print(f"Workflow analysis failed: {str(e)}, falling back to web")
            return ["web"]


#please give me a comprehensive strategy to trade options and search the web for hot stocks to trade them on