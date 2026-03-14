import os
try:
    import matplotlib.pyplot as plt
    PLOT_AVAILABLE = True
except ImportError:
    PLOT_AVAILABLE = False
    print("! matplotlib not found, skipping specific visualization functions")

from typing import Dict, List

def plot_training_progress(metrics: Dict[str, List[float]], output_dir: str):
    """
    Generate and save training plots.
    """
    if not PLOT_AVAILABLE:
        print("Skipping plotting due to missing matplotlib")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    episodes = metrics['episodes']
    
    # 1. Rewards
    plt.figure(figsize=(10, 6))
    plt.plot(episodes, metrics['reward'], label='Avg Reward')
    plt.title("Training Reward over Time")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_dir}/rewards.png")
    plt.close()
    
    # 2. Carbon
    plt.figure(figsize=(10, 6))
    plt.plot(episodes, metrics['carbon'], color='green', label='Avg Carbon (gCO2)')
    plt.title("Carbon Footprint Reduction")
    plt.xlabel("Episode")
    plt.ylabel("gCO2 per Query")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_dir}/carbon.png")
    plt.close()
    
    # 3. Satisfaction
    plt.figure(figsize=(10, 6))
    plt.plot(episodes, metrics['satisfaction'], color='orange', label='User Satisfaction')
    plt.title("User Satisfaction Scores")
    plt.xlabel("Episode")
    plt.ylabel("Rating (1-5)")
    plt.ylim(0, 5.5)
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_dir}/satisfaction.png")
    plt.close()
    
    # 4. Epsilon
    plt.figure(figsize=(10, 6))
    plt.plot(episodes, metrics['epsilon'], color='purple', label='Epsilon')
    plt.title("Exploration Rate Decay")
    plt.xlabel("Episode")
    plt.ylabel("Epsilon")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_dir}/epsilon.png")
    plt.close()
    
    print(f"Plots saved to {output_dir}/")
