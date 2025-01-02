from components.base_component import Component
from components.movement_component import MovementComponent
from utils.types import EntityState, TaskType
import pygame
from utils.config import TILE_SIZE

class TaskComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.current_task = None
        self._movement = None
        self._task_position = None
        self._work_progress = 0
        self._work_time = 2.0  # Default work time
        self._task_complete = False
        self._is_building = False

    def start(self) -> None:
        """Get reference to movement component"""
        self._movement = self.entity.get_component(MovementComponent)

    def has_task(self) -> bool:
        """Check if currently assigned to a task"""
        return self.current_task is not None

    def start_task(self, task) -> bool:
        """Attempt to start a new task"""
        if self.current_task:
            return False
            
        # Need to check if task is already assigned to another entity
        if task.assigned_to and task.assigned_to != id(self.entity):
            print(f"[DEBUG] Task already assigned to {task.assigned_to}, our id is {id(self.entity)}")
            return False
            
        self.current_task = task
        self._task_position = task.position
        self._work_progress = 0
        self._work_time = getattr(task, 'work_time', 2.0)
        self._task_complete = False
        self._is_building = False
        
        print(f"[DEBUG] Starting task {task.type} at {task.position} for cat {id(self.entity)}")
        return True

    def stop(self) -> None:
        """Stop current task"""
        if self.current_task:
            # Return task to system for reassignment
            self.entity.game_state.task_system.return_task(self.current_task)
            self.current_task = None
            self._task_position = None
            self._work_progress = 0
            self._task_complete = False
            self._is_building = False

    def get_task_position(self) -> tuple[int, int]:
        """Get current task position in tile coordinates"""
        return self._task_position if self._task_position else None

    def update(self, dt: float) -> bool:
        """Update task progress and handle completion"""
        if not self.current_task:
            return False
        
        # Only update progress if we're at the task location
        if self._is_at_task_position():
            # Don't increment if already at max progress
            if self._work_progress < self.current_task.work_time:
                self._work_progress += dt
                print(f"[DEBUG] Task update for {self.current_task.type}:")
                print(f"  - Progress: {self._work_progress:.1f}/{self.current_task.work_time}")

            # Check for task completion
            if self._work_progress >= self.current_task.work_time:
                print("[DEBUG] Task completed!")
                
                # Handle wire construction completion
                if self.current_task.type == TaskType.WIRE_CONSTRUCTION:
                    wire_pos = self.current_task.position
                    electrical_comp = self.entity.game_state.current_level.tilemap.get_electrical(wire_pos[0], wire_pos[1])
                    if electrical_comp:
                        electrical_comp.under_construction = False
                        electrical_comp.is_built = True  # Make sure to set this flag
                        print(f"[DEBUG] Wire at {wire_pos} marked as completed")
                
                # Complete task and notify task system
                self._complete_task()
                return True
        
        return False

    def _is_at_task_position(self) -> bool:
        """Check if entity is close enough to work on task"""
        if not self._task_position:
            return False
            
        # Convert pixel coordinates to tile coordinates
        cat_x = self.entity.position.x / TILE_SIZE
        cat_y = self.entity.position.y / TILE_SIZE
        
        # Get task center in tile coordinates
        task_x = self._task_position[0]  # Remove +0.5 offset
        task_y = self._task_position[1]  # Remove +0.5 offset
        
        # Calculate distance to task center
        dx = abs(task_x - cat_x)
        dy = abs(task_y - cat_y)
        
        # Use a larger working radius and check Manhattan distance
        working_radius = 2.0  # Increased from 1.5
        is_in_range = (dx + dy) <= working_radius  # Use Manhattan distance instead of separate checks
        
        return is_in_range

    def _complete_task(self) -> None:
        """Handle task completion"""
        if self.current_task:
            # Use task system to handle completion
            self.entity.game_state.task_system.complete_task(self.current_task)
            self.current_task = None
            self._task_position = None
            self._work_progress = 0
            self._task_complete = True
            self._is_building = False

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Render task progress if working"""
        if not self.current_task or not self._is_at_task_position():
            return

        # Draw work progress indicator
        zoom_level = self.entity.game_state.zoom_level
        screen_x = (self.entity.position.x - camera_x) * zoom_level
        screen_y = (self.entity.position.y - camera_y) * zoom_level
        
        progress = self._work_progress / self._work_time
        width = 40 * zoom_level * progress
        
        # Progress bar background
        pygame.draw.rect(surface, (100, 100, 100),
                        (screen_x - 20 * zoom_level,
                         screen_y - 30 * zoom_level,
                         40 * zoom_level, 5 * zoom_level))
        
        # Progress bar fill
        pygame.draw.rect(surface, (50, 200, 50),
                        (screen_x - 20 * zoom_level,
                         screen_y - 30 * zoom_level,
                         width, 5 * zoom_level)) 

    def get_current_task(self):
        """Get the current task (compatibility method for debug UI)"""
        return self.current_task

    def get_wire_task_info(self):
        """Get wire task info (compatibility method for debug UI)"""
        if not self.current_task or not self._task_position:
            return None
        
        return {
            'position': self._task_position,
            'queue': []  # Wire queue implementation can be added later if needed
        } 

    @property
    def progress(self) -> float:
        """Get current work progress"""
        return self.current_task._work_progress if self.current_task else 0.0

    @property
    def required_progress(self) -> float:
        """Get required work time"""
        return self.current_task.work_time if self.current_task else 2.0 