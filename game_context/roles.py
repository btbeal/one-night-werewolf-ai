from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Type
from enum import Enum
from game_agents.base_agent import BaseAgent
from game_agents.agent_registry import AGENT_REGISTRY


class Role(str, Enum):
    """All possible roles in One Night Werewolf"""
    # Village team
    VILLAGER = "villager"
    SEER = "seer"
    ROBBER = "robber"
    TROUBLEMAKER = "troublemaker"
    DRUNK = "drunk"
    INSOMNIAC = "insomniac"
    MASON = "mason"
    HUNTER = "hunter"
    
    # Werewolf team
    WEREWOLF = "werewolf"
    MINION = "minion"
    
    # Solo team
    TANNER = "tanner"

    def get_agent_class(self) -> Type['BaseAgent']:
        try:
            return AGENT_REGISTRY[self.value]
        except KeyError:
            raise ValueError(f"No agent class registered for role: {self.value}")