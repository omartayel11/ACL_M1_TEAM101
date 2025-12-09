"""
Casual Conversation Node - Handle greetings and casual chat
Responds to non-retrieval queries like "hi", "what can you do", "thank you"
"""

from state.graph_state import GraphState


def casual_conversation_node(state: GraphState) -> GraphState:
    """
    Handle casual conversation without retrieval
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with casual response
    """
    query = state.get("user_query", "").lower()
    
    # Determine response type
    response = ""
    
    # Greetings
    if any(word in query for word in ["hi", "hello", "hey", "greetings"]):
        response = """👋 Hello! I'm your Hotel Travel Assistant. I can help you with:

🏨 **Hotel Search** - Find hotels by city, country, or rating
⭐ **Recommendations** - Get top hotels by traveler type or quality metrics  
📝 **Reviews** - Look up guest reviews for specific hotels
📍 **Location** - Find hotels with the best location scores
✈️ **Visa Info** - Check visa requirements between countries
🎯 **Filters** - Filter hotels by cleanliness, comfort, value, or staff scores

What would you like to explore?"""
    
    # Asking about capabilities
    elif any(phrase in query for phrase in ["what can you", "what do you do", "your purpose", "help me", "how can you"]):
        response = """I'm a hotel travel assistant specialized in helping you find and explore hotels worldwide! 

**Here's what I can do:**

🔍 **Search Hotels** - By city, country, star rating, or minimum rating threshold
💡 **Recommend Hotels** - Best options for Business, Couples, Families, Solo travelers, or Groups
📊 **Show Reviews** - Guest feedback and ratings for any hotel
🗺️ **Location Insights** - Hotels with best location scores in any city
🛂 **Visa Information** - Requirements between countries
⚡ **Quality Filters** - Find hotels by cleanliness, comfort, value, or staff quality

I use a knowledge graph with real hotel data to give you accurate, relevant results. Just ask me anything!"""
    
    # Thank you
    elif any(phrase in query for phrase in ["thank", "thanks", "appreciate"]):
        response = "You're welcome! 😊 Feel free to ask if you need anything else about hotels or travel!"
    
    # Goodbye
    elif any(word in query for word in ["bye", "goodbye", "see you", "exit"]):
        response = "Goodbye! Safe travels! 🌍✈️ Come back anytime you need hotel recommendations!"
    
    # How are you
    elif any(phrase in query for phrase in ["how are you", "how's it going"]):
        response = "I'm doing great, thanks for asking! Ready to help you find the perfect hotel. What are you looking for?"
    
    # Generic fallback
    else:
        response = """I'm here to help you with hotel search and travel planning! You can ask me things like:
- "Find hotels in Paris"
- "What are the best hotels for couples?"
- "Show me reviews for Hotel Ritz"
- "Hotels with best location scores in Tokyo"

What would you like to know?"""
    
    # Return response without retrieval
    return {
        "llm_response": response,
        "metadata": {
            **state.get("metadata", {}),
            "casual_conversation": True,
            "no_retrieval": True
        }
    }


if __name__ == "__main__":
    # Test casual conversation node
    test_queries = [
        "hi",
        "what can you do?",
        "thank you",
        "bye"
    ]
    
    for query in test_queries:
        test_state: GraphState = {
            "user_query": query,
            "intent": "CasualConversation"
        }
        
        result = casual_conversation_node(test_state)
        print(f"\nQuery: {query}")
        print(f"Response: {result.get('llm_response')[:100]}...")
