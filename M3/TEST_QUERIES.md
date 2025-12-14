# Test Queries for Chatbot - Complex Query Types

This document contains test queries to verify that all 8 new complex queries are working correctly through the chatbot.

## Query 16: Multi-Criteria Filtering
**Purpose**: Filter hotels by multiple quality dimensions simultaneously
**Test Queries**:
1. "show me hotels with cleanliness more than 8 and comfort more than 9 in paris"
2. "find clean and comfortable hotels with good staff in london"
3. "show me hotels with cleanliness above 8.5 and comfort above 8.5 and value above 8 in tokyo"
4. "what hotels have high cleanliness and comfort scores in berlin?"

**Expected**: Returns hotels matching ALL quality criteria, ordered by overall rating

---

## Query 17: Comparative Analysis by Traveler Type in City
**Purpose**: Recommend hotels based on specific traveler type
**Test Queries**:
1. "if i want to go to paris, should i go solo or as a couple?"
2. "best hotels for families in london?"
3. "top hotels for business travelers in new york"
4. "which hotels are best for couples visiting tokyo?"

**Expected**: Returns top hotels for the specified traveler type, optionally filtered by city

---

## Query 18: Balanced Quality Scores
**Purpose**: Find hotels with consistent high scores across all dimensions
**Test Queries**:
1. "what hotels balance all the scores?"
2. "show me hotels with balanced quality across all dimensions"
3. "find hotels with consistent high ratings"
4. "which hotels have well-rounded scores across cleanliness, comfort, staff and value?"

**Expected**: Returns hotels where quality scores are balanced (low variance) across dimensions

---

## Query 19: Hotels by Traveler Origin Patterns
**Purpose**: Find hotels popular among travelers from a specific country
**Test Queries**:
1. "which hotels are popular among travellers from france?"
2. "what hotels do japanese travelers prefer?"
3. "which hotels are most popular among travelers from brazil?"
4. "show me hotels that are favorite destinations for travelers from canada"

**Expected**: Returns hotels popular among travelers from the specified country

---

## Query 20: Similar Hotels to Reference
**Purpose**: Find hotels with similar quality profiles to a reference hotel
**Test Queries**:
1. "find hotels similar to the ritz"
2. "show me hotels like the hilton"
3. "what hotels are comparable to the marriott?"
4. "find hotels similar to four seasons in terms of quality"

**Expected**: Returns hotels with similar quality profile (cleanliness, comfort, staff, value scores)

---

## Query 21: Hotels with Specialist Strength
**Purpose**: Find hotels that excel in specific quality dimensions
**Test Queries**:
1. "which hotels have the best cleanliness scores?"
2. "show me hotels with excellent comfort scores"
3. "find hotels with the highest staff service ratings"
4. "what are the best value for money hotels?"

**Expected**: Returns hotels ranked by the specified quality dimension

---

## Query 22: Hotels Trending Up (DISABLED)
**Status**: ❌ DISABLED - Cypher syntax error (avg() doesn't work on lists in Neo4j)
**Purpose**: Find hotels with improving review scores over time
**Test Queries**:
1. ~~"hotels with improving review scores"~~
2. ~~"which hotels are getting better?"~~
3. ~~"show me hotels that are trending up"~~
4. ~~"find hotels with the most improvement in ratings"~~

**Expected**: ~~Returns hotels showing recent improvement (newer reviews higher than base rating)~~

---

## Query 23: Best Value Hotels
**Purpose**: Find hotels with the best value for money
**Test Queries**:
1. "what are the best value hotels?"
2. "find affordable hotels with good quality"
3. "show me hotels with best value for money"
4. "which hotels offer the best bang for the buck?"

**Expected**: Returns hotels ranked by value-for-money score

---

## Quick Validation Test

Run this sequence to verify all query types work:

```
1. "show me clean comfortable hotels with good staff in paris" → Query 16 (Multi-criteria)
2. "if i want to go to paris, should i go solo or as a couple?" → Query 17 (Traveler type)
3. "what hotels balance all the scores?" → Query 18 (Balanced quality)
4. "which hotels are popular among travellers from france?" → Query 19 (Traveler origin)
5. "find hotels similar to the ritz" → Query 20 (Similar hotels)
6. "which hotels have the best cleanliness scores?" → Query 21 (Specialist strength)
7. ❌ Query 22 DISABLED (Trending up - Cypher error)
8. "what are the best value hotels?" → Query 23 (Best value)
```

7 of 8 queries should return results through the chatbot interface.
Query 22 is disabled due to a Cypher syntax limitation.
