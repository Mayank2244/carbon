# CarbonSense AI System - Backend

A production-ready FastAPI backend for carbon-efficient AI query routing. The system intelligently routes queries to the most carbon-efficient AI model while maintaining quality standards.

## 🌟 Features

- **Intelligent Query Analysis**: Uses spaCy to analyze complexity and requirements.
- **Carbon-Efficient Routing**: Dynamics routing based on real-time solar/wind availability.
- **Prompt Optimization**: Semantic compression (⚡ Badge) to reduce token count.
- **Adaptive Model Selection**: Uses Groq Llama 3.3-70B and 3.1-8B models.
- **RL Optimization**: Feedback-driven learning for the greenest routing decisions.
- **Real-time Stats**: Live tracking of latency and carbon savings.

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── __init__.py
│   ├── core/                   # Core configuration and utilities
│   │   ├── config.py          # Settings management
│   │   ├── logging.py         # Logging configuration
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── __init__.py
│   ├── db/                     # Database layer
│   │   ├── session.py         # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── redis.py           # Redis connection
│   │   └── __init__.py
│   ├── modules/                # Application modules
│   │   ├── query_analyzer/    # Query analysis
│   │   ├── carbon_router/     # Carbon-efficient routing
│   │   ├── cache_manager/     # Caching logic
│   │   ├── rag_engine/        # RAG implementation
│   │   ├── rl_optimizer/      # RL-based optimization
│   │   └── model_selector/    # AI model interactions
│   └── api/                    # API routes
│       └── v1/
│           ├── query.py       # Query endpoints
│           └── __init__.py
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── .gitignore
└── README.md

```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Setup database**
```bash
# Start PostgreSQL and Redis (if not using Docker)
# Or use Docker Compose:
docker-compose up -d postgres redis
```

6. **Run the application**
```bash
python -m app.main
# Or using uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access the API**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Root: http://localhost:8000/

### Docker Deployment

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Run in detached mode**
```bash
docker-compose up -d
```

3. **View logs**
```bash
docker-compose logs -f app
```

4. **Stop services**
```bash
docker-compose down
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Application
APP_NAME=CarbonSense AI
DEBUG=False
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Models
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## 📚 API Usage

### Process a Query

```bash
curl -X POST "http://localhost:8000/api/v1/query/process" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain quantum computing",
    "optimize_for": "carbon",
    "use_cache": true
  }'
```

### Response Example

```json
{
  "query": "Explain quantum computing",
  "response": "Quantum computing is...",
  "model_used": "gpt-3.5-turbo",
  "carbon_grams": 0.75,
  "tokens_used": 150,
  "latency_ms": 500,
  "cached": false,
  "metadata": {
    "query_type": "factual",
    "complexity": 0.45,
    "routing_reasoning": "Selected gpt-3.5-turbo for factual query..."
  }
}
```

## 🏗️ Architecture

### Module Descriptions

- **query_analyzer**: Analyzes queries to determine type, complexity, and requirements
- **carbon_router**: Routes queries to the most carbon-efficient model
- **cache_manager**: Manages Redis caching for query responses
- **rag_engine**: Retrieval-augmented generation for context-aware responses
- **rl_optimizer**: Reinforcement learning for adaptive routing optimization
- **model_selector**: Handles AI model API interactions (OpenAI, Anthropic)

### Database Models

- **Query**: User queries with metadata
- **ModelResponse**: AI model responses and metrics
- **CarbonMetrics**: Carbon emission tracking
- **RoutingDecision**: Model routing decisions
- **CacheEntry**: Cache metadata
- **RLFeedback**: Reinforcement learning feedback

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## 📊 Monitoring

- Prometheus metrics available at `:9090` (if enabled)
- Health check endpoint: `/health`
- System stats: `/api/v1/query/stats`

## 🔒 Security

- Non-root Docker user
- Environment variable validation
- CORS configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy

## 📝 Code Style

The project follows:
- PEP 8 style guidelines
- Type hints for all functions
- Comprehensive docstrings
- Async/await patterns

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write docstrings for all public functions
4. Add tests for new features
5. Update documentation

## 📄 License

ISC License

## 🙋 Support

For issues and questions, please open an issue in the repository.

---

**Built with ❤️ for a carbon-efficient AI future**
# carbonsense
