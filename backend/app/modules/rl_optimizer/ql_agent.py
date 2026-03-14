import numpy as np
import pickle
import random
from typing import Dict, Tuple, Any

class QLearningAgent:
    """
    Q-Learning Agent for Discrete Action Spaces.
    """
    
    def __init__(
        self,
        state_dim: int,
        num_actions: int,
        alpha: float = 0.1,
        gamma: float = 0.95,
        epsilon: float = 0.3,
        epsilon_decay: float = 0.995,
        min_epsilon: float = 0.01
    ):
        self.state_dim = state_dim
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        
        # Q-Table: Map state_hash -> unp.array(num_actions)
        self.q_table: Dict[int, np.ndarray] = {}
        
    def _discretize_state(self, state: np.ndarray) -> int:
        """
        Discretize continuous state into buckets to form a hashable key.
        Simplification: Bin each dimension into 4 buckets (0.25 steps).
        """
        bins = np.array([0, 0.25, 0.5, 0.75, 1.0])
        digitized = np.digitize(state, bins) - 1 # Indices 0-3
        # Hash the tuple of indices
        return hash(tuple(digitized))
        
    def get_q_values(self, state: np.ndarray) -> np.ndarray:
        """Get Q-values for a state, initializing if unknown."""
        state_key = self._discretize_state(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.num_actions)
        return self.q_table[state_key]

    def choose_action(self, state: np.ndarray, evaluate: bool = False) -> int:
        """
        Choose action using Epsilon-Greedy policy.
        If evaluate=True, use pure exploitation (greedy).
        """
        if not evaluate and random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        
        q_values = self.get_q_values(state)
        # Break ties randomly
        max_q = np.max(q_values)
        actions_with_max_q = np.where(q_values == max_q)[0]
        return np.random.choice(actions_with_max_q)

    def update_q_value(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray):
        """
        Update Q-value using the Bellman equation.
        Q(s,a) = Q(s,a) + alpha * [r + gamma * max(Q(s',a')) - Q(s,a)]
        """
        state_key = self._discretize_state(state)
        
        # Ensure entries exist
        current_q = self.get_q_values(state)
        next_q = self.get_q_values(next_state)
        
        # Update
        best_next_action_value = np.max(next_q)
        td_target = reward + self.gamma * best_next_action_value
        td_error = td_target - current_q[action]
        
        self.q_table[state_key][action] += self.alpha * td_error
        
    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
    def save_model(self, filepath: str):
        """Save Q-table to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'config': {
                    'state_dim': self.state_dim,
                    'num_actions': self.num_actions,
                    'epsilon': self.epsilon
                }
            }, f)
            
    def load_model(self, filepath: str):
        """Load Q-table from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.q_table = data['q_table']
            self.epsilon = data['config']['epsilon']
