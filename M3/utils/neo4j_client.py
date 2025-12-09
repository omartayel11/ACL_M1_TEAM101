"""
Neo4j client for Graph-RAG Hotel Travel Assistant
Provides singleton connection and query execution for Neo4j database
"""

import os
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver, Session
from pathlib import Path


class Neo4jClient:
    """
    Singleton Neo4j client for managing database connections and queries.
    Executes Cypher queries only - no vector search logic.
    """
    
    _instance: Optional['Neo4jClient'] = None
    _driver: Optional[Driver] = None
    _uri: Optional[str] = None
    _username: Optional[str] = None
    _password: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Neo4j client - reads credentials from config.txt"""
        if self._driver is None:
            self._load_credentials()
    
    def _load_credentials(self):
        """Load Neo4j credentials from config.txt"""
        # Look for config.txt in M3 directory or parent
        config_paths = [
            Path(__file__).parent.parent / "config.txt",
            Path(__file__).parent.parent.parent / "M2" / "config.txt"
        ]
        
        config_path = None
        for path in config_paths:
            if path.exists():
                config_path = path
                break
        
        if config_path is None:
            print("Warning: config.txt not found. Neo4j client not initialized.")
            print("Create config.txt with URI, USERNAME, PASSWORD")
            return
        
        # Parse config.txt
        config = {}
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip().upper()] = value.strip()
        
        self._uri = config.get('URI')
        self._username = config.get('USERNAME')
        self._password = config.get('PASSWORD')
        
        if not all([self._uri, self._username, self._password]):
            print("Warning: Incomplete Neo4j credentials in config.txt")
            return
        
        print(f"✓ Neo4j credentials loaded from {config_path}")
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database
        
        Returns:
            True if connection successful, False otherwise
        """
        if self._driver is not None:
            return True
        
        if not all([self._uri, self._username, self._password]):
            print("Error: Cannot connect - credentials not loaded")
            return False
        
        try:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password)
            )
            
            # Test connection
            with self._driver.session() as session:
                result = session.run("RETURN 1 AS test")
                result.single()
            
            print(f"✓ Connected to Neo4j at {self._uri}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to connect to Neo4j: {e}")
            self._driver = None
            return False
    
    def run_query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results
        
        Args:
            cypher: Cypher query string
            params: Query parameters
            
        Returns:
            List of result records as dictionaries
            
        Raises:
            ConnectionError: If not connected to Neo4j
            Exception: If query execution fails
        """
        if self._driver is None:
            if not self.connect():
                raise ConnectionError("Not connected to Neo4j")
        
        params = params or {}
        
        try:
            with self._driver.session() as session:
                result = session.run(cypher, params)
                records = [dict(record) for record in result]
                return records
                
        except Exception as e:
            print(f"Error executing query: {e}")
            print(f"Query: {cypher}")
            print(f"Params: {params}")
            raise
    
    def close(self):
        """Close Neo4j connection"""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            print("✓ Neo4j connection closed")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection status and info"""
        return {
            'connected': self._driver is not None,
            'uri': self._uri,
            'username': self._username
        }


# Convenience function for quick access
def get_neo4j_client() -> Neo4jClient:
    """Get Neo4jClient singleton instance"""
    return Neo4jClient()


if __name__ == "__main__":
    # Test Neo4j client
    client = Neo4jClient()
    
    print("\n=== Neo4j Client Test ===")
    print(f"Connection info: {client.get_connection_info()}")
    
    if client.connect():
        print("\n✓ Connection successful")
        
        # Test simple query
        try:
            result = client.run_query("MATCH (n) RETURN count(n) AS node_count LIMIT 1")
            print(f"Node count: {result[0]['node_count'] if result else 0}")
        except Exception as e:
            print(f"Query test failed: {e}")
        
        client.close()
    else:
        print("\n✗ Connection failed")
