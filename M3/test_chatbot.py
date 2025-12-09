"""
Quick test of the LangGraph-native chatbot
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chatbot import HotelChatbot

# Create chatbot
print("Creating chatbot...")
bot = HotelChatbot(workflow_mode="embedding_only")

# Test conversation
print("\n" + "="*60)
print("TEST 1: Initial query")
response1 = bot.chat("Find luxury hotels in Dubai")
print(f"\nResponse: {response1['answer'][:200]}...")
print(f"Results: {response1['result_count']}")

print("\n" + "="*60)
print("TEST 2: Follow-up with reference (should use query rewriting)")
response2 = bot.chat("What about 5-star hotels there?")
print(f"\nResponse: {response2['answer'][:200]}...")
print(f"Results: {response2['result_count']}")

print("\n" + "="*60)
print("TEST 3: Check conversation history")
history = bot.get_conversation_history()
print(f"Total messages: {len(history)}")
for i, msg in enumerate(history, 1):
    print(f"{i}. {msg['role']}: {msg['content'][:60]}...")

print("\n✓ Chatbot test complete!")
