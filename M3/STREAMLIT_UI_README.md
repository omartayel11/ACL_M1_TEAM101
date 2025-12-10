# 🏨 Hotel Travel Assistant - Streamlit UI

## Overview

Modern, futuristic Streamlit interface for the Graph-RAG Hotel Travel Assistant. Features a luxury hotel-themed design with a split-screen layout: main chat interface and developer console for real-time debugging.

## Features

### 🎨 User Interface
- **Modern Hotel Theme**: Luxury gold and deep blue color scheme
- **Responsive Layout**: Adapts to different screen sizes
- **Split-Screen Mode**: Chat interface + Developer console
- **Smooth Animations**: Button hover effects and transitions
- **Intuitive Controls**: Easy-to-use sidebar with all settings

### 💬 Chat Features
- **Multi-turn Conversations**: Full conversation memory with LangGraph
- **5 Workflow Modes**:
  1. **Baseline Only** (🔍): Structured Cypher queries only
  2. **Embedding Only** (🧠): Semantic search only
  3. **Hybrid** (⚡): Both baseline + embeddings
  4. **LLM Pipeline** (🤖): Full LLM autonomy (generates Cypher)
  5. **Conversational Hybrid** (💬): Memory + query rewriting + hybrid retrieval
- **Real-time Response Details**: Intent, entities, result count
- **Message History**: Persistent within session
- **Quick Actions**: Clear chat, export session

### 👨‍💻 Developer Console
- **Real-time Logs**: See all system activity as it happens
- **Color-coded Messages**:
  - 🟢 SUCCESS: Successful operations
  - 🔴 ERROR: Error messages
  - 🟡 USER: User queries
  - 🔵 SYSTEM: System events
  - ⚪ OUTPUT: Workflow outputs
- **Scrollable History**: Last 50 log entries
- **Timestamp Tracking**: Millisecond precision
- **Toggle On/Off**: Hide console for distraction-free chat

### 🤖 Model Selection
- **LLM Models**: Switch between available Groq models
  - GPT-OSS 120B (default)
  - Llama 4 Maverick 17B
  - Qwen 3 32B
- **Embedding Models**: Switch semantic search models
  - MiniLM L6 v2 (384D, fast)
  - MPNet Base v2 (768D, higher quality)
- **Auto-regeneration**: Embeddings rebuild when switching models

### 📊 Session Statistics
- Message count
- Thread ID (for debugging)
- Last query result count
- Current workflow/model info

## Installation

### Prerequisites
```bash
# Install all dependencies
pip install -r requirements.txt
```

### Environment Setup
1. Copy `.env.example` to `.env`
2. Add your Groq API key:
```
GROQ_API_KEY=your_key_here
```

3. Ensure Neo4j is running with hotel data
4. Generate embeddings (first time only):
```bash
python create_embeddings.py
```

## Running the UI

### Start the Application
```bash
streamlit run streamlit_app.py
```

The app will open automatically at `http://localhost:8501`

### Command Line Options
```bash
# Custom port
streamlit run streamlit_app.py --server.port 8080

# Custom theme
streamlit run streamlit_app.py --theme.base dark

# Disable file watcher (for production)
streamlit run streamlit_app.py --server.fileWatcherType none
```

## Usage Guide

### First Steps
1. **Select Workflow**: Choose from 5 workflows in the sidebar
2. **Choose Models**: Select LLM and embedding models
3. **Start Chatting**: Type your question in the chat input

### Example Queries
```
- Find hotels in Paris
- Best hotels for families
- Do I need a visa from USA to France?
- Hotels with high cleanliness scores
- Show me hotels in Dubai
- What's the best location score in London?
```

### Using the Developer Console
1. Toggle "Show Developer Console" in sidebar
2. Watch real-time logs as queries are processed
3. See:
   - Query rewriting
   - Intent classification
   - Entity extraction
   - Database retrieval
   - LLM generation
   - Errors and warnings

### Switching Models

#### LLM Model
1. Select new model from "LLM Model" dropdown
2. Change takes effect immediately
3. All future queries use new model

#### Embedding Model
1. Select new model from "Embedding Model" dropdown
2. Click "🔄 Regenerate Embeddings" button
3. Wait for regeneration (1-2 minutes)
4. New embeddings are used automatically

### Session Management
- **Clear Chat**: Reset conversation history (new thread)
- **Clear Logs**: Empty developer console
- **Export Session**: Save conversation (future feature)

## Architecture

