from abc import ABC, abstractmethod
import pygame

class State(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def handle_events(self, events):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self, screen):
        pass

    def enter_state(self):
        pass

    def exit_state(self):
        pass 