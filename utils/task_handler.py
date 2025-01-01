from typing import Optional, Tuple
from utils.config import TILE_SIZE
from utils.types import Task, TaskType, EntityState
import pygame

class TaskHandler:
    def __init__(self, entity):
        self.entity = entity
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
            
        if self.current_task.type == TaskType.WIRE_CONSTRUCTION:
            self._update_wire_construction(dt)
    
    def _update_wire_construction(self, dt: float) -> None:
        """Handle wire construction task updates"""
        if not self.wire_task:
            return

        # Get current tile position
        current_tile = (
            int(self.entity.position.x // TILE_SIZE),
            int(self.entity.position.y // TILE_SIZE)
        )
        wire_pos = self.wire_task[0]

        print(f"\n=== WIRE TASK UPDATE ===")
        print(f"Entity at {current_tile}")
        print(f"Target wire at {wire_pos}")
        
        # Check if we're close enough to build
        if (abs(wire_pos[0] - current_tile[0]) <= 1 and 
            abs(wire_pos[1] - current_tile[1]) <= 1):
            
            if not self.is_building:
                print("Starting wire construction")
                self.is_building = True
                self.build_timer = 0
                return
            
            # Update building progress
            self.build_timer += dt
            print(f"Building progress: {self.build_timer}/{self.build_time_required}")
            
            if self.build_timer >= self.build_time_required:
                print("Wire construction complete")
                self.complete_current_task()

    def start_task(self, task: Task) -> bool:
        """Start a new task"""
        if task.type == TaskType.WIRE_CONSTRUCTION:
            return self.set_wire_task(task.position, 'wire')
        return False

    def set_wire_task(self, wire_pos: Tuple[int, int], wire_type: str) -> bool:
        """Set up a wire construction task"""
        print(f"\n=== WIRE TASK ASSIGNMENT ===")
        print(f"Entity {id(self.entity)} receiving wire task:")
        print(f"Position: {wire_pos}")
        print(f"Wire type: {wire_type}")
        
        # Get the actual Task object from the task system
        task = self.entity.game_state.task_system.get_available_task(self.entity)
        if not task or task.type != TaskType.WIRE_CONSTRUCTION:
            return False
            
        if task.position != wire_pos:
            print(f"Task position {task.position} doesn't match wire position {wire_pos}")
            return False
            
        print(f"Entity got matching task: {task.type.value} @ {task.position}")
        self.current_task = task
        self.wire_task = (wire_pos, wire_type)
        return True

    def complete_current_task(self) -> bool:
        """Complete the current task"""
        if not self.current_task:
            return False
            
        print(f"\n=== Entity {id(self.entity)} completing task ===")
        print(f"Task position: {self.current_task.position}")
        
        # Complete the task in the task system
        result = self.entity.game_state.task_system.complete_task(self.current_task)
        
        # Reset all task-related states
        self.is_building = False
        self.build_timer = 0
        self.wire_task = None
        self.current_task = None
        
        return result

    def has_task(self) -> bool:
        """Check if entity has an active task"""
        return self.current_task is not None

    def get_task_position(self) -> Optional[Tuple[int, int]]:
        """Get the position of the current task"""
        if self.wire_task:
            return self.wire_task[0]
        return None

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