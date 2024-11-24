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
        """Process query through appropriate agents"""
        try:
            print("\nAnalyzing workflow...")
            
            # Get required agents
            required_agents = self._analyze_query(query)
            
            print("Selected agents:")
            for agent in required_agents:
                print(f"- {agent}: {self.registry.get_agent_purpose(agent)}")
            
            print("\nGathering information...")
            
            # Clear workpad for new query
            self.workpad.clear()
            
            # Process agents and save to workpad
            for agent_name in required_agents:
                agent = self.registry.get_agent(agent_name)
                if agent:
                    print(f"\nProcessing {agent_name} agent...")
                    response = agent.process(query)
                    print(f"Got response from {agent_name}: {response[:100]}...")
                    # Save to workpad using write method
                    self.workpad.write(agent_name, response)
            
            print("\nSynthesizing response...")
            
            # Debug: Print workpad content
            content = self.workpad.get_all_content()
            print(f"\nWorkpad content: {content}")
            
            final_response = self._synthesize_from_workpad(query)
            print(f"\nFinal response: {final_response}")
            
            return final_response
            
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

    def _analyze_query(self, query: str) -> List[str]:
        """Extract required agents from workflow analysis"""
        try:
            # Get workflow steps
            workflow = self._analyze_workflow(query)
            
            # Extract unique agent names from workflow
            required_agents = []
            for step in workflow:
                agent = step.get("agent")
                if agent and agent not in required_agents:
                    required_agents.append(agent)
            
            # Print workflow analysis
            print("Workflow analysis...")
            for step in workflow:
                print(f"- {step['agent']}: {step['reason']}")
            
            return required_agents
            
        except Exception as e:
            print(f"Analysis failed: {str(e)}")
            return ["web"]  # Fallback to web agent