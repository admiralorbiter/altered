from components.base_component import Component

class HealthComponent(Component):
    def __init__(self, entity, max_health=100, max_morale=100):
        super().__init__(entity)
        self.max_health = max_health
        self.health = max_health
        self.max_morale = max_morale
        self.morale = max_morale
        self.is_corpse = False

    def take_damage(self, amount: float) -> None:
        """Reduce health by amount, clamped to 0"""
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self._handle_death()

    def heal(self, amount: float) -> None:
        """Increase health by amount, clamped to max_health"""
        if self.is_corpse:  # Can't heal corpses
            return
        self.health = min(self.max_health, self.health + amount)

    def change_morale(self, amount: float) -> None:
        """Change morale by amount, clamped between 0 and max_morale"""
        if self.is_corpse:  # Corpses don't have morale
            return
        self.morale = max(0, min(self.max_morale, self.morale + amount))

    def _handle_death(self) -> None:
        """Handle entity death and transition to corpse state"""
        self.is_corpse = True
        self.health = 0
        self.morale = 0
        
        # Disable components that shouldn't work when dead
        if hasattr(self.entity, 'movement'):
            self.entity.movement.enabled = False
        if hasattr(self.entity, 'ai'):
            self.entity.ai.enabled = False
        if hasattr(self.entity, 'task'):
            self.entity.task.enabled = False
        if hasattr(self.entity, 'pathfinding'):
            self.entity.pathfinding.enabled = False

    @property
    def is_alive(self) -> bool:
        """Check if entity is alive"""
        return self.health > 0 