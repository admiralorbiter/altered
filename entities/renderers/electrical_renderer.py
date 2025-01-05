from .renderer_registry import RendererRegistry

class ElectricalRendererSystem:
    def __init__(self):
        self.registry = RendererRegistry()
    
    def render(self, component, surface, screen_x, screen_y, zoom_level):
        """Render an electrical component using its appropriate renderer"""
        renderer = self.registry.get_renderer(component.type)
        if renderer:
            renderer.render(component, surface, screen_x, screen_y, zoom_level) 