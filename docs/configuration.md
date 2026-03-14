# Configuration Guide ⚙️

CarbonSense AI is configured primarily via environment variables (`.env`). This file explains every available option and how to tune the system for your needs.

## 🔑 Required API Keys

| Variable | Description | Where to get it |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | Primary inference engine | [groq.com](https://groq.com) |
| `ELECTRICITY_MAPS_KEY`| Real-time carbon data | [electricitymaps.com](https://www.electricitymaps.com/free-tier) |
| `ANTHROPIC_API_KEY` | Secondary LLM provider | [anthropic.com](https://anthropic.com) |

---

## 🎛️ Optimization Settings

### `CARBON_BUDGET_HOURLY`
- **Default**: `100.0`
- **Description**: The maximum amount of CO2 (in grams) the system is allowed to "spend" per hour. If the budget is low, the `CarbonRouter` will aggressively favor smaller models and green regions, even if latency is higher.

### `OPTIMIZE_FOR`
- **Values**: `carbon`, `cost`, `balanced`
- **Description**:
  - `carbon`: Minimizes gCO2 regardless of latency or cost.
  - `cost`: Minimizes API spend.
  - `balanced`: Attempts to find a middle ground.

---

## 💾 Caching Configuration

### `CACHE_TTL`
- **Default**: `86400` (24 hours)
- **Description**: How long exact L1 matches stay in Redis.

### `VECTOR_CACHE_THRESHOLD`
- **Default**: `0.93`
- **Description**: The cosine similarity score required to trigger an L2 cache hit. Lowering this increases the hit rate but may return slightly less relevant answers.

---

## 📚 GraphRAG Settings

### `GRAG_CONFIDENCE_THRESHOLD`
- **Default**: `0.85`
- **Description**: Minimum confidence required for the Knowledge Graph to answer a query without calling an LLM.

### `GRAG_MAX_DEPTH`
- **Default**: `2`
- **Description**: How deep the graph traversal should go when looking for entity relationships.

---

## 🧠 RL Optimizer

### `RL_LEARNING_RATE`
- **Default**: `0.001`
- **Description**: The step size for Q-value updates.

### `RL_EXPLORATION_RATE`
- **Default**: `0.1`
- **Description**: The probability (`epsilon`) that the system will try a random model to "explore" new efficiencies.

---

## 🔌 Database Connections

```bash
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:pass@localhost:5432/carbonsense
NEO4J_URI=bolt://localhost:7687
```

## 📋 Best Practices for Production
1. **Low Budget Mode**: In environments with strict ESG targets, set `CARBON_BUDGET_HOURLY` to `10.0`. This forces the system into "Minimalist Mode".
2. **Warm Cache**: Run `scripts/precompute_common_queries.py` to seed the L1 cache before launch.
3. **Region Pinning**: If you are legally required to keep data in a specific region (e.g., GDPR), use `ALLOWED_REGIONS=['eu-west-1']` to bypass carbon-aware global routing.
