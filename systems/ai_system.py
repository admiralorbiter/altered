from utils.pathfinding import find_path
import pygame
from utils.config import *

class AISystem:
    def __init__(self):
        self.update_interval = 0.5  # Update AI every 0.5 seconds
        self.update_timer = 0
        
    def update(self, dt, game_state):
        self.update_timer += dt
        if self.update_timer >= self.update_interval:
            self.update_timer = 0
            self.update_enemy_behaviors(dt, game_state)
            
    def update_enemy_behaviors(self, dt, game_state):
        """Update all enemy AI behaviors"""
        for enemy in game_state.current_level.enemies:
            if not enemy.active:
                continue
                
            # Update AI state
            enemy.update_ai_state(dt, game_state)
            
            # Handle different states
            if enemy.state == 'patrol':
                self.handle_patrol_state(enemy, game_state)
            elif enemy.state == 'chase':
                self.handle_chase_state(enemy, game_state)
            elif enemy.state == 'attack':
                self.handle_attack_state(enemy, game_state)
                
    def handle_patrol_state(self, enemy, game_state):
        """Handle patrol behavior"""
        if not enemy.moving and enemy.patrol_points:
            current_tile = (int(enemy.position.x // TILE_SIZE),
                          int(enemy.position.y // TILE_SIZE))
            target_point = enemy.patrol_points[enemy.current_patrol_index]
            
            # Find path to next patrol point
            enemy.path = find_path(current_tile, target_point, game_state.current_level.tilemap)
            if enemy.path:
                enemy.current_waypoint = 1 if len(enemy.path) > 1 else 0
                next_tile = enemy.path[enemy.current_waypoint]
                enemy.target_position = pygame.math.Vector2(
                    (next_tile[0] + 0.5) * TILE_SIZE,
                    (next_tile[1] + 0.5) * TILE_SIZE
                )
                enemy.moving = True
                
            # Move to next patrol point
            enemy.current_patrol_index = (enemy.current_patrol_index + 1) % len(enemy.patrol_points)
                
    def handle_chase_state(self, enemy, game_state):
        """Handle chase behavior"""
        if enemy.target and enemy.target.active:
            current_tile = (int(enemy.position.x // TILE_SIZE),
                          int(enemy.position.y // TILE_SIZE))
            target_tile = (int(enemy.target.position.x // TILE_SIZE),
                         int(enemy.target.position.y // TILE_SIZE))
            
            # Update path to target every few frames
            if not enemy.moving or not enemy.path:
                enemy.path = find_path(current_tile, target_tile, game_state.current_level.tilemap)
                if enemy.path:
                    enemy.current_waypoint = 1 if len(enemy.path) > 1 else 0
                    next_tile = enemy.path[enemy.current_waypoint]
                    enemy.target_position = pygame.math.Vector2(
                        (next_tile[0] + 0.5) * TILE_SIZE,
                        (next_tile[1] + 0.5) * TILE_SIZE
                    )
                    enemy.moving = True
                    
    def handle_attack_state(self, enemy, game_state):
        """Handle attack behavior"""
        if enemy.target and enemy.target.active:
            enemy.attack(enemy.target) 