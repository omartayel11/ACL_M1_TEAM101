"""
Configuration loader for Graph-RAG Hotel Travel Assistant
Loads and validates config.yaml with default fallbacks
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigLoader:
    """
    Singleton configuration loader that reads config.yaml and provides
    easy access to configuration values with validation and defaults.
    """
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize config loader - loads config.yaml if not already loaded"""
        if not self._config:
            self.load_config()
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to config.yaml (defaults to ./config.yaml)
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config.yaml doesn't exist
            yaml.YAMLError: If config.yaml is invalid
        """
        if config_path is None:
            # Look for config.yaml in M3 directory
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not os.path.exists(config_path):
            print(f"Warning: config.yaml not found at {config_path}, using defaults")
            self._config = self._get_default_config()
            return self._config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
            
            # Merge with defaults for missing keys
            self._config = self._merge_with_defaults(self._config)
            
            print(f"✓ Configuration loaded from {config_path}")
            return self._config
            
        except yaml.YAMLError as e:
            print(f"Error parsing config.yaml: {e}")
            print("Using default configuration")
            self._config = self._get_default_config()
            return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'llm.model' or 'retrieval.baseline.max_results')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Examples:
            >>> config = ConfigLoader()
            >>> config.get('llm.model')
            'openai/gpt-oss-120b'
            >>> config.get('retrieval.baseline.max_results', 10)
            10
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary"""
        return self._config.copy()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'workflows': {
                'default': 'hybrid',
                'available': ['baseline_only', 'embedding_only', 'hybrid', 'llm_pipeline']
            },
            'llm': {
                'provider': 'groq',
                'default_model': 'openai/gpt-oss-120b',
                'available_models': [
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
                ],
                'temperature': 0.7,
                'max_tokens': 500,
                'api_key_env': 'GROQ_API_KEY'
            },
            'retrieval': {
                'baseline': {
                    'enabled': True,
                    'max_results': 10
                },
                'embedding': {
                    'enabled': True,
                    'max_results': 10,
                    'similarity_threshold': 0.7
                },
                'merge': {
                    'max_context_tokens': 2500
                }
            },
            'embedding': {
                'default_model': 'all-MiniLM-L6-v2',
                'available_models': [
                    {
                        'name': 'all-MiniLM-L6-v2',
                        'display_name': 'MiniLM L6 v2',
                        'description': 'Fast, 384 dimensions',
                        'dimensions': 384
                    },
                    {
                        'name': 'all-mpnet-base-v2',
                        'display_name': 'MPNet Base v2',
                        'description': 'Better quality, 768 dimensions',
                        'dimensions': 768
                    }
                ],
                'cache_embeddings': True,
                'batch_size': 32
            },
            'neo4j': {
                'uri': None,
                'username': None,
                'password': None
            },
            'ui': {
                'show_debug': True,
                'max_display_results': 5,
                'enable_graph_viz': False
            }
        }
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults for missing keys"""
        defaults = self._get_default_config()
        return self._deep_merge(defaults, config)
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def reload(self, config_path: Optional[str] = None):
        """Reload configuration from file"""
        self._config = {}
        self.load_config(config_path)


# Convenience function for quick access
def get_config() -> ConfigLoader:
    """Get ConfigLoader singleton instance"""
    return ConfigLoader()


if __name__ == "__main__":
    # Test configuration loader
    config = ConfigLoader()
    print("\n=== Configuration Test ===")
    print(f"Default workflow: {config.get('workflows.default')}")
    print(f"LLM provider: {config.get('llm.provider')}")
    print(f"LLM model: {config.get('llm.model')}")
    print(f"Embedding model: {config.get('embedding.model')}")
    print(f"Max baseline results: {config.get('retrieval.baseline.max_results')}")
    print("\nFull config:")
    import json
    print(json.dumps(config.get_all(), indent=2))
