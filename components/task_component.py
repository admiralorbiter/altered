from components.base_component import Component
from components.movement_component import MovementComponent
from utils.types import TaskType
import pygame
from utils.config import TILE_SIZE

class TaskComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.current_task = None
        self._movement = None
        self._task_position = None
        self._work_progress = 0
        self._work_time = 0
        self._task_complete = False

    def start(self) -> None:
        """Get reference to movement component when starting"""
        self._movement = self.entity.get_component(MovementComponent)

    def has_task(self) -> bool:
        """Check if currently assigned to a task"""
        return self.current_task is not None

    def start_task(self, task) -> bool:
        """
        Attempt to start a new task
        
        Args:
            task: Task object to start
            
        Returns:
            bool: True if task was successfully started
        """
        if self.current_task:
            return False
            
        self.current_task = task
        self._task_position = task.position
        self._work_progress = 0
        self._work_time = task.work_time
        self._task_complete = False
        return True

    def stop(self) -> None:
        """Stop current task"""
        if self.current_task:
            self.current_task.abandon()
            self.current_task = None
            self._task_position = None
            self._work_progress = 0
            self._task_complete = False

    def get_task_position(self) -> tuple[int, int]:
        """Get current task position in tile coordinates"""
        return self._task_position if self._task_position else None

    def update(self, dt: float) -> None:
        """
        Update task progress
        
        Args:
            dt: Delta time since last update
        """
        if not self.current_task:
            return

        # Check if we're close enough to work
        if not self._is_at_task_position():
            return

        # Update work progress
        self._work_progress += dt
        
        # Check for task completion
        if self._work_progress >= self._work_time:
            self._complete_task()

    def _is_at_task_position(self) -> bool:
        """Check if entity is close enough to work on task"""
        if not self._task_position:
            return False
            
        current_tile = (
            int(self.entity.position.x // TILE_SIZE),
            int(self.entity.position.y // TILE_SIZE)
        )
        
        dx = abs(self._task_position[0] - current_tile[0])
        dy = abs(self._task_position[1] - current_tile[1])
        
        return dx <= 1 and dy <= 1

    def _complete_task(self) -> None:
        """Handle task completion"""
        if self.current_task:
            self.current_task.complete()
            self.current_task = None
            self._task_position = None
            self._work_progress = 0
            self._task_complete = True

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