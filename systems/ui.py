import pygame
from utils.config import *

class UIElement:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.active = True
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def handle_event(self, event):
        if not self.active:
            return False
        
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        return False

    def update(self, dt):
        if not self.active:
            return
        
        for child in self.children:
            child.update(dt)

    def draw(self, surface):
        if not self.visible:
            return
        
        for child in self.children:
            child.draw(surface)

class Label(UIElement):
    def __init__(self, x, y, text, font_size=32, color=WHITE):
        self.font = pygame.font.Font(None, font_size)
        self.text = text
        self.color = color
        text_surface = self.font.render(text, True, color)
        super().__init__(x, y, text_surface.get_width(), text_surface.get_height())

    def set_text(self, text):
        self.text = text
        text_surface = self.font.render(text, True, self.color)
        self.rect.width = text_surface.get_width()
        self.rect.height = text_surface.get_height()

    def draw(self, surface):
        if not self.visible:
            return
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, self.rect)
        super().draw(surface)

class Button(UIElement):
    def __init__(self, x, y, width, height, text, callback=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 32)
        self.normal_color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.pressed_color = (50, 50, 50)
        self.current_color = self.normal_color
        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.current_color = self.hover_color if self.is_hovered else self.normal_color
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True
                self.current_color = self.pressed_color
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                if self.is_hovered and self.callback:
                    self.callback()
                self.current_color = self.hover_color if self.is_hovered else self.normal_color
                return True

        return super().handle_event(event)

    def draw(self, surface):
        if not self.visible:
            return
            
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        super().draw(surface)

class HUD(UIElement):
    def __init__(self, game_state):
        super().__init__(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.game_state = game_state
        
        # Create status labels
        self.health_label = Label(10, 10, "Health: 100%")
        self.add_child(self.health_label)
        
        self.morale_label = Label(10, 40, "Morale: 100%")
        self.add_child(self.morale_label)
        
        # Add a simple button example
        self.menu_button = Button(WINDOW_WIDTH - 110, 10, 100, 30, "Menu", 
                                lambda: game_state.game.change_state('pause'))
        self.add_child(self.menu_button)

    def update(self, dt):
        # Update labels based on game state
        if self.game_state.current_level and self.game_state.current_level.aliens:
            selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                                 if alien.selected), None)
            if selected_alien:
                health = getattr(selected_alien, 'health', 0)
                morale = getattr(selected_alien, 'morale', 0)
                self.health_label.set_text(f"Health: {health}%")
                self.morale_label.set_text(f"Morale: {morale}%")
        
        super().update(dt) 