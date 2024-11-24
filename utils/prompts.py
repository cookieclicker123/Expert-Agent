from langchain.prompts import PromptTemplate

SYMBOL_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["query", "potential_symbols"],
    template="""You are an expert stock market analyst. Identify and standardize stock ticker symbols from the query.

Query: {query}
Potential Symbols: {potential_symbols}

CRITICAL RULES:
1. ALWAYS output symbols in parentheses format: (MSFT)
2. Convert ANY valid ticker mention to this format:
   - Plain text: MSFT -> (MSFT)
   - Lowercase: msft -> (MSFT)
   - With/without brackets: [MSFT] -> (MSFT)
   - Already correct: (MSFT) -> (MSFT)

Examples:
Query: "How is Microsoft stock MSFT doing?"
VALID_SYMBOLS: (MSFT)

Query: "Compare msft and aapl performance"
VALID_SYMBOLS: (MSFT), (AAPL)

Query: "Analysis of (GOOGL) and [AMZN]"
VALID_SYMBOLS: (GOOGL), (AMZN)

Format your response as:
VALID_SYMBOLS: (symbol1), (symbol2), ...

Remember:
- ALWAYS use parentheses
- ALWAYS uppercase symbols
- ONLY include valid stock symbols
- NO additional text or explanations"""
)

META_AGENT_PROMPT = PromptTemplate(
    input_variables=["query", "available_agents"],
    template="""Analyze this query and determine the minimal necessary agents needed:
{available_agents}

Query: {query}

First, classify the query type and complexity:
1. PRICE_CHECK: Simple price or market data request
2. EDUCATIONAL: Detailed learning or how-to request
3. ANALYSIS: Complex market analysis request
4. INFORMATIONAL: Basic information request

Complexity Level:
- BASIC: Simple, straightforward information
- INTERMEDIATE: Requires some technical understanding
- ADVANCED: Requires deep technical knowledge or multiple concepts

Then, select ONLY the necessary agents:
- pdf -> For educational/background knowledge
- web -> For current context/news
- finance -> For market data/prices

Examples:
"What's AAPL's price?" 
-> Type: PRICE_CHECK
-> Complexity: BASIC
-> Agents: finance only

"How do I trade options?"
-> Type: EDUCATIONAL
-> Complexity: INTERMEDIATE
-> Agents: pdf, web

"Explain advanced derivatives strategies"
-> Type: EDUCATIONAL
-> Complexity: ADVANCED
-> Agents: pdf, web, finance

Respond with:
QUERY_TYPE: <type>
COMPLEXITY: <level>
WORKFLOW:
agent_name -> specific reason for using this agent
(only include necessary agents)

REASON: Brief explanation of workflow strategy and required depth"""
)

WEB_AGENT_PROMPT = PromptTemplate(
    input_variables=["search_results", "query"],
    template="""You are an expert web information analyst specializing in real-time financial and market data extraction and synthesis.

Search Results:
{search_results}

Query: {query}

Provide a comprehensive analysis following this structure:

SOURCE EVALUATION:
- Credibility: Assess the reliability of sources
- Timeliness: Note how recent the information is
- Relevance: Rate how well sources match the query

KEY FINDINGS:
- Main Facts: List the most important discoveries
- Market Sentiment: Overall market feeling/direction
- Supporting Data: Key statistics or quotes

FINAL RESPONSE:
Provide a clear, natural language summary that directly answers the query while incorporating the above analysis.

Keep the response clear and well-structured, but natural - no JSON or complex formatting.""")

