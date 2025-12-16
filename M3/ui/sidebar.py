"""
Sidebar UI component
"""

import sys
from pathlib import Path
import streamlit as st
import uuid
import subprocess

# Add M3 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.checkpoint.memory import MemorySaver
from workflows.workflow_factory import list_workflows
from utils.llm_client import LLMClient
from utils.embedding_client import EmbeddingClient
from core import initialize_workflow, add_dev_log


def regenerate_embeddings(model_name: str):
    """Regenerate embeddings with new model"""
    add_dev_log('SYSTEM', f"Regenerating embeddings with model: {model_name}")
    
    try:
        # Update embedding client to use new model
        EmbeddingClient._instance = None
        EmbeddingClient._model = model_name
        
        # Run create_embeddings.py
        add_dev_log('SYSTEM', "Running create_embeddings.py...")
        
        result = subprocess.run(
            [sys.executable, "create_embeddings.py"],
            cwd=str(Path(__file__).parent.parent),
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
        # Header with icon
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖</div>
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700;">AI Assistant</h2>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Control Panel</p>
        </div>
        """, unsafe_allow_html=True)
        
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
            initialize_workflow()
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
                initialize_workflow()
                add_dev_log('SYSTEM', "Chat history cleared")
                st.rerun()
        
        with col2:
            if st.button("📋 Clear Logs", key="clear_logs", use_container_width=True):
                st.session_state.dev_logs = []
                add_dev_log('SYSTEM', "Developer logs cleared")
                st.rerun()
        
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
