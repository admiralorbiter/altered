import pygame
from .base_state import State
from utils.config import *
from utils.save_load import get_save_files

class SlotSelectState(State):
    """
    Save/Load slot selection state handling game persistence.
    Features multiple save slots with timestamps and empty slot handling.
    """
    def __init__(self, game, mode='save'):
        super().__init__(game)
        self.mode = mode  # 'save' or 'load'
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 64)
        self.selected_slot = 0
        self.slots = []
        self.refresh_slots()

    def refresh_slots(self):
        """
        Update available save slots.
        Creates empty slots if needed and limits total slots to 3.
        """
        self.slots = []
        saves = get_save_files()
        
        # Add empty slots if we're in save mode
        while len(saves) < 3:
            saves.append({'filename': 'Empty Slot', 'timestamp': None})
        
        self.slots = saves[:3]  # Limit to 3 slots

    def handle_events(self, events):
        """
        Handle slot selection and confirmation.
        Supports keyboard navigation and slot interaction.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state('pause')
                elif event.key == pygame.K_UP:
                    self.selected_slot = (self.selected_slot - 1) % len(self.slots)
                elif event.key == pygame.K_DOWN:
                    self.selected_slot = (self.selected_slot + 1) % len(self.slots)
                elif event.key == pygame.K_RETURN:
                    self.handle_selection()

    def handle_selection(self):
        """
        Process slot selection for save/load operations.
        Handles both saving to empty slots and loading existing saves.
        """
        if self.mode == 'save':
            self.game.states['game'].save_game_state(slot=self.selected_slot + 1)
            self.game.change_state('game')
        else:  # load mode
            if self.slots[self.selected_slot]['timestamp']:  # If slot isn't empty
                self.game.states['game'].load_game_state(self.slots[self.selected_slot]['filepath'])
                self.game.change_state('game')

    def render(self, screen):
        """
        Render slot selection interface with timestamps.
        Creates semi-transparent overlay with slot information.
        """
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        # Draw title based on mode
        title_text = f"Select Slot to {'Save' if self.mode == 'save' else 'Load'}"
        title = self.title_font.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        screen.blit(title, title_rect)

        # Draw slot options with timestamps
        for i, slot in enumerate(self.slots):
            color = (255, 255, 0) if i == self.selected_slot else WHITE
            
            # Format slot text with timestamp if available
            if slot['timestamp']:
                from datetime import datetime
                timestamp = datetime.fromisoformat(slot['timestamp'])
                slot_text = f"Slot {i+1} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                slot_text = f"Slot {i+1} - Empty"

            text = self.font.render(slot_text, True, color)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 60))
            screen.blit(text, rect)

        # Draw navigation instructions
        instructions = self.font.render("Press ESC to return", True, WHITE)
        inst_rect = instructions.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.8))
        screen.blit(instructions, inst_rect)

    def update(self, dt):
        # Refresh slots periodically to catch any new saves
        # This is optional, but useful if saves can happen from elsewhere
        pass 