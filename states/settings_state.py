import pygame

from states.pause_menu_state import PauseMenuState
from .base_state import State
from utils.config import *
from utils.settings_manager import load_settings, save_settings

class SettingsState(State):
    """
    Settings menu state handling game configuration options.
    Features volume control and persistent settings storage.
    """
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 64)
        
        # Load saved settings from storage
        self.settings = load_settings()
        
        # Settings configuration
        self.options = [f'Volume: {self.settings["volume"]}%', 'Back']
        self.selected_option = 0
        self.volume = self.settings["volume"]
        
        # Create text surfaces for menu options
        self.text_surfaces = []
        self.text_rects = []
        
        # Initialize menu text elements
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + i * 80))
            self.text_surfaces.append(text)
            self.text_rects.append(rect)
    
    def handle_events(self, events):
        """
        Handle settings menu navigation and value adjustments.
        Supports keyboard controls for menu interaction and volume control.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.return_to_previous()
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.options[self.selected_option] == 'Back':
                        self.return_to_previous()
                elif self.selected_option == 0:  # Volume control
                    if event.key == pygame.K_LEFT:
                        self.volume = max(0, self.volume - 10)
                        self.update_volume_text()
                    elif event.key == pygame.K_RIGHT:
                        self.volume = min(100, self.volume + 10)
                        self.update_volume_text()
    
    def update_volume_text(self):
        """
        Update volume display and save changes.
        Persists volume setting to storage.
        """
        self.options[0] = f'Volume: {self.volume}%'
        self.text_surfaces[0] = self.font.render(self.options[0], True, WHITE)
        # Save settings when volume changes
        self.settings["volume"] = self.volume
        save_settings(self.settings)
    
    def return_to_previous(self):
        """
        Return to the previous menu state.
        Handles both pause menu and main menu returns.
        """
        # Return to pause menu if we came from there, otherwise main menu
        previous_state = 'pause' if isinstance(self.game.states['pause'], PauseMenuState) else 'menu'
        self.game.change_state(previous_state)
        
    def update(self, dt):
        pass
        
    def render(self, screen):
        """
        Render settings menu with interactive elements.
        Displays volume control and navigation options.
        """
        # Draw dark background
        screen.fill(BLACK)
        
        # Draw title
        title = self.font.render("Settings", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 6))
        screen.blit(title, title_rect)
        
        # Draw options with selection highlight
        for i, (text, rect) in enumerate(zip(self.text_surfaces, self.text_rects)):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font.render(self.options[i], True, color)
            screen.blit(text, rect)
            
            # Draw volume control indicators when selected
            if i == 0 and self.selected_option == 0:
                text = self.font.render("<   >", True, (255, 255, 0))
                rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
                screen.blit(text, rect) 