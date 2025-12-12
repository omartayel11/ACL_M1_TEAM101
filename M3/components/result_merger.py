"""
Result Merger for Graph-RAG Hotel Travel Assistant
Merges and deduplicates baseline + embedding results
"""

from typing import List, Dict, Any
from utils.config_loader import ConfigLoader


class ResultMerger:
    """
    Merge and deduplicate results from baseline (Cypher) and embedding (FAISS) retrieval.
    Ranks results and formats context for LLM consumption.
    """
    
    def __init__(self):
        """Initialize result merger"""
        config = ConfigLoader()
        self.max_context_tokens = config.get('retrieval.merge.max_context_tokens', 2500)
        self.chars_per_token = 4  # Rough estimate
        self.max_chars = self.max_context_tokens * self.chars_per_token
    
    def merge(
        self,
        baseline_results: List[Dict[str, Any]],
        embedding_results: List[Dict[str, Any]]
    ) -> str:
        """
        Merge and deduplicate baseline + embedding results
        
        Args:
            baseline_results: Results from Cypher query
            embedding_results: Results from FAISS vector search
            
        Returns:
            Formatted context string for LLM
        """
        baseline_results = baseline_results or []
        embedding_results = embedding_results or []
        
        # Deduplicate results
        merged = self._deduplicate(baseline_results, embedding_results)
        
        # Rank by relevance
        ranked = self._rank_results(merged)
        
        # Format for LLM consumption
        context = self._format_context(ranked)
        
        return context
    
    def _deduplicate(
        self,
        baseline_results: List[Dict[str, Any]],
        embedding_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate results by hotel_id or review_id
        
        Args:
            baseline_results: Baseline results
            embedding_results: Embedding results
            
        Returns:
            Deduplicated list with combined scores
        """
        seen = {}
        
        # Process baseline results first (prioritize)
        for i, result in enumerate(baseline_results):
            key = result.get('hotel_id') or result.get('review_id')
            # For non-hotel/review results (visa, etc.), use index as key
            if not key:
                key = f"other_{i}"
            result['source'] = 'baseline'
            result['relevance_score'] = result.get('relevance_score', 1.0)
            seen[key] = result
        
        # Process embedding results
        for i, result in enumerate(embedding_results):
            key = result.get('hotel_id') or result.get('review_id')
            # For non-hotel/review results, use index as key
            if not key:
                key = f"other_emb_{i}"
            if key:
                if key in seen:
                    # Duplicate found - combine scores
                    existing = seen[key]
                    # Weighted average: baseline 0.6, embedding 0.4
                    baseline_score = existing.get('relevance_score', 1.0)
                    embedding_score = result.get('similarity_score', result.get('relevance_score', 0.5))
                    combined_score = (baseline_score * 0.6) + (embedding_score * 0.4)
                    existing['relevance_score'] = combined_score
                    existing['source'] = 'hybrid'
                else:
                    # New result from embedding
                    result['source'] = 'embedding'
                    result['relevance_score'] = result.get('similarity_score', result.get('relevance_score', 0.5))
                    seen[key] = result
        
        return list(seen.values())
    
    def _rank_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank results by relevance score
        
        Args:
            results: List of results
            
        Returns:
            Sorted list by relevance_score descending
        """
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format results into context string for LLM
        
        Args:
            results: Ranked results
            
        Returns:
            Formatted context string (max ~2500 tokens)
        """
        if not results:
            return "No results found."
        
        context_parts = []
        current_chars = 0
        
        # Separate hotels, reviews, and other results (visa, general data)
        hotels = [r for r in results if 'hotel_name' in r or 'hotel_id' in r]
        reviews = [r for r in results if 'review_text' in r or 'review_id' in r]
        other_results = [r for r in results if r not in hotels and r not in reviews]
        
        # Format other results first (visa questions, general queries)
        if other_results:
            for i, result in enumerate(other_results, 1):
                other_text = self._format_other_result(result, i)
                if current_chars + len(other_text) > self.max_chars:
                    break
                context_parts.append(other_text)
                current_chars += len(other_text)
        
        # Format hotels
        if hotels and current_chars < self.max_chars:
            context_parts.append("=== HOTELS ===\n")
            for i, hotel in enumerate(hotels, 1):
                hotel_text = self._format_hotel(hotel, i)
                if current_chars + len(hotel_text) > self.max_chars:
                    break
                context_parts.append(hotel_text)
                current_chars += len(hotel_text)
        
        # Format reviews
        if reviews and current_chars < self.max_chars:
            context_parts.append("\n=== REVIEWS ===\n")
            for i, review in enumerate(reviews, 1):
                review_text = self._format_review(review, i)
                if current_chars + len(review_text) > self.max_chars:
                    break
                context_parts.append(review_text)
                current_chars += len(review_text)
        
        return "".join(context_parts)
    
    def _format_hotel(self, hotel: Dict[str, Any], index: int) -> str:
        """Format a single hotel result"""
        name = hotel.get('hotel_name', 'Unknown Hotel')
        city = hotel.get('city', '')
        country = hotel.get('country', '')
        star_rating = hotel.get('star_rating', '')
        avg_score = hotel.get('avg_score', hotel.get('average_reviews_score', ''))
        relevance = hotel.get('relevance_score', 0)
        
        location = f"{city}, {country}" if city and country else city or country or "Location unknown"
        
        text = f"{index}. {name}\n"
        text += f"   Location: {location}\n"
        if star_rating:
            text += f"   Star Rating: {star_rating}\n"
        if avg_score:
            text += f"   Average Score: {avg_score:.2f}\n" if isinstance(avg_score, (int, float)) else f"   Average Score: {avg_score}\n"
        text += f"   Relevance: {relevance:.2f}\n"
        
        # Add quality scores if available (prioritize dynamic scores from reviews)
        scores = []
        
        # Dynamic scores from Review aggregations (preferred)
        if 'avg_cleanliness' in hotel:
            scores.append(f"Cleanliness: {hotel['avg_cleanliness']:.2f}")
        elif 'cleanliness_base' in hotel:
            scores.append(f"Cleanliness: {hotel['cleanliness_base']}")
        
        if 'avg_comfort' in hotel:
            scores.append(f"Comfort: {hotel['avg_comfort']:.2f}")
        elif 'comfort_base' in hotel:
            scores.append(f"Comfort: {hotel['comfort_base']}")
        
        if 'avg_value' in hotel:
            scores.append(f"Value: {hotel['avg_value']:.2f}")
        elif 'value_for_money_base' in hotel:
            scores.append(f"Value: {hotel['value_for_money_base']}")
        
        if 'avg_staff_score' in hotel:
            scores.append(f"Staff: {hotel['avg_staff_score']:.2f}")
        elif 'staff_base' in hotel:
            scores.append(f"Staff: {hotel['staff_base']}")
        
        if 'avg_location_score' in hotel:
            scores.append(f"Location: {hotel['avg_location_score']:.2f}")
        elif 'location_base' in hotel:
            scores.append(f"Location: {hotel['location_base']}")
        
        if 'avg_facilities' in hotel:
            scores.append(f"Facilities: {hotel['avg_facilities']:.2f}")
        elif 'facilities_base' in hotel:
            scores.append(f"Facilities: {hotel['facilities_base']}")
        
        if 'avg_rating' in hotel:
            scores.append(f"Overall Rating: {hotel['avg_rating']:.2f}")
        
        if scores:
            text += f"   Scores: {', '.join(scores)}\n"
        
        if 'review_count' in hotel:
            text += f"   Reviews: {hotel['review_count']}"
            if 'traveller_type' in hotel:
                text += f" (by {hotel['traveller_type']} travellers)"
            text += "\n"
        
        text += "\n"
        return text
    
    def _format_review(self, review: Dict[str, Any], index: int) -> str:
        """Format a single review result"""
        review_text = review.get('review_text', review.get('text', 'No review text'))
        hotel_name = review.get('hotel_name', 'Unknown Hotel')
        score = review.get('score_overall', review.get('score', ''))
        relevance = review.get('relevance_score', 0)
        
        text = f"{index}. Review for {hotel_name}\n"
        if score:
            text += f"   Score: {score}\n"
        text += f"   Relevance: {relevance:.2f}\n"
        text += f"   Text: {review_text[:200]}{'...' if len(review_text) > 200 else ''}\n\n"
        
        return text
    
    def _format_other_result(self, result: Dict[str, Any], index: int) -> str:
        """Format non-hotel, non-review results (visa, general queries, etc.)"""
        text = ""
        
        # Check for traveller count without visa (Query11) - check this FIRST as it has all 3 fields
        if 'from_country' in result and 'to_country' in result and 'traveller_count' in result:
            from_country = result.get('from_country', 'Unknown')
            to_country = result.get('to_country', 'Unknown')
            count = result.get('traveller_count', 0)
            
            text = f"{index}. TRAVELLER STATISTICS\n"
            text += f"   From: {from_country}\n"
            text += f"   Destination: {to_country}\n"
            text += f"   Travellers (no visa required): {count}\n"
            text += "\n"
        # Check for visa-specific fields (Query10)
        elif 'from_country' in result and 'to_country' in result:
            from_country = result.get('from_country', 'Unknown')
            to_country = result.get('to_country', 'Unknown')
            visa_required = result.get('visa_required', False)
            visa_type = result.get('visa_type', 'Not specified')
            
            text = f"{index}. VISA INFORMATION\n"
            text += f"   From: {from_country}\n"
            text += f"   To: {to_country}\n"
            text += f"   Visa Required: {'Yes' if visa_required else 'No'}\n"
            if visa_required and visa_type and visa_type != 'Not specified':
                text += f"   Visa Type: {visa_type}\n"
            text += "\n"
        else:
            # Generic formatting for other types of results
            text = f"=== QUERY RESULT {index} ===\n\n"
            for key, value in result.items():
                if key not in ['source', 'relevance_score']:
                    text += f"{key.replace('_', ' ').title()}: {value}\n"
            text += "\n"
        
        return text


if __name__ == "__main__":
    # Test result merger
    merger = ResultMerger()
    
    print("=== Result Merger Test ===\n")
    print(f"Max context tokens: {merger.max_context_tokens}")
    print(f"Max chars: {merger.max_chars}\n")
    
    # Mock baseline results
    baseline = [
        {
            'hotel_id': 'h1',
            'hotel_name': 'Hotel Paris',
            'city': 'Paris',
            'country': 'France',
            'star_rating': 4,
            'avg_score': 8.5,
            'relevance_score': 1.0
        },
        {
            'hotel_id': 'h2',
            'hotel_name': 'London Inn',
            'city': 'London',
            'country': 'UK',
            'star_rating': 3,
            'avg_score': 7.8,
            'relevance_score': 0.9
        }
    ]
    
    # Mock embedding results (h1 overlaps)
    embedding = [
        {
            'hotel_id': 'h1',
            'hotel_name': 'Hotel Paris',
            'city': 'Paris',
            'country': 'France',
            'star_rating': 4,
            'avg_score': 8.5,
            'similarity_score': 0.92
        },
        {
            'hotel_id': 'h3',
            'hotel_name': 'Berlin Hotel',
            'city': 'Berlin',
            'country': 'Germany',
            'star_rating': 5,
            'avg_score': 9.0,
            'similarity_score': 0.85
        }
    ]
    
    context = merger.merge(baseline, embedding)
    print("Merged Context:")
    print(context)
