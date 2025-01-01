from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
from entities.base_entity import Entity

class TaskType(Enum):
    WIRE_CONSTRUCTION = "wire_construction"
    # Future task types can be added here

class EntityState(Enum):
    IDLE = "idle"
    WANDERING = "wandering"
    WORKING = "working"
    SEEKING_FOOD = "seeking_food"

@dataclass
class Task:
    type: TaskType
    position: Tuple[int, int]
    assigned_to: Optional['Entity'] = None  # Forward reference to Entity
    priority: int = 1  # 0 = low, 1 = normal, 2 = high, 3 = critical
    completed: bool = False
    
    def should_interrupt(self) -> bool:
        """Whether this task should interrupt current activities"""
        return self.priority >= 2  # High and Critical tasks interrupt 