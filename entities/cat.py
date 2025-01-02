import pygame
import random
from components.base_entity import Entity
from utils.config import TILE_SIZE
from components.movement_component import MovementComponent
from components.cat_render_component import CatRenderComponent
from components.health_component import HealthComponent
from components.hunger_component import HungerComponent
from components.cat_ai_component import CatAIComponent
from components.task_component import TaskComponent
from components.pathfinding_component import PathfindingComponent

class Cat(Entity):
    """
    Autonomous cat entity with complex AI behaviors, hunger system, and task handling.
    Uses component-based architecture for modularity and maintainability.
    """
    def __init__(self, x: int, y: int, game_state):
        # Set entity_id first before any component initialization
        self._entity_id = id(self)
        
        # Convert tile coordinates to pixel coordinates
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
                
        # Store game state reference
        self.game_state = game_state
        
        # Generate random cat attributes
        color = (random.randint(150, 200),
                random.randint(150, 200),
                random.randint(150, 200))
        speed = random.uniform(250, 350)
        
        # Add components
        self.renderer = self.add_component(CatRenderComponent(self, color))
        self.movement = self.add_component(MovementComponent(self, speed=speed))
        self.health = self.add_component(HealthComponent(self, max_health=100))
        self.hunger = self.add_component(HungerComponent(self))
        self.pathfinding = self.add_component(PathfindingComponent(self))
        self.ai = self.add_component(CatAIComponent(self))
        self.task = self.add_component(TaskComponent(self))
                
        # Initialize components
        for component in self.components.values():
            if hasattr(component, 'start'):
                component.start()

    def update(self, dt: float) -> None:
        """Update cat and all its components"""
        if not self.health.is_alive:
            return
        super().update(dt)

    @classmethod
    def from_dict(cls, data: dict, game_state) -> 'Cat':
        """Create a cat from serialized data"""
        cat = cls(
            int(data['position'][0] // TILE_SIZE),
            int(data['position'][1] // TILE_SIZE),
            game_state
        )
        
        # Restore component states
        if 'health' in data:
            cat.health.health = data['health']
        if 'morale' in data:
            cat.health.morale = data['morale']
            
        return cat

    def to_dict(self) -> dict:
        """Serialize cat state to dictionary"""
        return {
            'type': 'Cat',
            'position': [self.position.x, self.position.y],
            'health': self.health.health,
            'morale': self.health.morale
        } 

    @property
    def is_dead(self) -> bool:
        """Compatibility property for death state"""
        return not self.health.is_alive if self.health else True

    @property
    def state(self):
        """Compatibility property for direct state access"""
        return self.ai.state if self.ai else None

    @property
    def movement_handler(self):
        """Compatibility property for old movement handler access"""
        return self.movement

    @property
    def moving(self) -> bool:
        """Compatibility property for movement state"""
        return self.movement.moving if self.movement else False

    @property
    def task_handler(self):
        """Compatibility property for old task handler access"""
        if not hasattr(self, '_task_handler_wrapper'):
            # Create a wrapper that makes TaskComponent look like old TaskHandler
            class TaskHandlerWrapper:
                def __init__(self, task_component):
                    self.task_component = task_component
                    
                @property
                def current_task(self):
                    return self.task_component.current_task
                    
                @property
                def wire_task(self):
                    if not self.task_component.current_task:
                        return None
                    return (self.task_component._task_position, 'wire')
                    
                def has_task(self):
                    return self.task_component.has_task()
                    
                def get_task_position(self):
                    return self.task_component.get_task_position()
                    
                def get_current_task(self):
                    return self.task_component.get_current_task()
                    
                def get_wire_task_info(self):
                    return self.task_component.get_wire_task_info()
                    
            self._task_handler_wrapper = TaskHandlerWrapper(self.task)
        return self._task_handler_wrapper

    @property
    def ai_state(self):
        """Compatibility property for AI state access"""
        return self.ai.state if self.ai else None 

    @property
    def entity_id(self):
        """Unique identifier for this cat"""
        return self._entity_id 

    def take_damage(self, amount: float) -> None:
        """Delegate damage handling to HealthComponent"""
        if self.health:
            self.health.take_damage(amount) 