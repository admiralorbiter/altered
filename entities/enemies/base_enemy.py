from components.base_entity import Entity
from abc import ABC, abstractmethod
import pygame
from systems.capture_system import CaptureState
from utils.config import *
import random

from utils.pathfinding import find_path

class BaseEnemy(Entity, ABC):
    """
    Abstract base class for all enemy entities in the game.
    Provides core enemy functionality including AI states, pathfinding, and capture mechanics.
    """
    def __init__(self, x, y):
        super().__init__(x, y)
        
        # Movement and positioning constraints
        self.min_distance = TILE_SIZE * 0.9  # Minimum distance to maintain from target
        
        # AI state management
        self.state = 'idle'  # Current AI state: 'idle', 'patrol', 'chase', 'attack'
        self.target = None   # Current target entity (alien or cat)
        self.path = None     # Current pathfinding route
        self.current_waypoint = 0  # Index of current waypoint in path
        self.moving = False  # Whether enemy is currently moving
        self.target_position = None  # Destination position
        self.path_update_timer = 0   # Timer for path recalculation
        
        # Patrol behavior configuration
        self.patrol_points = []  # List of patrol waypoints
        self.current_patrol_index = 0  # Current patrol point index
        
        # Detection and combat properties
        self.wander_radius = 5  # Random movement radius in tiles
        self.detection_range = TILE_SIZE * 5  # Range for detecting targets
        self.attack_range = TILE_SIZE * 1.5   # Range for initiating attacks
        
        # Capture system integration
        self.capture_state = CaptureState.NONE  # Current capture status
        self.unconscious_timer = 0  # Timer for unconscious state
        self.carrier = None  # Reference to entity carrying this enemy
        self.awareness_level = 0  # Awareness of surroundings (0-1)
        self.struggle_chance = 0.1  # Probability to break free when captured
        
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
        """
        Updates the enemy's AI state based on nearby targets and current conditions.
        Handles target detection, state transitions, and combat engagement.
        
        Args:
            dt (float): Delta time since last update
            game_state: Current game state containing level and entity information
        """
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
        """
        Handles collision resolution between entities to prevent overlapping.
        Implements basic separation behavior when entities get too close.
        
        Args:
            game_state: Current game state for entity access
            
        Returns:
            bool: True if separation was performed
        """
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

    def is_aware_of(self, entity):
        """Check if enemy is aware of the given entity"""
        if self.capture_state in [CaptureState.UNCONSCIOUS, CaptureState.BEING_CARRIED]:
            return False
            
        if self.awareness_level > 0:
            distance = (entity.position - self.position).length()
            return distance < self.detection_range
        return False
        
    def update(self, dt):
        # Handle captured state first
        if self.capture_state == CaptureState.UNCONSCIOUS:
            self.unconscious_timer -= dt
            if self.unconscious_timer <= 0:
                self.capture_state = CaptureState.NONE
                return
        elif self.capture_state == CaptureState.BEING_CARRIED:
            # Update position to follow carrier
            if self.carrier:
                self.position = self.carrier.position
                # Chance to break free
                if random.random() < self.struggle_chance * dt:
                    self.capture_state = CaptureState.NONE
                    self.carrier.carrying_target = None
                    self.carrier = None
            return
            
        # Only proceed with normal updates if not captured
        if self.capture_state == CaptureState.NONE:
            super().update(dt)
            
    def render_with_offset(self, surface, camera_x, camera_y):
        if not self.active:
            return
            
        screen_x = (self.position.x - camera_x) * self.game_state.zoom_level
        screen_y = (self.position.y - camera_y) * self.game_state.zoom_level
        
        # Draw capture glow effect
        if self.capture_state == CaptureState.BEING_CARRIED:
            glow_radius = int(30 * self.game_state.zoom_level)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 0, 100), 
                             (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, 
                        (screen_x - glow_radius, 
                         screen_y - glow_radius))
        
        # Continue with normal rendering
        super().render_with_offset(surface, camera_x, camera_y) 