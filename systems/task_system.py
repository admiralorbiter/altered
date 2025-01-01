from dataclasses import dataclass
from typing import Tuple, List, Optional
from utils.types import Task, TaskType, EntityState
from entities.base_entity import Entity
from utils.config import TILE_SIZE

class TaskSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.available_tasks = []
        self.assigned_tasks = []

    def add_task(self, task_type, position, priority=1):
        """Add a new task to the system"""
        print(f"\n=== Adding New Task ===")
        print(f"Type: {task_type}")
        print(f"Position: {position}")
        
        task = Task(type=task_type, position=position, priority=priority)
        self.available_tasks.append(task)
        print(f"Available tasks after adding: {len(self.available_tasks)}")
        return task

    def get_available_task(self, entity):
        """Get the closest available task for an entity"""
        # First check if this entity already has a task
        for task in self.assigned_tasks:
            if task.assigned_to == entity:
                # Important: Make sure the entity knows about this task through its handler
                if not entity.task_handler.has_task():
                    print(f"Reassigning existing task at {task.position}")
                    entity.task_handler.set_wire_task(task.position, 'wire')
                return task
            
        # If no tasks available, return None
        if not self.available_tasks:
            return None
        
        # Get closest task
        sorted_tasks = sorted(
            self.available_tasks,
            key=lambda t: (
                (entity.position.x // TILE_SIZE - t.position[0]) ** 2 + 
                (entity.position.y // TILE_SIZE - t.position[1]) ** 2
            )
        )
        
        task = sorted_tasks[0]
        print(f"Assigning new task at {task.position}")
        
        # Move task from available to assigned
        self.available_tasks.remove(task)
        task.assigned_to = entity
        self.assigned_tasks.append(task)
        
        return task

    def complete_task(self, task):
        """Complete a task"""
        if task in self.assigned_tasks:
            self.assigned_tasks.remove(task)
        task.completed = True
        task.assigned_to = None
        return True 