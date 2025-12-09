"""
GraphState TypedDict definition for LangGraph workflows
Supports all 4 workflow modes with optional fields
"""

from typing import TypedDict, Optional, List, Dict, Any


class GraphState(TypedDict, total=False):
    """
    Shared state for all Graph-RAG workflows.
    Uses total=False to make all fields optional.
    """
    
    # Input
    user_query: str
    
    # Intent & Entities (baseline/hybrid workflows)
    intent: Optional[str]  # 7 types: HotelSearch, HotelRecommendation, ReviewLookup, LocationQuery, VisaQuestion, AmenityFilter, GeneralQuestionAnswering
    entities: Optional[Dict[str, Any]]  # city, country, hotel_name, traveller_type, ratings, etc.
    
    # Baseline retrieval
    baseline_cypher: Optional[str]
    baseline_params: Optional[Dict[str, Any]]
    baseline_results: Optional[List[Dict[str, Any]]]
    
    # Embedding retrieval
    query_embedding: Optional[List[float]]
    embedding_results: Optional[List[Dict[str, Any]]]
    
    # LLM-generated query (llm_pipeline workflow)
    llm_generated_cypher: Optional[str]
    llm_query_results: Optional[List[Dict[str, Any]]]
    
    # Merged/Final context
    merged_context: Optional[str]
    
    # Answer generation
    llm_response: Optional[str]
    
    # Conversation context (for multi-turn dialogue)
    chat_history: Optional[List[Dict[str, Any]]]  # Previous conversation turns
    conversation_context: Optional[str]  # Formatted context string
    
    # Output
    final_output: Optional[Dict[str, Any]]
    
    # Metadata
    metadata: Optional[Dict[str, Any]]  # timings, model names, result counts
    error: Optional[str]
