"""
Core functionality for session management and query processing
"""

import sys
from pathlib import Path
import streamlit as st
import uuid
import io
import contextlib
from typing import Dict, Any
from datetime import datetime

# Add M3 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.checkpoint.memory import MemorySaver
from workflows.workflow_factory import get_workflow_with_memory, list_workflows
from utils.config_loader import ConfigLoader
from utils.llm_client import LLMClient
from utils.embedding_client import EmbeddingClient


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
        st.session_state.last_response = None
        st.session_state.pending_query = None
        
        # Initialize workflow
        initialize_workflow()


def initialize_workflow():
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
            "workflow": st.session_state.workflow_mode,
            "baseline_cypher": result.get("baseline_cypher"),
            "baseline_params": result.get("baseline_params"),
            "llm_generated_cypher": result.get("llm_generated_cypher")
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
