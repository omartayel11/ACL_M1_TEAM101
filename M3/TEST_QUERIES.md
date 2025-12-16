# Test Queries for Chatbot - All Query Types

This document contains comprehensive test queries for all active queries in query_library.py.

## Query 1: Hotels by City
**Purpose**: Get all hotels in a specific city with their ratings
**Test Queries**:
1. "show me hotels in paris"
2. "what hotels are in london?"
3. "find hotels in tokyo"
4. "hotels in new york"

**Expected**: Returns all hotels in the specified city with ratings and location info

---

## Query 2: Hotels by Country
**Purpose**: Get all hotels in a specific country
**Test Queries**:
1. "show me hotels in france"
2. "what hotels are in japan?"
3. "find hotels in united states"
4. "hotels in italy"

**Expected**: Returns all hotels in the specified country ordered by rating

---

## Query 3: Hotels by Rating Threshold
**Purpose**: Get hotels with average review score above a threshold
**Test Queries**:
1. "show me hotels with rating above 8"
2. "find hotels with at least 9 rating"
3. "hotels with minimum rating 8.5"

**Expected**: Returns hotels with average review score above the specified threshold

---

## Query 5: Top Hotels for Traveller Type
**Purpose**: Get top-rated hotels based on reviews from specific traveller type
**Test Queries**:
1. "best hotels for business travelers"
2. "top hotels for families"
3. "which hotels are best for couples?"
4. "show me hotels for solo travelers"

**Expected**: Returns top hotels rated by the specified traveller type

---

## Query 6: Hotels by Cleanliness Score
**Purpose**: Get hotels with high cleanliness scores
**Test Queries**:
1. "show me the cleanest hotels"
2. "find hotels with high cleanliness"
3. "which hotels have best cleanliness scores?"
4. "hotels with cleanliness above 8.5"

**Expected**: Returns hotels with high cleanliness scores from reviews

---

## Query 7: Reviews by Hotel Name
**Purpose**: Get recent reviews for a specific hotel
**Test Queries**:
1. "show me reviews for the ritz"
2. "what do people say about hilton?"
3. "find reviews for marriott"
4. "reviews for four seasons"

**Expected**: Returns recent reviews for the specified hotel with detailed scores

---

## Query 9: Hotels with Best Location Scores
**Purpose**: Get hotels with highest location scores
**Test Queries**:
1. "which hotels have the best location?"
2. "find hotels with excellent location in paris" \\ the intent is hotelSearch
3. "show me hotels with best location scores"
4. "hotels with great location in london"

**Expected**: Returns hotels with highest location scores, optionally filtered by city

---

## Query 10: Check Visa Requirements
**Purpose**: Check if visa is required between two countries
**Test Queries**:
1. "do i need a visa from usa to france?"
2. "visa requirements from india to japan"
3. "is visa required from brazil to germany?"
4. "check visa from canada to united kingdom"

**Expected**: Returns visa requirement status between the two countries
---

## Query 12: Hotels by Comfort Score
**Purpose**: Get hotels with high comfort scores from reviews
**Test Queries**:
1. "show me the most comfortable hotels"
2. "find hotels with excellent comfort"
3. "which hotels have best comfort scores?"
4. "hotels with comfort above 8"

**Expected**: Returns hotels with high comfort scores ordered by rating

---

## Query 13: Hotels by Value for Money
**Purpose**: Get hotels with best value for money scores
**Test Queries**:
1. "show me hotels with good value for money"
2. "find affordable hotels with good quality"
3. "which hotels offer best value?"
4. "hotels with best value for money"

**Expected**: Returns hotels ranked by value-for-money scores

---

## Query 14: Hotels with Best Staff Scores
**Purpose**: Get hotels with highest staff service scores
**Test Queries**:
1. "which hotels have the best staff?"
2. "show me hotels with excellent service"
3. "find hotels with best staff ratings"
4. "hotels with great staff service"

**Expected**: Returns hotels ranked by staff service scores

---

## Query 15: Hotel Full Details
**Purpose**: Get comprehensive details about a specific hotel
**Test Queries**:
1. "tell me everything about the ritz"
2. "full details for hilton hotel"
3. "give me complete information about marriott"
4. "show me all details for four seasons"

**Expected**: Returns comprehensive hotel details including all quality dimensions

---

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
**Purpose**: Recommend hotels based on specific traveler type in a city
**Test Queries**:
1. "best hotels for families in london?"
2. "top hotels for business travelers in new york"
3. "which hotels are best for couples visiting tokyo?"
4. "if i want to go to paris, should i go solo or as a couple?"

**Expected**: Returns top hotels for the specified traveler type in the city

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

## Quick Validation Test

Run this sequence to verify all active query types work:

```
1. "show me hotels in paris" → Query 1 (Hotels by city)
2. "show me hotels in france" → Query 2 (Hotels by country)
3. "hotels with rating above 8" → Query 3 (Rating threshold)
4. "best hotels for business travelers" → Query 5 (Traveller type)
5. "show me the cleanest hotels" → Query 6 (Cleanliness)
6. "show me reviews for the ritz" → Query 7 (Reviews by name)
7. "which hotels have the best location?" → Query 9 (Location scores)
8. "do i need a visa from usa to france?" → Query 10 (Visa requirements)
9. "show me the most comfortable hotels" → Query 12 (Comfort)
10. "hotels with good value for money" → Query 13 (Value)
11. "which hotels have the best staff?" → Query 14 (Staff scores)
12. "tell me everything about the ritz" → Query 15 (Full details)
13. "show me clean comfortable hotels with good staff in paris" → Query 16 (Multi-criteria)
14. "best hotels for families in london?" → Query 17 (Traveler type in city)
15. "what hotels balance all the scores?" → Query 18 (Balanced quality)
16. "which hotels are popular among travellers from france?" → Query 19 (Traveler origin)
```

All 16 active queries should return results through the chatbot interface.
