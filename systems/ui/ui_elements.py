import pygame
import math

class StylizedUIElements:
    def __init__(self):
        """Initialize shared resources for UI elements"""
        self.font = pygame.font.Font(None, 24)
        
    def draw_health_orb(self, surface, x, y, health, max_health, radius=20):
        """Draw a glowing circular health indicator"""
        # Base circle
        pygame.draw.circle(surface, (40, 40, 40), (x, y), radius)
        
        # Health fill
        health_percent = health / max_health
        if health_percent > 0:
            # Create gradient colors based on health
            if health_percent > 0.7:
                color = (0, 255, 0)  # Green
            elif health_percent > 0.3:
                color = (255, 165, 0)  # Orange
            else:
                color = (255, 0, 0)  # Red
                
            # Draw filled arc
            angle = health_percent * 2 * math.pi
            pygame.draw.arc(surface, color, 
                          (x - radius, y - radius, radius * 2, radius * 2),
                          0, angle, radius)
            
            # Add inner glow
            glow_radius = int(radius * 0.8)
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, 100), 
                            (radius, radius), glow_radius)
            surface.blit(glow_surface, (x - radius, y - radius))
            
    def draw_morale_bar(self, surface, x, y, morale, max_morale, width=100):
        """Draw a stylized morale bar with glow effect"""
        height = 8
        # Background
        pygame.draw.rect(surface, (40, 40, 40),
                        (x, y, width, height), border_radius=4)
        
        # Morale fill
        fill_width = (width * morale) / max_morale
        if fill_width > 0:
            # Create gradient based on morale level
            color = (100, 149, 237)  # Cornflower blue
            
            # Main bar
            pygame.draw.rect(surface, color,
                           (x, y, fill_width, height), border_radius=4)
            
            # Glow effect
            glow_surface = pygame.Surface((width, height * 3), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*color, 50),
                           (0, height, fill_width, height), border_radius=4)
            surface.blit(glow_surface, (x, y - height))

    def draw_status_icons(self, surface, x, y, entity):
        """Draw status effect icons"""
        icon_size = 16
        spacing = 20
        current_x = x
        
        # Dead status
        if hasattr(entity, 'is_dead') and entity.is_dead:
            pygame.draw.circle(surface, (150, 0, 0), (current_x, y), icon_size//2)
            pygame.draw.line(surface, (255, 255, 255),
                           (current_x - 5, y - 5),
                           (current_x + 5, y + 5), 2)
            pygame.draw.line(surface, (255, 255, 255),
                           (current_x - 5, y + 5),
                           (current_x + 5, y - 5), 2)
            current_x += spacing
            
        # Selected status
        if hasattr(entity, 'selected') and entity.selected:
            pygame.draw.circle(surface, (255, 215, 0), (current_x, y), icon_size//2, 2)
            current_x += spacing

    def draw_selection_highlight(self, surface, entity, camera_x, camera_y, zoom_level):
        """Draw an animated selection highlight"""
        if not hasattr(entity, 'selected') or not entity.selected:
            return
            
        screen_x = (entity.position.x - camera_x) * zoom_level
        screen_y = (entity.position.y - camera_y) * zoom_level
        radius = 20 * zoom_level
        
        # Animate the selection ring
        time = pygame.time.get_ticks() / 1000
        pulse = (math.sin(time * 4) + 1) * 0.5  # Pulse between 0 and 1
        
        # Draw outer ring
        pygame.draw.circle(surface, (255, 215, 0), 
                         (int(screen_x), int(screen_y)),
                         int(radius * (1 + pulse * 0.2)), 2)

    def draw_name_tag(self, surface, x, y, entity_type, entity_id):
        """Draw a stylized name tag for the entity"""
        # Create background panel
        text = f"{entity_type}-{entity_id}"
        text_surface = self.font.render(text, True, (255, 255, 255))
        padding = 5
        
        background_rect = pygame.Rect(x, y - padding,
                                    text_surface.get_width() + padding * 2,
                                    text_surface.get_height() + padding * 2)
        
        # Draw panel background with gradient
        gradient_surface = pygame.Surface(background_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(gradient_surface, (0, 0, 0, 180), 
                        gradient_surface.get_rect(), border_radius=4)
        surface.blit(gradient_surface, background_rect)
        
        # Draw text
        surface.blit(text_surface, (x + padding, y))
