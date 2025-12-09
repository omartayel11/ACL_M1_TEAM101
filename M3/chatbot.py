"""
Full-Featured Chatbot for Graph-RAG Hotel Travel Assistant
Handles multi-turn conversations using LangGraph's native memory
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import uuid

# Add M3 to path
sys.path.insert(0, str(Path(__file__).parent))

from langgraph.checkpoint.memory import MemorySaver
from workflows.workflow_factory import get_workflow_with_memory, get_workflow, list_workflows
from utils.config_loader import ConfigLoader


class HotelChatbot:
    """
    Full-featured chatbot with LangGraph native conversation memory
    Uses MemorySaver for persistent conversation state
    """
    
    def __init__(
        self,
        workflow_mode: str = "conversational_hybrid",  # Changed default!
        thread_id: Optional[str] = None
    ):
        """
        Initialize chatbot with LangGraph memory
        
        Args:
            workflow_mode: Workflow to use (baseline_only, embedding_only, hybrid, conversational_hybrid, llm_pipeline)
            thread_id: Conversation thread ID (generates new if None)
        """
        self.config = ConfigLoader()
        self.workflow_mode = workflow_mode
        self.thread_id = thread_id or str(uuid.uuid4())
        
        # LangGraph memory saver
        self.memory = MemorySaver()
        
        # Get workflow with memory
        self.workflow = get_workflow_with_memory(workflow_mode, self.memory)
        
        # Track conversation locally for quick access
        self.message_history: List[Dict[str, Any]] = []
        
        print(f"✓ Chatbot initialized with workflow: {workflow_mode}")
        print(f"✓ Thread ID: {self.thread_id}")
        if workflow_mode == "conversational_hybrid":
            print(f"✓ Full conversation support (query rewriting + chat history)")
    
    def chat(self, user_query: str) -> Dict[str, Any]:
        """
        Process user query using LangGraph with memory
        
        Args:
            user_query: User's question or request
            
        Returns:
            Response dictionary with answer, results, and metadata
        """
        print(f"\n{'='*60}")
        print(f"User: {user_query}")
        print(f"{'='*60}")
        
        # Execute workflow with LangGraph memory (query rewriting handled inside workflow)
        try:
            initial_state = {
                "user_query": user_query,
                "intent": None,
                "entities": {},
                "baseline_results": [],
                "embedding_results": [],
                "llm_query_results": [],
                "merged_context": "",
                "llm_response": "",
                "chat_history": self.message_history.copy(),
                "error": None,
                "metadata": {}
            }
            
            # LangGraph config with thread_id for memory
            config = {
                "configurable": {
                    "thread_id": self.thread_id
                }
            }
            
            # Invoke workflow with memory checkpointing
            result = self.workflow.invoke(initial_state, config)
            
            # Step 3: Extract results and format response
            response = self._format_response(result, user_query)
            
            # Step 4: Update local message history
            self.message_history.append({
                "role": "user",
                "content": user_query,
                "metadata": {
                    "intent": result.get("intent"),
                    "entities": result.get("entities", {}),
                    "workflow": self.workflow_mode,
                    "query_rewritten": result.get("metadata", {}).get("query_rewritten", False)
                }
            })
            
            self.message_history.append({
                "role": "assistant",
                "content": response["answer"],
                "metadata": {
                    "workflow": self.workflow_mode,
                    "result_count": response.get("result_count", 0),
                    "intent": result.get("intent")
                }
            })
            
            return response
            
        except Exception as e:
            error_msg = f"I encountered an error processing your request: {str(e)}"
            print(f"❌ Error: {error_msg}")
            
            self.message_history.append({"role": "user", "content": user_query, "metadata": {"error": str(e)}})
            self.message_history.append({"role": "assistant", "content": error_msg, "metadata": {"error": True}})
            
            return {
                "answer": error_msg,
                "error": str(e),
                "results": [],
                "result_count": 0
            }
    
    def _format_response(
        self,
        workflow_result: Dict[str, Any],
        original_query: str
    ) -> Dict[str, Any]:
        """
        Format workflow result into user-friendly response
        
        Args:
            workflow_result: Result from workflow execution
            original_query: Original user query
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "answer": "",
            "results": [],
            "result_count": 0,
            "workflow": self.workflow_mode,
            "intent": workflow_result.get("intent"),
            "entities": workflow_result.get("entities", {}),
            "metadata": workflow_result.get("metadata", {})
        }
        
        # Use LLM response from workflow (all workflows generate this)
        response["answer"] = workflow_result.get("llm_response", "I couldn't find any results for your query. Try rephrasing or using different criteria.")
        
        # Extract results based on workflow type
        if self.workflow_mode == "baseline_only":
            results = workflow_result.get("baseline_results", [])
            response["results"] = results
            response["result_count"] = len(results)
            
        elif self.workflow_mode == "embedding_only":
            results = workflow_result.get("embedding_results", [])
            response["results"] = results
            response["result_count"] = len(results)
            
        elif self.workflow_mode in ["hybrid", "conversational_hybrid"]:
            baseline_results = workflow_result.get("baseline_results", [])
            embedding_results = workflow_result.get("embedding_results", [])
            all_results = self._merge_results(baseline_results, embedding_results)
            response["results"] = all_results
            response["result_count"] = len(all_results)
            
        elif self.workflow_mode == "llm_pipeline":
            results = workflow_result.get("llm_query_results", [])
            response["results"] = results
            response["result_count"] = len(results)
        
        return response
    
    def _merge_results(self, baseline: List[Dict], embedding: List[Dict]) -> List[Dict]:
        """
        Merge and deduplicate results from baseline and embedding workflows
        
        Args:
            baseline: Results from baseline workflow
            embedding: Results from embedding workflow
            
        Returns:
            Merged list of unique results
        """
        seen_ids = set()
        merged = []
        
        # Add all baseline results first (prioritize structured queries)
        for result in baseline:
            result_id = result.get("hotel_id") or result.get("review_id")
            if result_id and result_id not in seen_ids:
                seen_ids.add(result_id)
                merged.append(result)
        
        # Add embedding results that aren't duplicates
        for result in embedding:
            result_id = result.get("hotel_id") or result.get("review_id")
            if result_id and result_id not in seen_ids:
                seen_ids.add(result_id)
                merged.append(result)
        
        return merged
    
    def switch_workflow(self, new_workflow: str):
        """
        Switch to a different workflow (creates new workflow with same memory)
        
        Args:
            new_workflow: Name of workflow to switch to
        """
        available = list_workflows()
        if new_workflow not in available:
            print(f"❌ Invalid workflow: {new_workflow}")
            print(f"Available workflows: {', '.join(available)}")
            return
        
        self.workflow_mode = new_workflow
        self.workflow = get_workflow_with_memory(new_workflow, self.memory)
        print(f"✓ Switched to workflow: {new_workflow}")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history"""
        return self.message_history.copy()
    
    def clear_history(self):
        """Clear conversation history and create new thread"""
        self.message_history = []
        self.thread_id = str(uuid.uuid4())
        self.memory = MemorySaver()
        self.workflow = get_workflow_with_memory(self.workflow_mode, self.memory)
        print(f"✓ Conversation history cleared (new thread: {self.thread_id})")
    
    def get_thread_state(self) -> Dict[str, Any]:
        """Get LangGraph checkpoint state for current thread"""
        config = {"configurable": {"thread_id": self.thread_id}}
        try:
            state = self.workflow.get_state(config)
            return state
        except Exception as e:
            print(f"Could not retrieve state: {e}")
            return {}
    
    def export_session(self) -> Dict[str, Any]:
        """Export session data for persistence"""
        return {
            "thread_id": self.thread_id,
            "workflow_mode": self.workflow_mode,
            "message_history": self.message_history,
            "message_count": len(self.message_history)
        }
    
    def import_session(self, data: Dict[str, Any]):
        """Import session data from saved file"""
        if "message_history" in data:
            self.message_history = data["message_history"]
        if "thread_id" in data:
            self.thread_id = data["thread_id"]
        if "workflow_mode" in data:
            self.workflow_mode = data["workflow_mode"]
            self.workflow = get_workflow_with_memory(self.workflow_mode, self.memory)
        print(f"✓ Imported session with {len(self.message_history)} messages")


def interactive_chat():
    """Run interactive chat session"""
    print("="*60)
    print("🏨 Hotel Travel Assistant Chatbot")
    print("="*60)
    print("\nAvailable workflows:")
    for i, wf in enumerate(list_workflows(), 1):
        print(f"  {i}. {wf}")
    
    workflow_choice = input("\nSelect workflow (1-5) or press Enter for conversational_hybrid: ").strip()
    workflow_map = {
        "1": "baseline_only",
        "2": "embedding_only",
        "3": "hybrid",
        "4": "llm_pipeline",
        "5": "conversational_hybrid"
    }
    workflow = workflow_map.get(workflow_choice, "conversational_hybrid")  # Changed default!
    
    chatbot = HotelChatbot(workflow_mode=workflow)
    
    print("\n" + "="*60)
    print("Chat started! Type 'quit' to exit, 'clear' to clear history")
    print("Type 'switch' to change workflow, 'history' to see chat history")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == "clear":
                chatbot.clear_history()
                continue
            
            if user_input.lower() == "switch":
                print("\nAvailable workflows:")
                for wf in list_workflows():
                    print(f"  - {wf}")
                new_wf = input("Enter workflow name: ").strip()
                chatbot.switch_workflow(new_wf)
                continue
            
            if user_input.lower() == "history":
                history = chatbot.get_conversation_history()
                print(f"\n--- Conversation History ({len(history)} messages) ---")
                for msg in history:
                    role = msg["role"].capitalize()
                    content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                    print(f"{role}: {content}")
                print("-" * 60)
                continue
            
            # Process query
            response = chatbot.chat(user_input)
            
            print(f"\n🤖 Assistant: {response['answer']}")
            print(f"\n📊 Results: {response['result_count']} | Workflow: {response['workflow']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    interactive_chat()
