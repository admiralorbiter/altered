from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum
from entities.base_entity import Entity
from utils.config import TILE_SIZE

class TaskType(Enum):
    WIRE_CONSTRUCTION = "wire_construction"
    # Future task types can be added here

@dataclass
class Task:
    type: TaskType
    position: Tuple[int, int]
    assigned_to: Optional[Entity] = None
    priority: int = 1
    completed: bool = False

class TaskSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.available_tasks = []
        self.assigned_tasks = []

    def add_task(self, task_type, position, priority=1):
        task = Task(type=task_type, position=position, priority=priority)
        self.available_tasks.append(task)
        return task

    def get_available_task(self, entity):
        """Get the closest available task for an entity"""
        if not self.available_tasks:
            return None
        
        sorted_tasks = sorted(
            self.available_tasks,
            key=lambda t: (
                (entity.position.x // TILE_SIZE - t.position[0]) ** 2 + 
                (entity.position.y // TILE_SIZE - t.position[1]) ** 2
            )
        )
        
        task = sorted_tasks[0]
        
        task.assigned_to = entity
        self.available_tasks.remove(task)
        self.assigned_tasks.append(task)
        return task

    def complete_task(self, task):
        """Complete a task"""
        print(f"\n=== TASK COMPLETION DEBUG ===")
        print(f"Task type: {task.type}")
        print(f"Task position: {task.position}")
        
        if task.type == TaskType.WIRE_CONSTRUCTION:
            result = self.game_state.wire_system.complete_wire_construction(task.position)
            if result:
                if task in self.assigned_tasks:
                    self.assigned_tasks.remove(task)
                task.completed = True
            print(f"Wire construction result: {result}")
            return result
        return False 