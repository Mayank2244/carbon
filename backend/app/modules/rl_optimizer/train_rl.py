import numpy as np
import os
import time
import pickle

# Optional dependencies
try:
    import matplotlib.pyplot as plt
    PLOT_AVAILABLE = True
except ImportError:
    PLOT_AVAILABLE = False
    print("! matplotlib not found, skipping plots")

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm not installed
    def tqdm(iterable, desc=""):
        return iterable
    print("! tqdm not found, using simple progress")

from app.modules.rl_optimizer.rl_environment import CarbonRLEnvironment
from app.modules.rl_optimizer.ql_agent import QLearningAgent

def train(
    num_episodes: int = 1000,
    steps_per_episode: int = 20,
    model_path: str = "app/modules/rl_optimizer/model.pkl"
):
    """
    Train the RL Agent.
    """
    env = CarbonRLEnvironment()
    agent = QLearningAgent(
        state_dim=env.STATE_DIM,
        num_actions=len(env.ACTIONS),
        epsilon=1.0,  # Start with full exploration
        min_epsilon=0.05
    )
    
    print(f"Starting Training: {num_episodes} episodes, {steps_per_episode} steps each")
    
    rewards_history = []
    
    start_time = time.time()
    
    # Progress bar wrapper
    iterator = range(num_episodes)
    if 'tqdm' in globals():
        iterator = tqdm(range(num_episodes), desc="Training")
    
    for episode in iterator:
        state = env.reset()
        episode_reward = 0
        
        for step in range(steps_per_episode):
            # Choose Action
            action_idx = agent.choose_action(state)
            
            # Act
            next_state, reward, done, info = env.step(action_idx)
            
            # Learn
            agent.update_q_value(state, action_idx, reward, next_state)
            
            # Update State
            state = next_state
            episode_reward += reward
            
        # Decay Epsilon
        agent.decay_epsilon()
        rewards_history.append(episode_reward / steps_per_episode)
        
        # Log occasionally if no tqdm
        if (episode + 1) % 100 == 0:
            avg_rew = rewards_history[-1]
            # print(f"Ep {episode+1}: Avg Reward {avg_rew:.3f}, Epsilon {agent.epsilon:.3f}")
            
    training_time = time.time() - start_time
    print(f"\nTraining Completed in {training_time:.2f}s")
    
    # Save Model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    agent.save_model(model_path)
    print(f"Model saved to {model_path}")
    
    # Plot if available
    if PLOT_AVAILABLE:
        try:
            plt.figure(figsize=(10, 5))
            plt.plot(rewards_history)
            plt.title("Training Progress")
            plt.xlabel("Episode")
            plt.ylabel("Average Reward")
            plt.savefig(model_path.replace(".pkl", ".png"))
            print(f"Plot saved to {model_path.replace('.pkl', '.png')}")
        except Exception as e:
            print(f"Plotting failed: {e}")
    
    return rewards_history

def evaluate(model_path: str, num_queries: int = 200):
    """
    Evaluate the trained agents performance.
    """
    env = CarbonRLEnvironment()
    agent = QLearningAgent(state_dim=env.STATE_DIM, num_actions=len(env.ACTIONS))
    agent.load_model(model_path)
    
    print("\nRunning Evaluation...")
    total_reward = 0
    carbon_total = 0
    latency_total = 0
    user_sat_total = 0
    
    state = env.reset()
    
    for _ in range(num_queries):
        # Pure Exploitation
        action_idx = agent.choose_action(state, evaluate=True)
        
        # Depending on complexity, 'small' model might fail
        # This simulation logic is inside env.step()
        
        next_state, reward, done, info = env.step(action_idx)
        
        total_reward += reward
        carbon_total += info['carbon_gco2']
        latency_total += info['latency_ms']
        user_sat_total += info['user_rating']
        
        state = next_state
        
    print("-" * 30)
    print("EVALUATION RESULTS")
    print("-" * 30)
    print(f"Avg Reward: {total_reward / num_queries:.3f}")
    print(f"Avg Carbon: {carbon_total / num_queries:.2f} gCO2")
    print(f"Avg Latency: {latency_total / num_queries:.1f} ms")
    print(f"Avg Satisfaction: {user_sat_total / num_queries:.2f} / 5.0")
    print("-" * 30)

if __name__ == "__main__":
    # Ensure directory exists
    os.makedirs("app/modules/rl_optimizer", exist_ok=True)
    
    # Train
    history = train(num_episodes=1000)
    
    # Evaluate
    evaluate("app/modules/rl_optimizer/model.pkl")
