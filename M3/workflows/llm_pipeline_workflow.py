"""
LLM Pipeline Workflow - Full LLM Autonomy
LLM generates Cypher queries and answers from retrieved context
"""

from langgraph.graph import StateGraph, END
from state.graph_state import GraphState
from nodes import (
    input_node,
    llm_query_node,
    answer_node,
    output_node
)


def create_llm_pipeline_workflow():
    """
    Create LLM pipeline workflow graph
    
    Flow: Input → LLMQuery → Answer → Output
    
    Use Case: Full LLM autonomy
    - No intent/entity extraction needed
    - LLM generates Cypher query directly from natural language
    - Executes generated query on Neo4j
    - LLM generates final answer from results
    - Most flexible but variable quality
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("llm_query", llm_query_node)
    workflow.add_node("answer", answer_node)
    workflow.add_node("output", output_node)
    
    # Define edges (linear flow)
    workflow.set_entry_point("input")
    workflow.add_edge("input", "llm_query")
    workflow.add_edge("llm_query", "answer")
    workflow.add_edge("answer", "output")
    workflow.add_edge("output", END)
    
    # Compile and return
    return workflow.compile()


if __name__ == "__main__":
    # Test LLM pipeline workflow
    workflow = create_llm_pipeline_workflow()
    
    test_query = "What are the top 3 hotels in Paris with the best reviews?"
    print(f"Testing LLM Pipeline Workflow with query: '{test_query}'")
    print("=" * 60)
    
    result = workflow.invoke({"user_query": test_query})
    
    print("\n=== Results ===")
    print(f"LLM-generated Cypher:\n{result.get('llm_generated_cypher', 'N/A')}\n")
    print(f"Query results count: {len(result.get('llm_query_results', []))}")
    
    llm_response = result.get('llm_response', 'N/A')
    print(f"LLM Response:\n{llm_response[:300] if llm_response != 'N/A' else 'N/A'}...\n")
    
    final_output = result.get('final_output', {})
    print(f"Workflow: {final_output.get('workflow')}")
    answer = final_output.get('answer', 'N/A')
    print(f"Answer: {answer[:200] if answer != 'N/A' and answer else 'N/A'}...")