### File Structure
```
M3/
├── streamlit_app.py          # Main UI application
├── chatbot.py                 # Chatbot logic (used by UI)
├── config.yaml                # Configuration
├── create_embeddings.py       # Embedding generation
├── components/                # Core components
│   ├── intent_classifier.py
│   ├── entity_extractor.py
│   ├── query_builder.py
│   ├── vector_searcher.py
│   └── result_merger.py
├── nodes/                     # LangGraph nodes
│   ├── intent_node.py
│   ├── entity_node.py
│   ├── baseline_query_node.py
│   ├── embedding_query_node.py
│   └── answer_node.py
├── workflows/                 # LangGraph workflows
│   ├── baseline_workflow.py
│   ├── embedding_workflow.py
│   ├── hybrid_workflow.py
│   ├── llm_pipeline_workflow.py
│   └── conversational_hybrid_workflow.py
└── utils/                     # Utilities
    ├── llm_client.py
    ├── embedding_client.py
    ├── neo4j_client.py
    └── config_loader.py
```

### Workflow Execution
1. User types query in UI
2. Query sent to `process_query()` function
3. LangGraph workflow invoked with memory
4. Nodes execute in sequence/parallel:
   - Intent classification
   - Entity extraction
   - Retrieval (baseline/embedding/both)
   - Result merging
   - Answer generation
5. Response displayed in chat
6. All outputs logged to developer console

### State Management
- **Session State**: Streamlit's `st.session_state`
  - Messages: Chat history
  - Thread ID: LangGraph conversation thread
  - Memory: LangGraph MemorySaver
  - Workflow: Current workflow instance
  - Models: Current LLM/embedding models
  - Logs: Developer console entries
- **LangGraph State**: Conversation checkpoints
  - Query rewriting context
  - Chat history
  - Intent/entities
  - Results

## Customization

### Theme Colors
Edit CSS in `streamlit_app.py`:
```python
--hotel-gold: #D4AF37    # Primary accent
--hotel-blue: #1B2838    # Background
--hotel-silver: #C0C0C0  # Secondary
--hotel-cream: #F5F5DC   # Text highlights
```

### Default Settings
Edit `config.yaml`:
```yaml
llm:
  default_model: "openai/gpt-oss-120b"
  temperature: 0.7
  max_tokens: 500

embedding:
  default_model: "all-MiniLM-L6-v2"
  similarity_threshold: 0.3
```

### Adding New Models
1. Add to `config.yaml`:
```yaml
llm:
  available_models:
    - name: "new-model-name"
      display_name: "Model Display Name"
      description: "Model description"
```

2. Restart Streamlit app

## Troubleshooting

### Port Already in Use
```bash
# Kill existing process
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run streamlit_app.py --server.port 8502
```

### Embeddings Not Found
```bash
# Regenerate embeddings
python create_embeddings.py

# Check files exist
ls hotel_embeddings.faiss
ls hotel_id_mapping.json
```

### Neo4j Connection Error
1. Check Neo4j is running: `http://localhost:7474`
2. Verify `config.txt` has correct credentials
3. Test connection: `python test_neo4j_hotels.py`

### LLM API Errors
1. Check `.env` has valid `GROQ_API_KEY`
2. Verify API key at: https://console.groq.com
3. Check rate limits

### Developer Console Not Showing Logs
1. Toggle console off and on again
2. Clear logs and rerun query
3. Check `capture_output_as_log()` function

## Performance Tips

### Faster Response Times
1. Use **baseline_only** workflow (no embeddings)
2. Select faster LLM model (Qwen 3 32B)
3. Reduce `max_tokens` in config
4. Lower similarity threshold (fewer embedding results)

### Better Answer Quality
1. Use **conversational_hybrid** workflow
2. Select larger LLM model (GPT-OSS 120B)
3. Use MPNet embeddings (768D)
4. Increase `max_tokens` to 1000

### Memory Management
1. Clear chat history regularly
2. Keep developer logs under 100 entries
3. Use `clear_logs` button when console gets full

## Known Limitations

1. **Embedding Regeneration**: Takes 1-2 minutes for full rebuild
2. **Session Persistence**: Chat history cleared on page refresh
3. **Concurrent Users**: Single memory instance (use different ports for multiple users)
4. **Large Results**: UI may slow with >50 results
5. **Model Switching**: LLM switch is immediate, embeddings require rebuild

## Future Enhancements

- [ ] Session export/import (save conversations)
- [ ] Multi-user support with separate threads
- [ ] Graph visualization (Neo4j results)
- [ ] Result filtering UI
- [ ] Query suggestions
- [ ] Voice input
- [ ] Dark/light theme toggle
- [ ] Mobile responsive design
- [ ] Analytics dashboard
- [ ] A/B testing for workflows

## Support

For issues or questions:
1. Check developer console for error logs
2. Review `IMPLEMENTATION_STATUS.md`
3. Test with `test_chatbot.py` to isolate UI vs. logic issues
4. Verify all dependencies are installed

## License

Part of ACL M1 TEAM101 project.
