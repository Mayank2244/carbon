from datetime import datetime, timedelta
from typing import Dict, List
import asyncio

class StatsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatsManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Initialize with zero values - all data comes from real queries."""
        self.total_requests = 0
        self.total_tokens_used = 0
        self.total_tokens_saved = 0
        self.total_carbon_saved = 0.0
        self.total_carbon_used = 0.0
        
        # Track energy separately to account for fluctuating grid intensity
        self.total_energy_saved_kwh = 0.0
        self.total_energy_used_kwh = 0.0
        
        self.current_carbon_intensity = 475.0 # Default global average
        
        self.cache_hits = 0
        self.cache_misses = 0
        
        self.model_usage: Dict[str, int] = {}
        self.hourly_activity: List[Dict] = [] 
        self.latencies: List[float] = []
        
        self.daily_emissions: Dict[str, float] = {} 
        self.daily_requests: Dict[str, int] = {}

        # NEW: Granular Tracking
        self.savings_by_category = {
            "cache": 0.0,
            "model_selection": 0.0,
            "optimization": 0.0
        }
        self.region_usage: Dict[str, int] = {}

    def record_request(
        self, 
        model: str, 
        tokens_used: int, 
        tokens_saved: int, 
        carbon_saved: float, 
        carbon_used: float, 
        latency: float, 
        cached: bool,
        energy_used_kwh: float = 0.0,
        energy_saved_kwh: float = 0.0,
        provider: str = "unknown",
        region: str = "unknown", 
        savings_breakdown: Dict[str, float] = None
    ):
        self.total_requests += 1
        self.total_tokens_used += tokens_used
        self.total_tokens_saved += tokens_saved
        self.total_carbon_saved += carbon_saved
        self.total_carbon_used += carbon_used
        
        # Accumulate explicit energy values (Physically accurate)
        self.total_energy_saved_kwh += energy_saved_kwh
        self.total_energy_used_kwh += energy_used_kwh
        
        if cached:
            self.cache_hits += 1
            # If cached, attribute all savings to cache
            self.savings_by_category["cache"] += carbon_saved
        else:
            self.cache_misses += 1
            if savings_breakdown:
                self.savings_by_category["model_selection"] += savings_breakdown.get("model", 0.0)
                self.savings_by_category["optimization"] += savings_breakdown.get("optimization", 0.0)

        # Track usage
        self.model_usage[model] = self.model_usage.get(model, 0) + 1
        
        # Track region/provider
        region_key = f"{provider} ({region})"
        self.region_usage[region_key] = self.region_usage.get(region_key, 0) + 1
        
        self.latencies.append(latency)
        if len(self.latencies) > 50:
            self.latencies.pop(0)

        # Track daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_requests[today] = self.daily_requests.get(today, 0) + 1
        self.daily_emissions[today] = self.daily_emissions.get(today, 0.0) + carbon_saved

    def update_carbon_intensity(self, intensity: float):
        """Update the current grid carbon intensity."""
        if intensity > 0:
            self.current_carbon_intensity = intensity

    def get_live_metrics(self) -> Dict:
        total_cache = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_cache) if total_cache > 0 else 0
        
        # Calculate percentages for model usage
        dist = []
        for model, count in self.model_usage.items():
            percentage = (count / self.total_requests) * 100 if self.total_requests > 0 else 0
            dist.append({"name": model, "value": round(percentage, 1)})
        
        # Saved percentages
        total_potential_tokens = self.total_tokens_used + self.total_tokens_saved
        tokens_saved_percent = (self.total_tokens_saved / total_potential_tokens * 100) if total_potential_tokens > 0 else 0
        
        energy_saved_kwh = self.total_energy_saved_kwh
        energy_used_kwh = self.total_energy_used_kwh
        energy_baseline_kwh = energy_used_kwh + energy_saved_kwh
        
        # Efficiency Score Calculation (0-100)
        # Based on Ratio of Saved / (Used + Saved)
        efficiency_score = 0
        if energy_baseline_kwh > 0:
            efficiency_score = int((energy_saved_kwh / energy_baseline_kwh) * 100)
        
        # Format Top Saving Actions
        actions = [
            {"action": "Cache Optimization", "savings": f"{self.savings_by_category['cache']:.1f}g", "impact": "High"},
            {"action": "Model Selection", "savings": f"{self.savings_by_category['model_selection']:.1f}g", "impact": "Med"},
            {"action": "Prompt Optimization", "savings": f"{self.savings_by_category['optimization']:.1f}g", "impact": "Low"},
        ]
        # Sort by savings value
        actions.sort(key=lambda x: float(x['savings'].replace('g','')), reverse=True)
        
        # Format Regional Breakdown
        regions = []
        for name, count in self.region_usage.items():
            load = int((count / self.total_requests) * 100) if self.total_requests > 0 else 0
            intensity = "Low" # Default for Cloud/Groq
            if "local" in name.lower(): intensity = "Low"
            elif "azure" in name.lower(): intensity = "Med" # Hypothetical
            
            regions.append({"region": name, "load": load, "intensity": intensity})
        
        return {
            "carbon_intensity": int(self.current_carbon_intensity), 
            "cache_hit_rate": round(hit_rate, 2),
            "tokens_saved": self.total_tokens_saved,
            "tokens_saved_percent": round(tokens_saved_percent, 1),
            "carbon_saved_today": round(self.total_carbon_saved, 2),
            
            "energy_saved_kwh": round(energy_saved_kwh, 4),
            "energy_used_kwh": round(energy_used_kwh, 4),
            "energy_baseline_kwh": round(energy_baseline_kwh, 4),
            
            "active_model_dist": sorted(dist, key=lambda x: x['value'], reverse=True),
            "response_times": [{"id": i, "latency": l} for i, l in enumerate(self.latencies)],
            
            # NEW: Real Analytics Data
            "efficiency_score": efficiency_score,
            "top_actions": actions,
            "regional_breakdown": regions
        }

    def get_analytics_trends(self, days=7) -> Dict:
        # Generate last 7 days structure
        trends = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
            # Day name
            day_name = (datetime.now() - timedelta(days=6-i)).strftime("%a")
            
            trends.append({
                "day": day_name,
                "date": date,
                "emissions": round(self.daily_emissions.get(date, 0.0) / 10.0, 1), # Scaled for chart visibility
                "requests": self.daily_requests.get(date, 0)
            })
            
        return {
            "weekly_data": trends,
            "total_emissions": round(self.total_carbon_saved, 2), # Using saved as proxy for impact metric for now
            "total_requests": self.total_requests,
            
            # NEW: Add Efficiency Score history (simulated for now as we don't prefer persistent db yet)
            "efficiency_current": self.get_live_metrics()["efficiency_score"] 
        }

stats_manager = StatsManager()
