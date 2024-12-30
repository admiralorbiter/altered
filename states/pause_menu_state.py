import pygame
from .base_state import State
from utils.config import *
from utils.save_load import get_save_files
from .slot_select_state import SlotSelectState

class PauseMenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 64)
        
        # Menu options
        self.options = ['Resume', 'Save', 'Load', 'Settings', 'Quit to Menu']
        self.selected_option = 0
        
        # Create text surfaces
        self.text_surfaces = []
        self.text_rects = []
        
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + i * 80))
            self.text_surfaces.append(text)
            self.text_rects.append(rect)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state('game')
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.handle_selection()
    
    def handle_selection(self):
        if self.options[self.selected_option] == 'Resume':
            self.game.change_state('game')
        elif self.options[self.selected_option] == 'Save':
            self.game.states['slot_select'] = SlotSelectState(self.game, mode='save')
            self.game.change_state('slot_select')
        elif self.options[self.selected_option] == 'Load':
            self.game.states['slot_select'] = SlotSelectState(self.game, mode='load')
            self.game.change_state('slot_select')
        elif self.options[self.selected_option] == 'Settings':
            self.game.change_state('settings')
        elif self.options[self.selected_option] == 'Quit to Menu':
            self.game.change_state('menu')

    def update(self, dt):
        pass
        
    def render(self, screen):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw menu options
        for i, (text, rect) in enumerate(zip(self.text_surfaces, self.text_rects)):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font.render(self.options[i], True, color)
            screen.blit(text, rect) 