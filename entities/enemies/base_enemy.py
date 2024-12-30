from entities.base_entity import Entity
from abc import ABC, abstractmethod
import pygame
from utils.config import *
import random

from utils.pathfinding import find_path

class BaseEnemy(Entity, ABC):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        # Add minimum distance to maintain from target
        self.min_distance = TILE_SIZE * 0.9  # Slightly less than one tile
        
        # AI properties
        self.state = 'idle'
        self.target = None
        self.path = None
        self.current_waypoint = 0
        self.moving = False
        self.target_position = None
        self.path_update_timer = 0
        
        # Patrol properties
        self.patrol_points = []
        self.current_patrol_index = 0
        
        # Configurable properties
        self.wander_radius = 5  # tiles
        self.detection_range = TILE_SIZE * 5
        self.attack_range = TILE_SIZE * 1.5
        
    def set_patrol_points(self, points):
        """Set patrol route for the enemy"""
        self.patrol_points = points
        self.current_patrol_index = 0
        
    def set_target_position(self, target_pos):
        """Set new target position and start moving"""
        self.target_position = target_pos
        self.moving = True
        
    def set_path(self, path):
        """Set new path and update waypoint"""
        self.path = path
        if path and len(path) > 1:
            self.current_waypoint = 1
            next_tile = path[self.current_waypoint]
            self.set_target_position(pygame.math.Vector2(
                (next_tile[0] + 0.5) * TILE_SIZE,
                (next_tile[1] + 0.5) * TILE_SIZE
            )) 
        
    def update_ai_state(self, dt, game_state):
        """Update AI state based on conditions"""
        # Find nearest target (alien or cat)
        nearest_target = None
        min_distance = float('inf')
        
        # Check aliens
        for alien in game_state.current_level.aliens:
            if alien.active:
                distance = (alien.position - self.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = alien
                    
        # Check cats
        for cat in game_state.current_level.cats:
            if cat.active and not cat.is_dead:
                distance = (cat.position - self.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = cat
        
        # Update state based on distance to nearest target
        if nearest_target:
            if min_distance <= self.attack_range:
                self.state = 'attack'
                self.target = nearest_target
            elif min_distance <= self.detection_range:
                self.state = 'chase'
                self.target = nearest_target
            else:
                self.state = 'patrol'
                self.target = None
        else:
            self.state = 'patrol'
            self.target = None 

    def handle_collision_separation(self, game_state):
        """Handle separation when entities overlap"""
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        
        # Check for other entities in the same tile or adjacent tiles
        for entity in game_state.current_level.entity_manager.entities:
            if entity == self or not entity.active:
                continue
            
            # Calculate actual distance between entities
            distance = (entity.position - self.position).length()
            if distance < TILE_SIZE * 0.9:  # If too close
                # Calculate separation vector
                diff = self.position - entity.position
                if diff.length() < 1:  # If exactly overlapping
                    diff = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                
                # Move away based on relative positions
                normalized_diff = diff.normalize()
                separation_distance = TILE_SIZE * 0.5
                
                # The entity with higher x coordinate moves right, lower moves left
                if self.position.x > entity.position.x:
                    self.position.x += separation_distance
                else:
                    self.position.x -= separation_distance
                    
                # Recalculate path with delay to prevent immediate collision
                if self.target and self.state == 'chase':
                    self.path_update_timer = 0.2  # Small delay before recalculating
                    self.moving = False
                return True
        return False 