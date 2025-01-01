import pygame
import math
from .base_state import State
from utils.config import *
from states.slot_select_state import SlotSelectState

class MenuState(State):
    """
    Main menu state handling game entry points and level selection.
    Features psychedelic background effect and interactive menu options.
    """
    def __init__(self, game):
        super().__init__(game)
        # Font and title setup
        self.font = pygame.font.Font(None, 74)
        self.title = self.font.render("ALTERED", True, WHITE)
        self.title_rect = self.title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        
        # Menu options with submenu for level selection
        self.main_menu = ['New Game', 'Load Game', 'Quit']
        self.level_menu = ['UFO Level', 'Abduction Level', 'Test Level', 'Back']
        
        # Menu state tracking
        self.current_menu = self.main_menu
        self.selected_option = 0
        self.in_level_select = False
        
        # Create text surfaces for options
        self.update_menu_surfaces()
        
        # Psychedelic effect parameters
        self.time = 0
        self.surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    def update_menu_surfaces(self):
        """
        Update menu text surfaces and positions.
        Called when switching between menus or initializing.
        """
        self.option_surfaces = []
        self.option_rects = []
        for i, option in enumerate(self.current_menu):
            text = self.font.render(option, True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 80))
            self.option_surfaces.append(text)
            self.option_rects.append(rect)
        
    def handle_events(self, events):
        """
        Handle menu navigation and selection events.
        Supports keyboard controls for menu interaction.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.current_menu)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.current_menu)
                elif event.key == pygame.K_RETURN:
                    self.handle_selection()
                elif event.key == pygame.K_ESCAPE and self.in_level_select:
                    self.return_to_main_menu()

    def return_to_main_menu(self):
        """Return to main menu from level select submenu"""
        self.current_menu = self.main_menu
        self.selected_option = 0
        self.in_level_select = False
        self.update_menu_surfaces()

    def handle_selection(self):
        """
        Process menu option selection.
        Handles navigation between menus and game state changes.
        """
        if not self.in_level_select:
            # Main menu options
            if self.current_menu[self.selected_option] == 'New Game':
                self.current_menu = self.level_menu
                self.selected_option = 0
                self.in_level_select = True
                self.update_menu_surfaces()
            elif self.current_menu[self.selected_option] == 'Load Game':
                self.game.states['slot_select'] = SlotSelectState(self.game, mode='load')
                self.game.change_state('slot_select')
            elif self.current_menu[self.selected_option] == 'Quit':
                self.game.running = False
        else:
            # Handle level selection
            if self.current_menu[self.selected_option] == 'UFO Level':
                self.game.change_state('game')
                self.game.states['game'].change_level('ufo')
            elif self.current_menu[self.selected_option] == 'Abduction Level':
                self.game.change_state('game')
                self.game.states['game'].change_level('abduction')
            elif self.current_menu[self.selected_option] == 'Test Level':
                self.game.change_state('game')
                self.game.states['game'].change_level('test')
            elif self.current_menu[self.selected_option] == 'Back':
                self.return_to_main_menu()

    def update(self, dt):
        self.time += dt
        
    def render(self, screen):
        """
        Render menu with psychedelic background effect.
        Creates dynamic visual pattern and menu options.
        """
        # Create psychedelic background
        for x in range(0, WINDOW_WIDTH, 4):
            for y in range(0, WINDOW_HEIGHT, 4):
                dx = x - WINDOW_WIDTH // 2
                dy = y - WINDOW_HEIGHT // 2
                distance = math.sqrt(dx * dx + dy * dy)
                angle = math.atan2(dy, dx)
                swirl = math.sin(distance / 30 - self.time * 2 + angle * 3)
                
                r = (math.sin(self.time + swirl) * 127 + 128)
                g = (math.sin(self.time * 0.5 + swirl) * 127 + 128)
                b = (math.sin(self.time * 0.25 + swirl) * 127 + 128)
                
                pygame.draw.rect(screen, (r, g, b), (x, y, 4, 4))
        
        # Add darkening overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(100)
        screen.blit(overlay, (0, 0))
        
        # Draw title and menu options
        screen.blit(self.title, self.title_rect)
        
        # Draw menu options
        for i, (text, rect) in enumerate(zip(self.option_surfaces, self.option_rects)):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font.render(self.current_menu[i], True, color)
            screen.blit(text, rect) 