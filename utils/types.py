from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
from entities.base_entity import Entity

class TaskType(Enum):
    WIRE_CONSTRUCTION = "wire_construction"
    # Future task types can be added here

class EntityState(Enum):
    WANDERING = "wandering"
    SEEKING_FOOD = "seeking_food"
    WORKING = "working"
    IDLE = "idle"

@dataclass
class Task:
    type: TaskType
    position: Tuple[int, int]
    assigned_to: Optional[Entity] = None
    priority: int = 1
    completed: bool = False 