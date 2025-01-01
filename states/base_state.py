from abc import ABC, abstractmethod
import pygame

class State(ABC):
    """
    Abstract base class for game states (e.g., menu, gameplay, pause).
    Provides core functionality for state management and transitions.
    """
    def __init__(self, game):
        """
        Initialize the state with a reference to the game instance.
        
        Args:
            game: Main game instance that manages states
        """
        self.game = game

    @abstractmethod
    def handle_events(self, events):
        """
        Process input events for the current state.
        Must be implemented by concrete states.
        
        Args:
            events (list): List of pygame events to process
        """
        pass

    @abstractmethod
    def update(self, dt):
        """
        Update state logic based on elapsed time.
        Must be implemented by concrete states.
        
        Args:
            dt (float): Delta time since last update in seconds
        """
        pass

    @abstractmethod
    def render(self, screen):
        """
        Render the current state to the screen.
        Must be implemented by concrete states.
        
        Args:
            screen (pygame.Surface): Target surface for rendering
        """
        pass

    def enter_state(self):
        """
        Called when entering this state.
        Override to handle state initialization.
        """
        pass

    def exit_state(self):
        """
        Called when exiting this state.
        Override to handle cleanup.
        """
        pass 