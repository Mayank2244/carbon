import os
import yaml
import numpy as np
import time
from typing import Dict, Any, List
from pathlib import Path

from app.modules.rl_optimizer.rl_environment import CarbonRLEnvironment
from app.modules.rl_optimizer.ql_agent import QLearningAgent
from app.modules.rl_optimizer.query_generator import QueryDataGenerator
from app.modules.rl_optimizer.visualize import plot_training_progress

class RLTrainer:
    """
    Manages the training lifecycle for Carbon-Aware RL Agent.
    """
    
    def __init__(self, config_path: str = "app/modules/rl_optimizer/config.yaml"):
        self.config = self._load_config(config_path)
        self.env = CarbonRLEnvironment()
        self.agent = QLearningAgent(
            state_dim=self.env.STATE_DIM,
            num_actions=len(self.env.ACTIONS),
            epsilon=self.config['training']['epsilon_start'],
            epsilon_decay=self.config['training']['epsilon_decay'],
            min_epsilon=self.config['training']['epsilon_end'],
            alpha=self.config['training']['learning_rate'],
            gamma=self.config['training']['discount_factor']
        )
        self.data_gen = QueryDataGenerator()
        
        self.metrics = {
            'episodes': [],
            'reward': [],
            'carbon': [],
            'satisfaction': [],
            'epsilon': []
        }
        self.best_reward = -float('inf')
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def train(self):
        """Main training loop."""
        num_episodes = self.config['training']['num_episodes']
        max_steps = self.config['training']['max_steps_per_episode']
        
        print(f"Starting Training: {num_episodes} episodes...")
        
        start_time = time.time()
        
        for episode in range(num_episodes):
            # Generate synthetic session
            queries = self.data_gen.generate_training_episode(max_steps)
            
            ep_reward = 0
            ep_carbon = 0
            ep_satisfaction = 0
            
            # Reset environment for new session (logic handled in loop)
            # Actually, our Env.reset() gives random state. 
            # We override it with the generated query data.
            
            for query_data in queries:
                # 1. State
                state = self.data_gen.encode_state(query_data)
                
                # 2. Action
                action_idx = self.agent.choose_action(state)
                
                # 3. Step (Using Env logic to simulate outcome)
                # Override env state manually to match query
                self.env.state = state 
                _, reward, _, info = self.env.step(action_idx)
                
                # 4. Next Query is Next Initial State (No direct transition link in this formulation)
                # In session-based, next state is next query.
                # Simplification: we treat each query as separate transition OR sequence.
                # Let's say next_state is the next query in list, or random if last.
                next_state = state # Placeholder if end of session
                
                # Update Q-Value (simplified S->A->R->S' where S' is effectively new independent state)
                # In routing, S' matters less unless state carries over (like budget).
                # We assume budget updates in query_data stream.
                self.agent.update_q_value(state, action_idx, reward, state) # S' roughly same distribution
                
                ep_reward += reward
                ep_carbon += info['carbon_gco2']
                ep_satisfaction += info['user_rating']
            
            # Decay Epsilon
            self.agent.decay_epsilon()
            
            # Log Metrics
            self.metrics['episodes'].append(episode)
            self.metrics['reward'].append(ep_reward / len(queries))
            self.metrics['carbon'].append(ep_carbon / len(queries))
            self.metrics['satisfaction'].append(ep_satisfaction / len(queries))
            self.metrics['epsilon'].append(self.agent.epsilon)
            
            # Periodic Checkpoint & Eval
            if (episode + 1) % self.config['training']['checkpoint_interval'] == 0:
                self.evaluate_and_save(episode + 1)
                
        duration = time.time() - start_time
        print(f"Training Complete in {duration:.2f}s")
        
        # Save Final Visualizations
        plot_training_progress(self.metrics, self.config['visualization']['plot_dir'])

    def evaluate_and_save(self, episode):
        """Eval current policy and save."""
        avg_reward = np.mean(self.metrics['reward'][-50:])
        print(f"Ep {episode}: Avg Reward {avg_reward:.3f} | Epsilon {self.agent.epsilon:.3f}")
        
        check_dir = self.config['visualization']['checkpoint_dir']
        os.makedirs(check_dir, exist_ok=True)
        
        # Save generic checkpoint
        self.agent.save_model(f"{check_dir}/model_ep{episode}.pkl")
        
        # Save best
        if avg_reward > self.best_reward:
            self.best_reward = avg_reward
            self.agent.save_model(f"{check_dir}/best_model.pkl")
            print(f" >> New Best Model Saved (Rew: {avg_reward:.3f})")
