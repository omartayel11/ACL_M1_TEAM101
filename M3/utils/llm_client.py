"""
LLM client for Graph-RAG Hotel Travel Assistant
Provides unified interface for LLM inference using Groq API
"""

import os
import json
from typing import Any, Dict, List, Optional
from groq import Groq
from dotenv import load_dotenv


class LLMClient:
    """
    Singleton LLM client using Groq API for fast inference.
    Supports text generation and structured output with multiple models.
    """
    
    _instance: Optional['LLMClient'] = None
    _client: Optional[Groq] = None
    _api_key: Optional[str] = None
    _model: str = "openai/gpt-oss-120b"  # Default fallback
    _temperature: float = 0.7
    _max_tokens: int = 500
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Initialize LLM client with Groq
        
        Args:
            model: Groq model name (if None, uses default from config)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        if self._client is None:
            # Load default model from config if not specified
            if model is None:
                from .config_loader import ConfigLoader
                config = ConfigLoader()
                model = config.get('llm.default_model', 'openai/gpt-oss-120b')
            
            self._model = model
            self._temperature = temperature
            self._max_tokens = max_tokens
            self._load_api_key()
            self._initialize_client()
    
    def _load_api_key(self):
        """Load Groq API key from environment"""
        # Load from .env file
        load_dotenv()
        
        # Try environment variable
        self._api_key = os.getenv('GROQ_API_KEY')
        
        if not self._api_key:
            print("Warning: GROQ_API_KEY not found in environment")
            print("Set GROQ_API_KEY in .env file or environment variables")
        else:
            print("✓ Groq API key loaded")
    
    def _initialize_client(self):
        """Initialize Groq client"""
        if not self._api_key:
            print("Warning: Cannot initialize Groq client - no API key")
            return
        
        try:
            self._client = Groq(api_key=self._api_key)
            print(f"✓ Groq client initialized (model: {self._model})")
        except Exception as e:
            print(f"✗ Failed to initialize Groq client: {e}")
            self._client = None
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        return_usage: bool = False
    ) -> str:
        """
        Generate text completion from prompt
        
        Args:
            prompt: User prompt/query
            temperature: Sampling temperature (overrides default)
            max_tokens: Max tokens in response (overrides default)
            system_prompt: Optional system message
            return_usage: If True, return tuple of (text, usage_dict)
            
        Returns:
            Generated text response, or (text, usage_dict) if return_usage=True
            
        Raises:
            RuntimeError: If client not initialized
            Exception: If API call fails
        """
        if self._client is None:
            raise RuntimeError("LLM client not initialized - check API key")
        
        temperature = temperature if temperature is not None else self._temperature
        max_tokens = max_tokens if max_tokens is not None else self._max_tokens
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            text = response.choices[0].message.content
            
            if return_usage:
                usage = {
                    'prompt_tokens': response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                    'completion_tokens': response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                    'total_tokens': response.usage.total_tokens if hasattr(response, 'usage') else 0,
                    'model': self._model
                }
                return text, usage
            
            return text
            
        except Exception as e:
            print(f"Error in LLM generation: {e}")
            raise
    
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON) from prompt
        
        Args:
            prompt: User prompt/query
            schema: JSON schema for expected output structure
            temperature: Sampling temperature
            system_prompt: Optional system message
            
        Returns:
            Parsed JSON object matching schema
            
        Example:
            >>> schema = {
            ...     "intent": "string",
            ...     "entities": {"city": "string", "min_rating": "number"}
            ... }
            >>> result = client.generate_structured(query, schema)
            >>> print(result['intent'])
        """
        if self._client is None:
            raise RuntimeError("LLM client not initialized - check API key")
        
        temperature = temperature if temperature is not None else self._temperature
        
        # Add JSON schema instruction to prompt
        schema_str = json.dumps(schema, indent=2)
        enhanced_prompt = f"{prompt}\n\nRespond ONLY with valid JSON matching this schema:\n{schema_str}"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": "You are a helpful assistant that always responds with valid JSON."
            })
        messages.append({"role": "user", "content": enhanced_prompt})
        
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=self._max_tokens
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON
            try:
                # Remove markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON response: {e}")
                print(f"Raw response: {content}")
                # Return empty dict matching schema keys
                return {key: None for key in schema.keys()}
                
        except Exception as e:
            print(f"Error in structured generation: {e}")
            raise
    
    def set_model(self, model: str):
        """Change the model used for generation"""
        self._model = model
        print(f"✓ Model changed to: {model}")
    
    def set_temperature(self, temperature: float):
        """Change the temperature for generation"""
        self._temperature = temperature
    
    def set_max_tokens(self, max_tokens: int):
        """Change max tokens for generation"""
        self._max_tokens = max_tokens
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            'model': self._model,
            'temperature': self._temperature,
            'max_tokens': self._max_tokens,
            'initialized': self._client is not None
        }
    
    @staticmethod
    def calculate_cost(usage: Dict[str, Any]) -> float:
        """
        Calculate estimated cost based on token usage
        
        Args:
            usage: Usage dict with prompt_tokens, completion_tokens, model
            
        Returns:
            Estimated cost in USD
            
        Note: Prices are approximate and based on Groq's pricing
        Groq offers free tier, so actual cost may be $0
        """
        # Groq pricing (as of Dec 2025, free tier available)
        # These are placeholder values - Groq offers generous free tier
        PRICING = {
            'openai/gpt-oss-120b': {'prompt': 0.0, 'completion': 0.0},  # Free tier
            'meta-llama/llama-4-maverick-17b-128e-instruct': {'prompt': 0.0, 'completion': 0.0},  # Free tier
            'qwen/qwen3-32b': {'prompt': 0.0, 'completion': 0.0},  # Free tier
            'default': {'prompt': 0.0, 'completion': 0.0}
        }
        
        model = usage.get('model', 'default')
        pricing = PRICING.get(model, PRICING['default'])
        
        prompt_cost = (usage.get('prompt_tokens', 0) / 1000000) * pricing['prompt']
        completion_cost = (usage.get('completion_tokens', 0) / 1000000) * pricing['completion']
        
        return prompt_cost + completion_cost
    
    @staticmethod
    def get_available_models() -> List[Dict[str, str]]:
        """
        Get list of available LLM models from config
        
        Returns:
            List of model dicts with name, display_name, description
        """
        from .config_loader import ConfigLoader
        config = ConfigLoader()
        return config.get('llm.available_models', [
            {
                'name': 'openai/gpt-oss-120b',
                'display_name': 'GPT-OSS 120B',
                'description': 'OpenAI open-source model'
            },
            {
                'name': 'meta-llama/llama-4-maverick-17b-128e-instruct',
                'display_name': 'Llama 4 Maverick 17B',
                'description': 'Meta Llama 4 instruction model'
            },
            {
                'name': 'qwen/qwen3-32b',
                'display_name': 'Qwen 3 32B',
                'description': 'Alibaba Qwen 3 model'
            }
        ])


# Convenience function for quick access
def get_llm_client() -> LLMClient:
    """Get LLMClient singleton instance"""
    return LLMClient()


if __name__ == "__main__":
    # Test LLM client
    client = LLMClient()
    
    print("\n=== LLM Client Test ===")
    print(f"Config: {client.get_config()}")
    
    if client._client:
        print("\n--- Test 1: Simple generation ---")
        try:
            response = client.generate(
                "What is the capital of France? Answer in one word.",
                max_tokens=100
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Test failed: {e}")
        
        print("\n--- Test 2: Structured output ---")
        try:
            schema = {
                "intent": "string",
                "entities": {
                    "city": "string"
                }
            }
            response = client.generate_structured(
                "I want to find hotels in Paris",
                schema
            )
            print(f"Response: {json.dumps(response, indent=2)}")
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("\n✗ Client not initialized - check API key")
