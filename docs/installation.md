# Installation & Setup Guide 📦

This guide provide detailed instructions for setting up CarbonSense AI in various environments.

## 🏁 Prerequisites

Before you begin, ensure you have the following installed:
- **Python**: version 3.10 or higher.
- **Git**: To clone the repository.
- **Node.js & npm**: (Optional but recommended for the frontend dashboard).

### External Services
You will need API keys for the following (many have free tiers):
1. **Groq API**: For high-speed LLM inference.
2. **Electricity Maps**: For real-time carbon intensity data.
3. **Neo4j**: (Optional) For the Knowledge Graph RAG module.
4. **Redis**: For caching layers.

---

## 💻 Local Desktop Setup

### Windows
1. Install [Python 3.10+](https://www.python.org/downloads/windows/).
2. Open PowerShell or Command Prompt.
3. Clone the repo: `git clone https://github.com/yourusername/carbonsense-ai.git`
4. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\\venv\\Scripts\\activate
   ```
5. Install dependencies: `pip install -r requirements.txt`
6. Copy environment template: `cp .env.example .env`

### macOS / Linux
1. Ensure Python 3.10+ is installed (`python3 --version`).
2. Clone the repo: `git clone https://github.com/yourusername/carbonsense-ai.git`
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies: `pip install -r requirements.txt`
5. Copy environment template: `cp .env.example .env`

---

## 🐳 Docker Installation (Recommended)

Docker provides the most reliable way to run CarbonSense AI with all its dependencies (Redis, Neo4j) pre-configured.

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Navigate to the root folder.
3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
   This will launch:
   - **Backend**: Port 8000
   - **Frontend**: Port 3000
   - **Redis**: Port 6379
   - **Neo4j**: Port 7474

---

## ⚙️ Configuration

Open the `.env` file and fill in your credentials:

```bash
# Core APIs
GROQ_API_KEY=your_key_here
ELECTRICITY_MAPS_API_KEY=your_key_here

# Databases
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# App Settings
CARBON_BUDGET_HOURLY=100
OPTIMIZE_FOR=carbon  # options: carbon, cost, balanced
```

---

## 🛠️ Troubleshooting

### Redis Connection Errors
- Ensure Redis is running: `redis-cli ping` should return `PONG`.
- If using Docker, check `docker ps` to ensure the Redis container is healthy.

### Neo4j Linking Issues
- If you get "GraphRAG deactivated" logs, check your Neo4j credentials.
- Ensure the `neo4j` database exists and the user has sufficient permissions.

### Python Dependency Conflicts
- Always use a virtual environment.
- If `pip install` fails, try updating pip: `pip install --upgrade pip`.
- If you have Apple Silicon (M1/M2), you may need to install `sentence-transformers` via conda if pip fails.

---

## 🧪 Verifying Installation

Run the health check script:
```bash
python scripts/health_check.py
```
If everything is green, you are ready to process your first carbon-aware query!
