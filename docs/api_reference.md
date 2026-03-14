# API Reference 🔌

This document provides a detailed reference for the core classes and methods in the CarbonSense AI library.

## 🧠 Core Orchestrator

### `CarbonSenseAI`
The main entry point for the system.

**Constructor:*
```python
CarbonSenseAI(
    carbon_budget: float = 100.0,
    enable_rl: bool = True,
    optimize_for: str = "carbon"
)
```
- `carbon_budget`: Maximum allowable gCO2 per hour.
- `enable_rl`: Whether to use Reinforcement Learning for decision making.
- `optimize_for`: Priority metric ("carbon", "cost", or "balanced").

**Methods:**
- `query(text: str) -> CarbonResponse`: Processes a user query through the full optimization pipeline.

---

## 🔍 Modules

### `QueryAnalyzer`
Located in `app.modules.query_analyzer`.

**Method: `analyze(query: str) -> QueryAnalysisResult`**
- Analyzes text for complexity, intent, and domain.
- Returns a dataclass with classification labels and token estimates.

### `CarbonRouter`
Located in `app.modules.carbon_router`.

**Method: `route(analysis: QueryAnalysisResult) -> RoutingDecision`**
- Fetches real-time carbon data from `CarbonAPIClient`.
- Returns the selected region and model suggestion.

### `CacheManager`
Located in `app.modules.cache_manager`.

**Method: `get_query_response(query: str) -> Optional[Dict]`**
- Checks L1 (Redis) and L2 (ChromaDB) for matches.
**Method: `cache_query_response(query: str, response: Dict)`**
- Stores the response in both cache layers.

### `GraphRAG`
Located in `app.modules.graph_rag`.

**Method: `query(text: str) -> RAGResponse`**
- Performs entity extraction and Neo4j traversal.
- Returns an answer if confidence exceeds the internal threshold.

### `RLOptimizer`
Located in `app.modules.rl_optimizer`.

**Method: `select_action(state: RLState) -> RLAction`**
- Picks a model based on current energy mix and query complexity.
**Method: `update(state, action, reward, next_state)`**
- Updates internal Q-values based on system performance.

---

## 📦 Data Models

### `CarbonResponse` (Returned by `ai.query`)
- `answer` (str): The final text response.
- `carbon_gco2` (float): Estimated carbon footprint in grams.
- `model_name` (str): The LLM that generated the answer.
- `region` (str): The data center region used.
- `cached` (bool): Whether the response came from cache.
- `source` (str): One of "CACHE", "GRAG", or "LLM".

---

## 🛠️ Internal Clients

### `CarbonAPIClient`
- `get_carbon_intensity(lat, lon) -> CarbonData`
- `get_region_carbon(region_code) -> CarbonData`
- Automatically handles API switching (Electricity Maps → WattTime) and fallbacks.
