from utils.config import TILE_SIZE


class EntityManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.entities = []
        self.items = []
        
    def add_entity(self, entity):
        entity.game_state = self.game_state
        self.entities.append(entity)
        
    def add_item(self, item):
        item.game_state = self.game_state
        self.items.append(item)
        
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            
    def update(self, dt):
        for entity in self.entities:
            if entity.active:
                entity.update(dt)
                
    def render(self, surface, camera_x, camera_y):
        # Render all active entities and items
        for item in self.items:
            if item.active:
                item.render_with_offset(surface, camera_x, camera_y)
        
        for entity in self.entities:
            if entity.active:
                entity.render_with_offset(surface, camera_x, camera_y)
                
    def clear(self):
        self.entities.clear()
        self.items.clear()
        
    def is_tile_occupied(self, position: tuple, ignore_entity=None) -> bool:
        """Check if a tile is occupied by any entity"""
        tile_x, tile_y = position
        
        for entity in self.entities:
            if entity == ignore_entity or not entity.active:
                continue
                
            entity_tile = (int(entity.position.x // TILE_SIZE),
                          int(entity.position.y // TILE_SIZE))
            if entity_tile == position:
                return True
        return False 