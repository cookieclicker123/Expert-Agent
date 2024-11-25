from agents.base_agent import BaseAgent
from tools.finance_tools import VantageFinanceTool
from utils.prompts import FINANCE_AGENT_PROMPT, SYMBOL_EXTRACTION_PROMPT
import json
import re
from typing import List, Set

class FinanceAgent(BaseAgent):
    def __init__(self, callbacks=None):
        super().__init__("finance", callbacks)
        self.finance_tool = VantageFinanceTool()
        self.prompt = FINANCE_AGENT_PROMPT
        self.common_words = {
            'A', 'THE', 'FOR', 'AND', 'OR', 'OF', 'IN', 'IS', 'ARE', 'WHAT',
            'PRICE', 'CURRENT', 'NOW', 'TODAY', 'PE', 'EPS', 'CEO', 'CFO', 'USA'
        }
        
    def process(self, query: str) -> str:
        """Process financial queries with comprehensive analysis"""
        try:
            symbols = self._extract_symbols(query)
            market_data = {symbol: self.finance_tool.get_stock_data(symbol) for symbol in symbols}
            
            prompt = self.prompt.format(
                market_data=json.dumps(market_data, indent=2),
                query=query
            )
            
            # Use streaming invoke
            return self._invoke_llm(prompt)
            
        except Exception as e:
            return self._format_error_response(str(e))
            
    def _extract_symbols(self, query: str) -> List[str]:
        """Hybrid approach to extract stock symbols using regex and LLM"""
        symbols: Set[str] = set()
        
        # Step 1: Check for parentheses first (high confidence)
        parens_symbols = set(re.findall(r'\(([A-Z]{1,5})\)', query.upper()))
        if parens_symbols:
            symbols.update(s for s in parens_symbols if s not in self.common_words)
            
        # Step 2: If no parentheses found, try standalone capitals
        if not symbols:
            standalone_symbols = set(re.findall(r'\b[A-Z]{1,5}\b', query.upper()))
            potential_symbols = {s for s in standalone_symbols if s not in self.common_words}
            
            # Step 3: Use LLM for validation
            if potential_symbols:
                llm_prompt = SYMBOL_EXTRACTION_PROMPT.format(
                    query=query,
                    potential_symbols=list(potential_symbols)
                )
                try:
                    llm_response = self.llm.invoke(llm_prompt)
                    if "VALID_SYMBOLS:" in llm_response:
                        valid_symbols_str = llm_response.split("VALID_SYMBOLS:")[1].strip()
                        validated_symbols = [
                            re.search(r'\(([A-Z]+)\)', s.strip()).group(1)
                            for s in valid_symbols_str.split(",")
                            if re.search(r'\(([A-Z]+)\)', s.strip())
                        ]
                        symbols.update(validated_symbols)
                except Exception as e:
                    symbols.update(potential_symbols)
        
        valid_symbols = [s for s in symbols if self._is_valid_symbol_format(s)]
        
        if not valid_symbols:
            raise Exception(
                "No valid stock symbols found. Please include symbols like 'AAPL' or '(MSFT)'. "
                "Use parentheses for clearer symbol identification, e.g., (AAPL)."
            )
        
        return valid_symbols
        
    def _is_valid_symbol_format(self, symbol: str) -> bool:
        """Basic validation of symbol format"""
        return (
            isinstance(symbol, str) and
            1 <= len(symbol) <= 5 and
            symbol.isalpha() and
            symbol not in self.common_words
        )
        
    def _format_error_response(self, error_msg: str) -> str:
        """Format error messages consistently"""
        return json.dumps({
            "error": {
                "message": error_msg,
                "agent": self.name
            }
        }, indent=2) 