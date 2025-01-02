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
        if task.is_assigned() and not task.is_assigned_to(self.entity):
            return False
            
        self.current_task = task
        self._task_position = task.position
        self._work_progress = 0
        self._work_time = getattr(task, 'work_time', 2.0)
        
        # Now actually assign and remove from available pool
        task.assign_to(self.entity)
        if task in self.entity.game_state.task_system.available_tasks:
            self.entity.game_state.task_system.available_tasks.remove(task)
        
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
        """Update task progress"""
        if not self.current_task:
            return False
        
        # Only handle wire construction tasks
        if self.current_task.type != TaskType.WIRE_CONSTRUCTION:
            return False
        
        # Check if we're at the task position
        if not self._is_at_task_position():
            return False
        
        # Start construction if not already building
        if not self._is_building:
            self._is_building = True
        
        # Update work progress
        old_progress = self._work_progress
        self._work_progress += dt
        
        # Update wire construction progress in wire system
        wire_system = self.entity.game_state.wire_system
        if not wire_system.update_construction_progress(self._task_position, dt):
            return False
        
        if self._work_progress >= self._work_time:
            if not wire_system.complete_wire_construction(self._task_position):
                return False
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
        task_x = self._task_position[0]
        task_y = self._task_position[1]
        
        # Calculate Manhattan distance (grid-based distance)
        manhattan_dist = abs(task_x - cat_x) + abs(task_y - cat_y)
        
        # More lenient range check and "sticky" behavior
        is_in_range = manhattan_dist <= 2.0
        if hasattr(self, '_last_in_range') and self._last_in_range:
            # If we were in range before, be more lenient about leaving
            is_in_range = manhattan_dist <= 2.2
        
        self._last_in_range = is_in_range
        return is_in_range

    def _complete_task(self) -> None:
        """Handle task completion"""
        if not self.current_task:
            return
        
        print(f"[TASK DEBUG] Completing task at {self._task_position}")  # Debug line
        self.entity.game_state.task_system.complete_task(self.current_task)
        self.current_task = None
        self._task_position = None
        self._work_progress = 0
        self._is_building = False  # Make sure to reset building state
        
        # Reset any movement restrictions that might have been set
        if self._movement:
            self._movement.allow_movement()

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