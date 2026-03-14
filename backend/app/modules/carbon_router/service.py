"""
Carbon Router Module
Routes queries to the greenest data center region in real-time.
"""

import math
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import pytz
from pydantic import BaseModel

from app.core.logging import get_logger
from app.modules.query_analyzer import QueryAnalysisResult, QueryComplexity, QueryUrgency
from app.modules.carbon_router.models import Region, RouteResult
from app.modules.model_selector import ModelRequest, ModelResponse

logger = get_logger(__name__)

# Constants
REGIONS = {
    'us-west-1': Region(
        id='us-west-1',
        name='California',
        coordinates=(37.7749, -122.4194),
        endpoints=['https://api-usw1.carbonsense.ai'],
        timezone='America/Los_Angeles'
    ),
    'us-east-1': Region(
        id='us-east-1',
        name='Virginia',
        coordinates=(38.9072, -77.0369),
        endpoints=['https://api-use1.carbonsense.ai'],
        timezone='America/New_York'
    ),
    'eu-west-1': Region(
        id='eu-west-1',
        name='Ireland',
        coordinates=(53.3498, -6.2603),
        endpoints=['https://api-euw1.carbonsense.ai'],
        timezone='Europe/Dublin'
    )
}

class RoutingDecision(BaseModel): # Keeping existing model for compatibility
    selected_model: str
    confidence_score: float
    reasoning: str
    alternative_models: List[str]
    estimated_carbon_grams: float
    metadata: Dict[str, Any] = {}

class CarbonRouter:
    """
    Intelligent router for carbon-aware query processing.

    This class selects the optimal geographic region and AI model for a given
    query by balancing real-time grid carbon intensity and latency requirements.

    Attributes:
        regions (dict): A dictionary of supported cloud regions and their metadata.
        base_latencies (dict): Hardcoded base latencies for simulated routing decisions.
    """
    
    def __init__(self):
        self.regions = REGIONS
        # Base latency from user (simulated, assuming user is in US)
        self.base_latencies = {
            'us-west-1': 40,
            'us-east-1': 80,
            'eu-west-1': 150
        }

    async def route(
        self,
        query_analysis: QueryAnalysisResult,
        optimize_for: str = "carbon"
    ) -> RoutingDecision:
        """
        Calculates the optimal routing path for a query.

        Args:
            query_analysis (QueryAnalysisResult): Metadata about the incoming query.
            optimize_for (str): The primary metric to optimize (default: "carbon").

        Returns:
            RoutingDecision: A structured object containing the selected model,
                region, reasoning, and estimated carbon impact.
        """
        logger.info(f"Routing query: {query_analysis.intent} (Urgency: {query_analysis.urgency})")
        
        # 1. Select Region
        region_result = self._select_optimal_region(query_analysis.urgency)
        
        # 2. Select Model (Simplified for this task to focus on Region)
        # In a real system, available models would depend on the region.
        # Here we just pick a standard efficient model for the demo.
        if query_analysis.complexity == QueryComplexity.COMPLEX:
            model_name = "llama-3.3-70b-versatile" 
            tokens_per_g = 0.8
        else:
            model_name = "llama-3.1-8b-instant"
            tokens_per_g = 0.15
            
        estimated_carbon = tokens_per_g * (query_analysis.estimated_tokens / 1000) * (region_result.carbon_intensity / 200) # Normalize

        reasoning = (
            f"Routed to {region_result.selected_region} ({self.regions[region_result.selected_region].name}). "
            f"Carbon Intensity: {region_result.carbon_intensity:.0f} gCO2/kWh. "
            f"Score: {region_result.score:.2f}. "
            f"{region_result.reasoning}"
        )

        return RoutingDecision(
            selected_model=model_name,
            confidence_score=query_analysis.confidence_score,
            reasoning=reasoning,
            alternative_models=[],
            estimated_carbon_grams=estimated_carbon,
            metadata={
                "region": region_result.selected_region,
                "region_name": self.regions[region_result.selected_region].name,
                "carbon_intensity": region_result.carbon_intensity,
                "score": region_result.score
            }
        )

    def _select_optimal_region(self, urgency: QueryUrgency) -> RouteResult:
        """
        Determines the best data center region based on current metrics.

        Calculates a scores for each region using a weighted combination of
        carbon intensity and latency. Weights vary based on query urgency.

        Args:
            urgency (QueryUrgency): The urgency level of the query.

        Returns:
            RouteResult: Metadata about the selected region and its performance.
        """
        
        best_region = None
        best_score = -float('inf')
        results = []

        # Weights
        if urgency == QueryUrgency.URGENT:
            w_carbon = 0.3
            w_latency = 0.7
        else:
            w_carbon = 0.8
            w_latency = 0.2

        for region_id, region in self.regions.items():
            # 1. Get Real-time Metrics
            carbon_intensity = self._get_simulated_carbon_intensity(region)
            latency = self.base_latencies.get(region_id, 100)
            
            # 2. Normalize (Lower is better, so 1 - normalized)
            # Carbon: 0-600 gCO2/kWh
            norm_carbon = min(carbon_intensity / 600, 1.0)
            carbon_score = 1 - norm_carbon
            
            # Latency: 0-300 ms
            norm_latency = min(latency / 300, 1.0)
            latency_score = 1 - norm_latency
            
            # 3. Calculate Final Score
            total_score = (w_carbon * carbon_score) + (w_latency * latency_score)
            
            if total_score > best_score:
                best_score = total_score
                best_region = region_id

            results.append({
                "id": region_id,
                "carbon": carbon_intensity,
                "score": total_score
            })
            
        selected = self.regions[best_region]
        metrics = next(r for r in results if r["id"] == best_region)
        
        reasoning = "Chosen for " + ("lowest latency" if w_latency > w_carbon else "lowest carbon emission")
        
        return RouteResult(
            selected_region=best_region,
            selected_endpoint=selected.endpoints[0],
            carbon_intensity=metrics["carbon"],
            latency_ms=self.base_latencies.get(best_region, 100),
            score=metrics["score"],
            reasoning=reasoning
        )

    def _get_simulated_carbon_intensity(self, region: Region) -> float:
        """
        Simulates real-time carbon intensity (gCO2/kWh) for a region.

        Models the 'solar curve' where carbon intensity is lower during
        daylight hours. Adds random noise to simulate grid fluctuations.

        Args:
            region (Region): The region to simulate data for.

        Returns:
            float: Simulated carbon intensity value.
        """
        tz = pytz.timezone(region.timezone)
        current_hour = datetime.now(tz).hour
        
        # Base intensity for the region (grid mix)
        base_grid = {
            'us-west-1': 200, # California (Cleaner)
            'us-east-1': 450, # Virginia (Coal/Gas mix)
            'eu-west-1': 350  # Ireland (Wind + Gas)
        }
        
        base = base_grid.get(region.id, 300)
        
        # Solar modifier: -30% during peak sun (10am - 4pm)
        if 10 <= current_hour <= 16:
            modifier = 0.7 
        elif 8 <= current_hour <= 18:
            modifier = 0.85
        else:
            modifier = 1.0 # Night
            
        # Add some random noise for "real-time" feel
        noise = random.uniform(-10, 10)
        
        return (base * modifier) + noise
