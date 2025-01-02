from typing import Optional, Tuple
from utils.config import TILE_SIZE
from utils.types import Task, TaskType, EntityState
import pygame
import random

# TaskHandler manages and executes tasks for game entities (like cats)
# It handles task validation, progress tracking, and completion
class TaskHandler:
    def __init__(self, entity):
        """Initialize a new TaskHandler for an entity.
        
        Args:
            entity: The game entity (e.g., cat) this handler is attached to
        """
        self.entity = entity
        self.game_state = entity.game_state  # Get game_state from entity
        self.current_task: Optional[Task] = None
        self.wire_task: Optional[Tuple[Tuple[int, int], str]] = None  # ((x,y), type)
        
        # Building state
        self.is_building = False
        self.build_timer = 0
        self.build_time_required = 2.0
        
    def update(self, dt: float) -> None:
        """Update the current task's progress.
        
        Handles the building state and timer for task completion.
        
        Args:
            dt: Delta time (time since last update) in seconds
        """
        if not self.current_task:
            return
        
        # Handle wire construction tasks
        if self.current_task.type == TaskType.WIRE_CONSTRUCTION:
            self._update_wire_construction(dt)
            return
        
        # Default task progress handling
        if not self.is_building:
            self.is_building = True
            self.build_timer = 0
            return
        
        # Update build progress
        self.build_timer += dt
        
        if self.build_timer >= self.build_time_required:
            self.complete_current_task()

    def _update_wire_construction(self, dt: float) -> None:
        """Handle the progress of wire construction tasks."""
        if not self.wire_task:
            return

        wire_pos = self.wire_task[0]
        current_tile = (
            int(self.entity.position.x // TILE_SIZE),
            int(self.entity.position.y // TILE_SIZE)
        )
        
        # Simple distance check with tolerance
        dx = abs(wire_pos[0] - current_tile[0])
        dy = abs(wire_pos[1] - current_tile[1])
        
        if dx <= 1.1 and dy <= 1.1:  # Within range
            if not self.is_building:
                print(f"[WIRE DEBUG] Starting construction at {wire_pos}")
                self.is_building = True
                self.entity.stop_movement()
                self.entity.set_state(EntityState.WORKING)
                self.entity.movement_handler.disable_pathfinding()
                return
            
            # Update construction progress through wire system
            if self.entity.game_state.wire_system.update_construction_progress(wire_pos, dt):
                print(f"[WIRE DEBUG] Construction complete at {wire_pos}!")
                # Ensure wire is properly marked as built
                wire = self.entity.game_state.current_level.tilemap.get_electrical(wire_pos[0], wire_pos[1])
                if wire:
                    wire.under_construction = False
                    wire.is_built = True
                self.complete_current_task()
                self.is_building = False
                self.entity.set_state(EntityState.WANDERING)
                self.entity.movement_handler.enable_pathfinding()
        else:
            if self.is_building:
                print(f"[WIRE DEBUG] Moved away from construction site")
                self.is_building = False
                self.entity.set_state(EntityState.MOVING)  # Reset to moving if we leave construction site
                # Re-enable pathfinding if we move away
                self.entity.movement_handler.enable_pathfinding()

    def start_task(self, task: Task) -> bool:
        """Attempt to start a new task for the entity."""
        if not self.validate_wire_task(task):
            return False
        
        # Check if task is already assigned to another entity
        if task.assigned_to and task.assigned_to != id(self.entity):
            print(f"[DEBUG] Task already assigned to {task.assigned_to}, our id is {id(self.entity)}")
            return False
        
        self.current_task = task
        task.assigned_to = id(self.entity)
        print(f"[DEBUG] Starting task {task.type} at {task.position} for cat {id(self.entity)}")
        return True

    def set_wire_task(self, position: Tuple[int, int], wire_type: str) -> bool:
        """Configure the wire construction task details.
        
        Args:
            position: Grid coordinates (x, y) for wire placement
            wire_type: Type of wire to construct
            
        Returns:
            bool: True if wire task was set up successfully
        """
        self.wire_task = (position, wire_type)
        return True

    def complete_current_task(self) -> bool:
        """Mark the current task as complete and reset entity state.
        
        Notifies task system, clears task-related states, and
        returns entity to wandering behavior.
        
        Returns:
            bool: True if task was successfully completed
        """
        if not self.current_task:
            return False
        
        result = self.entity.game_state.task_system.complete_task(self.current_task)
        
        # Clear all task-related state
        self.is_building = False
        self.build_timer = 0
        self.wire_task = None
        self.current_task = None
        
        # Stop current movement but don't prevent future movement
        self.entity.movement_handler.stop()
        self.entity.movement_handler.allow_movement()  # Immediately allow new movements
        
        # Switch to wandering state
        self.entity._switch_state(EntityState.WANDERING)
        
        return result

    def has_task(self) -> bool:
        """Check if the entity currently has an assigned task.
        
        Returns:
            bool: True if there is an active task
        """
        return self.current_task is not None

    def get_task_position(self) -> Optional[Tuple[int, int]]:
        """Retrieve the grid coordinates of the current wire task.
        
        Returns:
            Optional[Tuple[int, int]]: Grid coordinates or None if no task
        """
        if not self.current_task:
            return None
        
        if not self.wire_task:
            return None
        
        return self.wire_task[0]

    def stop(self) -> None:
        """Pause the current task's progress without canceling it.
        
        Resets building state and timer while preserving task assignment.
        """
        self.is_building = False
        self.build_timer = 0
        # Note: We don't clear the task itself as it might need to be resumed 

    def get_current_task(self) -> Optional[Task]:
        """Retrieve the currently assigned task.
        
        Returns:
            Optional[Task]: Current task object or None if no task
        """
        return self.current_task

    def get_wire_task_info(self) -> Optional[dict]:
        """Get details about the current wire construction task.
        
        Returns:
            Optional[dict]: Dictionary containing wire task position and queue,
                          or None if no wire task exists
        """
        if not self.wire_task or not self.current_task:
            return None
            
        return {
            'position': self.wire_task[0],
            'queue': []  # Wire queue implementation can be added later if needed
        } 

    def validate_wire_task(self, task: Task) -> bool:
        """Verify if a task is a valid wire construction task.
        
        Checks task type and attempts to set up wire construction data.
        
        Args:
            task: Task object to validate
            
        Returns:
            bool: True if task is valid wire construction, False otherwise
        """
        
        # Compare the enum values directly
        if task.type.value != TaskType.WIRE_CONSTRUCTION.value:
            return False
        
        # Set up the wire task data
        if not self.set_wire_task(task.position, 'wire'):
            return False
        
        return True 
        return True 