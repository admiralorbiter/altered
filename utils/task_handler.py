from typing import Optional, Tuple
from utils.config import TILE_SIZE
from utils.types import Task, TaskType, EntityState
import pygame
import random

class TaskHandler:
    def __init__(self, entity):
        self.entity = entity
        self.game_state = entity.game_state  # Get game_state from entity
        self.current_task: Optional[Task] = None
        self.wire_task: Optional[Tuple[Tuple[int, int], str]] = None  # ((x,y), type)
        
        # Building state
        self.is_building = False
        self.build_timer = 0
        self.build_time_required = 2.0
        
    def update(self, dt: float) -> None:
        """Update task progress"""
        if not self.current_task:
            return
        
        if not self.is_building:
            self.is_building = True
            self.build_timer = 0
            return
        
        # Update build progress
        self.build_timer += dt
        
        if self.build_timer >= self.build_time_required:
            
            # Complete the wire construction
            if self.game_state.wire_system.complete_wire_construction(self.current_task.position):
                # Just complete the task, let the cat's update handle the state change
                self.complete_current_task()
                # Don't force an immediate update

    def _update_wire_construction(self, dt: float) -> None:
        """Handle wire construction task updates"""
        if not self.wire_task:
            return

        wire_pos = self.wire_task[0]
        current_tile = (
            int(self.entity.position.x // TILE_SIZE),
            int(self.entity.position.y // TILE_SIZE)
        )
        
        # Simple distance check
        dx = abs(wire_pos[0] - current_tile[0])
        dy = abs(wire_pos[1] - current_tile[1])
        
        if dx <= 1 and dy <= 1:  # We're adjacent to wire
            if not self.is_building:
                self.is_building = True
                self.build_timer = 0
            
            self.build_timer += dt
            if self.build_timer >= self.build_time_required:
                if self.entity.game_state.wire_system.complete_wire_construction(wire_pos):
                    self.complete_current_task()
                    self.is_building = False
                    self.build_timer = 0
                    return
        else:
            # Reset building state if we move away
            if self.is_building:
                self.is_building = False
                self.build_timer = 0

    def start_task(self, task: Task) -> bool:
        """Start a new task"""
        if not self.validate_wire_task(task):
            return False
        
        self.current_task = task
        self.entity.movement_handler.allow_movement()  # Allow movement for new task
        return True

    def set_wire_task(self, position: Tuple[int, int], wire_type: str) -> bool:
        """Set up wire task data"""
        self.wire_task = (position, wire_type)
        return True

    def complete_current_task(self) -> bool:
        """Complete the current task"""
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
        """Check if entity has an active task"""
        return self.current_task is not None

    def get_task_position(self) -> Optional[Tuple[int, int]]:
        """Get the position of the current task"""
        if not self.current_task:
            return None
        
        if not self.wire_task:
            return None
        
        return self.wire_task[0]

    def stop(self) -> None:
        """Stop current task"""
        self.is_building = False
        self.build_timer = 0
        # Note: We don't clear the task itself as it might need to be resumed 

    def get_current_task(self) -> Optional[Task]:
        """Get the current task"""
        return self.current_task

    def get_wire_task_info(self) -> Optional[dict]:
        """Get information about current wire task"""
        if not self.wire_task or not self.current_task:
            return None
            
        return {
            'position': self.wire_task[0],
            'queue': []  # Wire queue implementation can be added later if needed
        } 

    def validate_wire_task(self, task: Task) -> bool:
        """Validate and set up a wire construction task"""
        
        # Compare the enum values directly
        if task.type.value != TaskType.WIRE_CONSTRUCTION.value:
            return False
        
        # Set up the wire task data
        if not self.set_wire_task(task.position, 'wire'):
            return False
        
        return True 