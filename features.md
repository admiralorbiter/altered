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

