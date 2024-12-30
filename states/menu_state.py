import pygame
import math
from .base_state import State
from utils.config import *
from states.slot_select_state import SlotSelectState

class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 74)
        self.title = self.font.render("ALTERED", True, WHITE)
        self.title_rect = self.title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        
        # Menu options
        self.options = ['New Game', 'Load Game', 'Quit']
        self.selected_option = 0
        
        # Create text surfaces for options
        self.option_surfaces = []
        self.option_rects = []
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 80))
            self.option_surfaces.append(text)
            self.option_rects.append(rect)
        
        # Psychedelic effect parameters
        self.time = 0
        self.surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.handle_selection()

    def handle_selection(self):
        if self.options[self.selected_option] == 'New Game':
            self.game.change_state('game')
        elif self.options[self.selected_option] == 'Load Game':
            self.game.states['slot_select'] = SlotSelectState(self.game, mode='load')
            self.game.change_state('slot_select')
        elif self.options[self.selected_option] == 'Quit':
            self.game.running = False

    def update(self, dt):
        self.time += dt
        
    def render(self, screen):
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
        
        # Draw title
        screen.blit(self.title, self.title_rect)
        
        # Draw menu options
        for i, (text, rect) in enumerate(zip(self.option_surfaces, self.option_rects)):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font.render(self.options[i], True, color)
            screen.blit(text, rect) 