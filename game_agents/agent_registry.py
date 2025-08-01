from typing import Dict, Type
from game_agents.base_agent import BaseAgent

AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {}

def register_agent(role_name: str):
    def decorator(cls):
        AGENT_REGISTRY[role_name.lower()] = cls
        return cls
    return decorator