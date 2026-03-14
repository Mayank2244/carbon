import random
import numpy as np
from typing import List, Dict, Any
from datetime import datetime

class QueryDataGenerator:
    """
    Generates synthetic user queries and context for RL training.
    Simulates realistic traffic patterns and context variability.
    """
    
    COMPLEXITIES = ['SIMPLE', 'MEDIUM', 'COMPLEX']
    QUERY_TYPES = ['factual', 'creative', 'code', 'analysis']
    URGENCIES = ['urgent', 'flexible']
    
    def __init__(self):
        pass
        
    def generate_training_episode(self, num_queries: int = 50) -> List[Dict[str, Any]]:
        """
        Generate a sequence of queries representing a user session.
        includes varied difficulties and environmental contexts.
        """
        episode_queries = []
        
        # Simulate base environmental factors for the episode (session)
        # e.g., A session happens at a specific time of day
        hour_of_day = random.randint(0, 23)
        day_of_week = random.randint(0, 6)
        
        # Carbon intensities fluctuate but are correlated in a session
        base_carbon_west = random.uniform(50, 400)
        base_carbon_east = random.uniform(50, 400)
        base_carbon_eu = random.uniform(20, 300)
        
        for _ in range(num_queries):
            # Query Attributes
            q_type = random.choice(self.QUERY_TYPES)
            complexity_level = random.choices(self.COMPLEXITIES, weights=[0.4, 0.4, 0.2])[0]
            urgency = random.choice(self.URGENCIES)
            
            # Map complexity to float
            complexity_score = {
                'SIMPLE': random.uniform(0.1, 0.3),
                'MEDIUM': random.uniform(0.4, 0.6),
                'COMPLEX': random.uniform(0.7, 0.9)
            }[complexity_level]
            
            # Context / Environment State
            # Add small noise to carbon for each query
            query_data = {
                'query_type': q_type,
                'complexity': complexity_score,
                'urgency': urgency,
                'ci_west': max(0, base_carbon_west + random.gauss(0, 10)),
                'ci_east': max(0, base_carbon_east + random.gauss(0, 10)),
                'ci_eu': max(0, base_carbon_eu + random.gauss(0, 10)),
                'hour': hour_of_day,
                'day': day_of_week,
                'cache_prob': random.uniform(0, 1) if q_type == 'factual' else 0.0,
                'budget': random.uniform(0.1, 1.0) # Normalized remaining budget
            }
            
            episode_queries.append(query_data)
            
        return episode_queries

    def encode_state(self, query_data: Dict[str, Any]) -> np.ndarray:
        """
        Convert query dict to state vector for the RL agent.
        Matches CarbonRLEnvironment state definition.
        """
        # Normalize Carbon (approx max 500)
        return np.array([
            query_data['complexity'],
            query_data['ci_west'] / 500.0,
            query_data['ci_east'] / 500.0,
            query_data['ci_eu'] / 500.0,
            query_data['hour'] / 24.0,
            query_data['day'] / 7.0,
            query_data.get('cache_prob', 0.0),
            query_data.get('budget', 1.0)
        ], dtype=np.float32)
