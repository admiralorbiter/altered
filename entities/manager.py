class EntityManager:
    def __init__(self):
        self.entities = []
        
    def add_entity(self, entity):
        self.entities.append(entity)
        
    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            
    def update(self, dt):
        for entity in self.entities:
            if entity.active:
                entity.update(dt)
            
    def render(self, surface):
        # Render all active entities
        for entity in self.entities:
            if entity.active:
                entity.render(surface)
                
    def clear(self):
        self.entities.clear() 