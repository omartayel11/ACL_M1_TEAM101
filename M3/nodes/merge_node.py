"""
Merge Node - Merge baseline and embedding results
"""

from state.graph_state import GraphState
from components.result_merger import ResultMerger

# Initialize merger once
merger = ResultMerger()


def _get_context_header(intent: str, entities: dict) -> str:
    """
    Generate an intent-based context header to explain what the results represent
    
    Args:
        intent: Classification intent
        entities: Extracted entities
        
    Returns:
        Context header string
    """
    headers = {
        "HotelSearch": "Search Results for Hotels",
        "HotelRecommendation": "Recommended Hotels",
        "ReviewLookup": "Reviews and Feedback",
        "LocationQuery": "Hotels by Location",
        "VisaQuestion": "Visa Information",
        "AmenityFilter": "Hotels Matching Your Criteria",
        "GeneralQuestionAnswering": "Hotel Information"
    }
    
    base_header = headers.get(intent, "Search Results")
    
    # Add entity-specific context
    # Check from_country for both HotelRecommendation and GeneralQuestionAnswering
    if entities.get("from_country"):
        return f"Hotels Popular Among Travelers from {entities['from_country']}"
    elif intent == "HotelRecommendation" and entities.get("traveller_type") and entities.get("city"):
        return f"Top Hotels in {entities['city']} for {entities['traveller_type']} Travelers"
    elif intent == "HotelRecommendation" and entities.get("traveller_type"):
        return f"Top Hotels for {entities['traveller_type']} Travelers"
    elif entities.get("reference_hotel"):
        return f"Hotels Similar to {entities['reference_hotel']}"
    elif intent == "AmenityFilter" and any(k.startswith("min_") for k in entities.keys()):
        criteria = []
        if entities.get("min_cleanliness"):
            criteria.append(f"Cleanliness ≥ {entities['min_cleanliness']}")
        if entities.get("min_comfort"):
            criteria.append(f"Comfort ≥ {entities['min_comfort']}")
        if entities.get("min_staff"):
            criteria.append(f"Staff ≥ {entities['min_staff']}")
        if entities.get("min_value"):
            criteria.append(f"Value ≥ {entities['min_value']}")
        if criteria and entities.get("city"):
            return f"Hotels in {entities['city']} matching: {', '.join(criteria)}"
        elif criteria:
            return f"Hotels matching: {', '.join(criteria)}"
    elif entities.get("balanced"):
        return "Hotels with Balanced Quality Scores Across All Dimensions"
    # Query 22 (trending) disabled
    # elif entities.get("is_trending"):
    #     return "Hotels with Improving Review Scores (Trending Up)"
    
    return base_header


def merge_node(state: GraphState) -> GraphState:
    """
    Merge and deduplicate baseline + embedding results
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with merged context
    """
    baseline_results = state.get("baseline_results", [])
    embedding_results = state.get("embedding_results", [])
    intent = state.get("intent", "")
    entities = state.get("entities", {})
    
    # Merge results into formatted context
    merged_context = merger.merge(baseline_results, embedding_results)
    
    # Add intent-based context header to explain what these results represent
    context_header = _get_context_header(intent, entities)
    if context_header and merged_context != "No results found.":
        merged_context = context_header + "\n\n" + merged_context
    
    # Print merged context for visibility
    print(f"\n📋 [MERGED CONTEXT FOR LLM]")
    print(f"Baseline results: {len(baseline_results)} | Embedding results: {len(embedding_results)}")
    print(f"Context length: {len(merged_context)} characters")
    print(f"\nContext preview:\n{'-'*60}")
    print(merged_context[:500] + ("..." if len(merged_context) > 500 else ""))
    print(f"{'-'*60}")
    
    # Return only changed fields
    return {"merged_context": merged_context}


if __name__ == "__main__":
    # Test merge node
    test_state: GraphState = {
        "baseline_results": [
            {
                "hotel_id": "h1",
                "hotel_name": "Hotel Paris",
                "city": "Paris",
                "avg_score": 8.5
            }
        ],
        "embedding_results": [
            {
                "hotel_id": "h2",
                "hotel_name": "London Inn",
                "city": "London",
                "avg_score": 7.8,
                "similarity_score": 0.92
            }
        ]
    }
    
    result = merge_node(test_state)
    print("Merge Node Test:")
    print(f"Baseline count: {len(test_state['baseline_results'])}")
    print(f"Embedding count: {len(test_state['embedding_results'])}")
    print(f"\nMerged Context:\n{result.get('merged_context', 'None')[:300]}...")
