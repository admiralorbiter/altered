from enum import Enum
import random
import pygame
from utils.config import *

class CaptureState(Enum):
    NONE = 0
    MARKED = 1
    UNCONSCIOUS = 2
    BEING_CARRIED = 3
    CAPTURED = 4

class CaptureSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.marked_target = None
        self.capture_mode = False  # Toggle between lethal/non-lethal
        self.stealth_mode = False  # Toggle between stealth/force approach
        
    def mark_target(self, target):
        """Mark a target for capture"""
        if hasattr(target, 'capture_state'):
            self.marked_target = target
            target.capture_state = CaptureState.MARKED
            return True
        return False
        
    def attempt_knockout(self, attacker, target):
        """Attempt to knock out a target"""
        if not hasattr(target, 'capture_state'):
            return False
            
        # Check if we're in stealth and undetected
        if self.stealth_mode and not target.is_aware_of(attacker):
            success_chance = 0.95  # 95% chance in stealth
        else:
            # Base it on relative health/strength
            success_chance = 0.4 * (attacker.health / attacker.max_health)
            
        if random.random() < success_chance:
            target.capture_state = CaptureState.UNCONSCIOUS
            target.unconscious_timer = 10.0  # 10 seconds of unconsciousness
            return True
        return False
        
    def start_carrying(self, carrier, target):
        """Start carrying a captured target"""
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
        """Stop carrying a target"""
        if hasattr(carrier, 'carrying_target'):
            target = carrier.carrying_target
            target.capture_state = CaptureState.UNCONSCIOUS
            target.carrier = None
            carrier.carrying_target = None
            carrier.speed *= 2  # Restore normal speed
            
    def update(self, dt):
        """Update capture system state"""
        # Update unconscious timers
        for entity in self.game_state.current_level.entity_manager.entities:
            if hasattr(entity, 'capture_state') and entity.capture_state == CaptureState.UNCONSCIOUS:
                if hasattr(entity, 'unconscious_timer'):
                    entity.unconscious_timer -= dt
                    if entity.unconscious_timer <= 0:
                        entity.capture_state = CaptureState.NONE 