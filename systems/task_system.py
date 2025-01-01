from dataclasses import dataclass
from typing import Tuple, List, Optional
from utils.types import Task, TaskType, EntityState
from components.base_entity import Entity
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
        self.assigned_tasks = {}  # Change to dict with entity as key

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
        print(f"[DEBUG] New task added: {task.type} at {task.position}")
        return task

    def get_available_task(self, entity):
        """Find and assign the closest available task to an entity."""
        # First check if the entity already has a task assigned
        if entity in self.assigned_tasks:
            print(f"[DEBUG] Entity already has task: {self.assigned_tasks[entity].type}")
            return self.assigned_tasks[entity]

        # Get available unassigned tasks
        available_tasks = [t for t in self.available_tasks 
                          if t.assigned_to is None]
        if not available_tasks:
            return None

        # Sort by distance and priority
        sorted_tasks = sorted(
            available_tasks,
            key=lambda t: (
                -t.priority,  # Higher priority first
                (entity.position.x // TILE_SIZE - t.position[0]) ** 2 + 
                (entity.position.y // TILE_SIZE - t.position[1]) ** 2
            )
        )

        # Assign the task
        task = sorted_tasks[0]
        self.available_tasks.remove(task)
        task.assigned_to = id(entity)
        self.assigned_tasks[entity] = task
        print(f"[DEBUG] Assigned task to entity {id(entity)}: {task.type} at {task.position}")
        return task

    def complete_task(self, task):
        """Mark a task as completed and remove it from tracking"""
        if task.assigned_to in self.assigned_tasks:
            del self.assigned_tasks[task.assigned_to]
        task.completed = True
        print(f"[DEBUG] Task completed: {task.type} at {task.position}")

    def return_task(self, task):
        """Return an assigned task back to the available pool"""
        for entity, assigned_task in self.assigned_tasks.items():
            if assigned_task == task:
                del self.assigned_tasks[entity]
                break
        
        task.unassign()
        if task not in self.available_tasks:
            self.available_tasks.append(task)
            print(f"[DEBUG] Task returned to pool: {task.type} at {task.position}")

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

    def assign_task(self, entity) -> bool:
        """
        Assigns a task to an entity if one is available
        Returns True if task was assigned
        """
        if not self.available_tasks:
            return False
        
        # Don't reassign if entity already has this task
        if entity in self.assigned_tasks:
            return False
        
        # Get highest priority unassigned task
        available_tasks = [t for t in self.available_tasks if not t.assigned_to]
        if not available_tasks:
            return False
        
        task = max(available_tasks, key=lambda t: t.priority)
        
        # Mark task as assigned and add to tracking
        task.assigned_to = entity
        self.available_tasks.remove(task)
        self.assigned_tasks[entity] = task
        
        print(f"[DEBUG] Assigned task to entity: {task.type} at {task.position}")
        return True 