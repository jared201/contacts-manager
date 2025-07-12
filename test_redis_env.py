import os
import sys
from service.redis_manager import RedisManager

def test_redis_env_vars():
    """
    Test that RedisManager correctly reads connection parameters from environment variables.
    """
    print("Testing RedisManager environment variable handling...")
    
    # Test 1: Default values when no environment variables or parameters are set
    manager1 = RedisManager()
    print("\nTest 1: Default values")
    print(f"Host: {manager1.redis_client.connection_pool.connection_kwargs['host']} (expected: localhost)")
    print(f"Port: {manager1.redis_client.connection_pool.connection_kwargs['port']} (expected: 6379)")
    print(f"Password: {manager1.redis_client.connection_pool.connection_kwargs['password']} (expected: None)")
    
    # Test 2: Environment variables
    print("\nTest 2: Setting environment variables")
    os.environ['REDIS__HOST'] = 'redis.example.com'
    os.environ['REDIS_PORT'] = '6380'
    os.environ['REDIS_PASSWORD'] = 'secret123'
    
    manager2 = RedisManager()
    print(f"Host: {manager2.redis_client.connection_pool.connection_kwargs['host']} (expected: redis.example.com)")
    print(f"Port: {manager2.redis_client.connection_pool.connection_kwargs['port']} (expected: 6380)")
    print(f"Password: {manager2.redis_client.connection_pool.connection_kwargs['password']} (expected: secret123)")
    
    # Test 3: Explicit parameters override environment variables
    print("\nTest 3: Explicit parameters override environment variables")
    manager3 = RedisManager(host='explicit.example.com', port=6381, password='explicit123')
    print(f"Host: {manager3.redis_client.connection_pool.connection_kwargs['host']} (expected: explicit.example.com)")
    print(f"Port: {manager3.redis_client.connection_pool.connection_kwargs['port']} (expected: 6381)")
    print(f"Password: {manager3.redis_client.connection_pool.connection_kwargs['password']} (expected: explicit123)")
    
    # Clean up environment variables
    del os.environ['REDIS__HOST']
    del os.environ['REDIS_PORT']
    del os.environ['REDIS_PASSWORD']
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_redis_env_vars()