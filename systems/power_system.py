from typing import Dict, Set, Tuple
from components.reactor_component import ReactorComponent
from components.life_support_component import LifeSupportComponent

class PowerSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.power_sources = {}  # Reactor -> available power
        self.power_consumers = {}  # Component -> required power
        self.powered_components = set()  # Currently powered components
        
    def register_power_source(self, reactor: ReactorComponent):
        """Register a reactor as a power source"""
        self.power_sources[reactor] = 10.0  # Each reactor provides 10 power
        
    def register_power_consumer(self, component, power_required: float):
        """Register a component that needs power"""
        self.power_consumers[component] = power_required
        
    def update(self):
        """Update power distribution"""
        self.powered_components.clear()
        available_power = {reactor: power for reactor, power in self.power_sources.items()}
        
        # For each consumer, try to find a connected power source
        for consumer, required_power in self.power_consumers.items():
            if self._find_power_path(consumer, required_power, available_power):
                self.powered_components.add(consumer)
                consumer.set_power_state(True)
            else:
                consumer.set_power_state(False)
    
    def _find_power_path(self, consumer, required_power: float, available_power: Dict) -> bool:
        """Find a path from consumer to a reactor with enough power"""
        visited = set()
        to_visit = set(consumer.connected_tiles)
        
        while to_visit:
            current = to_visit.pop()
            visited.add(current)
            
            # Get the component at this tile
            component = self.game_state.current_level.tilemap.get_electrical(current[0], current[1])
            if not component or not component.is_built:
                continue
                
            # If it's a reactor with enough power, use it
            if isinstance(component, ReactorComponent) and available_power.get(component, 0) >= required_power:
                available_power[component] -= required_power
                return True
                
            # Add connected tiles we haven't visited
            for tile in component.connected_tiles:
                if tile not in visited:
                    to_visit.add(tile)
                    
        return False 