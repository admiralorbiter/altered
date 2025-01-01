# Standard library and third-party imports
import pygame
import sys
from utils.config import *
from utils.settings_manager import load_settings
from states.menu_state import MenuState
from states.game_state import GameState
from states.pause_menu_state import PauseMenuState
from states.slot_select_state import SlotSelectState
from states.settings_state import SettingsState

class Game:
    """
    Main game class that handles the game loop, state management, and core functionality.
    Acts as the central controller for the entire application.
    """
    def __init__(self):
        """
        Initialize the game, set up the display, and create game states.
        Sets up pygame, creates the window, and initializes core game components.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.delta_time = 0  # Time since last frame, used for frame-independent movement
        
        # Load user settings from configuration file
        self.settings = load_settings()
        
        # Initialize all game states and store them in a dictionary for easy access
        self.states = {
            'menu': MenuState(self),
            'game': GameState(self),
            'pause': PauseMenuState(self),
            'slot_select': SlotSelectState(self, mode='save'),
            'settings': SettingsState(self)
        }
        self.current_state = self.states['menu']  # Set initial state to menu

    def change_state(self, state_name):
        """
        Switch between different game states (menu, game, pause, etc.).
        
        Args:
            state_name (str): Key of the state to switch to
        """
        self.current_state.exit_state()  # Clean up current state
        self.current_state = self.states[state_name]  # Switch to new state
        self.current_state.enter_state()  # Initialize new state

    def handle_events(self):
        """
        Process all pygame events and delegate them to the current state.
        Handles global events (like quitting) and passes others to the active state.
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        self.current_state.handle_events(events)

    def update(self):
        """
        Update the game logic for the current frame.
        Delegates update responsibility to the current state.
        """
        self.current_state.update(self.delta_time)

    def render(self):
        """
        Render the current frame to the screen.
        Delegates rendering responsibility to the current state and updates the display.
        """
        self.current_state.render(self.screen)
        pygame.display.flip()  # Update the full display

    def run(self):
        """
        Main game loop that keeps the game running.
        Handles timing, updates, and rendering until the game is closed.
        """
        while self.running:
            self.delta_time = self.clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
            self.handle_events()
            self.update()
            self.render()

        pygame.quit()
        sys.exit()

def main():
    """
    Entry point of the application.
    Creates and runs the game instance.
    """
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

