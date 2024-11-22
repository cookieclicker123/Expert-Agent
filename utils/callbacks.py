from langchain.callbacks.base import BaseCallbackHandler
import sys

class StreamingHandler(BaseCallbackHandler):
    def __init__(self):
        self.text = ""
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Stream tokens to stdout as they're generated"""
        sys.stdout.write(token)
        sys.stdout.flush()
        self.text += token 