import pygame
from components.base_entity import Entity
from components.movement_component import MovementComponent
from components.alien_render_component import AlienRenderComponent
from components.health_component import HealthComponent
from components.selectable_component import SelectableComponent
from components.capture_component import CaptureComponent
from components.pathfinding_component import PathfindingComponent
from utils.config import TILE_SIZE

class TestTilemap:
    """Simple tilemap for testing"""
    def __init__(self, width, height):
        print(f"\nTILEMAP INIT DEBUG:")
        self.width = width
        self.height = height
        # Make all tiles walkable
        self.tiles = [[True for _ in range(height)] for _ in range(width)]
        print(f"Tilemap dimensions: {width}x{height}")
        print("All tiles set to walkable")

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if the given tile coordinates are walkable"""
        print(f"\nCHECKING WALKABLE: ({x}, {y})")
        if 0 <= x < self.width and 0 <= y < self.height:
            try:
                result = self.tiles[x][y]
                print(f"Tile ({x}, {y}) walkable: {result}")
                return result
            except IndexError:
                print(f"Index error accessing tile ({x}, {y})")
                return False
        print(f"Tile ({x}, {y}) out of bounds")
        return False

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Draw walls and grid"""
        # Draw grid
        for x in range(self.width):
            for y in range(self.height):
                rect = pygame.Rect(
                    x * TILE_SIZE - camera_x,
                    y * TILE_SIZE - camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                # Only draw grid lines (no walls)
                pygame.draw.rect(surface, (50, 50, 50), rect, 1)

class TestGameState:
    """Simple game state for testing"""
    def __init__(self):
        print("\nGAME STATE INIT DEBUG:")
        self.zoom_level = 1
        self.tilemap = TestTilemap(25, 19)
        print(f"Tilemap created: {self.tilemap is not None}")
        self.current_level = type('Level', (), {'tilemap': self.tilemap})()
        print(f"Current level created: {self.current_level is not None}")
        print(f"Level has tilemap: {hasattr(self.current_level, 'tilemap')}")
        self.current_time = 0

class TestAlien(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.position = pygame.math.Vector2(x, y)  # Ensure position is set
        self.size = pygame.math.Vector2(32, 32)
        print(f"Created alien at position: {self.position}")  # Debug
        
        # Add components
        self.movement = self.add_component(MovementComponent(self))
        self.renderer = self.add_component(AlienRenderComponent(self))
        self.health = self.add_component(HealthComponent(self))
        self.selectable = self.add_component(SelectableComponent(self))
        self.capture = self.add_component(CaptureComponent(self))
        self.pathfinding = self.add_component(PathfindingComponent(self))
        
        # Initialize components
        for component in self.components.values():
            if hasattr(component, 'start'):
                component.start()

# Initialize pygame and create window
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Create game state and entities
game_state = TestGameState()
alien = TestAlien(400, 300)
target = TestAlien(200, 200)
alien.game_state = game_state
target.game_state = game_state

# Game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0
    game_state.current_time += dt

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Convert mouse position to tile coordinates
            tile_x = mouse_x // TILE_SIZE
            tile_y = mouse_y // TILE_SIZE
            
            if event.button == 1:  # Left click
                # Select if clicked on alien
                alien_rect = pygame.Rect(
                    alien.position.x - 16, 
                    alien.position.y - 16, 
                    32, 32
                )
                if alien_rect.collidepoint(mouse_x, mouse_y):
                    if alien.selectable.is_selected:
                        alien.selectable.deselect()
                    else:
                        alien.selectable.select()
                        
            elif event.button == 3:  # Right click
                # Only move if alien is selected
                if alien.selectable.is_selected:
                    print(f"\nRIGHT CLICK DEBUG:")
                    print(f"Mouse position: ({mouse_x}, {mouse_y})")
                    print(f"Converting to tile: ({tile_x}, {tile_y})")
                    print(f"Alien selected: {alien.selectable.is_selected}")
                    print(f"Tile walkable: {game_state.tilemap.is_walkable(tile_x, tile_y)}")
                    
                    if game_state.tilemap.is_walkable(tile_x, tile_y):
                        print("Calling pathfinding.set_target()...")
                        result = alien.pathfinding.set_target(tile_x, tile_y)
                        print(f"set_target() returned: {result}")

    # Update entities
    alien.update(dt)
    target.update(dt)
    
    # Draw
    screen.fill((0, 0, 0))
    
    # Draw tilemap first
    game_state.tilemap.render(screen, 0, 0)
    
    # Draw entities
    target.render(screen, 0, 0)
    alien.render(screen, 0, 0)
    
    # Draw debug info
    if alien.selectable.is_selected:
        # Show selection status
        text = font.render("Selected", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        # Show path info if moving
        if alien.pathfinding.path:
            path_text = font.render("Following path...", True, (255, 255, 255))
            screen.blit(path_text, (10, 40))
            
        # Show current position
        pos_text = font.render(f"Pos: ({int(alien.position.x)}, {int(alien.position.y)})", True, (255, 255, 255))
        screen.blit(pos_text, (10, 70))
    
    if alien.movement.moving:
        print(f"Alien moving: Current={alien.position}, Target={alien.movement.target_position}")
    
    pygame.display.flip()

pygame.quit()
