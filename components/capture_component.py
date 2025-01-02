import pygame
from components.base_component import Component
from typing import Optional
from enum import Enum
from components.movement_component import MovementComponent
from components.selectable_component import SelectableComponent
from utils.config import TILE_SIZE

class CaptureState(Enum):
    NONE = "none"
    UNCONSCIOUS = "unconscious"
    CARRIED = "carried"

class CaptureComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.carrying_target = None
        self.capture_range = TILE_SIZE * 2  # Default capture range
        self.capture_strength = 50
        self.capture_state = CaptureState.NONE
        self.carrier = None

    def can_capture(self, target) -> bool:
        """Check if target is within capture range"""
        target_capture = target.get_component(CaptureComponent)
        if not target_capture:
            return False
            
        distance = (target.position - self.entity.position).length()
        return distance <= self.capture_range

    def attempt_capture(self, target) -> bool:
        """
        Attempt to capture a target entity.
        Handles both knockout and carrying mechanics.
        """
        if not self.can_capture(target):
            return False
            
        target_capture = target.get_component(CaptureComponent)
        if not target_capture:
            return False

        # If target is already being carried, ignore
        if target_capture.capture_state == CaptureState.CARRIED:
            return False

        # If we're already carrying someone, release them first
        if self.carrying_target:
            self.release_target()

        # Handle different capture states
        if target_capture.capture_state == CaptureState.NONE:
            success = self.attempt_knockout(target)
            if success:
                # Start carrying immediately after knockout
                self.start_carrying(target)
            return success
        elif target_capture.capture_state == CaptureState.UNCONSCIOUS:
            return self.start_carrying(target)
        return False

    def attempt_knockout(self, target) -> bool:
        """Attempt to knock out the target"""
        target_capture = target.get_component(CaptureComponent)
        if target_capture:
            target_capture.capture_state = CaptureState.UNCONSCIOUS
            # Set unconscious timer on the target
            if hasattr(target, 'unconscious_timer'):
                target.unconscious_timer = 10.0  # 10 seconds unconscious
            return True
        return False

    def start_carrying(self, target) -> bool:
        """Start carrying an unconscious target"""
        target_capture = target.get_component(CaptureComponent)
        if target_capture and target_capture.capture_state == CaptureState.UNCONSCIOUS:
            self.carrying_target = target
            target_capture.capture_state = CaptureState.CARRIED
            target_capture.carrier = self.entity
            # Slow down carrier
            movement = self.entity.get_component(MovementComponent)
            if movement:
                movement.speed *= 0.6
            return True
        return False

    def release_target(self) -> None:
        """Release currently carried target"""
        if self.carrying_target:
            target_capture = self.carrying_target.get_component(CaptureComponent)
            if target_capture:
                target_capture.capture_state = CaptureState.NONE
                target_capture.carrier = None
            self.carrying_target = None
            # Restore normal speed
            movement = self.entity.get_component(MovementComponent)
            if movement:
                movement.speed /= 0.6

    def update(self, dt: float) -> None:
        """Update carried target position"""
        if self.carrying_target:
            self.carrying_target.position = self.entity.position

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Draw capture range and status indicators"""
        if self.entity.get_component(SelectableComponent).is_selected:
            # Get zoom level from game state
            zoom_level = self.entity.game_state.zoom_level
            
            # Calculate screen position with zoom
            screen_pos = (
                (self.entity.position.x - camera_x) * zoom_level,
                (self.entity.position.y - camera_y) * zoom_level
            )
            
            # Draw capture range circle scaled by zoom
            pygame.draw.circle(surface, (255, 0, 0), 
                             (int(screen_pos[0]), int(screen_pos[1])),
                             int(self.capture_range * zoom_level), 1)
            
            # Draw line to carried target
            if self.carrying_target:
                target_pos = (
                    (self.carrying_target.position.x - camera_x) * zoom_level,
                    (self.carrying_target.position.y - camera_y) * zoom_level
                )
                pygame.draw.line(surface, (255, 0, 0),
                               screen_pos,
                               target_pos, 2) 