from entities.base_entity import Entity
from abc import ABC, abstractmethod
import pygame
from utils.config import *

class BaseEnemy(Entity, ABC):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        # Basic enemy stats
        self.max_health = 100
        self.health = self.max_health
        self.attack_power = 10
        self.speed = 200
        self.detection_range = TILE_SIZE * 5  # 5 tiles detection range
        self.attack_range = TILE_SIZE * 1.5   # 1.5 tiles attack range
        
        # AI state
        self.state = 'idle'  # idle, patrol, chase, attack
        self.target = None
        self.patrol_points = []
        self.current_patrol_index = 0
        self.path = None
        self.current_waypoint = 0
        
        # Movement
        self.moving = False
        self.target_position = None
        
        # Size and scale properties
        self.base_size = pygame.Vector2(TILE_SIZE, TILE_SIZE)
        self.size = self.base_size.copy()
        
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.die()
            
    def die(self):
        self.active = False
        
    def set_patrol_points(self, points):
        """Set patrol points for the enemy"""
        self.patrol_points = points
        
    @abstractmethod
    def attack(self, target):
        """Implement specific attack behavior"""
        pass
        
    def update_ai_state(self, dt, game_state):
        """Update AI state based on conditions"""
        # Find nearest alien
        nearest_alien = None
        min_distance = float('inf')
        
        for alien in game_state.current_level.aliens:
            if alien.active:
                distance = (alien.position - self.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_alien = alien
                    
        # Update state based on distance to nearest alien
        if nearest_alien:
            if min_distance <= self.attack_range:
                self.state = 'attack'
                self.target = nearest_alien
            elif min_distance <= self.detection_range:
                self.state = 'chase'
                self.target = nearest_alien
            else:
                self.state = 'patrol'
                self.target = None
        else:
            self.state = 'patrol'
            self.target = None 