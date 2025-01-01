import pygame
from systems.wire_system import TaskType
from utils.config import *
from utils.types import EntityState

class DebugUI:
    def __init__(self, game_state):
        self.game_state = game_state
        self.font = pygame.font.Font(None, 24)
        self.enabled = True
        self.position = (10, 10)
        self.line_height = 20
        self.background_color = (0, 0, 0, 128)
        self.text_color = (255, 255, 255)

    def toggle(self):
        self.enabled = not self.enabled

    def draw(self, surface):
        if not self.enabled:
            return

        debug_info = []
        
        # Game State Information
        debug_info.append("=== Game State ===")
        debug_info.append(f"Wire Mode: {self.game_state.wire_mode}")
        debug_info.append(f"Electrical Components: {list(self.game_state.current_level.tilemap.electrical_components.keys())}")
        debug_info.append("")
        
        # Task System Information
        debug_info.append("=== Task System ===")
        debug_info.append(f"Available Tasks: {len(self.game_state.task_system.available_tasks)}")
        debug_info.append(f"Assigned Tasks: {len(self.game_state.task_system.assigned_tasks)}")
        
        # Available Tasks Details
        debug_info.append("Available Tasks:")
        for i, task in enumerate(self.game_state.task_system.available_tasks):
            debug_info.append(f"{i+1}. Type: {task.type.value} Pos: {task.position}")

        # Assigned Tasks Details
        debug_info.append("Assigned Tasks:")
        for i, task in enumerate(self.game_state.task_system.assigned_tasks):
            assigned_to = "None" if not task.assigned_to else f"Cat-{id(task.assigned_to)}"
            debug_info.append(f"{i+1}. Type: {task.type.value} Pos: {task.position} -> {assigned_to}")

        # Cat Information (More Detailed)
        debug_info.append("\n=== Cats ===")
        for i, cat in enumerate(self.game_state.current_level.cats):
            # Basic info with more details
            state_str = f"Cat {i+1} ({id(cat)}): "
            state_str += f"State={cat.state.value} "
            state_str += f"Pos=({int(cat.position.x // TILE_SIZE)}, {int(cat.position.y // TILE_SIZE)})"
            
            # Movement and target info
            if cat.movement_handler.moving:
                state_str += " [Moving]"
                if cat.movement_handler.target_position:
                    target_x = int(cat.movement_handler.target_position.x // TILE_SIZE)
                    target_y = int(cat.movement_handler.target_position.y // TILE_SIZE)
                    state_str += f" -> ({target_x}, {target_y})"
            
            # Task details
            if cat.task_handler.has_task():
                current_task = cat.task_handler.get_current_task()
                state_str += f" [Task: {current_task.type.value} @ {current_task.position}]"
                
                # Get wire task info from task handler
                if current_task.type == TaskType.WIRE_CONSTRUCTION:
                    wire_info = cat.task_handler.get_wire_task_info()
                    if wire_info:
                        state_str += f" [Wire: {wire_info['position']}]"
                        if wire_info.get('queue'):
                            state_str += f" [Queue: {[pos for pos, _ in wire_info['queue']]}]"
            
            # Status flags
            flags = []
            if cat.is_dead:
                flags.append("DEAD")
            if cat.state == EntityState.SEEKING_FOOD:
                flags.append("HUNGRY")
            if cat.movement_handler.path:
                flags.append(f"Path:{len(cat.movement_handler.path)}")
            if flags:
                state_str += f" [{' '.join(flags)}]"
            
            debug_info.append(state_str)

        # Render with background
        y_offset = self.position[1]
        for line in debug_info:
            text_surface = self.font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (self.position[0], y_offset)
            
            # Draw background
            background_rect = text_rect.inflate(20, 5)
            background_surface = pygame.Surface(background_rect.size, pygame.SRCALPHA)
            background_surface.fill(self.background_color)
            surface.blit(background_surface, background_rect.topleft)
            
            # Draw text
            surface.blit(text_surface, text_rect)
            y_offset += self.line_height 