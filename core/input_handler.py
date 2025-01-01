import pygame


class InputHandler:
    def __init__(self, game_state):
        self.game_state = game_state
        
    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            return self._handle_keyboard(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click(event)
        elif event.type == pygame.MOUSEWHEEL:
            return self._handle_mouse_wheel(event)
        return False
        
    def _handle_keyboard(self, event):
        if event.key == pygame.K_ESCAPE:
            self.game_state.game.change_state('pause')
            return True
        elif event.key == pygame.K_TAB:
            new_level = 'abduction' if self.game_state.current_level == self.game_state.levels['ufo'] else 'ufo'
            self.game_state.change_level(new_level)
            return True
        return False