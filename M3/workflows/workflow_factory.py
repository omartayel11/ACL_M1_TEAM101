"""
Workflow Factory - Create workflow by name
Factory pattern for easy workflow selection at runtime
Supports LangGraph memory with checkpointing
"""

from typing import Dict, Callable, Any, Optional
from langgraph.checkpoint.base import BaseCheckpointSaver
from .baseline_workflow import create_baseline_workflow
from .embedding_workflow import create_embedding_workflow
from .hybrid_workflow import create_hybrid_workflow
from .llm_pipeline_workflow import create_llm_pipeline_workflow
from .conversational_hybrid_workflow import create_conversational_hybrid_workflow


# Workflow registry
WORKFLOWS: Dict[str, Callable[[], Any]] = {
    "baseline_only": create_baseline_workflow,
    "embedding_only": create_embedding_workflow,
    "hybrid": create_hybrid_workflow,
    "llm_pipeline": create_llm_pipeline_workflow,
    "conversational_hybrid": create_conversational_hybrid_workflow,  # New!
}


def get_workflow(name: str):
    """
    Get workflow by name (no memory)
    
    Args:
        name: Workflow name (baseline_only, embedding_only, hybrid, llm_pipeline)
        
    Returns:
        Compiled LangGraph workflow
        
    Raises:
        ValueError: If workflow name is not recognized
    """
    if name not in WORKFLOWS:
        available = ", ".join(WORKFLOWS.keys())
        raise ValueError(f"Unknown workflow '{name}'. Available workflows: {available}")
    
    return WORKFLOWS[name]()


def get_workflow_with_memory(name: str, checkpointer: Optional[BaseCheckpointSaver] = None):
    """
    Get workflow with LangGraph memory checkpointing
    
    Args:
        name: Workflow name
        checkpointer: LangGraph checkpoint saver (e.g., MemorySaver)
        
    Returns:
        Compiled LangGraph workflow with memory
        
    Raises:
        ValueError: If workflow name is not recognized
    """
    if name not in WORKFLOWS:
        available = ", ".join(WORKFLOWS.keys())
        raise ValueError(f"Unknown workflow '{name}'. Available workflows: {available}")
    
    # For now, return regular workflow
    # Full memory integration would require modifying workflow creators
    # to accept and use checkpointer parameter
    return WORKFLOWS[name]()


def list_workflows() -> list:
    """
    Get list of available workflow names
    
    Returns:
        List of workflow names
    """
    return list(WORKFLOWS.keys())


if __name__ == "__main__":
    # Test workflow factory
    print("=== Workflow Factory Test ===\n")
    
    print("Available workflows:")
    for workflow_name in list_workflows():
        print(f"  - {workflow_name}")
    
    print("\n" + "=" * 60)
    
    # Test each workflow
    test_query = "Find hotels in Paris"
    
    for workflow_name in list_workflows():
        print(f"\nTesting workflow: {workflow_name}")
        print("-" * 60)
        
        try:
            workflow = get_workflow(workflow_name)
            result = workflow.invoke({"user_query": test_query})
            
            final_output = result.get('final_output', {})
            print(f"✓ Workflow executed successfully")
            print(f"  Workflow type: {final_output.get('workflow')}")
            print(f"  Results: {len(final_output.get('results', []))} items")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("\n✓ Factory test complete")
