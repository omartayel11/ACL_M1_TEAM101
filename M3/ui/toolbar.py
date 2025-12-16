"""
Toolbar navigation component
"""

import streamlit as st


def render_toolbar():
    """Render horizontal toolbar with navigation tabs"""
    st.markdown("""
    <style>
    /* Toolbar container - responsive */
    .toolbar-container {
        background: linear-gradient(135deg, 
            rgba(15, 23, 42, 0.95) 0%, 
            rgba(30, 41, 59, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-bottom: 2px solid rgba(79, 70, 229, 0.3);
        padding: 0.75rem 1rem;
        margin: -1rem -1rem 1.5rem -1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        position: sticky;
        top: 0;
        z-index: 1000;
        transition: all 0.3s ease;
    }
    
    /* Tab buttons - responsive design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        padding: 0;
        width: 100%;
        display: flex;
        justify-content: flex-start;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 10px;
        color: var(--text-secondary);
        padding: 0 1.75rem;
        font-size: 0.95rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        white-space: nowrap;
        flex: 0 1 auto;
        min-width: fit-content;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(79, 70, 229, 0.15);
        border-color: rgba(79, 70, 229, 0.4);
        color: var(--primary);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, #6366F1 100%);
        border-color: var(--primary);
        color: white !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding: 0;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .toolbar-container {
            padding: 0.5rem 0.75rem;
            margin: -1rem -0.75rem 1rem -0.75rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 44px;
            padding: 0 1.25rem;
            font-size: 0.875rem;
        }
    }
    
    @media (max-width: 640px) {
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            padding: 0 1rem;
            font-size: 0.8rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize active tab in session state
    if 'active_tab_index' not in st.session_state:
        st.session_state.active_tab_index = 0
    
    # Create tabs
    tab1, tab2 = st.tabs([
        "💬 Chat Assistant",
        "📚 Query Library"
    ])
    
    # Check if we should switch to chat tab
    if hasattr(st.session_state, 'switch_to_chat') and st.session_state.switch_to_chat:
        st.session_state.switch_to_chat = False
        # Use JavaScript to click the first tab
        st.markdown("""
        <script>
        setTimeout(function() {
            const tabs = parent.document.querySelectorAll('[data-baseweb="tab"]');
            if (tabs && tabs.length > 0) {
                tabs[0].click();
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
    
    return tab1, tab2
