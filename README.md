# SkyWave Combat

A wave-based flight combat game with progressive challenges, resource management, and enemy combat built with Python and Pygame.

## About the Game

SkyWave Combat is an action-packed 2D flight game where we can pilot an aircraft through 5 increasingly difficult waves. Manage your fuel and health while collecting power-ups, shooting obstacles, and ultimately facing enemy aircraft in the final wave. The game features dynamic visuals, intuitive controls, and an exciting combat system.

## Game Features

### Core Gameplay
- **Wave Progression**: 5 waves with 30-second survival challenges
- **Resource Management**: Monitor and replenish health and fuel
- **Combat System**: Shoot obstacles and enemy aircraft
- **Power-ups**: Collect items to restore health, fuel, and increase speed
- **Dynamic Environment**: Mountains grow taller with each wave
- **Enemy AI**: Face intelligent enemy aircraft in the final wave

### Visual Elements
- Gradient sky background
- Animated clouds
- Detailed mountains with snow caps
- Particle effects (engine exhaust, trails)
- Visual feedback for damage and power-ups
- Comprehensive HUD with status bars

### Game Systems
- High score tracking
- Wave transition screens
- Victory and game over states
- Screenshot functionality

## How to Play

### Installation
```bash
# Install required package
pip install pygame

# Run the game
python flight_game.py
```

### Requirements
- Python 3.x
- Pygame library

### Controls
- **Arrow Left/Right**: Turn the airplane
- **Arrow Up/Down**: Increase/decrease speed
- **Spacebar**: Shoot
- **F12**: Take screenshot
- **ESC**: Quit game
- **Spacebar**: Restart (when game over)

### Gameplay Instructions

1. **Objective**: 
   Survive all 5 waves, with the final wave lasting 30 seconds against enemy aircraft.

2. **Wave System**:
   - Each wave lasts 30 seconds
   - Mountains grow taller with each wave
   - More obstacles appear in later waves
   - Enemy aircraft appear only in wave 5

3. **Resource Management**:
   - **Health** (red bar): Decreases when hitting obstacles, mountains, or enemy fire
   - **Fuel** (yellow bar): Decreases over time and with speed increases
   - Collect power-ups to replenish resources:
     - Gold items (F): Replenish fuel
     - Green items (+): Restore health
     - Blue items (S): Increase maximum speed

4. **Combat Tips**:
   - Shoot star obstacles to destroy them and earn points
   - In Wave 5, prioritize shooting enemy aircraft
   - Use wrap-around screen edges to your advantage
   - Maintain distance from mountains, especially in later waves

## Screenshots

Press F12 during gameplay to capture screenshots. Images will be saved in the same directory as the game with timestamps in their filenames.

## Future Enhancements
- Multiplayer mode
- Additional enemy types
- More varied environments
- Power-up special effects
- Boss battles

## License
[MIT License](LICENSE)