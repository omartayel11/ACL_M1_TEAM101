"""
Answer Generator for Graph-RAG Hotel Travel Assistant
LLM generates final answers from retrieved context
"""

from typing import Optional, List, Dict, Any
from utils.llm_client import LLMClient


class AnswerGenerator:
    """
    Generate final answers using LLM based on retrieved context.
    Ensures grounded responses with citations.
    Supports conversation history for context-aware responses.
    """
    
    def __init__(self):
        """Initialize answer generator"""
        try:
            self.llm_client = LLMClient()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM client for answer generation: {e}")
    
    def generate(
        self,
        query: str,
        context: str,
        intent: Optional[str] = None,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate answer from query and context
        
        Args:
            query: User's original query
            context: Retrieved context (hotels, reviews, etc.)
            intent: Optional intent classification for guidance
            chat_history: Optional conversation history for context
            
        Returns:
            Generated answer string
        """
        if not context or context.strip() == "No results found.":
            return "I couldn't find any relevant information to answer your question. Please try rephrasing or asking about something else."
        
        # Build intent-specific guidance
        intent_guidance = self._get_intent_guidance(intent)
        
        # Format conversation history if available
        history_context = ""
        if chat_history and len(chat_history) > 0:
            history_context = self._format_chat_history(chat_history)
        
        prompt = f"""You are a helpful hotel travel assistant. Answer the user's question using ONLY the provided context.

{intent_guidance}

CRITICAL RULES:
- Base your answer ONLY on the provided context
- Do NOT make up information or hallucinate
- If the context doesn't contain the answer, say "I don't have enough information to answer that"
- Cite specific hotels, scores, or reviews from the context
- Be concise but complete
- Use natural language, not technical jargon
- Consider the conversation history when formulating your answer

{history_context}

Context:
{context}

User Question: "{query}"

Answer:"""

        try:
            response = self.llm_client.generate(prompt, temperature=0.3, max_tokens=400)
            
            return response.strip()
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I'm sorry, I encountered an error while generating the answer. Please try again."
    
    def _format_chat_history(self, chat_history: List[Dict[str, Any]]) -> str:
        """
        Format chat history for prompt context
        
        Args:
            chat_history: List of conversation turns
            
        Returns:
            Formatted history string
        """
        if not chat_history:
            return ""
        
        # Take last 3 turns for context
        recent_history = chat_history[-6:]  # 3 turns = 6 messages (user + assistant)
        
        lines = ["Previous conversation:"]
        for msg in recent_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            # Truncate long messages
            if len(content) > 150:
                content = content[:150] + "..."
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def _get_intent_guidance(self, intent: Optional[str]) -> str:
        """Get intent-specific guidance for answer generation"""
        guidance_map = {
            "HotelSearch": "Provide a list of hotels with their key details (location, rating, scores).",
            "HotelRecommendation": "Recommend hotels based on the criteria, explaining why they're good choices.",
            "ReviewLookup": "Summarize the reviews, highlighting common themes and specific feedback.",
            "LocationQuery": "Focus on location-related information and scores.",
            "VisaQuestion": "Provide clear visa requirement information.",
            "AmenityFilter": "Highlight hotels that meet the quality criteria with specific scores.",
            "GeneralQuestionAnswering": "Provide comprehensive information about the hotel or topic."
        }
        
        return guidance_map.get(intent, "Answer the question clearly and directly.")


if __name__ == "__main__":
    # Test answer generator
    generator = AnswerGenerator()
    
    print("=== Answer Generator Test ===\n")
    
    # Mock context
    context = """=== HOTELS ===

1. Hotel Paris
   Location: Paris, France
   Star Rating: 4
   Average Score: 8.50
   Relevance: 1.00
   Scores: Cleanliness: 8.5, Comfort: 8.3, Location: 9.2, Staff: 8.7

2. London Inn
   Location: London, UK
   Star Rating: 3
   Average Score: 7.80
   Relevance: 0.90
   Scores: Cleanliness: 7.5, Comfort: 7.8, Location: 8.0, Staff: 8.2
"""
    
    test_queries = [
        ("Find hotels in Paris", "HotelSearch"),
        ("Which hotel has better location?", "LocationQuery"),
        ("What are the top hotels?", "HotelRecommendation")
    ]
    
    for query, intent in test_queries:
        print(f"Query: {query}")
        print(f"Intent: {intent}")
        answer = generator.generate(query, context, intent)
        print(f"Answer: {answer}\n")
