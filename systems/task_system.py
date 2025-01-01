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

    def add_task(self, type: TaskType, position: Tuple[int, int], priority: int = 1) -> Task:
        """Add a new task with specified priority"""
        task = Task(type=type, position=position, priority=priority)
        self.available_tasks.append(task)
        return task

    def get_available_task(self, entity):
        """Get the closest available task for an entity"""
        # First check if this entity already has a task
        for task in self.assigned_tasks:
            if task.assigned_to == entity:
                return task  # Don't reassign if entity already has this task
            
        # If no tasks available, return None
        if not self.available_tasks:
            return None
        
        # Get closest task that isn't already assigned
        available_tasks = [t for t in self.available_tasks if not t.assigned_to]
        if not available_tasks:
            return None
        
        sorted_tasks = sorted(
            available_tasks,
            key=lambda t: (
                (entity.position.x // TILE_SIZE - t.position[0]) ** 2 + 
                (entity.position.y // TILE_SIZE - t.position[1]) ** 2
            )
        )
        
        task = sorted_tasks[0]
        # Move task from available to assigned
        self.available_tasks.remove(task)
        task.assigned_to = entity
        self.assigned_tasks.append(task)
        
        return task

    def complete_task(self, task):
        """Complete a task"""
        
        if task in self.assigned_tasks:
            self.assigned_tasks.remove(task)
            # Clear the entity's reference to this task
            if task.assigned_to:
                task.assigned_to.task_handler.current_task = None
                task.assigned_to.task_handler.wire_task = None
        
        task.completed = True
        task.assigned_to = None
        return True

    def return_task(self, task):
        """Return a task to the available pool"""
        if task in self.assigned_tasks:
            self.assigned_tasks.remove(task)
            task.assigned_to = None
            self.available_tasks.append(task)

    def get_highest_priority_task(self, entity) -> Optional[Task]:
        """Get the highest priority available task"""
        available_tasks = [
            task for task in self.available_tasks 
            if not task.assigned_to
        ]
        
        if not available_tasks:
            return None
            
        # Sort by priority (highest first)
        available_tasks.sort(key=lambda t: t.priority, reverse=True)
        return available_tasks[0] 