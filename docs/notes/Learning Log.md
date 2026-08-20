# Learning Log: Docker & Infrastructure Setup

## Date: 2026-08-18
## Session: Docker Compose setup (Postgres + RabbitMQ)

---

### Q: Why does RabbitMQ need two ports?
**A:** 5672 is the AMQP protocol port (Celery workers connect here). 15672 is the management UI (browser dashboard). Different protocols, different ports.

### Q: Why do containers connect via service name (postgres:5432) and not localhost?
**A:** Inside the Docker network, each container has its own IP. Docker Compose sets up DNS resolution so service names map to container IPs. `localhost` inside a container points to ITSELF, not other containers. Host machine reaches containers via `localhost:5432` (port mapping).

### Q: What does "5432:5432" mean in docker-compose ports?
**A:** `host:container`. When I hit `localhost:5432` on my computer, Docker forwards to port 5432 inside the container.

### Q: What is a Docker volume and why do we need it?
**A:** A volume maps a container path to a host machine directory. Containers are ephemeral — their filesystem dies when the container stops. Volumes persist data across container restarts. Without a volume, Postgres would lose all data on `docker-compose down`.

### Q: How does Postgres know the username/password?
**A:** Environment variables (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) are passed into the container at startup. The official Postgres image reads them and creates the initial user/database. Applications connect using the same credentials in their connection string.

### Q: What is a healthcheck in docker-compose?
**A:** A command Docker runs periodically inside the container. If it succeeds (exit code 0), the container is marked healthy. Used to ensure services are ready before dependent services start. Example: `pg_isready -U oncall -d oncall_investigator` checks Postgres is accepting connections.

### Q: What does "pg_isready -U oncall" actually do?
**A:** `pg_isready` is a Postgres utility that checks if the database server is accepting connections. `-U oncall` checks for user "oncall". Without `-d`, it defaults to checking a database with the same name as the user — which caused our error (database "oncall" did not exist). Fixed by adding `-d ${POSTGRES_DB}`.

### Q: Why externalize passwords to .env instead of hardcoding in docker-compose?
**A:** Security best practice. .env is gitignored (not committed to repo). .env.example shows the expected variables with placeholder values. Interviewers will notice this — it signals production-grade thinking.

### Q: What's the difference between docker-compose down and stop?
**A:** `down` removes containers AND networks (but keeps volumes). `stop` just stops containers — networks and volumes remain. Data in volumes survives both.

---

## Key commands learned

```bash
docker-compose up -d          # start services in background
docker ps                     # list running containers
docker logs <container-name>  # view container output
docker-compose down           # stop and remove containers + networks
docker stop <container-name>  # stop a single container