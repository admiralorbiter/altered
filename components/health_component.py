from components.base_component import Component

class HealthComponent(Component):
    def __init__(self, entity, max_health=100, max_morale=100):
        super().__init__(entity)
        self.max_health = max_health
        self.health = max_health
        self.max_morale = max_morale
        self.morale = max_morale

    def take_damage(self, amount: float) -> None:
        """Reduce health by amount, clamped to 0"""
        self.health = max(0, self.health - amount)

    def heal(self, amount: float) -> None:
        """Increase health by amount, clamped to max_health"""
        self.health = min(self.max_health, self.health + amount)

    def change_morale(self, amount: float) -> None:
        """Change morale by amount, clamped between 0 and max_morale"""
        self.morale = max(0, min(self.max_morale, self.morale + amount))

    @property
    def is_alive(self) -> bool:
        """Check if entity is alive"""
        return self.health > 0 