from components.base_entity import Entity
from abc import ABC, abstractmethod
import pygame
from systems.capture_system import CaptureState
from utils.config import *
import random
import math

from utils.pathfinding import find_path
from components.capture_component import CaptureComponent

class BaseEnemy(Entity, ABC):
    """
    Abstract base class for all enemy entities in the game.
    Provides core enemy functionality including AI states, pathfinding, and capture mechanics.
    """
    def __init__(self, x, y):
        super().__init__(x, y)
        
        # Add CaptureComponent to the enemy
        self.capture = self.add_component(CaptureComponent(self))
        
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
        
        # Field of View properties
        self.fov_angle = 90  # Field of view in degrees
        self.view_direction = pygame.math.Vector2(1, 0)  # Initial direction (facing right)
        self.rotation_speed = 180  # Degrees per second
        
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
        """Updates the enemy's AI state based on nearby targets"""
        nearest_target = None
        min_distance = float('inf')
        
        # Check aliens
        for alien in game_state.current_level.aliens:
            if (alien.active and 
                not (hasattr(alien, 'health') and alien.health.is_corpse) and 
                self.is_aware_of(alien)):
                distance = (alien.position - self.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = alien
                    
        # Check cats
        for cat in game_state.current_level.cats:
            if cat.active and not cat.is_dead and self.is_aware_of(cat):
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
            # If we lose sight of target, keep last known position for a short time
            if self.state == 'chase' and self.target:
                # Keep chasing for a short time even if target leaves FOV
                if not hasattr(self, 'lost_target_timer'):
                    self.lost_target_timer = 1.0  # 1 second memory
                self.lost_target_timer -= dt
                if self.lost_target_timer <= 0:
                    self.state = 'patrol'
                    self.target = None
            else:
                self.state = 'patrol'
                self.target = None

    def handle_collision_separation(self, game_state):
        """Enhanced separation with smoother resolution"""
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        
        # Add small random offset to prevent perfect alignment
        separation_distance = TILE_SIZE * (0.5 + random.uniform(-0.1, 0.1))
        
        # Check immediate neighbors only
        for entity in game_state.current_level.entity_manager.get_nearby_entities(current_tile):
            if entity == self or not entity.active:
                continue
            
            distance = (entity.position - self.position).length()
            if distance < TILE_SIZE:
                # Calculate smoother separation vector
                diff = self.position - entity.position
                if diff.length() < 1:
                    diff = pygame.math.Vector2(random.uniform(-1, 1), 
                                             random.uniform(-1, 1))
                
                # Apply separation with slight randomness
                normalized_diff = diff.normalize()
                self.position += normalized_diff * separation_distance
                return True
        return False 

    def is_aware_of(self, entity):
        """Check if enemy is aware of the given entity using FOV"""
        if self.capture_state in [CaptureState.UNCONSCIOUS, CaptureState.BEING_CARRIED]:
            return False
            
        # Calculate vector to target
        to_target = entity.position - self.position
        distance = to_target.length()
        
        # Check if within detection range
        if distance > self.detection_range:
            return False
            
        # Check if within FOV angle
        if distance > 0:  # Prevent division by zero
            # Calculate angle between view direction and target
            angle = math.degrees(
                math.acos(
                    max(-1.0, min(1.0, to_target.normalize().dot(self.view_direction)))
                )
            )
            return angle <= self.fov_angle / 2
                
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

    def update_view_direction(self, dt):
        """Update view direction based on movement or target"""
        if self.state == 'chase' and self.target:
            # When chasing, always face the target
            to_target = self.target.position - self.position
            if to_target.length_squared() > 0:
                # Ensure view direction points towards target
                self.view_direction = to_target.normalize()
        elif self.moving and self.target_position:
            # When moving (patrolling), face movement direction
            movement_dir = self.target_position - self.position
            if movement_dir.length_squared() > 0:
                # Ensure view direction points in movement direction
                self.view_direction = movement_dir.normalize()
                
        # Ensure view_direction is always normalized
        if self.view_direction.length_squared() > 0:
            self.view_direction.normalize_ip() 