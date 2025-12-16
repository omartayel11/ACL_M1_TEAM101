"""
Query Library component - predefined sample queries
"""

import streamlit as st


def render_query_library():
    """Render a library of predefined queries organized by category"""
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
        <h2 style="font-size: clamp(1.5rem, 3vw, 2rem); margin-bottom: 0.5rem; font-weight: 700;">
            📚 Query Library
        </h2>
        <p style="color: var(--text-secondary); font-size: 1rem; max-width: 700px; margin: 0 auto;">
            Explore pre-built queries to discover what the AI Assistant can do
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Query categories
    categories = {
        "🏨 Hotel Search": [
            "Find hotels in Paris",
            "Show me luxury hotels in Tokyo",
            "Best budget hotels in London",
            "Hotels near the Eiffel Tower",
            "Family-friendly hotels in Rome",
            "5-star hotels with swimming pools"
        ],
        "🌟 Recommendations": [
            "Best family hotels",
            "Top rated hotels for business travelers",
            "Romantic hotels for couples",
            "Pet-friendly hotels",
            "Hotels with the best reviews",
            "Most popular hotels in Europe"
        ],
        "✈️ Visa Information": [
            "USA to France visa requirements",
            "Do I need a visa for Japan?",
            "Schengen visa requirements",
            "UK tourist visa information",
            "Visa-free countries for US citizens",
            "How to apply for a travel visa?"
        ],
        "🔍 Advanced Queries": [
            "Hotels with gym and spa in New York",
            "Cheap hotels near airports",
            "What are the visa requirements for China?",
            "Best hotels with city views",
            "Hotels that allow late checkout",
            "Compare hotels in Barcelona"
        ]
    }
    
    # Render categories
    for category, queries in categories.items():
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.15rem; font-weight: 600; margin-bottom: 1rem; 
                       color: var(--text-primary); display: flex; align-items: center;">
                {category}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create responsive grid of query buttons (3 cols desktop, 2 cols tablet, 1 col mobile)
        # Desktop: 3 columns
        cols = st.columns(3, gap="medium")
        for idx, query in enumerate(queries):
            col_idx = idx % 3
            with cols[col_idx]:
                if st.button(
                    query,
                    key=f"query_{category}_{idx}",
                    use_container_width=True,
                    type="secondary"
                ):
                    # Add query to chat
                    timestamp = _format_timestamp()
                    st.session_state.messages.append({
                        "role": "user",
                        "content": query,
                        "timestamp": timestamp
                    })
                    st.session_state.pending_query = query
                    st.session_state.switch_to_chat = True  # Signal to switch tabs
                    st.rerun()
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Info section
    st.markdown("""
    <div style="background: rgba(79, 70, 229, 0.08); 
                padding: 1.5rem; border-radius: 12px; 
                border: 1px solid rgba(79, 70, 229, 0.2);
                margin-top: 2rem;">
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0; line-height: 1.6;">
            💡 <strong>Tip:</strong> Click any query to automatically switch to the Chat Assistant and see the AI's response!
        </p>
    </div>
    """, unsafe_allow_html=True)


def _format_timestamp():
    """Generate formatted timestamp"""
    from datetime import datetime
    return datetime.now().strftime("%I:%M %p")
