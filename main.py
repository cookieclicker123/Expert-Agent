from agents.meta_agent import MetaAgent
from agents.pdf_agent import PDFAgent
from agents.finance_agent import FinanceAgent
from agents.web_agent import WebAgent
import json

class ExpertSystem:
    def __init__(self):
        print("Loading Expert System...")
        # Initialize meta agent
        self.meta_agent = MetaAgent()
        
        # Initialize and register available agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize and register all available agents"""
        print("Initializing PDF agent...")
        pdf_agent = PDFAgent()
        print("Initializing Finance agent...")
        finance_agent = FinanceAgent()
        print("Initializing Web agent...")
        web_agent = WebAgent()
        
        # Register all agents
        self.meta_agent.registry.register("pdf", pdf_agent)
        self.meta_agent.registry.register("finance", finance_agent)
        self.meta_agent.registry.register("web", web_agent)
        
    def process_query(self, query: str) -> str:
        """Process a query through the meta agent"""
        try:
            response = self.meta_agent.process(query)
            return self._format_response(response)
        except Exception as e:
            return self._format_error(str(e))
            
    def _format_response(self, response: str) -> str:
        """Format the final response"""
        try:
            # Ensure response is valid JSON
            json_response = json.loads(response)
            return json.dumps(json_response, indent=2)
        except json.JSONDecodeError:
            return response  # Return as is if not JSON
            
    def _format_error(self, error_msg: str) -> str:
        """Format error messages"""
        return json.dumps({
            "error": {
                "message": error_msg,
                "type": "system_error"
            }
        }, indent=2)

def main():
    print("Initializing Expert System...")
    system = ExpertSystem()
    
    print("System Ready!")
    print("Available Agents:", system.meta_agent.registry.list_agents())
    print("\nEnter your questions (type 'exit' to quit)")
    
    # Main interaction loop
    while True:
        try:
            query = input("\nQuery: ")
            if query.lower() == 'exit':
                print("Shutting down Expert Agent System...")
                break
                
            response = system.process_query(query)
            print("\nResponse:")
            print(response)
            
        except KeyboardInterrupt:
            print("\nShutting down Expert Agent System...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
