# Reinforcement Learning Training Guide 🧠

CarbonSense AI uses a Q-Learning based reinforcement learning (RL) agent to optimize model selection decisions. This guide explains how the agent works and how to train or fine-tune it for your specific workloads.

## 🏗️ The RL Architecture

The agent solves a **Contextual Multi-Armed Bandit** problem. For every query, it must decide which LLM model to use to maximize a reward function that balances quality and carbon impact.

### State Space
The `RLState` consists of:
- `query_complexity`: Normalized score (0.0 to 1.0).
- `query_type`: Factual, Creative, Analytical, etc.
- `context_required`: Boolean.
- `estimated_tokens`: Length of the query.

### Reward Function
The agent learns by observing rewards:
`Reward = (UserSatisfaction * 10) - (CarbonGrams / BudgetRatio) - (LatencySeconds * 2)`

---

## 📈 Training the Agent

### 1. Cold Start (Simulation)
If you are starting with zero user data, you can run a simulation to bootstrap the Q-table:
```bash
python scripts/train_rl.py --episodes 5000 --simulation-mode
```
This uses a heuristic "Expert" to provide initial labels, allowing the agent to learn the basic tradeoffs between `Llama-8B` and `Claude-Opus` before seeing a real user.

### 2. Fine-tuning with User Feedback
Once in production, the agent continuously learns from `UserSatisfaction` scores (0.0 to 5.0).
- When a user marks a response as "Helpful", the agent receives a high reward.
- If the response is marked as "Too Slow" or "Incorrect", the agent receives a penalty.

---

## 🎛️ Hyperparameter Tuning

You can adjust the agent's behavior in `app/core/config.py`:

- **Learning Rate (`RL_ALPHA`)**: Default `0.001`. Increase this if your query distribution changes rapidly.
- **Discount Factor (`RL_GAMMA`)**: Default `0.95`. Since queries are mostly independent, this is less critical than in traditional RL.
- **Exploration Rate (`RL_EPSILON`)**: Default `0.1`. Controls how often the agent tries a suboptimal model to see if it has improved.

---

## 📊 Monitoring Progress

You can view the agent's current "Knowledge" via the admin dashboard or CLI:
```bash
python scripts/inspect_rl.py --verbose
```
**Output Example:**
```text
State: [Analytical, Complexity 0.8, Context True]
- Model: gpt-4-turbo     | Q-Value: 8.42 (Exploiting)
- Model: llama-3-70b     | Q-Value: 7.91
- Model: llama-3-8b      | Q-Value: 4.10
```

## 🛠️ Resetting the Brain
If the agent learns "bad habits" due to corrupted feedback data, you can clear the Q-table:
```bash
redis-cli DEL carbonsense:rl:qtable
```
The agent will start exploring from scratch.
