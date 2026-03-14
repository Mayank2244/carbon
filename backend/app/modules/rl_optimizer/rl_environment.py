import numpy as np
from typing import Tuple, Dict, List, Any
import math

class CarbonRLEnvironment:
    """
    RL Environment for Carbon-Aware Routing.
    Optimizes for Carbon, Latency, User Satisfaction, and Cost.
    """
    
    # State space dimensions
    STATE_DIM = 8
    
    # Actions: (Region, Model, Cache_Strategy)
    ACTIONS = [
        ('us-west', 'tiny', 'cache_first'),
        ('us-west', 'small', 'cache_first'),
        ('us-west', 'medium', 'bypass_cache'),
        ('us-east', 'tiny', 'cache_first'),
        ('us-east', 'small', 'cache_first'),
        ('us-east', 'medium', 'bypass_cache'),
        ('eu-central', 'tiny', 'cache_first'),
        ('eu-central', 'small', 'cache_first'),
        ('eu-central', 'medium', 'bypass_cache'),
        ('local', 'tiny', 'cache_first'),
        ('local', 'small', 'cache_first'),
        ('groq', 'medium', 'bypass_cache')  # 12th action
    ]
    
    def __init__(self):
        self.state = None
        self.done = False
        
    def reset(self) -> np.ndarray:
        """Reset environment to initial random state (simulated new request)."""
        # Simulate a random query context
        self.state = np.random.rand(self.STATE_DIM)
        self.done = False
        return self.state
        
    def step(self, action_idx: int) -> Tuple[np.ndarray, float, bool, dict]:
        """
        Execute action in the environment.
        Simulates the outcome based on probabilistic models of the real world.
        """
        if self.done:
            raise ValueError("Environment is done. Call reset()")
            
        action = self.decode_action(action_idx)
        
        # Simulate outcome based on action and current state
        outcome = self._simulate_outcome(action, self.state)
        
        # Calculate reward
        reward = self.calculate_reward(outcome)
        
        # Update state (new query comes in)
        self.state = np.random.rand(self.STATE_DIM)
        
        # In this simplistic session model, each step is independent 
        # (or we could model a session of N queries). 
        # Let's say done=False effectively to allow continuous training, 
        # or we treat single step as episode. 
        # The prompt says "Episode: 1 user session (10-50 queries)".
        # Let's handle done externally or random chance.
        
        return self.state, reward, False, outcome

    def encode_state(self, query_data: Dict[str, Any]) -> np.ndarray:
        """
        Convert query metadata to state vector.
        Expects keys: complexity, carbon_intensities (list), time, cache_prob, budget
        """
        # Placeholder for actual production encoding logic
        # For simulation, we assume state is already vector
        return np.array([
            query_data.get('complexity', 0.5),
            query_data.get('ci_west', 0.5),
            query_data.get('ci_east', 0.5),
            query_data.get('ci_eu', 0.5),
            query_data.get('hour', 0.5),
            query_data.get('users', 0.5),
            query_data.get('cache_prob', 0.5),
            query_data.get('budget', 0.5)
        ], dtype=np.float32)

    def decode_action(self, action_idx: int) -> Dict[str, str]:
        """Convert action index to routing decision dictionary."""
        region, model, strategy = self.ACTIONS[action_idx]
        return {
            "region": region,
            "model_tier": model,
            "caching_strategy": strategy
        }
        
    def calculate_reward(self, outcome: Dict[str, Any]) -> float:
        """
        Compute reward based on multiple objectives.
        Range roughly [-1.0, 1.0]
        """
        # Normalize inputs (assumed ranges)
        # Carbon: 0-200g
        carbon_score = 1.0 - min(outcome['carbon_gco2'] / 100.0, 1.0)
        
        # Latency: 0-5000ms
        latency_score = 1.0 - min(outcome['latency_ms'] / 2000.0, 1.0)
        
        # Satisfaction: 1-5
        satisfaction_score = (outcome['user_rating'] - 1) / 4.0
        
        # Cost: $0 - $0.05
        cost_score = 1.0 - min(outcome['cost_usd'] / 0.01, 1.0)
        
        # Weighted Combination
        # Weights: Carbon=0.4, Sat=0.3, Lat=0.2, Cost=0.1
        reward = (
            0.4 * carbon_score +
            0.3 * satisfaction_score +
            0.2 * latency_score +
            0.1 * cost_score
        )
        
        # Penalty for poor user experience
        if outcome['user_rating'] < 3:
            reward -= 0.5
            
        return float(reward)

    def _simulate_outcome(self, action: Dict[str, str], state: np.ndarray) -> Dict[str, Any]:
        """
        Simulate the metric outcome of an action given the state.
        This acts as the 'World Model' for training.
        """
        # Extract state factors
        # state = [img_complexity, ci_w, ci_e, ci_eu, hour, load, cache_p, budget]
        complexity = state[0]
        carbon_intensity = state[1] # Simplification: using just one for base
        
        model_tier = action['model_tier']
        region = action['region']
        
        # Base Latency & Satisfaction based on Model vs Complexity
        # If model is too small for complexity -> High latency (retries), Low satisfaction
        if model_tier == 'tiny':
            capacity = 0.3
            base_lat = 50
            cost = 0.0
            carbon_base = 0.5
        elif model_tier == 'small':
            capacity = 0.6
            base_lat = 200
            cost = 0.0
            carbon_base = 2.0
        elif model_tier == 'medium':
            capacity = 0.9
            base_lat = 400
            cost = 0.005
            carbon_base = 5.0
        else: # Large (not in default action set but handled)
            capacity = 1.0
            base_lat = 1000
            cost = 0.02
            carbon_base = 15.0
            
        # Outcome Logic
        if complexity > capacity + 0.1:
            # Under-provisioned
            user_rating = max(1, 5 * (capacity / complexity))
            latency_ms = base_lat * 2  # Penalty
        else:
            # Well-provisioned
            user_rating = 5
            latency_ms = base_lat
            
        # Carbon Calculation
        carbon_gco2 = carbon_base * (1.0 + carbon_intensity)
        
        return {
            'carbon_gco2': carbon_gco2,
            'latency_ms': latency_ms,
            'user_rating': user_rating,
            'cost_usd': cost
        }