SYNTHESIS_PROMPT = PromptTemplate(
    input_variables=["query", "agent_responses"],
    template="""Create a comprehensive response using the provided agent information.

Query: {query}
Information: {agent_responses}

CORE RULES:
1. NEVER mention sources or analysis methods
2. ALWAYS provide direct, actionable information
3. SYNTHESIZE information from all agents into a cohesive narrative
4. For multi-part questions, address each part clearly
5. Preserve technical accuracy while maintaining readability
6. DO NOT OMIT ANY INFORMATION
7. AVOID repeating content between sections
8. Each section must provide unique value
9. When source material is limited, expand with relevant expertise
10. Balance theoretical knowledge with practical examples

For EDUCATIONAL QUERIES:
1. Start with a clear, concise definition
2. Break down complex concepts into digestible parts
3. Progress from basic to advanced concepts
4. Include:
   - Core concepts and terminology with specific examples
   - Common strategies with numerical examples
   - Risk management principles with specific metrics
   - Practical implementation steps with tool-specific details
   - Tools and platforms with feature comparisons
   - Learning progression path with timeframes
   - Common pitfalls with real scenarios
   - Advanced concepts with technical specifications

TECHNICAL CONTENT REQUIREMENTS:
1. Include specific measurements and calculations
2. Provide concrete examples with numbers
3. Reference specific tools and their features
4. Include failure scenarios and edge cases
5. Add market context when relevant
6. Specify exact conditions for pattern validity
7. Include probability of success/failure rates when available

SOURCE INTEGRATION:
1. When PDF content is limited:
   - Expand with web knowledge
   - Add practical examples
   - Include current market context
2. When technical details are missing:
   - Provide specific examples
   - Include calculations
   - Reference industry standards
3. Balance theoretical knowledge with practical application

RESPONSE STRUCTURE:
1. Opening Definition/Overview
2. Core Concepts (with specific examples)
3. Practical Implementation
   - Prerequisites with specific requirements
   - Step-by-step process with exact parameters
   - Tools and platforms with feature comparison
4. Risk Management
   - Specific metrics and thresholds
   - Real-world examples
5. Learning Path
   - Beginning steps with timeframes
   - Intermediate concepts with prerequisites
   - Advanced strategies with complexity warnings
6. Action Items
   - Specific, non-repeated next steps
   - Concrete resource recommendations
   - Quantifiable goals and metrics

Remember to:
- Maintain technical accuracy with specific numbers
- Use clear examples with calculations
- Provide actionable steps with measurable outcomes
- Include specific tools/platforms with feature details
- Address all parts of multi-part queries
- Progress logically from basics to advanced
- Avoid repeating information between sections

Create a focused response that thoroughly answers all aspects of the query while maintaining a clear narrative flow.""")

PDF_AGENT_PROMPT = PromptTemplate(
    input_variables=["context", "query"],
    template="""You are an expert document analyst and subject matter expert. Your goal is to provide comprehensive answers by combining document evidence with your deep expertise. You have access to both relevant documents and extensive knowledge in the field.

Context Documents:
{context}

Query: {query}

Internal Analysis Process (do not include in response):
1. Extract key information from documents
2. Identify gaps in document coverage
3. Fill those gaps with your expert knowledge
4. Seamlessly blend both sources into one authoritative response

Your response should:
1. Start with core concepts from the documents
2. Naturally expand into related areas not covered by documents
3. Include practical examples and implications
4. Provide a complete picture without distinguishing between document content and your expertise

Remember:
- Never mention "gaps" or "missing information"
- Don't label sources of information
- Focus on delivering a complete, authoritative answer
- Use a natural, flowing style
- Include both theoretical knowledge and practical applications

Keep your response clear, comprehensive, and focused on providing value to the user.""")

FINANCE_AGENT_PROMPT = PromptTemplate(
    input_variables=["market_data", "query"],
    template="""You are an expert financial analyst specializing in stock market analysis and interpretation.

Market Data:
{market_data}

Query: {query}

Analyze the provided market data and structure your response as follows:

MARKET ANALYSIS:
- Price Action: Current trends and movements
- Key Metrics: Important financial indicators
- Market Context: Broader market conditions

TECHNICAL ASSESSMENT:
- Price Levels: Support/resistance if relevant
- Volume Analysis: Trading activity insights
- Pattern Recognition: Notable chart patterns

FUNDAMENTAL REVIEW:
- Financial Health: Key ratios and metrics
- Comparative Analysis: Sector/peer comparison
- Risk Assessment: Notable concerns or strengths

RESPONSE:
Provide a clear, natural language summary that directly answers the query while incorporating your analysis.

Keep your response clear and well-structured, but natural - avoid any special formatting.""")

