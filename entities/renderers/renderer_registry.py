from typing import Dict, Type
from .base_renderer import BaseElectricalRenderer
from .wire_renderer import WireRenderer
from .reactor_renderer import ReactorRenderer
from .lifesupport_renderer import LifeSupportRenderer

class RendererRegistry:
    """Central registry for all component renderers"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the renderer registry with all available renderers"""
        self.renderers = {
            'wire': WireRenderer(),
            'reactor': ReactorRenderer(),
            'life_support': LifeSupportRenderer(),
        }
    
    def get_renderer(self, component_type: str) -> BaseElectricalRenderer:
        """Get the appropriate renderer for a component type"""
        return self.renderers.get(component_type)
    
    def register_renderer(self, component_type: str, renderer: BaseElectricalRenderer) -> None:
        """Register a new renderer"""
        self.renderers[component_type] = renderer 