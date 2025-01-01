from typing import Optional, Tuple
from utils.config import TILE_SIZE
from utils.types import Task, TaskType, EntityState
import pygame

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
            print(f"Starting construction at {self.current_task.position}")
            self.is_building = True
            self.build_timer = 0
            return
        
        # Update build progress
        self.build_timer += dt
        print(f"Building progress: {self.build_timer:.1f}/{self.build_time_required}")
        
        if self.build_timer >= self.build_time_required:
            print(f"\n=== COMPLETING TASK ===")
            print(f"Task at {self.current_task.position}")
            
            # Complete the wire construction
            if self.game_state.wire_system.complete_wire_construction(self.current_task.position):
                print("Wire construction completed successfully")
                # Mark task as complete and clear it
                self.game_state.task_system.complete_task(self.current_task)
                self.current_task = None
                self.is_building = False
                self.build_timer = 0
                # Switch entity back to idle state
                self.entity._switch_state(EntityState.IDLE)
            else:
                print("Failed to complete wire construction")

    def _update_wire_construction(self, dt: float) -> None:
        """Handle wire construction task updates"""
        if not self.wire_task:
            print("No wire task to update")
            return

        wire_pos = self.wire_task[0]
        current_tile = (
            int(self.entity.position.x // TILE_SIZE),
            int(self.entity.position.y // TILE_SIZE)
        )
        
        print(f"\n=== WIRE CONSTRUCTION UPDATE ===")
        print(f"Entity {id(self.entity)} at {current_tile}")
        print(f"Target wire at {wire_pos}")
        print(f"Building: {self.is_building}, Timer: {self.build_timer:.1f}/{self.build_time_required}")
        
        # Simple distance check
        dx = abs(wire_pos[0] - current_tile[0])
        dy = abs(wire_pos[1] - current_tile[1])
        
        if dx <= 1 and dy <= 1:  # We're adjacent to wire
            if not self.is_building:
                print("Starting construction")
                self.is_building = True
                self.build_timer = 0
            
            self.build_timer += dt
            if self.build_timer >= self.build_time_required:
                print("Construction complete")
                if self.entity.game_state.wire_system.complete_wire_construction(wire_pos):
                    print("Wire updated successfully")
                    self.complete_current_task()
                    self.is_building = False
                    self.build_timer = 0
                    return
                else:
                    print("Failed to update wire")
        else:
            print(f"Too far to build: dx={dx}, dy={dy}")
            # Reset building state if we move away
            if self.is_building:
                print("Resetting building state")
                self.is_building = False
                self.build_timer = 0

    def start_task(self, task: Task) -> bool:
        """Start a new task"""
        if not self.validate_wire_task(task):
            return False
        
        print(f"\n=== TASK START ===")
        print(f"Entity {id(self.entity)} starting task at {task.position}")
        
        self.current_task = task
        self.entity.movement_handler.allow_movement()  # Allow movement for new task
        return True

    def set_wire_task(self, position: Tuple[int, int], wire_type: str) -> bool:
        """Set up wire task data"""
        print(f"Setting up wire task at {position}")
        self.wire_task = (position, wire_type)
        return True

    def complete_current_task(self) -> bool:
        """Complete the current task"""
        if not self.current_task:
            return False
        
        print(f"\n=== TASK COMPLETE ===")
        print(f"Entity {id(self.entity)} completed task at {self.current_task.position}")
        
        result = self.entity.game_state.task_system.complete_task(self.current_task)
        
        self.is_building = False
        self.build_timer = 0
        self.wire_task = None
        self.current_task = None
        self.entity.movement_handler.stop()  # Stop movement after task complete
        
        return result

    def has_task(self) -> bool:
        """Check if entity has an active task"""
        return self.current_task is not None

    def get_task_position(self) -> Optional[Tuple[int, int]]:
        """Get the position of the current task"""
        if not self.current_task:
            print("No current task")
            return None
        
        if not self.wire_task:
            print("No wire task data")
            return None
        
        print(f"\n=== TASK POSITION CHECK ===")
        print(f"Current task position: {self.current_task.position}")
        print(f"Wire task position: {self.wire_task[0]}")
        
        # These should match
        if self.current_task.position != self.wire_task[0]:
            print("WARNING: Task position mismatch!")
        
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
        print(f"Validating task: {task.type} == {TaskType.WIRE_CONSTRUCTION}?")
        print(f"Type comparison: {type(task.type)} vs {type(TaskType.WIRE_CONSTRUCTION)}")
        print(f"Values: {task.type.value} vs {TaskType.WIRE_CONSTRUCTION.value}")
        
        # Compare the enum values directly
        if task.type.value != TaskType.WIRE_CONSTRUCTION.value:
            print("Not a wire construction task")
            return False
        
        print(f"\n=== WIRE TASK VALIDATION ===")
        print(f"Entity {id(self.entity)} validating wire task:")
        print(f"Position: {task.position}")
        
        # Set up the wire task data
        if not self.set_wire_task(task.position, 'wire'):
            print("Failed to set wire task")
            return False
        
        return True 