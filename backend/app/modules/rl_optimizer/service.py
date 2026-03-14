"""
RL Optimizer Module
Reinforcement learning-based optimization for routing decisions.
"""

from typing import Dict, Any, List
from pydantic import BaseModel
import random

from app.core.logging import get_logger

logger = get_logger(__name__)


class RLState(BaseModel):
    """RL state representation."""
    
    query_complexity: float
    query_type: str
    context_required: bool
    estimated_tokens: int


class RLAction(BaseModel):
    """RL action (model selection)."""
    
    model_name: str
    expected_reward: float


class RLOptimizer:
    """
    Reinforcement learning-based optimizer for model routing decisions.

    Uses a Q-learning approach to learn the best model for a given query state
    (complexity, type, context) over time, based on observed rewards (carbon
    efficiency vs performance).

    Attributes:
        learning_rate (float): Step size for Q-value updates.
        discount_factor (float): How much future rewards are valued.
        exploration_rate (float): Epsilon for epsilon-greedy selection.
        q_table (dict): The learned state-action values.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.001,
        discount_factor: float = 0.95,
        exploration_rate: float = 0.1
    ):
        """
        Initialize RL optimizer.
        
        Args:
            learning_rate: Learning rate for updates
            discount_factor: Discount factor for future rewards
            exploration_rate: Epsilon for epsilon-greedy exploration
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        logger.info(
            f"RL optimizer initialized (lr={learning_rate}, "
            f"gamma={discount_factor}, epsilon={exploration_rate})"
        )
    
    async def select_action(
        self,
        state: RLState,
        available_models: List[str]
    ) -> RLAction:
        """
        Selects the optimal model (action) for the given state.

        Uses an epsilon-greedy policy: with probability epsilon, it explores
        by selecting a random model; otherwise, it exploits the best known model.

        Args:
            state (RLState): The current query state metadata.
            available_models (List[str]): Models available for selection.

        Returns:
            RLAction: The selected model and its predicted reward.
        """
        state_key = self._state_to_key(state)
        
        # Epsilon-greedy exploration
        if random.random() < self.exploration_rate:
            # Explore: random action
            model_name = random.choice(available_models)
            logger.debug(f"Exploring: selected {model_name}")
        else:
            # Exploit: best known action
            model_name = self._get_best_action(state_key, available_models)
            logger.debug(f"Exploiting: selected {model_name}")
        
        expected_reward = self._get_q_value(state_key, model_name)
        
        return RLAction(
            model_name=model_name,
            expected_reward=expected_reward
        )
    
    async def update(
        self,
        state: RLState,
        action: str,
        reward: float,
        next_state: RLState
    ) -> None:
        """
        Updates the Q-table based on the observed reward for an action.

        Implements the standard Q-learning update rule to improve future decisions.

        Args:
            state (RLState): The state before the action.
            action (str): The model that was selected.
            reward (float): The reward (feedback) received.
            next_state (RLState): The state after the action.
        """
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # Get current Q-value
        current_q = self._get_q_value(state_key, action)
        
        # Get max Q-value for next state
        max_next_q = max(
            self.q_table.get(next_state_key, {}).values(),
            default=0.0
        )
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        # Update Q-table
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        self.q_table[state_key][action] = new_q
        
        logger.info(f"Updated Q-value for {action}: {current_q:.3f} -> {new_q:.3f}")
    
    def _state_to_key(self, state: RLState) -> str:
        """Convert state to string key for Q-table."""
        complexity_bucket = int(state.query_complexity * 10)
        return f"{state.query_type}_{complexity_bucket}_{state.context_required}"
    
    def _get_q_value(self, state_key: str, action: str) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get(state_key, {}).get(action, 0.0)
    
    def _get_best_action(self, state_key: str, available_models: List[str]) -> str:
        """Retrieves the action with the highest Q-value for a given state."""
        if state_key not in self.q_table:
            return random.choice(available_models)
        
        state_actions = self.q_table[state_key]
        available_actions = {
            model: state_actions.get(model, 0.0)
            for model in available_models
        }
        
        return max(available_actions, key=available_actions.get)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returns performance and training metrics for the optimizer.

        Returns:
            Dict[str, Any]: Statistics including total states explored and hyperparameters.
        """
        return {
            "total_states": len(self.q_table),
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "exploration_rate": self.exploration_rate,
        }
