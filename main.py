import random
from battlefield import BattleField, Troop, BARBARIAN, ARCHER

def create_random_battlefield(width=100, height=100, num_troops_per_team=20):
    """Create a battlefield with randomly placed troops"""
    battlefield = BattleField(width, height)
    
    # Add troops for team True (blue)
    for _ in range(num_troops_per_team):
        # Random troop type
        troop_type = random.choice([BARBARIAN, ARCHER])
        # Random position
        position = (random.randint(0, width-1), random.randint(0, height-1))
        troop = Troop(troop_type, position, team=True)
        battlefield.add_troop(troop)
    
    # Add troops for team False (red)
    for _ in range(num_troops_per_team):
        # Random troop type
        troop_type = random.choice([BARBARIAN, ARCHER])
        # Random position
        position = (random.randint(0, width-1), random.randint(0, height-1))
        troop = Troop(troop_type, position, team=False)
        battlefield.add_troop(troop)
    
    return battlefield

def create_formation_battle(width=100, height=100):
    """Create a battlefield with troops arranged in formations"""
    battlefield = BattleField(width, height)
    
    # Team True (blue) - left side formation
    # Front line of barbarians
    for i in range(10):
        y_pos = 30 + i * 4
        troop = Troop(BARBARIAN, (20, y_pos), team=True)
        battlefield.add_troop(troop)
    
    # Back line of archers
    for i in range(8):
        y_pos = 32 + i * 5
        troop = Troop(ARCHER, (10, y_pos), team=True)
        battlefield.add_troop(troop)
    
    # Team False (red) - right side formation
    # Front line of barbarians
    for i in range(10):
        y_pos = 30 + i * 4
        troop = Troop(BARBARIAN, (80, y_pos), team=False)
        battlefield.add_troop(troop)
    
    # Back line of archers
    for i in range(8):
        y_pos = 32 + i * 5
        troop = Troop(ARCHER, (90, y_pos), team=False)
        battlefield.add_troop(troop)
    
    return battlefield

def asymmetric_battle(width=100, height=100):
    """Create an asymmetric battle: many barbarians vs few archers"""
    battlefield = BattleField(width, height)
    
    # Team True (blue) - lots of barbarians
    for _ in range(25):
        position = (random.randint(0, 30), random.randint(0, height-1))
        troop = Troop(BARBARIAN, position, team=True)
        battlefield.add_troop(troop)
    
    # Team False (red) - fewer but powerful archers
    for _ in range(10):
        position = (random.randint(70, width-1), random.randint(0, height-1))
        troop = Troop(ARCHER, position, team=False)
        battlefield.add_troop(troop)
    
    return battlefield

def main():
    print("Battle Simulation Options:")
    print("1. Random Battle (20 vs 20 mixed troops)")
    print("2. Formation Battle (organized armies)")
    print("3. Asymmetric Battle (barbarians vs archers)")
    print("4. Custom Battle")
    
    choice = input("Choose a battle type (1-4): ").strip()
    
    if choice == "1":
        print("Creating random battle...")
        battlefield = create_random_battlefield()
        
    elif choice == "2":
        print("Creating formation battle...")
        battlefield = create_formation_battle()
        
    elif choice == "3":
        print("Creating asymmetric battle...")
        battlefield = asymmetric_battle()
        
    elif choice == "4":
        print("Custom battle setup:")
        width = int(input("Battlefield width (default 100): ") or "100")
        height = int(input("Battlefield height (default 100): ") or "100")
        num_troops = int(input("Troops per team (default 15): ") or "15")
        battlefield = create_random_battlefield(width, height, num_troops)
        
    else:
        print("Invalid choice, using random battle...")
        battlefield = create_random_battlefield()
    
    # Get simulation parameters
    print("\nSimulation parameters:")
    max_iter = input("Maximum iterations (press Enter for unlimited): ").strip()
    max_iterations = int(max_iter) if max_iter else None
    
    stagnation = input("Stagnation threshold (default 150): ").strip()
    stagnation_threshold = int(stagnation) if stagnation else 150
    
    # Show initial state
    team_counts = battlefield.get_team_counts()
    print(f"\nStarting battle:")
    print(f"Team Blue: {team_counts[0]} troops")
    print(f"Team Red: {team_counts[1]} troops")
    print(f"Total troops: {sum(team_counts)}")
    print("\nRunning simulation...")
    
    # Run the simulation
    try:
        iterations = battlefield.run(max_iterations=max_iterations, 
                                   stagnation_threshold=stagnation_threshold)
        
        # Show final results
        final_counts = battlefield.get_team_counts()
        print(f"\nSimulation completed after {iterations} iterations!")
        print(f"Final state:")
        print(f"Team Blue: {final_counts[0]} troops remaining")
        print(f"Team Red: {final_counts[1]} troops remaining")
        
        if battlefield.png_renderer.output_folder:
            print(f"\nImages saved to: {battlefield.png_renderer.output_folder}")
            print(f"Total frames: {battlefield.frame_counter - 1}")
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        print(f"Ran for {battlefield.frame_counter - 1} iterations.")

if __name__ == "__main__":
    main()