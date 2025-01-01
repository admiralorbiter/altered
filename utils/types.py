from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

class TaskType(Enum):
    """Defines the different types of tasks that entities can perform in the game."""
    WIRE_CONSTRUCTION = 1
    # Future task types can be added here

class EntityState(Enum):
    """Represents the possible states an entity can be in during gameplay."""
    IDLE = "idle"
    WANDERING = "wandering"
    WORKING = "working"
    SEEKING_FOOD = "seeking_food"

@dataclass
class Task:
    """Represents a task that can be assigned to an entity."""
    type: TaskType
    position: Tuple[int, int]
    priority: int = 1
    completed: bool = False
    work_time: float = 2.0
    assigned_to: Optional[int] = None  # This stores the entity's ID directly
    _work_progress: float = 0.0  # Add this line to track progress

    def assign_to(self, entity) -> None:
        """Safely assign task to an entity by storing its ID"""
        self.assigned_to = id(entity)
        self._work_progress = 0.0  # Reset progress when reassigning
        print(f"[DEBUG] Task assigned to entity ID: {self.assigned_to}")

    def unassign(self) -> None:
        """Clear task assignment"""
        print(f"[DEBUG] Task unassigned from entity ID: {self.assigned_to}")
        self.assigned_to = None
        self._work_progress = 0.0  # Reset progress when unassigning

    def is_assigned(self) -> bool:
        """Check if task is currently assigned"""
        return self.assigned_to is not None

    def is_assigned_to(self, entity) -> bool:
        """Check if task is assigned to specific entity"""
        return self.assigned_to == id(entity)
    
    def should_interrupt(self) -> bool:
        """
        Determines if this task is important enough to interrupt an entity's current activity.
        
        Returns:
            bool: True if the task priority is high (2) or critical (3), False otherwise
        """
        return self.priority >= 2  # High and Critical tasks interrupt 