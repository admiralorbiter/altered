from typing import Dict, List
import pygame
from utils.config import *

class MutationSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.available_mutations = 999  # Temporary unlimited mutations until resource system
        
        # Define all possible mutations
        self.mutations = {
            "quick_paws": {
                "id": "quick_paws",
                "name": "Quick Paws",
                "description": "Cats can occasionally skip a tile when moving",
                "cost": 100,
                "icon": "⚡",
                "stats": ["+1 Movement Range", "50% Skip Chance"],
                "unlocked": False,
                "prerequisites": [],
                "apply": self._apply_quick_paws,
                "remove": self._remove_quick_paws
            }
        }
        
        # Track which mutations are active
        self.active_mutations: Dict[str, bool] = {
            mutation_id: False for mutation_id in self.mutations.keys()
        }

    def can_unlock(self, mutation_id: str) -> bool:
        """Check if a mutation can be unlocked"""
        mutation = self.mutations.get(mutation_id)
        if not mutation:
            return False
            
        # Check if already unlocked
        if mutation["unlocked"]:
            return False
            
        # Check if we have enough resources
        if self.available_mutations < mutation["cost"]:
            return False
            
        return True

    def unlock_mutation(self, mutation_id: str) -> bool:
        """Attempt to unlock and apply a mutation"""
        if not self.can_unlock(mutation_id):
            return False
            
        mutation = self.mutations[mutation_id]
        
        # Deduct cost
        self.available_mutations -= mutation["cost"]
        
        # Mark as unlocked and active
        mutation["unlocked"] = True
        self.active_mutations[mutation_id] = True
        
        # Apply the mutation effect
        mutation["apply"]()
        return True

    def _apply_quick_paws(self):
        """Apply the Quick Paws mutation effect to all cats"""
        for cat in self.game_state.current_level.cats:
            if not hasattr(cat, 'movement_skip_chance'):
                cat.movement_skip_chance = 0.0
            cat.movement_skip_chance = 0.5  # 50% chance to skip a tile
            cat.base_movement_range += 1

    def _remove_quick_paws(self):
        """Remove the Quick Paws mutation effect from all cats"""
        for cat in self.game_state.current_level.cats:
            cat.movement_skip_chance = 0.0
            cat.base_movement_range -= 1 