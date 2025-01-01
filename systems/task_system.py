from dataclasses import dataclass
from typing import Tuple, List, Optional
from utils.types import Task, TaskType, EntityState
from entities.base_entity import Entity
from utils.config import TILE_SIZE

class TaskSystem:
    """
    Manages the creation, assignment, and completion of tasks within the game.
    Handles task prioritization and assignment to entities.
    """
    def __init__(self, game_state):
        """
        Initialize the task system.
        
        Args:
            game_state: Reference to the main game state
        """
        self.game_state = game_state
        self.available_tasks = []  # Tasks that haven't been assigned to any entity
        self.assigned_tasks = []   # Tasks currently being worked on by entities

    def add_task(self, type: TaskType, position: Tuple[int, int], priority: int = 1) -> Task:
        """
        Create and add a new task to the available tasks pool.
        
        Args:
            type: The type of task to create (TaskType enum)
            position: (x, y) coordinates where the task should be performed
            priority: Task priority level, higher numbers = higher priority (default: 1)
            
        Returns:
            Task: The newly created task
        """
        task = Task(type=type, position=position, priority=priority)
        self.available_tasks.append(task)
        return task

    def get_available_task(self, entity):
        """
        Find and assign the closest available task to an entity.
        
        Args:
            entity: The entity requesting a task
            
        Returns:
            Task: The closest available task, or None if no tasks are available
        """
        # Check if entity already has an assigned task
        for task in self.assigned_tasks:
            if task.assigned_to == entity:
                return task  # Prevent multiple task assignments
            
        # Exit early if no tasks are available
        if not self.available_tasks:
            return None
        
        # Filter out tasks that are already assigned
        available_tasks = [t for t in self.available_tasks if not t.assigned_to]
        if not available_tasks:
            return None
        
        # Sort tasks by distance to entity (using squared distance for efficiency)
        sorted_tasks = sorted(
            available_tasks,
            key=lambda t: (
                (entity.position.x // TILE_SIZE - t.position[0]) ** 2 + 
                (entity.position.y // TILE_SIZE - t.position[1]) ** 2
            )
        )
        
        # Assign the closest task to the entity
        task = sorted_tasks[0]
        self.available_tasks.remove(task)
        task.assigned_to = entity
        self.assigned_tasks.append(task)
        
        return task

    def complete_task(self, task):
        """
        Mark a task as completed and clean up related references.
        
        Args:
            task: The task to complete
            
        Returns:
            bool: True if task was successfully completed
        """
        if task in self.assigned_tasks:
            self.assigned_tasks.remove(task)
            # Clear task references from the entity
            if task.assigned_to:
                task.assigned_to.task_handler.current_task = None
                task.assigned_to.task_handler.wire_task = None
        
        task.completed = True
        task.assigned_to = None
        return True

    def return_task(self, task):
        """
        Return an assigned task back to the available tasks pool.
        Useful when an entity cannot complete its assigned task.
        
        Args:
            task: The task to return to the available pool
        """
        if task in self.assigned_tasks:
            self.assigned_tasks.remove(task)
            task.assigned_to = None
            self.available_tasks.append(task)

    def get_highest_priority_task(self, entity) -> Optional[Task]:
        """
        Find the highest priority task from the available tasks pool.
        
        Args:
            entity: The entity requesting a task
            
        Returns:
            Optional[Task]: The highest priority task, or None if no tasks are available
        """
        available_tasks = [
            task for task in self.available_tasks 
            if not task.assigned_to
        ]
        
        if not available_tasks:
            return None
            
        # Sort by priority (highest first)
        available_tasks.sort(key=lambda t: t.priority, reverse=True)
        return available_tasks[0] 