from enum import Enum
import random
import pygame
from utils.config import *

# Enums for tracking the various states an entity can be in during capture
class CaptureState(Enum):
    NONE = 0          # Default state, not involved in capture
    MARKED = 1        # Target has been marked for capture
    UNCONSCIOUS = 2   # Target has been knocked out
    BEING_CARRIED = 3 # Target is being carried by another entity
    CAPTURED = 4      # Target has been successfully captured

class CaptureSystem:
    """
    Manages the capture mechanics in the game, including marking targets,
    knocking them out, and carrying unconscious entities.
    """
    def __init__(self, game_state):
        """
        Initialize the capture system.
        
        Args:
            game_state: Reference to the main game state object
        """
        self.game_state = game_state
        self.marked_target = None      # Currently marked target for capture
        self.capture_mode = False      # Toggle between lethal/non-lethal
        self.stealth_mode = False      # Toggle between stealth/force approach
        
    def mark_target(self, target):
        """
        Mark a target for capture.
        
        Args:
            target: The entity to be marked
            
        Returns:
            bool: True if marking was successful, False otherwise
        """
        if hasattr(target, 'capture_state'):
            self.marked_target = target
            target.capture_state = CaptureState.MARKED
            return True
        return False
        
    def attempt_knockout(self, attacker, target):
        """
        Attempt to knock out a target. Success chance varies based on stealth
        and relative health.
        
        Args:
            attacker: The entity attempting the knockout
            target: The entity being targeted
            
        Returns:
            bool: True if knockout was successful, False otherwise
        """
        if not hasattr(target, 'capture_state'):
            return False
            
        # Calculate success chance based on approach
        if self.stealth_mode and not target.is_aware_of(attacker):
            success_chance = 0.95  # High chance of success when undetected
        else:
            # Lower chance in combat, based on attacker's health ratio
            success_chance = 0.4 * (attacker.health / attacker.max_health)
            
        if random.random() < success_chance:
            target.capture_state = CaptureState.UNCONSCIOUS
            target.unconscious_timer = 10.0  # 10 seconds of unconsciousness
            return True
        return False
        
    def start_carrying(self, carrier, target):
        """
        Start carrying an unconscious target. Reduces carrier's speed while active.
        
        Args:
            carrier: The entity doing the carrying
            target: The unconscious entity to be carried
            
        Returns:
            bool: True if carrying started successfully, False otherwise
        """
        if not hasattr(target, 'capture_state'):
            return False
            
        if target.capture_state == CaptureState.UNCONSCIOUS:
            target.capture_state = CaptureState.BEING_CARRIED
            target.carrier = carrier
            carrier.carrying_target = target
            carrier.speed *= 0.5  # Slow down while carrying
            return True
        return False
        
    def stop_carrying(self, carrier):
        """
        Stop carrying a target and restore carrier's normal speed.
        
        Args:
            carrier: The entity that was carrying a target
        """
        if hasattr(carrier, 'carrying_target'):
            target = carrier.carrying_target
            target.capture_state = CaptureState.UNCONSCIOUS
            target.carrier = None
            carrier.carrying_target = None
            carrier.speed *= 2  # Restore normal speed
            
    def update(self, dt):
        """
        Update the capture system state, including unconscious timer management.
        
        Args:
            dt: Delta time since last update (in seconds)
        """
        # Update unconscious timers
        for entity in self.game_state.current_level.entity_manager.entities:
            if hasattr(entity, 'capture_state') and entity.capture_state == CaptureState.UNCONSCIOUS:
                if hasattr(entity, 'unconscious_timer'):
                    entity.unconscious_timer -= dt
                    if entity.unconscious_timer <= 0:
                        entity.capture_state = CaptureState.NONE 