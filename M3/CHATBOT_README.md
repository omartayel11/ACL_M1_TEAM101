# 🏨 Hotel Travel Assistant Chatbot

## LangGraph-Native Conversational AI with Memory

Full-featured chatbot using LangGraph's native memory system (`MemorySaver`) for persistent conversation state across multiple turns.

---

## ✅ **What's Implemented**

### Core Features:
- ✅ **LangGraph Native Memory** - Uses `MemorySaver` with thread-based checkpointing
- ✅ **4 Workflow Modes** - baseline_only, embedding_only, hybrid, llm_pipeline
- ✅ **Query Rewriting** - Resolves references like "there", "that hotel" using conversation context
- ✅ **Conversation History** - Maintains full chat history with metadata
- ✅ **Thread Management** - Each conversation has a unique thread_id
- ✅ **Session Export/Import** - Save and restore conversations
- ✅ **Context-Aware Responses** - LLM sees recent conversation history

### Components:
1. **`chatbot.py`** - Main chatbot class with LangGraph memory
2. **`components/conversation_manager.py`** - Conversation history management
3. **`components/query_rewriter.py`** - Resolve references using LLM
4. **`workflows/workflow_factory.py`** - Workflow selection with memory support

---

## 🚀 **Quick Start**

### Interactive Chat (CLI):
```bash
python chatbot.py
```

### Programmatic Usage:
```python
from chatbot import HotelChatbot

# Create chatbot with workflow
bot = HotelChatbot(workflow_mode="hybrid")

# Chat
response = bot.chat("Find luxury hotels in Paris")
print(response['answer'])

# Follow-up (automatic context resolution)
response = bot.chat("What about 5-star hotels there?")
# "there" automatically resolves to "Paris"
print(response['answer'])

# Check history
history = bot.get_conversation_history()
print(f"Messages: {len(history)}")

# Export session
session_data = bot.export_session()

# Clear and start fresh
bot.clear_history()
```

---

## 📊 **Workflow Modes**

| Workflow | Description | Speed | Quality | Use Case |
|----------|-------------|-------|---------|----------|
| `baseline_only` | Intent → Entity → Cypher | ⚡ Fast | Good | Structured queries |
| `embedding_only` | Semantic vector search | ⚡ Fast | Better | Natural language |
| `hybrid` | Parallel baseline + embedding | 🐢 Slow | **Best** | Maximum accuracy |
| `llm_pipeline` | LLM generates Cypher | 🐢 Slowest | Variable | Full autonomy |

---

## 💬 **Query Rewriting Examples**

The chatbot automatically resolves references using conversation context:

```python
bot.chat("Find hotels in Tokyo")
# Next query:
bot.chat("What about luxury hotels there?")
# Rewrites to: "What about luxury hotels in Tokyo?"

bot.chat("Show me The Ritz Paris")
# Next query:
bot.chat("What are the reviews for that hotel?")
# Rewrites to: "What are the reviews for The Ritz Paris?"
```

---

## 🔧 **Advanced Features**

### Switch Workflows Mid-Conversation:
```python
bot = HotelChatbot(workflow_mode="embedding_only")
bot.chat("Find hotels in Rome")

# Switch to hybrid for better results
bot.switch_workflow("hybrid")
bot.chat("Show me 5-star hotels there")
```

### Export/Import Sessions:
```python
# Export
session = bot.export_session()
with open("session.json", "w") as f:
    json.dump(session, f)

# Import later
with open("session.json", "r") as f:
    session = json.load(f)
bot.import_session(session)
```

### Get LangGraph Thread State:
```python
state = bot.get_thread_state()
print(f"Thread ID: {bot.thread_id}")
print(f"Messages: {len(bot.message_history)}")
```

---

## 🧪 **Testing**

### Run Tests:
```bash
# Test chatbot functionality
python test_chatbot.py

# Test individual components
python components/conversation_manager.py
python components/query_rewriter.py

# Test workflows directly
python test_embedding_workflow.py
python -m workflows.baseline_workflow
```

---

## 🏗️ **Architecture**

```
User Query
    ↓
Query Rewriter (resolve "it", "there", etc.)
    ↓
LangGraph Workflow (with MemorySaver)
    ↓
    ├─ Intent Classification
    ├─ Entity Extraction
    ├─ Cypher Query / Vector Search
    ├─ Result Merging
    └─ LLM Answer Generation (with chat history)
    ↓
Response + Update History
    ↓
Store in MemorySaver (thread_id)
```

---

## 📝 **Configuration**

Edit `config.yaml`:
```yaml
retrieval:
  embedding:
    similarity_threshold: 0.3  # Lower = more results
    max_results: 10

llm:
  temperature: 0.7
  max_tokens: 500
```

---

## 🔮 **Next Steps**

1. ✅ **Chatbot with LangGraph Memory** - ✅ DONE
2. ⏳ **Streamlit UI** - Use chatbot in web interface
3. ⏳ **Evaluation Framework** - Compare workflow performance

---

## 📚 **References**

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Memory/Persistence**: https://langchain-ai.github.io/langgraph/how-tos/persistence/
- **Checkpointing**: https://langchain-ai.github.io/langgraph/how-tos/persistence_postgres/
