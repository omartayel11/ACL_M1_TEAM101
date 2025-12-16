"""
Streamlit UI for Graph-RAG Hotel Travel Assistant
Modern, professional interface with modular architecture
"""

import streamlit as st
from core import initialize_session_state, process_query
from ui import (
    apply_custom_styles,
    render_sidebar,
    render_toolbar,
    render_query_library,
    render_welcome_screen,
    render_message_with_actions,
    format_timestamp
)

# Page configuration
st.set_page_config(
    page_title="AI Travel Assistant | Powered by Graph-RAG",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI-powered travel assistant with Graph-RAG technology"
    }
)

# Apply custom CSS styles
apply_custom_styles()


def render_chat_interface():
    """Render main chat interface - messages and input only"""
    # Add invisible marker for CSS targeting
    st.markdown('<div class="chat-area-marker"></div>', unsafe_allow_html=True)
    
    # Show welcome screen if no messages
    if not st.session_state.messages:
        render_welcome_screen()
    else:
        # Display all chat messages with enhanced styling
        for idx, message in enumerate(st.session_state.messages):
            render_message_with_actions(message, idx)
    
    # Process pending query from Query Library
    if hasattr(st.session_state, 'pending_query') and st.session_state.pending_query:
        prompt = st.session_state.pending_query
        st.session_state.pending_query = None  # Clear pending query
        
        # Show typing indicator
        with st.spinner(""):
            # Process query
            response = process_query(prompt)
            st.session_state.last_response = response
        
        # Extract and add hotel data
        hotels = _extract_hotels(response)
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "timestamp": format_timestamp(),
            "metadata": {
                "intent": response.get("intent"),
                "result_count": response.get("result_count", 0),
                "workflow": response.get("workflow"),
                "entities": response.get("entities", {}),
                "hotels": hotels if hotels else None,
                "raw_data": {
                    "baseline_cypher": response.get("baseline_cypher"),
                    "baseline_params": response.get("baseline_params"),
                    "llm_generated_cypher": response.get("llm_generated_cypher"),
                    "baseline_results": response.get("baseline_results", []),
                    "embedding_results": response.get("embedding_results", []),
                    "llm_query_results": response.get("llm_query_results", []),
                    "merged_context": response.get("merged_context", "")
                }
            }
        })
        
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me about hotels, travel, or visa requirements..."):
        # Add timestamp to message
        timestamp = format_timestamp()
        
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Show typing indicator
        with st.spinner(""):
            # Process query
            response = process_query(prompt)
            st.session_state.last_response = response
        
        # Extract and add hotel data
        hotels = _extract_hotels(response)
        
        # Add assistant message to chat with timestamp
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "timestamp": format_timestamp(),
            "metadata": {
                "intent": response.get("intent"),
                "result_count": response.get("result_count", 0),
                "workflow": response.get("workflow"),
                "entities": response.get("entities", {}),
                "hotels": hotels if hotels else None,
                "raw_data": {
                    "baseline_cypher": response.get("baseline_cypher"),
                    "baseline_params": response.get("baseline_params"),
                    "llm_generated_cypher": response.get("llm_generated_cypher"),
                    "baseline_results": response.get("baseline_results", []),
                    "embedding_results": response.get("embedding_results", []),
                    "llm_query_results": response.get("llm_query_results", []),
                    "merged_context": response.get("merged_context", "")
                }
            }
        })
        
        st.rerun()


def _extract_hotels(response):
    """Extract hotel data from response and normalize field names"""
    from core import add_dev_log
    hotels = []
    
    # Debug: Log response structure
    add_dev_log('DEBUG', f"Response keys: {list(response.keys())}")
    add_dev_log('DEBUG', f"baseline_results: {len(response.get('baseline_results', []))} items")
    add_dev_log('DEBUG', f"embedding_results: {len(response.get('embedding_results', []))} items") 
    add_dev_log('DEBUG', f"llm_query_results: {len(response.get('llm_query_results', []))} items")
    
    def normalize_hotel(result, source):
        """Normalize hotel data to consistent field names"""
        if not isinstance(result, dict):
            return None
            
        # Check if this looks like a hotel result
        has_name = 'name' in result or 'hotel_name' in result
        if not has_name:
            add_dev_log('DEBUG', f"✗ {source} result missing hotel name field. Keys: {list(result.keys())}")
            return None
        
        # Normalize the hotel data
        normalized = {
            'name': result.get('hotel_name') or result.get('name', 'Unknown Hotel'),
            'rating': result.get('star_rating') or result.get('rating'),
            'city': result.get('city'),
            'country': result.get('country'),
            'location': result.get('location'),
            'description': result.get('description'),
            'amenities': result.get('amenities'),
            'price': result.get('price') or result.get('price_per_night'),
            'address': result.get('address'),
            'relevance_score': result.get('relevance_score') or result.get('score'),
            'hotel_id': result.get('hotel_id')
        }
        
        # Build location string if not present
        if not normalized['location']:
            location_parts = []
            if normalized['city']:
                location_parts.append(str(normalized['city']))
            if normalized['country']:
                location_parts.append(str(normalized['country']))
            if location_parts:
                normalized['location'] = ', '.join(location_parts)
        
        add_dev_log('DEBUG', f"✓ Normalized hotel from {source}: {normalized['name']}")
        return normalized
    
    # Get hotels from baseline results
    if response.get("baseline_results"):
        for result in response["baseline_results"]:
            normalized = normalize_hotel(result, "baseline")
            if normalized:
                hotels.append(normalized)
    
    # Get hotels from embedding results
    if response.get("embedding_results"):
        for result in response["embedding_results"]:
            normalized = normalize_hotel(result, "embedding")
            if normalized:
                # Avoid duplicates
                if not any(h.get("name") == normalized.get("name") for h in hotels):
                    hotels.append(normalized)
    
    # Get hotels from LLM query results
    if response.get("llm_query_results"):
        for result in response["llm_query_results"]:
            normalized = normalize_hotel(result, "llm_query")
            if normalized:
                # Avoid duplicates
                if not any(h.get("name") == normalized.get("name") for h in hotels):
                    hotels.append(normalized)
    
    add_dev_log('DEBUG', f"⚡ Total hotels extracted: {len(hotels)}")
    if hotels:
        add_dev_log('DEBUG', f"🏨 First hotel: {hotels[0]['name']} | Rating: {hotels[0].get('rating')} | Location: {hotels[0].get('location')}")
    
    return hotels


def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render toolbar with tabs
    tab_chat, tab_library = render_toolbar()
    
    # Tab 1: Chat Assistant
    with tab_chat:
        render_chat_interface()
    
    # Tab 2: Query Library
    with tab_library:
        render_query_library()


if __name__ == "__main__":
    main()