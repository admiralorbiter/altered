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
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.delta_time = 0
        
        # Load settings
        self.settings = load_settings()
        
        # State management
        self.states = {
            'menu': MenuState(self),
            'game': GameState(self),
            'pause': PauseMenuState(self),
            'slot_select': SlotSelectState(self, mode='save'),
            'settings': SettingsState(self)
        }
        self.current_state = self.states['menu']

    def change_state(self, state_name):
        self.current_state.exit_state()
        self.current_state = self.states[state_name]
        self.current_state.enter_state()

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        self.current_state.handle_events(events)

    def update(self):
        self.current_state.update(self.delta_time)

    def render(self):
        self.current_state.render(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.delta_time = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update()
            self.render()

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

