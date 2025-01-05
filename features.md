# Features

## Engine
- [x] Basic Game Loop
  - [x] Fixed time step
  - [x] State management
  - [x] Event handling
  - [x] Delta time updates

- [x] State System
  - [x] Abstract base state
  - [x] Menu state
  - [x] Game state
  - [x] Pause menu state
  - [x] Settings state
  - [x] Save/Load slot selection state

- [x] Entity System
  - [x] Base entity class
  - [x] Entity manager
  - [x] Component-based architecture
  - [x] Basic physics (position, velocity)
  - [x] Collision detection (bounding boxes)
  - [x] Entity serialization (save/load support)

- [x] Camera System
  - [x] Smooth following
  - [x] Zoom controls
  - [x] Bounds checking
  - [x] Mouse-based zoom targeting

- [x] Save/Load System
  - [x] JSON-based save files
  - [x] Multiple save slots
  - [x] Timestamp-based saves
  - [x] Entity serialization
  - [x] Save file management

- [x] Menu Systems
  - [x] Main menu with options
  - [x] Pause menu
  - [x] Settings menu
  - [x] Save/Load slot selection
  - [x] Navigation controls
  - [x] Visual feedback (highlighting)

- [x] Settings System
  - [x] Volume control
  - [x] Settings persistence
  - [x] Zoom settings

- [ ] Audio System (TODO)
  - [ ] Background music
  - [ ] Sound effects
  - [ ] Volume control implementation

- [ ] Graphics (TODO)
  - [ ] Sprite support
  - [ ] Animation system
  - [ ] Particle effects
  - [ ] Screen transitions

- [ ] UI System (TODO)
  - [x] HUD
  - [ ] Dialog system
  - [ ] Notifications 

- [x] Task System
  - [x] Task assignment
  - [x] Priority handling
  - [x] Work progress tracking
  - [x] Task completion
  - [x] Task interruption

- [x] Wire System
  - [x] Wire placement
  - [x] Connection logic
  - [x] Construction tasks
  - [x] Visual preview
  - [x] Validation checks

## Systems

- [x] Capture System
  - [x] Entity States
    - [x] None (Default)
    - [x] Marked (Target selected)
    - [x] Unconscious (Knocked out)
    - [x] Being Carried
    - [x] Captured
  - [x] Mechanics
    - [x] Target marking
    - [x] Stealth vs Force approach
    - [x] Knockout attempts
      - 95% success chance when stealthy
      - 40% base chance in combat (scaled by attacker health)
    - [x] Carrying system
      - [x] Speed reduction while carrying
      - [x] Drop/pickup controls
    - [x] Unconscious timer (10 seconds)
  - [x] Mode toggles
    - [x] Lethal/Non-lethal toggle
    - [x] Stealth/Force toggle

- [x] Power System
  - [x] Reactor placement
  - [x] Power generation
  - [x] Power distribution
  - [x] Wire connections
  - [x] Construction tasks

- [x] Oxygen System
  - [x] Grid-based oxygen simulation
  - [x] Oxygen consumption by entities
  - [x] Oxygen generation from life support
  - [x] Oxygen diffusion between tiles
  - [x] Critical oxygen damage
  - [x] Visual oxygen indicators
    - [x] Per-tile debug overlay
    - [x] Ship-wide oxygen level HUD
  - [x] Life support placement
  - [x] Construction tasks
  - Constants:
    - Consumption: 0.05 per entity/second
    - Generation: 0.2 per life support/second
    - Diffusion: 0.1 rate between tiles
    - Critical: 0.3 threshold for damage
    - Damage: 5.0 per second when depleted

## Entities

- [x] Alien
  - [x] Health/Morale system
  - [x] Movement
  - [x] Selection system
  - [x] Capture mechanics
  - [x] Wire construction
  - [x] Pathfinding

- [x] Cat
  - [x] AI behavior system
  - [x] Task handling
  - [x] Hunger system
  - [x] Movement
  - [x] Visual rendering
  - [x] State management

- [x] Human
  - [x] AI behavior
  - [x] Combat system
    - [ ] BUG: After killing a human, alien isn't targeting the cats and chasing
  - [x] Capture states
  - [x] Pathfinding
  - [x] Health system

## UI System
- [x] Base UI framework
  - [x] Component hierarchy
  - [x] Event propagation
  - [x] Visibility control
  - [x] Parent-child relationships

- [x] Debug UI
  - [x] Entity state display
  - [x] Task information
  - [x] Position tracking
  - [x] Path visualization

- [x] HUD Elements
  - [x] Labels
  - [x] Progress bars
  - [x] Task indicators
  - [x] Selection feedback

## Maps
- [x] UFO Level
  - [x] Circular layout
  - [x] Interior/exterior zones
  - [x] Wall placement

- [x] Abduction Level
  - [x] Outdoor environment
  - [x] Strategic barriers
  - [x] Terrain variety

