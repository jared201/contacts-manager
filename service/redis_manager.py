import json
import os
import redis
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from uuid import UUID
from pydantic import BaseModel

# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)

class RedisManager:
    """
    A Redis Manager component to manage all CRUD operations with Redis.
    """
    def __init__(self, host: str = None, port: int = None, db: int = 0, password: Optional[str] = None):
        """
        Initialize the Redis Manager with connection parameters.

        Connection parameters can be provided directly or through environment variables:
        - REDIS__HOST: Redis server host (default: 'localhost')
        - REDIS_PORT: Redis server port (default: 6379)
        - REDIS_PASSWORD: Redis server password (default: None)

        Explicitly passed parameters take precedence over environment variables.

        Args:
            host: Redis server host (overrides REDIS__HOST)
            port: Redis server port (overrides REDIS_PORT)
            db: Redis database number
            password: Redis server password (overrides REDIS_PASSWORD)
        """
        # Get connection parameters from environment variables if not explicitly provided
        self.env_host = os.getenv("REDIS_HOST") or os.getenv("REDIS__HOST", "localhost")
        env_port = os.getenv("REDIS_PORT", "6379")
        env_password = os.getenv("REDIS_PASSWORD", "password")
        print(self.env_host)
        # Use explicitly passed parameters if provided, otherwise use environment variables if available,
        # otherwise use default values
        final_host = host if host is not None else (self.env_host if self.env_host is not None else 'localhost')
        final_port = port if port is not None else (int(env_port) if env_port is not None else 6379)
        final_password = password if password is not None else env_password

        self.redis_client = redis.Redis(
            host=final_host,
            port=final_port,
            db=db,
            password=final_password,
            decode_responses=True
        )

    def _get_key(self, model_type: str, id: Union[UUID, str]) -> str:
        """
        Generate a Redis key for a specific model and ID.

        Args:
            model_type: The type of model (e.g., 'contact', 'customer')
            id: The UUID or string ID of the model instance

        Returns:
            A formatted Redis key
        """
        return f"{model_type}:{str(id)}"

    def _get_collection_key(self, model_type: str) -> str:
        """
        Generate a Redis key for a collection of models.

        Args:
            model_type: The type of model (e.g., 'contact', 'customer')

        Returns:
            A formatted Redis key for the collection
        """
        return f"{model_type}:all"

    def _serialize(self, obj: Any) -> str:
        """
        Serialize an object to a JSON string.

        Args:
            obj: The object to serialize

        Returns:
            A JSON string representation of the object
        """
        if isinstance(obj, BaseModel):
            # Handle both Pydantic v1 and v2
            if hasattr(obj, 'model_dump'):
                obj_dict = obj.model_dump()
            else:
                obj_dict = obj.dict()

            # Convert UUID to string for JSON serialization
            for key, value in obj_dict.items():
                if isinstance(value, UUID):
                    obj_dict[key] = str(value)

            return json.dumps(obj_dict)
        elif isinstance(obj, dict):
            # Convert UUID to string for JSON serialization
            obj_dict = obj.copy()
            for key, value in obj_dict.items():
                if isinstance(value, UUID):
                    obj_dict[key] = str(value)

            return json.dumps(obj_dict)
        else:
            return json.dumps(obj)

    def _deserialize(self, json_str: str, model_class: Type[T]) -> T:
        """
        Deserialize a JSON string to a Pydantic model instance.

        Args:
            json_str: The JSON string to deserialize
            model_class: The Pydantic model class

        Returns:
            An instance of the Pydantic model
        """
        data = json.loads(json_str)
        return model_class(**data)

    def create(self, model_type: str, model: BaseModel) -> BaseModel:
        """
        Create a new model instance in Redis.

        Args:
            model_type: The type of model (e.g., 'contact', 'customer')
            model: The Pydantic model instance to create

        Returns:
            The created model instance
        """
        # Get the ID from the model
        model_id = getattr(model, 'id')

        # Create the Redis key
        key = self._get_key(model_type, model_id)

        # Serialize the model
        model_json = self._serialize(model)

        # Store the model in Redis
        self.redis_client.set(key, model_json)

        # Add the ID to the collection set
        collection_key = self._get_collection_key(model_type)
        self.redis_client.sadd(collection_key, str(model_id))

        return model

    def get(self, model_type: str, model_id: Union[UUID, str], model_class: Type[T]) -> Optional[T]:
        """
        Get a model instance from Redis by ID.

        Args:
            model_type: The type of model (e.g., 'contact', 'customer')
            model_id: The UUID or string ID of the model instance
            model_class: The Pydantic model class

        Returns:
            The model instance if found, None otherwise
        """
        # Create the Redis key
        key = self._get_key(model_type, model_id)

        # Get the model from Redis
        model_json = self.redis_client.get(key)

        if model_json is None:
            return None

        # Deserialize the model
        return self._deserialize(model_json, model_class)

    def get_all(self, model_type: str, model_class: Type[T]) -> List[T]:
        """
        Get all model instances of a specific type from Redis.

        Args:
            model_type: The type of model (e.g., 'contact', 'customer')
            model_class: The Pydantic model class

        Returns:
            A list of model instances
        """
        # Get the collection key
        collection_key = self._get_collection_key(model_type)

        # Get all IDs from the collection set
        ids = self.redis_client.smembers(collection_key)

        # Get all models
        models = []
        for id in ids:
            model = self.get(model_type, id, model_class)
            if model:
                models.append(model)

        return models

    def update(self, model_type: str, model_id: Union[UUID, str], update_data: Dict[str, Any], model_class: Type[T]) -> Optional[T]:
        """
        Update a model instance in Redis.

        Args:
            model_type: The type of model (e.g., 'contact', 'customer')
            model_id: The UUID or string ID of the model instance
            update_data: A dictionary of fields to update
            model_class: The Pydantic model class

        Returns:
            The updated model instance if found, None otherwise
        """
        # Get the existing model
        model = self.get(model_type, model_id, model_class)

        if model is None:
            return None

        # Update the model
        for field, value in update_data.items():
            if hasattr(model, field):
                setattr(model, field, value)

        # Create the Redis key
        key = self._get_key(model_type, model_id)

        # Serialize the updated model
        model_json = self._serialize(model)

        # Store the updated model in Redis
        self.redis_client.set(key, model_json)

        return model

    def delete(self, model_type: str, model_id: Union[UUID, str]) -> bool:
        """
        Delete a model instance from Redis.

        Args:
            model_type: The type of model (e.g., 'contact', 'customer')
            model_id: The UUID or string ID of the model instance

        Returns:
            True if the model was deleted, False otherwise
        """
        # Create the Redis key
        key = self._get_key(model_type, model_id)

        # Check if the model exists
        if not self.redis_client.exists(key):
            return False

        # Delete the model from Redis
        self.redis_client.delete(key)

        # Remove the ID from the collection set
        collection_key = self._get_collection_key(model_type)
        self.redis_client.srem(collection_key, str(model_id))

        return True

    def get_by_field(self, model_type: str, field: str, value: Any, model_class: Type[T]) -> List[T]:
        """
        Get model instances by a specific field value.

        Args:
            model_type: The type of model (e.g., 'contact', 'customer')
            field: The field to filter by
            value: The value to filter for
            model_class: The Pydantic model class

        Returns:
            A list of model instances matching the field value
        """
        # Get all models of this type
        all_models = self.get_all(model_type, model_class)

        # Filter models by the specified field value
        return [model for model in all_models if getattr(model, field, None) == value]

    def close(self):
        """
        Close the Redis connection.
        """
        self.redis_client.close()

# Create a singleton instance of the Redis Manager
# This will use environment variables if available, otherwise default values
redis_manager = RedisManager()
