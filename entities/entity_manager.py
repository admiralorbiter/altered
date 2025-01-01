from utils.config import TILE_SIZE


class EntityManager:
    """
    Central manager for all game entities and items.
    Handles entity lifecycle, updates, rendering, and spatial queries.
    """
    def __init__(self, game_state):
        self.game_state = game_state
        self.entities = []  # List of all active entities
        self.items = []     # List of all items in the world
        
    def add_entity(self, entity):
        """
        Add a new entity to the game world.
        Sets up game state reference and adds to update list.
        
        Args:
            entity: Entity instance to add
        """
        entity.game_state = self.game_state
        self.entities.append(entity)
        
    def add_item(self, item):
        """
        Add a new item to the game world.
        Sets up game state reference and adds to item list.
        
        Args:
            item: Item instance to add
        """
        item.game_state = self.game_state
        self.items.append(item)
        
    def remove_item(self, item):
        """
        Remove an item from the game world.
        
        Args:
            item: Item instance to remove
        """
        if item in self.items:
            self.items.remove(item)
            
    def update(self, dt):
        """
        Update all active entities.
        Skips inactive entities for performance.
        
        Args:
            dt (float): Delta time since last update
        """
        for entity in self.entities:
            if entity.active:
                entity.update(dt)
                
    def render(self, surface, camera_x, camera_y):
        """
        Render all active entities and items.
        Handles camera offset for proper positioning.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
            camera_x, camera_y (float): Camera offset coordinates
        """
        # Render items first (under entities)
        for item in self.items:
            if item.active:
                item.render_with_offset(surface, camera_x, camera_y)
        
        # Then render entities
        for entity in self.entities:
            if entity.active:
                entity.render_with_offset(surface, camera_x, camera_y)
                
    def clear(self):
        self.entities.clear()
        self.items.clear()
        
    def is_tile_occupied(self, position: tuple, ignore_entity=None) -> bool:
        """
        Check if a tile position is occupied by any entity.
        Used for collision detection and pathfinding.
        
        Args:
            position (tuple): (x, y) tile coordinates to check
            ignore_entity: Optional entity to exclude from check
            
        Returns:
            bool: True if tile is occupied, False otherwise
        """
        tile_x, tile_y = position
        
        for entity in self.entities:
            if entity == ignore_entity or not entity.active:
                continue
                
            entity_tile = (int(entity.position.x // TILE_SIZE),
                          int(entity.position.y // TILE_SIZE))
            if entity_tile == position:
                return True
        return False 