# CarbonSense AI - Database & Docker Guide

This document contains all the essential commands for running, stopping, and accessing the databases (PostgreSQL, Neo4j, Redis) required for the CarbonSense AI backend.

---

## 🚀 General Docker Commands

These commands should be run inside the `backend` directory where the `docker-compose.yml` file is located:

**1. Start all databases in the background:**
```bash
docker-compose up -d
```

**2. Stop all databases:**
```bash
docker-compose down
```

**3. Check running containers:**
```bash
docker ps
```

**4. View logs for all containers:**
```bash
docker-compose logs -f
```

---

## 🗄️ PostgreSQL Commands

**Start only Postgres:**
```bash
docker-compose up -d postgres
```

**View Postgres logs:**
```bash
docker logs carbonsense_postgres
```

**Access Postgres inside the container (CLI):**
```bash
docker exec -it carbonsense_postgres psql -U carbonsense -d carbonsense_db
```

**Open Postgres Web UI (Adminer):**
1. Open up Safari/Chrome and go to: **[http://localhost:8080](http://localhost:8080)**
2. In the login screen, enter the following:
   - System: `PostgreSQL`
   - Server: `postgres`
   - Username: `carbonsense`
   - Password: `password`
   - Database: `carbonsense_db`

---

## 🕸️ Neo4j Commands

**Start only Neo4j:**
```bash
docker-compose up -d neo4j
```

**View Neo4j logs:**
```bash
docker logs carbonsense_neo4j
```

**Access Neo4j inside the container (Cypher CLI):**
```bash
docker exec -it carbonsense_neo4j cypher-shell -u neo4j -p password
```

**Open Neo4j Web UI (Browser):**
1. Open up Safari/Chrome and go to: **[http://localhost:7474](http://localhost:7474)**
2. In the login screen, enter the following:
   - Connect URL: `neo4j://localhost:7687` (or default)
   - Database: `neo4j`
   - Username: `neo4j`
   - Password: `password`

---

## 🔴 Redis Commands

**Start only Redis:**
```bash
docker-compose up -d redis
```

**View Redis logs:**
```bash
docker logs carbonsense_redis
```

**Access Redis inside the container (CLI):**
```bash
docker exec -it carbonsense_redis redis-cli
```
*(Once inside, you can type `ping` to verify it's working).*

**Open Redis Web UI (Redis Commander):**
1. Open up Safari/Chrome and go to: **[http://localhost:8081](http://localhost:8081)**
2. This will directly open the Redis database view without needing a password.

---

## 🧹 Cleaning Up (If Things Break)

If a service is constantly restarting or crashing, you can wipe its data completely. Make sure the container is stopped (`docker-compose down`) before doing this.

**Clear Postgres Data:**
```bash
docker volume rm backend_postgres_data
```

**Clear Neo4j Data:**
```bash
docker volume rm backend_neo4j_data
docker volume rm backend_neo4j_logs
```

**Clear Redis Data:**
```bash
docker volume rm backend_redis_data
```
*(Note: After removing a volume, data is lost permanently. Running `docker-compose up -d` will create a fresh, empty database).*
