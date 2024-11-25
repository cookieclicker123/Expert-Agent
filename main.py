from agents.meta_agent import MetaAgent
from agents.pdf_agent import PDFAgent
from agents.finance_agent import FinanceAgent
from agents.web_agent import WebAgent
import json
from utils.config import Config
from utils.callbacks import StreamingHandler

class ExpertSystem:
    def __init__(self):
        print("Loading Expert System...")
        # Initialize streaming handler
        self.streaming_handler = StreamingHandler()
        
        # Initialize meta agent with streaming
        self.meta_agent = MetaAgent(callbacks=[self.streaming_handler])
        
        # Initialize and register available agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize and register all available agents"""
        print("Initializing PDF agent...")
        pdf_agent = PDFAgent(callbacks=[self.streaming_handler])
        print("Initializing Finance agent...")
        finance_agent = FinanceAgent(callbacks=[self.streaming_handler])
        print("Initializing Web agent...")
        web_agent = WebAgent(callbacks=[self.streaming_handler])
        
        # Register all agents
        self.meta_agent.registry.register("pdf", pdf_agent)
        self.meta_agent.registry.register("finance", finance_agent)
        self.meta_agent.registry.register("web", web_agent)
        
    def process_query(self, query: str) -> str:
        """Process a query through the meta agent"""
        try:
            print("\nProcessing query...\n")
            # Get the response but don't print it - streaming handler will handle that
            response = self.meta_agent.process(query)
            print("\n")  # Add spacing after response
            return ""
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

def select_model():
    """Allow user to select model provider"""
    print("\nSelect Model Provider:")
    print("1. Local (Ollama LLaMA 3.2)")
    print("2. Groq (LLaMA 3.2 90B)")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == "1":
            Config.model_config.provider = "ollama"
            Config.model_config.model_name = "llama3.2"
            break
        elif choice == "2":
            Config.model_config.provider = "groq"
            Config.model_config.model_name = Config.model_config.groq_model_name
            if not Config.model_config.groq_api_key:
                print("Error: GROQ_API_KEY not found in environment variables")
                continue
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

def main():
    print("Initializing Expert System...")
    
    # Add model selection before system initialization
    select_model()
    
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
            if response:  # Only print if there's an error
                print("\nResponse:")
                print(response)
            
        except KeyboardInterrupt:
            print("\nShutting down Expert Agent System...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
