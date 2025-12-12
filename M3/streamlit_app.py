"""
Streamlit UI for Graph-RAG Hotel Travel Assistant
Modern, futuristic interface with hotel theming and developer console
"""

import sys
from pathlib import Path
import streamlit as st
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import io
import contextlib

# Add M3 to path
sys.path.insert(0, str(Path(__file__).parent))

from langgraph.checkpoint.memory import MemorySaver
from workflows.workflow_factory import get_workflow_with_memory, list_workflows
from utils.config_loader import ConfigLoader
from utils.llm_client import LLMClient
from utils.embedding_client import EmbeddingClient
import subprocess


# Page configuration
st.set_page_config(
    page_title="Hotel Travel Assistant",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern hotel-themed UI
st.markdown("""
<style>
    /* Main theme colors - hotel luxury gold and deep blue */
    :root {
        --hotel-gold: #D4AF37;
        --hotel-blue: #1B2838;
        --hotel-silver: #C0C0C0;
        --hotel-cream: #F5F5DC;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%);
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #D4AF37;
    }
    
    /* User message */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
        border-left-color: #D4AF37;
    }
    
    /* Assistant message */
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.15) 0%, rgba(52, 152, 219, 0.05) 100%);
        border-left-color: #3498DB;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1B2838 0%, #34495E 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Georgia', serif;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #B8960F 100%);
        color: #1B2838;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4);
    }
    
    /* Select boxes */
    .stSelectbox>div>div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: white;
    }
    
    /* Text input */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(212, 175, 55, 0.1);
        border-radius: 8px;
        color: #D4AF37;
        font-weight: bold;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 8px;
    }
    
    /* Metrics */
    .stMetric {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.05) 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    /* Developer console - clean and professional */
    .dev-console-container {
        position: sticky;
        top: 100px;
        height: calc(100vh - 200px);
        background: rgba(15, 20, 30, 0.95);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 0;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    .dev-console-header {
        padding: 1rem;
        background: rgba(212, 175, 55, 0.1);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        font-weight: bold;
        color: #D4AF37;
    }
    
    .dev-console-logs {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    .dev-log-entry {
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 3px solid;
    }
    
    .log-user { 
        border-left-color: #D4AF37; 
        background: rgba(212, 175, 55, 0.05);
        color: #D4AF37;
    }
    
    .log-system { 
        border-left-color: #3498DB; 
        background: rgba(52, 152, 219, 0.05);
        color: #3498DB;
    }
    
    .log-success { 
        border-left-color: #2ECC71; 
        background: rgba(46, 204, 113, 0.05);
        color: #2ECC71;
    }
    
    .log-error { 
        border-left-color: #E74C3C; 
        background: rgba(231, 76, 60, 0.05);
        color: #E74C3C;
    }
    
    .log-output { 
        border-left-color: #95A5A6; 
        background: rgba(149, 165, 166, 0.05);
        color: #BDC3C7;
    }
    
    .log-terminal {
        border-left: none;
        background: transparent;
        color: #ECF0F1;
        padding: 0.75rem;
        margin: 0;
        white-space: pre-wrap;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.8rem;
        line-height: 1.5;
    }
    
    .dev-console-logs::-webkit-scrollbar {
        width: 6px;
    }
    
    .dev-console-logs::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    
    .dev-console-logs::-webkit-scrollbar-thumb {
        background: rgba(212, 175, 55, 0.3);
        border-radius: 3px;
    }
    
    /* Chat area - use native Streamlit container with fixed height */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:has(.chat-area-marker) {
        position: sticky;
        top: 80px;
        height: calc(100vh - 160px);
        max-height: 80vh;
        background: rgba(27, 40, 56, 0.95);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 1rem;
        overflow-y: auto;
        overflow-x: hidden;
    }
    
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:has(.chat-area-marker)::-webkit-scrollbar {
        width: 6px;
    }
    
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:has(.chat-area-marker)::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:has(.chat-area-marker)::-webkit-scrollbar-thumb {
        background: rgba(212, 175, 55, 0.3);
        border-radius: 3px;
    }
    
    /* Chat input at bottom */
    .stChatFloatingInputContainer {
        position: sticky !important;
        bottom: 1rem !important;
        background: rgba(27, 40, 56, 0.98) !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
    }
    
    /* Prevent page scrolling */
    section.main > div {
        overflow: hidden !important;
        max-height: 100vh;
    }
    
    /* Marker styling */
    .chat-area-marker {
        display: none;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .badge-success {
        background: rgba(46, 204, 113, 0.2);
        color: #2ECC71;
        border: 1px solid #2ECC71;
    }
    
    .badge-info {
        background: rgba(52, 152, 219, 0.2);
        color: #3498DB;
        border: 1px solid #3498DB;
    }
    
    .badge-warning {
        background: rgba(241, 196, 15, 0.2);
        color: #F1C40F;
        border: 1px solid #F1C40F;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.config = ConfigLoader()
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.memory = MemorySaver()
        st.session_state.workflow_mode = "conversational_hybrid"
        st.session_state.workflow = None
        st.session_state.messages = []
        st.session_state.dev_logs = []
        st.session_state.current_llm_model = st.session_state.config.get('llm.default_model', 'openai/gpt-oss-120b')
        st.session_state.current_embedding_model = st.session_state.config.get('embedding.default_model', 'all-MiniLM-L6-v2')
        st.session_state.show_dev_console = True
        st.session_state.last_response = None
        
        # Initialize workflow
        _initialize_workflow()


def _initialize_workflow():
    """Initialize or reinitialize the workflow"""
    st.session_state.workflow = get_workflow_with_memory(
        st.session_state.workflow_mode,
        st.session_state.memory
    )


def add_dev_log(log_type: str, message: str):
    """Add a log entry to developer console"""
    st.session_state.dev_logs.append({
        'type': log_type,
        'message': message
    })
    # Keep only last 100 logs
    if len(st.session_state.dev_logs) > 100:
        st.session_state.dev_logs = st.session_state.dev_logs[-100:]


def capture_output_as_log(func, *args, **kwargs):
    """Capture print output and add to dev logs - preserve terminal formatting"""
    output_buffer = io.StringIO()
    
    with contextlib.redirect_stdout(output_buffer):
        result = func(*args, **kwargs)
    
    output = output_buffer.getvalue()
    if output.strip():
        # Add the entire output as one log entry to preserve formatting
        add_dev_log('TERMINAL', output.strip())
    
    return result


def process_query(user_query: str) -> Dict[str, Any]:
    """
    Process user query through the workflow
    
    Args:
        user_query: User's question
        
    Returns:
        Response dictionary with answer and metadata
    """
    add_dev_log('USER', f"User: {user_query}")
    add_dev_log('SYSTEM', f"{'='*60}\nWorkflow: {st.session_state.workflow_mode} | Thread: {st.session_state.thread_id[:8]}...\n{'='*60}")
    
    try:
        initial_state = {
            "user_query": user_query,
            "intent": None,
            "entities": {},
            "baseline_results": [],
            "embedding_results": [],
            "llm_query_results": [],
            "merged_context": "",
            "llm_response": "",
            "chat_history": [msg for msg in st.session_state.messages],
            "error": None,
            "metadata": {}
        }
        
        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id
            }
        }
        
        # Invoke workflow and capture output
        result = capture_output_as_log(
            st.session_state.workflow.invoke,
            initial_state,
            config
        )
        
        # Extract response
        response = {
            "answer": result.get("llm_response", "I couldn't process your request."),
            "intent": result.get("intent"),
            "entities": result.get("entities", {}),
            "baseline_results": result.get("baseline_results", []),
            "embedding_results": result.get("embedding_results", []),
            "llm_query_results": result.get("llm_query_results", []),
            "merged_context": result.get("merged_context", ""),
            "metadata": result.get("metadata", {}),
            "workflow": st.session_state.workflow_mode
        }
        
        # Calculate total results
        if st.session_state.workflow_mode == "baseline_only":
            response["result_count"] = len(response["baseline_results"])
        elif st.session_state.workflow_mode == "embedding_only":
            response["result_count"] = len(response["embedding_results"])
        elif st.session_state.workflow_mode in ["hybrid", "conversational_hybrid"]:
            response["result_count"] = len(response["baseline_results"]) + len(response["embedding_results"])
        elif st.session_state.workflow_mode == "llm_pipeline":
            response["result_count"] = len(response["llm_query_results"])
        else:
            response["result_count"] = 0
        
        add_dev_log('SUCCESS', f"✓ Query Complete | Intent: {response['intent']} | Results: {response['result_count']} | Answer: {len(response['answer'])} chars\n")
        
        return response
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        add_dev_log('ERROR', error_msg)
        return {
            "answer": f"I encountered an error: {str(e)}",
            "error": str(e),
            "result_count": 0,
            "workflow": st.session_state.workflow_mode
        }


def regenerate_embeddings(model_name: str):
    """Regenerate embeddings with new model"""
    add_dev_log('SYSTEM', f"Regenerating embeddings with model: {model_name}")
    
    try:
        # Update embedding client to use new model
        from utils.embedding_client import EmbeddingClient
        EmbeddingClient._instance = None
        EmbeddingClient._model = model_name
        
        # Run create_embeddings.py
        add_dev_log('SYSTEM', "Running create_embeddings.py...")
        
        result = subprocess.run(
            [sys.executable, "create_embeddings.py"],
            cwd=str(Path(__file__).parent),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            add_dev_log('SUCCESS', "Embeddings regenerated successfully!")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    add_dev_log('OUTPUT', line)
            return True
        else:
            add_dev_log('ERROR', f"Failed to regenerate embeddings: {result.stderr}")
            return False
            
    except Exception as e:
        add_dev_log('ERROR', f"Error regenerating embeddings: {str(e)}")
        return False


def render_sidebar():
    """Render the sidebar with controls"""
    with st.sidebar:
        st.markdown("# 🏨 Hotel Assistant")
        st.markdown("### Control Panel")
        st.markdown("---")
        
        # Workflow selection
        st.markdown("#### 🔄 Workflow")
        workflow_options = list_workflows()
        workflow_display = {
            "baseline_only": "🔍 Baseline Only (Cypher)",
            "embedding_only": "🧠 Embedding Only (Semantic)",
            "hybrid": "⚡ Hybrid (Both)",
            "llm_pipeline": "🤖 LLM Pipeline (Full Auto)",
            "conversational_hybrid": "💬 Conversational (Memory + Hybrid)"
        }
        
        selected_workflow = st.selectbox(
            "Select Workflow",
            workflow_options,
            index=workflow_options.index(st.session_state.workflow_mode),
            format_func=lambda x: workflow_display.get(x, x),
            key="workflow_selector"
        )
        
        if selected_workflow != st.session_state.workflow_mode:
            st.session_state.workflow_mode = selected_workflow
            _initialize_workflow()
            add_dev_log('SYSTEM', f"Switched to workflow: {selected_workflow}")
            st.rerun()
        
        st.markdown("---")
        
        # LLM Model selection
        st.markdown("#### 🤖 LLM Model")
        available_llm_models = st.session_state.config.get('llm.available_models', [])
        llm_model_names = [m['name'] for m in available_llm_models]
        llm_display_names = {m['name']: f"{m['display_name']} - {m['description']}" for m in available_llm_models}
        
        selected_llm = st.selectbox(
            "Select LLM",
            llm_model_names,
            index=llm_model_names.index(st.session_state.current_llm_model) if st.session_state.current_llm_model in llm_model_names else 0,
            format_func=lambda x: llm_display_names.get(x, x),
            key="llm_selector"
        )
        
        if selected_llm != st.session_state.current_llm_model:
            st.session_state.current_llm_model = selected_llm
            # Reinitialize LLM client
            LLMClient._instance = None
            LLMClient._model = selected_llm
            add_dev_log('SYSTEM', f"Switched to LLM: {selected_llm}")
            st.success(f"✓ LLM updated to {selected_llm}")
        
        st.markdown("---")
        
        # Embedding Model selection
        st.markdown("#### 🧠 Embedding Model")
        available_embedding_models = st.session_state.config.get('embedding.available_models', [])
        embedding_model_names = [m['name'] for m in available_embedding_models]
        embedding_display_names = {m['name']: f"{m['display_name']} ({m['dimensions']}D)" for m in available_embedding_models}
        
        selected_embedding = st.selectbox(
            "Select Embedding Model",
            embedding_model_names,
            index=embedding_model_names.index(st.session_state.current_embedding_model) if st.session_state.current_embedding_model in embedding_model_names else 0,
            format_func=lambda x: embedding_display_names.get(x, x),
            key="embedding_selector"
        )
        
        if selected_embedding != st.session_state.current_embedding_model:
            if st.button("🔄 Regenerate Embeddings", key="regen_embeddings"):
                with st.spinner("Regenerating embeddings... This may take a minute."):
                    if regenerate_embeddings(selected_embedding):
                        st.session_state.current_embedding_model = selected_embedding
                        st.success(f"✓ Embeddings regenerated with {selected_embedding}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to regenerate embeddings. Check developer console.")
        
        st.markdown("---")
        
        # Session controls
        st.markdown("#### 🎛️ Session Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", key="clear_chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.thread_id = str(uuid.uuid4())
                st.session_state.memory = MemorySaver()
                _initialize_workflow()
                add_dev_log('SYSTEM', "Chat history cleared")
                st.rerun()
        
        with col2:
            if st.button("📋 Clear Logs", key="clear_logs", use_container_width=True):
                st.session_state.dev_logs = []
                add_dev_log('SYSTEM', "Developer logs cleared")
                st.rerun()
        
        st.markdown("---")
        
        # Developer console toggle
        st.markdown("#### 👨‍💻 Developer Console")
        show_dev = st.checkbox(
            "Show Developer Console",
            value=st.session_state.show_dev_console,
            key="dev_console_toggle"
        )
        st.session_state.show_dev_console = show_dev
        
        st.markdown("---")
        
        # Statistics
        st.markdown("#### 📊 Session Stats")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Thread ID", st.session_state.thread_id[:8] + "...")
        if st.session_state.last_response:
            st.metric("Last Results", st.session_state.last_response.get('result_count', 0))
        
        st.markdown("---")
        st.markdown("##### ℹ️ Info")
        st.caption(f"Workflow: {st.session_state.workflow_mode}")
        st.caption(f"LLM: {st.session_state.current_llm_model.split('/')[-1]}")
        st.caption(f"Embeddings: {st.session_state.current_embedding_model}")


def render_developer_console():
    """Render developer console with logs - terminal style"""
    if not st.session_state.dev_logs:
        st.info("👨‍💻 Developer Console\n\nNo logs yet. Start chatting to see system activity!")
    else:
        # Build terminal-style log HTML
        log_html = '<div class="dev-console-container">'
        log_html += '<div class="dev-console-header">👨‍💻 Developer Console</div>'
        log_html += '<div class="dev-console-logs">'
        
        # Show last 50 logs in reverse order (newest first)
        for log in reversed(st.session_state.dev_logs[-50:]):
            log_type = log['type'].lower()
            message = log['message']
            
            if log_type == 'terminal':
                # Terminal output - preserve exact formatting
                log_html += f'<div class="log-terminal">{message}</div>'
            else:
                # System messages - compact format
                css_class = f"log-{log_type}"
                
                # Format message with icon
                if log_type == 'error':
                    icon = '❌'
                elif log_type == 'success':
                    icon = '✅'
                elif log_type == 'user':
                    icon = '👤'
                elif log_type == 'system':
                    icon = '⚙️'
                else:
                    icon = '📋'
                
                log_html += f'<div class="dev-log-entry {css_class}">'
                log_html += f'{icon} {message}'
                log_html += '</div>'
        
        log_html += '</div></div>'
        st.markdown(log_html, unsafe_allow_html=True)


def render_chat_interface():
    """Render main chat interface - messages and input only"""
    # Add invisible marker for CSS targeting
    st.markdown('<div class="chat-area-marker"></div>', unsafe_allow_html=True)
    
    # Header
    st.markdown("### 💬 Chat with Hotel Assistant")
    st.markdown("---")
    
    # Display all chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show metadata for assistant messages in a clean expander
            if message["role"] == "assistant" and "metadata" in message:
                with st.expander("📊 Details"):
                    meta = message["metadata"]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Intent", meta.get("intent", "N/A"))
                    with col2:
                        st.metric("Results", meta.get("result_count", 0))
                    with col3:
                        st.metric("Workflow", meta.get("workflow", "N/A"))
                    
                    if meta.get("entities"):
                        st.json(meta["entities"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about hotels, travel, or visa requirements..."):
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Process query
        response = process_query(prompt)
        st.session_state.last_response = response
        
        # Add assistant message to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "metadata": {
                "intent": response.get("intent"),
                "result_count": response.get("result_count", 0),
                "workflow": response.get("workflow"),
                "entities": response.get("entities", {})
            }
        })
        
        st.rerun()


def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 0;">🏨 Hotel Travel Assistant</h1>
        <p style="font-size: 1.2rem; color: #D4AF37; margin-top: 0;">
            Powered by Graph-RAG & LangGraph
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main layout - fixed modals for both chat and console
    if st.session_state.show_dev_console:
        # Split layout: chat on left, console on right (both in fixed containers)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            chat_container = st.container()
            with chat_container:
                render_chat_interface()
        
        with col2:
            render_developer_console()
    else:
        # Full width chat
        chat_container = st.container()
        with chat_container:
            render_chat_interface()


if __name__ == "__main__":
    main()
