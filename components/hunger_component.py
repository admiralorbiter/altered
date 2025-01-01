from components.base_component import Component


class HungerComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.hunger = 25
        self.max_hunger = 100
        self.hunger_rate = 2
        self.critical_hunger = 10

    @property
    def is_critical(self) -> bool:
        """Check if hunger is at critical level"""
        return self.hunger <= self.critical_hunger

    def feed(self, amount: float) -> None:
        """Feed the entity to restore hunger"""
        self.hunger = min(self.max_hunger, self.hunger + amount)

    def update(self, dt: float) -> None:
        """Update hunger level and apply damage if starving"""
        self.hunger = max(0, self.hunger - self.hunger_rate * dt)
        if self.hunger <= 0:
            self.entity.health.take_damage(5 * dt) 