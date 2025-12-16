"""
UI Components for rendering various elements
"""

import streamlit as st
from typing import Dict, Any, List
from datetime import datetime


def format_timestamp():
    """Generate formatted timestamp for messages"""
    return datetime.now().strftime("%I:%M %p")


def render_welcome_screen():
    """Render welcome screen when no messages"""
    # Hero section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem 1.5rem 1rem; animation: fadeIn 0.8s ease-out;">
        <div style="font-size: 3.5rem; margin-bottom: 0.75rem; line-height: 1;">🤖</div>
        <h1 style="font-size: clamp(1.75rem, 4vw, 2.25rem); margin-bottom: 0.5rem; font-weight: 700; letter-spacing: -0.02em;">
            AI Assistant
        </h1>
        <p style="color: var(--text-secondary); font-size: clamp(0.9rem, 2vw, 1rem); max-width: 600px; 
                  margin: 0 auto 0.75rem auto; line-height: 1.6;">
            Intelligent search powered by Graph-RAG & semantic understanding
        </p>
        <div style="display: inline-flex; gap: 0.6rem; margin-top: 0.5rem; flex-wrap: wrap; justify-content: center;">
            <span style="background: rgba(79, 70, 229, 0.08); padding: 0.35rem 0.85rem; 
                       border-radius: 20px; font-size: 0.75rem; color: var(--primary);
                       border: 1px solid rgba(79, 70, 229, 0.2); font-weight: 600;">
                ⚡ Fast
            </span>
            <span style="background: rgba(16, 185, 129, 0.08); padding: 0.35rem 0.85rem; 
                       border-radius: 20px; font-size: 0.75rem; color: var(--secondary);
                       border: 1px solid rgba(16, 185, 129, 0.2); font-weight: 600;">
                🧠 Smart
            </span>
            <span style="background: rgba(251, 191, 36, 0.08); padding: 0.35rem 0.85rem; 
                       border-radius: 20px; font-size: 0.75rem; color: var(--accent);
                       border: 1px solid rgba(251, 191, 36, 0.2); font-weight: 600;">
                🎯 Accurate
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Feature cards with consistent sizing
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(79, 70, 229, 0.08) 0%, rgba(79, 70, 229, 0.03) 100%); 
                    padding: 2rem 1.5rem; border-radius: 12px; border: 1px solid rgba(79, 70, 229, 0.15);
                    text-align: center; min-height: 200px; display: flex; flex-direction: column; 
                    justify-content: center; transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 3rem; margin-bottom: 1rem; line-height: 1;">🔍</div>
            <h3 style="color: var(--primary); margin-bottom: 0.625rem; font-size: 1.15rem; font-weight: 600;">
                Smart Search
            </h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
                Advanced semantic search capabilities
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(16, 185, 129, 0.03) 100%); 
                    padding: 2rem 1.5rem; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.15);
                    text-align: center; min-height: 200px; display: flex; flex-direction: column; 
                    justify-content: center; transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 3rem; margin-bottom: 1rem; line-height: 1;">⚡</div>
            <h3 style="color: var(--secondary); margin-bottom: 0.625rem; font-size: 1.15rem; font-weight: 600;">
                Instant Results
            </h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
                Get answers in milliseconds
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(251, 191, 36, 0.08) 0%, rgba(251, 191, 36, 0.03) 100%); 
                    padding: 2rem 1.5rem; border-radius: 12px; border: 1px solid rgba(251, 191, 36, 0.15);
                    text-align: center; min-height: 200px; display: flex; flex-direction: column; 
                    justify-content: center; transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 3rem; margin-bottom: 1rem; line-height: 1;">🎯</div>
            <h3 style="color: var(--accent); margin-bottom: 0.625rem; font-size: 1.15rem; font-weight: 600;">
                Context Aware
            </h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
                Understands your intent
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Sample queries section with consistent sizing
    st.markdown("""
    <div style="max-width: 1800px; margin: 0 auto; padding: 1.75rem 1.5rem; 
                background: rgba(255, 255, 255, 0.02); 
                border-radius: 12px; border: 1px solid var(--border);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
        <p style="color: var(--text-secondary); text-align: center; 
                  font-size: 0.85rem; margin-bottom: 1.25rem; font-weight: 600; 
                  text-transform: uppercase; letter-spacing: 0.05em;">
            💡 Try Asking
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
            <div style="background: rgba(79, 70, 229, 0.08); padding: 1rem 2rem; 
                       border-radius: 12px; color: var(--text-primary); font-size: 0.95rem; 
                       border: 1px solid rgba(79, 70, 229, 0.2); text-align: center;
                       transition: all 0.2s ease; cursor: pointer; flex: 1; min-width: 220px; max-width: 450px;
                       font-weight: 500; min-height: 60px; display: flex; align-items: center; justify-content: center;">
                "Find hotels in Paris"
            </div>
            <div style="background: rgba(16, 185, 129, 0.08); padding: 1rem 2rem; 
                       border-radius: 12px; color: var(--text-primary); font-size: 0.95rem;
                       border: 1px solid rgba(16, 185, 129, 0.2); text-align: center;
                       transition: all 0.2s ease; cursor: pointer; flex: 1; min-width: 220px; max-width: 450px;
                       font-weight: 500; min-height: 60px; display: flex; align-items: center; justify-content: center;">
                "Best family hotels"
            </div>
            <div style="background: rgba(251, 191, 36, 0.08); padding: 1rem 2rem; 
                       border-radius: 12px; color: var(--text-primary); font-size: 0.95rem;
                       border: 1px solid rgba(251, 191, 36, 0.2); text-align: center;
                       transition: all 0.2s ease; cursor: pointer; flex: 1; min-width: 220px; max-width: 450px;
                       font-weight: 500; min-height: 60px; display: flex; align-items: center; justify-content: center;">
                "USA to France visa?"
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)


def render_typing_indicator():
    """Show typing indicator while processing"""
    st.markdown("""
    <div style="animation: fadeIn 0.3s ease-out; padding: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; 
                    background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
                    padding: 1rem 1.25rem; border-radius: 12px; border-left: 3px solid var(--primary);">
            <div style="display: flex; gap: 0.4rem;">
                <div style="width: 8px; height: 8px; background: var(--primary); border-radius: 50%; 
                            animation: pulse 1.4s ease-in-out infinite;"></div>
                <div style="width: 8px; height: 8px; background: var(--secondary); border-radius: 50%; 
                            animation: pulse 1.4s ease-in-out 0.2s infinite;"></div>
                <div style="width: 8px; height: 8px; background: var(--accent); border-radius: 50%; 
                            animation: pulse 1.4s ease-in-out 0.4s infinite;"></div>
            </div>
            <span style="color: var(--text-primary); font-weight: 600;">Processing...</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_single_hotel_card(hotel: Dict[str, Any]):
    """Render a single hotel card - separated for easy styling updates"""
    # Extract hotel data
    name = str(hotel.get('name', 'Unknown Hotel'))
    rating = hotel.get('rating')
    city = hotel.get('city')
    country = hotel.get('country')
    price = hotel.get('price') or hotel.get('price_per_night')
    relevance = hotel.get('relevance_score')
    
    # Build location string - don't use 'location' field directly as it might have wrong data
    location_parts = []
    if city and str(city).strip():
        location_parts.append(str(city))
    if country and str(country).strip():
        location_parts.append(str(country))
    
    # Use the built location, or try the location field as fallback, or default
    if location_parts:
        location = ', '.join(location_parts)
    else:
        location_field = hotel.get('location')
        # Only use location field if it's not a number (scores might be in this field)
        if location_field and not isinstance(location_field, (int, float)):
            try:
                float(location_field)  # Try to convert to float
                location = 'Location Unknown'  # If it converts, it's a number, don't use it
            except (ValueError, TypeError):
                location = str(location_field)  # It's not a number, use it
        else:
            location = 'Location Unknown'
    
    # Calculate relevance percentage
    relevance_val = 0
    relevance_text = ""
    if relevance:
        try:
            relevance_val = float(relevance)
            # Clamp to [0.0, 1.0] range for progress bar
            relevance_val = max(0.0, min(1.0, relevance_val))
            relevance_text = f"{int(relevance_val * 100)}% Match"
        except:
            pass
    
    # Render the card
    with st.container(border=True):
        # Hotel name
        st.markdown(f"### 🏨 {name}")
        
        # Location
        st.markdown(f"📍 **{location}**")
        
        # Rating
        if rating and rating != 'N/A':
            st.markdown(f"⭐ **{rating} / 5.0**")
        
        # Divider
        st.markdown("---")
        
        # Price (if available)
        if price:
            st.markdown(f"### 💰 ${price}")
            st.caption("per night")
        
        # Match score - full width at bottom
        if relevance_text:
            st.markdown(f"**🎯 {relevance_text}**")
            st.progress(relevance_val)


def render_hotel_cards(hotels: List[Dict[str, Any]], message_index: int = 0):
    """Render hotels as compact premium cards with carousel navigation"""
    if not hotels:
        return
    
    # Initialize carousel state - use message_index for unique state per message
    carousel_key = f'hotel_carousel_page_{message_index}'
    if carousel_key not in st.session_state:
        st.session_state[carousel_key] = 0
    
    # Carousel settings
    hotels_per_page = 3
    total_pages = (len(hotels) + hotels_per_page - 1) // hotels_per_page
    current_page = st.session_state[carousel_key]
    
    # Ensure current page is valid
    if current_page >= total_pages:
        current_page = 0
        st.session_state[carousel_key] = 0
    
    # Calculate start and end indices
    start_idx = current_page * hotels_per_page
    end_idx = min(start_idx + hotels_per_page, len(hotels))
    display_hotels = hotels[start_idx:end_idx]
    
    # Display hotels in columns
    cols = st.columns(len(display_hotels))
    
    for col, hotel in zip(cols, display_hotels):
        with col:
            _render_single_hotel_card(hotel)
    
    # Navigation controls UNDER the cards (if more than 3 hotels)
    if len(hotels) > hotels_per_page:
        nav_cols = st.columns([1, 2, 1])
        
        with nav_cols[0]:
            if st.button("⬅️ Previous", disabled=(current_page == 0), use_container_width=True, key=f"prev_{message_index}"):
                st.session_state[carousel_key] = max(0, current_page - 1)
                st.rerun()
        
        with nav_cols[1]:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; color: #94A3B8; font-size: 0.9rem;">
                Page {current_page + 1} of {total_pages}
            </div>
            """, unsafe_allow_html=True)
        
        with nav_cols[2]:
            if st.button("Next ➡️", disabled=(current_page >= total_pages - 1), use_container_width=True, key=f"next_{message_index}"):
                st.session_state[carousel_key] = min(total_pages - 1, current_page + 1)
                st.rerun()


def render_response_view_selector(message: Dict[str, Any], index: int):
    """Render view selector buttons for assistant message (LLM Response, Cypher Query, Graph Nodes, JSON)"""
    import json
    
    # Initialize session state for this message's active view
    view_key = f"response_view_{index}"
    if view_key not in st.session_state:
        st.session_state[view_key] = "llm"  # Default to LLM response
    
    meta = message.get("metadata", {})
    raw_data = meta.get("raw_data", {})
    
    # Create button bar
    st.markdown("""
    <style>
    .response-view-bar {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0 0.75rem 0;
        padding: 0.5rem;
        background: rgba(15, 23, 42, 0.4);
        border-radius: 10px;
        border: 1px solid rgba(79, 70, 229, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Button row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("💬 LLM Response", key=f"view_llm_{index}", 
                    use_container_width=True,
                    type="primary" if st.session_state[view_key] == "llm" else "secondary"):
            st.session_state[view_key] = "llm"
            st.rerun()
    
    with col2:
        if st.button("🔍 Cypher Query", key=f"view_cypher_{index}",
                    use_container_width=True,
                    type="primary" if st.session_state[view_key] == "cypher" else "secondary"):
            st.session_state[view_key] = "cypher"
            st.rerun()
    
    with col3:
        if st.button("🌐 Graph Nodes", key=f"view_graph_{index}",
                    use_container_width=True,
                    type="primary" if st.session_state[view_key] == "graph" else "secondary"):
            st.session_state[view_key] = "graph"
            st.rerun()
    
    with col4:
        if st.button("📋 JSON Data", key=f"view_json_{index}",
                    use_container_width=True,
                    type="primary" if st.session_state[view_key] == "json" else "secondary"):
            st.session_state[view_key] = "json"
            st.rerun()
    
    with col5:

        if st.button("�👨‍💻 Dev Console", key=f"view_dev_{index}",
                    use_container_width=True,
                    type="primary" if st.session_state[view_key] == "dev" else "secondary"):
            st.session_state[view_key] = "dev"
            st.rerun()
    
    # Display content based on selected view
    if st.session_state[view_key] == "cypher":
        # Show Cypher queries
        st.markdown("### 🔍 Cypher Queries")
        
        workflow = meta.get("workflow", "")
        
        if workflow == "baseline_only" or workflow == "hybrid" or workflow == "conversational_hybrid":
            if raw_data.get("baseline_cypher"):
                st.markdown("**Baseline Query:**")
                st.code(raw_data["baseline_cypher"], language="cypher")
                if raw_data.get("baseline_params"):
                    st.markdown("**Parameters:**")
                    st.json(raw_data["baseline_params"])
            else:
                st.info("No baseline Cypher query available")
        
        if workflow == "llm_pipeline":
            if raw_data.get("llm_generated_cypher"):
                st.markdown("**LLM-Generated Query:**")
                st.code(raw_data["llm_generated_cypher"], language="cypher")
            else:
                st.info("No LLM-generated Cypher query available")
        
        if workflow == "embedding_only":
            st.info("This workflow uses vector similarity search (no Cypher queries)")
    
    elif st.session_state[view_key] == "graph":
        # Show graph nodes and relationships
        st.markdown("### 🌐 Knowledge Graph Retrieved Context")
        
        baseline_results = raw_data.get("baseline_results", [])
        embedding_results = raw_data.get("embedding_results", [])
        llm_results = raw_data.get("llm_query_results", [])
        
        if baseline_results:
            st.markdown("#### 🔍 Baseline Results (Neo4j Query)")
            st.markdown(f"**Retrieved {len(baseline_results)} nodes:**")
            
            for i, result in enumerate(baseline_results[:10], 1):  # Show first 10
                with st.expander(f"Node {i}: {result.get('hotel_name', result.get('name', 'Unknown'))}", expanded=i==1):
                    # Display all attributes
                    st.markdown("**Attributes:**")
                    for key, value in result.items():
                        if value is not None and key not in ['hotels']:
                            st.markdown(f"- **{key}**: {value}")
            
            if len(baseline_results) > 10:
                st.info(f"Showing first 10 of {len(baseline_results)} results")
        
        if embedding_results:
            st.markdown("#### 🧠 Embedding Results (Vector Search)")
            st.markdown(f"**Retrieved {len(embedding_results)} nodes:**")
            
            for i, result in enumerate(embedding_results[:10], 1):
                with st.expander(f"Node {i}: {result.get('hotel_name', result.get('name', 'Unknown'))} (Score: {result.get('relevance_score', 'N/A')})", expanded=i==1):
                    st.markdown("**Attributes:**")
                    for key, value in result.items():
                        if value is not None:
                            st.markdown(f"- **{key}**: {value}")
            
            if len(embedding_results) > 10:
                st.info(f"Showing first 10 of {len(embedding_results)} results")
        
        if llm_results:
            st.markdown("#### 🤖 LLM Query Results")
            st.markdown(f"**Retrieved {len(llm_results)} nodes:**")
            
            for i, result in enumerate(llm_results[:10], 1):
                with st.expander(f"Node {i}: {result.get('hotel_name', result.get('name', 'Unknown'))}", expanded=i==1):
                    st.markdown("**Attributes:**")
                    for key, value in result.items():
                        if value is not None:
                            st.markdown(f"- **{key}**: {value}")
            
            if len(llm_results) > 10:
                st.info(f"Showing first 10 of {len(llm_results)} results")
        
        if not baseline_results and not embedding_results and not llm_results:
            st.info("No graph nodes retrieved")
    
    elif st.session_state[view_key] == "json":
        # Show raw JSON
        st.markdown("### 📋 Raw JSON Data")
        
        json_data = {
            "workflow": meta.get("workflow"),
            "intent": meta.get("intent"),
            "entities": meta.get("entities"),
            "result_count": meta.get("result_count"),
            "raw_data": raw_data
        }
        
        st.json(json_data)
    
    elif st.session_state[view_key] == "dev":
        # Show developer console
        from ui.console import render_developer_console
        st.markdown("### 👨‍💻 Developer Console")
        render_developer_console()
    
    # LLM view is handled by the default message rendering (no extra display needed)


def render_message_with_actions(message: Dict[str, Any], index: int):
    """Render a message with timestamp and actions"""
    from core import add_dev_log
    
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", format_timestamp())
    
    # For assistant messages with raw_data, show view selector BEFORE the message
    if role == "assistant" and "metadata" in message and message["metadata"].get("raw_data"):
        render_response_view_selector(message, index)
        
        # Only show the actual message if "llm" view is selected
        view_key = f"response_view_{index}"
        if st.session_state.get(view_key, "llm") != "llm":
            # Don't show the message content for other views
            return
    
    # Render the chat message
    with st.chat_message(role):
        # Message header with timestamp
        col1, col2 = st.columns([6, 1])
        with col2:
            st.caption(f"🕒 {timestamp}")
        
        # Message content
        st.markdown(content)
        
        # Assistant message extras
        if role == "assistant":
            # Copy button (inline)
            if st.button("📋 Copy", key=f"copy_{index}", help="Copy response"):
                st.session_state[f"copied_{index}"] = True
                st.toast("✅ Copied to clipboard!", icon="📋")
            
            # Show metadata in enhanced card (only if there are hotels or important metadata)
            if "metadata" in message:
                meta = message["metadata"]
                has_hotels = meta.get("hotels") and len(meta.get("hotels", [])) > 0
                
                # Only show expander if there's useful info beyond hotel cards
                if meta.get("intent") or meta.get("entities"):
                    with st.expander("📊 View Details", expanded=False):
                        # Metrics in a compact layout
                        if meta.get("intent") or meta.get("workflow"):
                            col1, col2 = st.columns(2)
                            
                            if meta.get("intent"):
                                with col1:
                                    intent_icon = {
                                        "HotelSearch": "🔍",
                                        "HotelRecommendation": "⭐",
                                        "ReviewLookup": "💬",
                                        "VisaQuestion": "✈️",
                                        "LocationQuery": "📍",
                                        "AmenityFilter": "🏷️",
                                        "GeneralQuestionAnswering": "❓",
                                        "CasualConversation": "💭"
                                    }.get(meta.get("intent", ""), "📝")
                                    st.metric(
                                        "Intent",
                                        f"{intent_icon} {meta.get('intent', 'N/A')}"
                                    )
                            
                            if meta.get("workflow"):
                                with col2:
                                    workflow_icon = {
                                        "baseline_only": "🔍",
                                        "embedding_only": "🧠",
                                        "hybrid": "⚡",
                                        "llm_pipeline": "🤖",
                                        "conversational_hybrid": "💬"
                                    }.get(meta.get("workflow", ""), "🔄")
                                    st.metric(
                                        "Workflow",
                                        f"{workflow_icon} {meta.get('workflow', 'N/A')}"
                                    )
                        
                        # Entities as beautiful cards if present
                        if meta.get("entities") and any(meta["entities"].values()):
                            st.markdown("---")
                            st.markdown("**🏷️ Extracted Entities:**")
                            
                            # Filter out None/empty entities
                            active_entities = {k: v for k, v in meta["entities"].items() if v}
                            
                            if active_entities:
                                entity_html = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">'
                                for key, value in active_entities.items():
                                    entity_html += f'''
                                    <span style="background: rgba(79, 70, 229, 0.12); 
                                                 padding: 0.4rem 0.8rem; 
                                                 border-radius: 8px; 
                                                 border: 1px solid rgba(79, 70, 229, 0.25);
                                                 font-size: 0.85rem;
                                                 color: var(--primary);">
                                        <strong>{key}:</strong> {value}
                                    </span>
                                    '''
                                entity_html += '</div>'
                                st.markdown(entity_html, unsafe_allow_html=True)
    
    # For assistant messages, show hotel cards AFTER the chat message
    if role == "assistant" and "hotels" in message.get("metadata", {}):
        hotels = message["metadata"]["hotels"]
        if hotels:
            from core import add_dev_log
            add_dev_log('DEBUG', f"🎯 Rendering {len(hotels)} hotel cards AFTER chat message")
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            render_hotel_cards(hotels, message_index=index)
