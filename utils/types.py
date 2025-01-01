from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
from entities.base_entity import Entity

class TaskType(Enum):
    """Defines the different types of tasks that entities can perform in the game."""
    WIRE_CONSTRUCTION = "wire_construction"
    # Future task types can be added here

class EntityState(Enum):
    """Represents the possible states an entity can be in during gameplay."""
    IDLE = "idle"         # Entity is not performing any action
    WANDERING = "wandering"   # Entity is moving around without a specific goal
    WORKING = "working"       # Entity is performing a task
    SEEKING_FOOD = "seeking_food"  # Entity is looking for food resources

@dataclass
class Task:
    """
    Represents a task that can be assigned to an entity.
    
    Attributes:
        type (TaskType): The category of the task
        position (Tuple[int, int]): The (x, y) coordinates where the task should be performed
        assigned_to (Optional[Entity]): The entity currently assigned to this task, if any
        priority (int): Task priority level from 0 (lowest) to 3 (critical)
        completed (bool): Whether the task has been completed
    """
    type: TaskType
    position: Tuple[int, int]
    assigned_to: Optional['Entity'] = None  # Forward reference to Entity
    priority: int = 1  # 0 = low, 1 = normal, 2 = high, 3 = critical
    completed: bool = False
    
    def should_interrupt(self) -> bool:
        """
        Determines if this task is important enough to interrupt an entity's current activity.
        
        Returns:
            bool: True if the task priority is high (2) or critical (3), False otherwise
        """
        return self.priority >= 2  # High and Critical tasks interrupt 