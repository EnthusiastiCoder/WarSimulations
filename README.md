# ⚔️ War Simulations 🏹

A real-time tactical warfare simulation featuring autonomous troop combat with smooth animations and visual effects.

![Battle Animation](assets/battle_animation.svg)

*Live SVG animation showing troops engaging in tactical combat with smooth arrow transitions and collision avoidance*

## ✨ Features

### 🪖 Troop Types
- **Barbarians** (Circles): High health, close-range fighters
  - Health: 100, Attack: 20, Speed: 1, Range: 1
- **Archers** (Squares): Long-range units with moderate health
  - Health: 80, Attack: 30, Speed: 2, Range: 10

### 🎮 Combat Mechanics
- **Intelligent AI**: Troops automatically find and engage enemies
- **Dynamic Actions**: Attacking (red arrows), Moving (yellow arrows), Waiting (dotted arrows)
- **Collision Avoidance**: No troop overlapping with smart position adjustment
- **Health Systems**: Real-time health bars and damage visualization

### 🎬 Visual Output
- **High-Quality PNG Frames**: Individual battle snapshots
- **Smooth SVG Animations**: Vector-based animations with seamless transitions
- **MP4 Videos**: Compiled video output with configurable frame rates
- **Real-time Rendering**: Live battle state visualization

### 🏹 Arrow Animation System
- **Smart Positioning**: Arrows originate from troop edges and point to targets
- **State Visualization**: Different colors and styles for different actions
- **Smooth Transitions**: Fluid movement tracking with fade-out effects
- **Collision-Aware**: Arrows adjust to troop shapes (circles vs squares)

## 🚀 Quick Start

### Prerequisites
```bash
pip install pillow imageio
```

### Run Simulation
```python
python main.py
```

### Customize Battle
```python
from battlefield import BattleField, Troop, BARBARIAN, ARCHER

# Create battlefield
battlefield = BattleField(100, 100)

# Add troops
battlefield.add_troop(Troop(BARBARIAN, (20, 20), team=0))  # Team Blue
battlefield.add_troop(Troop(ARCHER, (80, 80), team=1))     # Team Red

# Run simulation
iterations = battlefield.run(max_iterations=200)
```

## 📁 Output Structure
```
battle_simulation_YYYYMMDD_HHMMSS/
├── frames/
│   ├── frame_0001.png
│   ├── frame_0002.png
│   └── ...
├── battle_animation.svg
└── battle_simulation.mp4
```

## 🏗️ Architecture

The project uses a modular architecture for clean separation of concerns:

- **`battlefield.py`**: Core simulation engine and troop AI
- **`png_renderer.py`**: High-quality PNG frame generation
- **`svg_renderer.py`**: SVG animation orchestration
- **`arrow_animator.py`**: Complex arrow animation system
- **`troop_animator.py`**: Troop movement and visibility animations
- **`health_bar_animator.py`**: Health bar animation logic

## ⚙️ Configuration

### Simulation Parameters
- **Stagnation Threshold**: Stop if no progress for N iterations (default: 150)
- **Max Iterations**: Maximum simulation length
- **Frame Rate**: Video output FPS (default: 2)
- **Scale**: Image resolution multiplier (default: 20)

### Troop Customization
Modify troop types in `battlefield.py`:
```python
# (health, attack, speed, attack_range, vision_range, cooldown)
BARBARIAN = (100, 20, 1, 1, 100, 2)
ARCHER = (80, 30, 2, 10, 100, 3)
```

## 🎯 Battle Mechanics

### AI Behavior
1. **Target Acquisition**: Find closest enemy within vision range
2. **Combat Decision**: Attack if in range, move if enemy visible, idle otherwise
3. **Action Execution**: Execute attack, movement, or random wandering
4. **Collision Resolution**: Avoid troop overlap with smart positioning

### Victory Conditions
- **Elimination**: All troops of one team defeated
- **Stagnation**: No progress for extended period
- **Iteration Limit**: Maximum simulation length reached

## 📊 Visual Legend

|      Element     |   Meaning  |
|------------------|------------|
| Blue             | Team A     |
| Red              | Team B     |
| Circle           | Barbarian  |
| Square           | Archer     |
| Red Solid Arrow  | Attacking  |
| Red Dotted Arrow | Waiting    |
| Yellow Arrow     | Chasing    |
| Green Bar        | Current HP |
| Red Bar          | Lost HP    |

## 🚀 Advanced Features

### Smooth Animations
- Linear interpolation for position changes
- Discrete transitions for state changes
- Fade-out effects for eliminated troops
- Dynamic arrow positioning and coloring

### Performance Optimizations
- Efficient collision detection
- Optimized rendering pipeline
- Smart frame data collection
- Modular animation system

## 📜 License

This project is open source and available under the MIT License.

---

*Built with Python, PIL, and lots of tactical planning* 🎯