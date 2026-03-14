# Production Deployment Guide 🚀

This document outlines the best practices and strategies for deploying CarbonSense AI in a production environment.

## 🏗️ Recommended Stack

For a robust production environment, we recommend the following:
- **Compute**: AWS ECS, EKS, or Google Kubernetes Engine.
- **Cache**: Managed Redis (AWS ElastiCache or GCP Memorystore).
- **Database**: Managed PostgreSQL (AWS RDS).
- **Search**: Dedicated ChromaDB or Pinecone instance for L2 cache.
- **Graph**: Neo4j Aura (Managed Cloud).

---

## 🐳 Containerization

Use the provided `Dockerfile` to build your production image:

```bash
docker build -t carbonsense-backend:latest ./backend
```

### Resource Allocation
- **Backend (API)**: 1 vCPU, 2GB RAM (Scales horizontally).
- **Redis**: 2GB RAM minimum (Depends on cache volume).
- **Neo4j**: 4GB RAM minimum for large knowledge graphs.

---

## 🌐 Global Infrastructure Strategy

To maximize carbon savings, consider a **Multi-Region Deployment**:

1. Deploy the CarbonSense AI orchestrator in a central region (e.g., `us-east-1`).
2. Configure worker LLM endpoints in multiple regions:
   - `eu-central-1` (Germany - High Renewable Mix)
   - `ca-central-1` (Canada - Hydro-dominant)
   - `us-west-1` (California - High Solar)

CarbonSense's `CarbonRouter` will automatically prioritize the greenest region for every request.

---

## 📊 Monitoring & Logging

### Health Checks
The backend provides a `/health` endpoint. Configure your load balancer to poll this every 30 seconds.

### ESG Reporting
CarbonSense logs emission data to PostgreSQL. To generate a weekly ESG report:
```bash
python scripts/generate_esg_report.py --period weekly --format pdf
```

### Error Tracking
Integrate **Sentry** or **Datadog** by setting the following env variables:
```bash
SENTRY_DSN=your_dsn_here
DATADOG_API_KEY=your_key_here
```

---

## 🛡️ Security Hardening

1. **API Authentication**: Use an API Key or OAuth2 gateway in front of the `CarbonSenseAI` service.
2. **Environment Variables**: Never commit `.env` files. Use AWS Secrets Manager or HashiCorp Vault.
3. **Database VPC**: Ensure Redis and PostgreSQL are only accessible from the Backend VPC.

---

## 📈 Scaling Considerations

- **Redis Scaling**: If your L1 cache hit rate drops, consider increasing Redis memory or using a cluster mode.
- **Graph Indexing**: As your Knowledge Graph grows, ensure you have proper indexes on `Entity(name)` and `Relationship(type)`.
- **API Rate Limits**: Ensure your Groq/Anthropic tier supports the expected peak RPS (Requests Per Second).

---

## 🏁 Deployment Checklist
- [ ] Environment variables set for all API keys.
- [ ] Redis and PostgreSQL connections verified.
- [ ] Neo4j indexes created.
- [ ] Persistence enabled for ChromaDB volume.
- [ ] Horizontal Pod Autoscaling (HPA) configured in K8s.
