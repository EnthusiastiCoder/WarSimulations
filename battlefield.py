import random
import os
import datetime
import imageio
import xml.etree.ElementTree as ET
from png_renderer import PNGRenderer
from svg_renderer import SVGRenderer

# (health, attack, speed, attack_range, vision_range, cooldown)
BARBARIAN   = (100, 20, 1,  1, 100, 2)
ARCHER      = (80 , 30, 2, 10, 100, 3)

STAGNATION_THRESHOLD = 150 
DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]
class Troop:
    def __init__(self, type: tuple, position: tuple, team: bool):
        self.max_health = type[0]
        self.health = type[0]
        self.attack = type[1]
        self.speed = type[2]
        self.attack_range = type[3]
        self.vision_range = type[4]
        self.cooldown = type[5]
        self.position = position
        self.cooldown_timer = 0
        self.team = team

    def moveRandomly(self):
        direction = DIRECTIONS[random.randint(0, 3)]
        new_x = self.position[0] + self.speed * direction[0]
        new_y = self.position[1] + self.speed * direction[1]
        self.position = (new_x, new_y)
    
        
class BattleField():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.troops = []
        self.frame_counter = 1
        self.animation_frames = []  # Store all frame data for SVG animation
        
        # Initialize renderers
        self.png_renderer = PNGRenderer(self)
        self.svg_renderer = SVGRenderer(self)

    def add_troop(self, troop):
        self.troops.append(troop)

    def remove_troop(self, troop):
        self.troops.remove(troop)

    def get_closest_enemy(self, troop):
        closest_enemy = None
        min_dist = float('inf')
        for warrior in self.troops:
            if warrior.team != troop.team:
                dist = ((warrior.position[0] - troop.position[0]) ** 2 + (warrior.position[1] - troop.position[1]) ** 2) ** 0.5
                if dist < min_dist and dist > 0:
                    min_dist = dist
                    closest_enemy = warrior

        return closest_enemy , min_dist
    
    def nuke_dead(self):
        for troop in self.troops:
            if troop.health <= 0:
                self.remove_troop(troop)

    def update(self):
        self.nuke_dead()
        
        # Track occupied positions to prevent overlaps
        occupied_positions = set()
        
        for troop in self.troops:
            # Store original position for collision resolution
            original_position = troop.position
            
            closest_enemy, distance = self.get_closest_enemy(troop)
            if not closest_enemy:
                troop.target = None
                troop.action = "idle"
                troop.moveRandomly()
            else:
                if distance <= troop.attack_range:
                    if troop.cooldown_timer == 0:
                        # Attack
                        troop.target = closest_enemy
                        troop.action = "attacking"
                        troop.cooldown_timer = troop.cooldown+1
                        closest_enemy.health -= troop.attack
                    else:
                        troop.target = closest_enemy
                        troop.action = "waiting"
                    
                elif distance <= troop.vision_range:
                    # Move towards enemy
                    troop.target = closest_enemy
                    troop.action = "moving"
                    direction = (closest_enemy.position[0] - troop.position[0], closest_enemy.position[1] - troop.position[1])
                    step = (troop.speed if direction[0] > 0 else -troop.speed, troop.speed if direction[1] > 0 else -troop.speed)
                    new_x = troop.position[0] + step[0]
                    new_y = troop.position[1] + step[1]
                    troop.position = (new_x, new_y)
                else:
                    troop.target = None
                    troop.action = "idle"
                    troop.moveRandomly()
            
            # Check for position collision and resolve it
            if troop.position in occupied_positions:
                # Choose random axis to adjust (0 = x-axis, 1 = y-axis)
                axis = random.choice([0, 1])
                
                if axis == 0:  # Adjust X towards original position
                    adjustment = 1 if original_position[0] > troop.position[0] else -1
                    troop.position = (troop.position[0] + adjustment, troop.position[1])
                else:  # Adjust Y towards original position
                    adjustment = 1 if original_position[1] > troop.position[1] else -1
                    troop.position = (troop.position[0], troop.position[1] + adjustment)
            
            # Add current position to occupied set
            occupied_positions.add(troop.position)

            if troop.cooldown_timer > 0:
                troop.cooldown_timer -= 1
    
    def capture_frame_data(self):
        """Capture current frame data for SVG animation"""
        frame_data = {
            'frame_number': self.frame_counter,
            'troops': [],
            'arrows': []
        }
        
        # Capture troop data
        for troop in self.troops:
            troop_data = {
                'id': id(troop),  # Unique ID for tracking
                'position': troop.position,
                'team': troop.team,
                'health_ratio': troop.health / troop.max_health,
                'type': 'barbarian' if troop.attack == 20 else 'archer',
                'alive': troop.health > 0
            }
            frame_data['troops'].append(troop_data)
            
            # Capture arrow data
            if hasattr(troop, 'target') and troop.target and hasattr(troop, 'action'):
                if troop.action in ['attacking', 'moving', 'waiting']:
                    arrow_data = {
                        'from_id': id(troop),
                        'to_id': id(troop.target),
                        'from_pos': troop.position,
                        'to_pos': troop.target.position,
                        'color': 'red' if troop.action in ['attacking', 'waiting'] else 'yellow',
                        'stroke_style': '5,5' if troop.action == 'waiting' else 'none'  # dotted for waiting
                    }
                    frame_data['arrows'].append(arrow_data)
        
        self.animation_frames.append(frame_data)
        self.frame_counter += 1
    
    def save_board_state(self, scale=20):
        """Save the current board state as a high-quality image"""
        return self.png_renderer.save_board_state(scale)

    def get_team_counts(self):
        """Return count of troops for each team"""
        team_true_count = sum(1 for troop in self.troops if troop.team)
        team_false_count = sum(1 for troop in self.troops if not troop.team)
        return team_true_count, team_false_count
    
    def save_video(self, fps=2):
        """Save all frames as a video with each frame showing for 0.5 seconds (fps=2)"""
        if not self.png_renderer.output_folder:
            print("No output folder found. Run simulation first.")
            return
            
        video_path = os.path.join(self.png_renderer.output_folder, "battle_simulation.mp4")
        frames_folder = self.png_renderer.frames_folder
        
        with imageio.get_writer(video_path, fps=fps) as writer:
            for i in range(1, self.frame_counter):  # Start from 1 since frame_counter starts at 1
                frame_path = os.path.join(frames_folder, f"frame_{i:04d}.png")
                if os.path.exists(frame_path):
                    # First and last frames stay longer, others stay for 0.5 seconds
                    frame_count = 5 if i == 1 or i == self.frame_counter - 1 else 1
                    for _ in range(frame_count):
                        writer.append_data(imageio.imread(frame_path))
        
        print(f"Video saved to {video_path}")
    
    def create_animated_svg(self, scale=20, frame_duration=0.5):
        """Create an animated SVG from all captured frame data"""
        return self.svg_renderer.create_animated_svg(scale, frame_duration)
    
    
    def run(self, max_iterations=None, stagnation_threshold=STAGNATION_THRESHOLD):
        """
        Run the simulation for a specified number of iterations or until stagnation.
        
        Args:
            max_iterations: Maximum number of iterations to run (None for unlimited)
            stagnation_threshold: Stop if troop counts don't change for this many iterations (default 100)
        
        Returns:
            Number of iterations completed
        """
        iteration = 0
        troop_count_history = []
        
        while True:
            # Check if we've reached max iterations
            if max_iterations is not None and iteration >= max_iterations:
                break
            
            # Capture frame data and save state first, then update simulation
            self.capture_frame_data()
            self.save_board_state()
            self.update()
            
            # Track troop counts for stagnation detection
            team_counts = self.get_team_counts()
            troop_count_history.append(team_counts)
            
            # Check for stagnation (no change in troop counts for threshold iterations)
            if len(troop_count_history) >= stagnation_threshold:
                recent_counts = troop_count_history[-stagnation_threshold:]
                if all(counts == recent_counts[0] for counts in recent_counts):
                    print(f"Simulation stopped due to stagnation after {iteration + 1} iterations")
                    break
            
            # Check if one side has won (no troops left for one team)
            if team_counts[0] == 0 or team_counts[1] == 0:
                winner = "Team Blue" if team_counts[0] > 0 else "Team Red"
                print(f"Simulation ended: {winner} wins after {iteration + 1} iterations!")
                break
            
            iteration += 1
        
        # Create animated SVG after simulation ends
        print("Creating animated SVG from simulation data...")
        self.create_animated_svg()
        
        # Create video after simulation ends
        print("Creating video from simulation frames...")
        self.save_video()
        
        return iteration + 1