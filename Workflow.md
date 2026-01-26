# Database Migration and Optimization Playbook

## 1. Goals and Constraints
- Objective: (upgrade | replatform | cloud move | multi-region | compliance)
- RTO: <X minutes> | RPO: <Y minutes>
- Downtime tolerance: (zero | <= N minutes)
- Target: <engine/version/cloud/region>
- Rollback: <snapshot | PITR | dual-writes | traffic flip-back>

## 2. Inventory and Assessment
- Engine/version, extensions/plugins
- Data volume per table; growth rate
- Critical tables and SLAs
- Top slow queries, long transactions
- Dependencies: ETL, jobs, BI, triggers, functions

## 3. Migration Plan

### 3.1 Postgres (examples)
- Backup:
  ```bash
  pg_dump -Fc -j 4 -h <src_host> -U <user> -d <db> -f dump.dump
  pg_restore -j 8 -h <tgt_host> -U <user> -d <db> dump.dump
  ```
- Logical replication:
  ```sql
  -- Source
  CREATE PUBLICATION app_pub FOR ALL TABLES;
  -- Target
  CREATE SUBSCRIPTION app_sub CONNECTION 'host=<src> dbname=<db> user=<user> password=<pwd>' PUBLICATION app_pub;
  ```
- Post-restore:
  ```sql
  VACUUM (ANALYZE);
  -- Concurrent index creation to avoid write locks:
  CREATE INDEX CONCURRENTLY idx_orders_created_at ON orders (created_at);
  ```

### 3.2 MySQL (examples)
- Consistent backup:
  ```bash
  mysqldump --single-transaction --routines --triggers --events --hex-blob -h <src> -u <user> -p <db> > dump.sql
  mysql -h <tgt> -u <user> -p <db> < dump.sql
  ```
- Online schema change:
  ```bash
  gh-ost --host=<src> --database=<db> --table=<table> --alter="ADD COLUMN ..." --cut-over=default --execute
  # or
  pt-online-schema-change --alter "ADD COLUMN ..." D=<db>,t=<table> --execute
  ```

### 3.3 Cross-engine (e.g., MySQL → Postgres)
- Tools: AWS DMS, pgloader, ora2pg
- Tasks: type mapping, function/trigger rewrites, index strategy translation, query testing

### 3.4 CDC / Dual-run
- Debezium + Kafka: stream changes to target
- Validate parity, then cut over writes to target

## 4. Validation

### 4.1 Data parity
```sql
-- Row counts
SELECT table_name, row_count FROM (
  -- Implement per-engine count logic
) t;

-- Example Postgres checksum (per table)
SELECT md5(string_agg(id::text || ':' || updated_at::text, '|')) FROM orders;
```

### 4.2 Referential integrity
```sql
-- Ensure constraints enabled and no violations
-- Postgres:
SELECT conname, convalidated FROM pg_constraint WHERE convalidated = false;
```

### 4.3 Application checks
- Read/write smoke tests
- Business-critical flows
- Error rates and latency under representative load

## 5. Cutover
- Freeze writes or enable dual-writes
- Switch connection strings/DNS
- Health checks, observe metrics
- Rollback ready: <procedure and trigger condition>

## 6. Post-migration Optimization

### 6.1 Index Strategy
- Composite index order matches WHERE and ORDER BY
- Covering indexes for hot read paths
- Partial indexes (Postgres) on active subsets
- Specialized indexes: GIN/GiST for JSONB/FTS

### 6.2 Query Tuning
```sql
-- Postgres
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
-- MySQL
EXPLAIN FORMAT=JSON SELECT ...;
```
- Avoid SELECT *
- Parameterized queries
- Fix N+1 joins, batch reads

### 6.3 Config Tuning (examples)
- Postgres:
  - shared_buffers: ~25% RAM
  - effective_cache_size: ~50–75% RAM
  - work_mem: sized for concurrent sorts
  - maintenance_work_mem: larger for index builds
  - autovacuum: tune thresholds and cost limits
  - WAL archiving for PITR
- MySQL:
  - innodb_buffer_pool_size: ~70–80% RAM
  - innodb_log_file_size: adequate for write load
  - innodb_flush_method: O_DIRECT (where appropriate)

### 6.4 Data Layout
- Partition large tables (range/hash) for pruning
- Materialized views for heavy aggregates
- Cache hot reads (Redis)
- Archive cold data; manage bloat

## 7. Monitoring and Maintenance
- Metrics: P95 latency, slow query log, deadlocks, replication lag, cache hit, CPU/IO, locks
- Maintenance: ANALYZE/VACUUM (Postgres), OPTIMIZE where relevant (MySQL)
- Backups: full + incremental; periodic restore tests; PITR drills

## 8. Checklists

### Pre-migration
- [ ] Inventory completed
- [ ] Compatibility and feature review
- [ ] Backup/CDC pipeline tested
- [ ] Dry run successful
- [ ] Validation scripts ready
- [ ] Rollback plan documented

### Cutover
- [ ] Writes frozen or dual-writes enabled
- [ ] Switch executed
- [ ] Health checks passed
- [ ] Metrics stable

### Post-migration
- [ ] Indexes created and validated
- [ ] Queries tuned
- [ ] Config tuned
- [ ] Backup and monitoring confirmed


Great question. Here’s a simple, beginner-friendly way to get started with database migration and optimization through a hands-on project. I’ll give you three project options, then a detailed step-by-step path for one recommended starter project with ready-to-use files you can run locally.

Starter project options
- Option A (Recommended): Postgres migration + optimization using the Pagila sample dataset. Migrate from local Postgres to a managed Postgres instance (e.g., a cloud DB), measure performance, add indexes, and tune a few queries.
- Option B: MySQL migration + optimization using the Sakila sample dataset. Migrate from local MySQL to a cloud MySQL, apply online schema changes, and analyze slow query logs.
- Option C: Cross-engine migration (MySQL → Postgres) using pgloader. Move data, fix type mappings, validate parity, and optimize on the target.

What you’ll learn
- How to stand up a DB locally and load sample data
- How to take a consistent backup and restore it elsewhere
- How to validate data parity after migration
- How to measure query performance and optimize with indexes/config tuning

Recommended beginner path: Postgres local → cloud migration
- Day 1: Set up local Postgres, load sample data (Pagila)
- Day 2: Learn backup/restore (pg_dump/pg_restore) and cutover basics
- Day 3: Validate data and run EXPLAIN on key queries
- Day 4: Add indexes and measure improvements
- Day 5: Tweak basic Postgres settings and review monitoring

Files to run locally
Use these files to spin up Postgres quickly and follow the steps below.

```yaml name=docker-compose.yml
version: "3.8"
services:
  postgres:
    image: postgres:16
    container_name: local_postgres
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: appsecret
      POSTGRES_DB: pagila
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./scripts:/docker-entrypoint-initdb.d
  pgadmin:
    image: dpage/pgadmin4:8
    container_name: local_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: adminsecret
    ports:
      - "8080:80"
    depends_on:
      - postgres
volumes:
  pg_data:
```

````markdown name=getting-started-migration-project.md
# Getting Started: Postgres Migration + Optimization (Pagila)

This guide helps you learn database migration and optimization using a local Postgres and a managed Postgres target. You’ll deploy, migrate, validate, and optimize queries with measurable before/after results.

## Prerequisites
- Docker + Docker Compose installed
- psql client installed (optional but handy)
- Basic terminal skills

## 1) Start local Postgres with Pagila
1. `docker compose up -d`
2. Load the Pagila sample dataset into the `pagila` database:
   - Place `pagila-schema.sql` and `pagila-data.sql` into `./scripts/` so they auto-run.
   - Alternatively, run:
     ```bash
     docker exec -i local_postgres psql -U appuser -d pagila -f /docker-entrypoint-initdb.d/pagila-schema.sql
     docker exec -i local_postgres psql -U appuser -d pagila -f /docker-entrypoint-initdb.d/pagila-data.sql
     ```
3. Open pgAdmin at http://localhost:8080 and connect to `local_postgres` (host: `postgres`, user: `appuser`, db: `pagila`).

## 2) Baseline performance and data checks
1. Row counts:
   ```sql
   SELECT relname AS table, n_live_tup AS estimated_rows
   FROM pg_stat_user_tables
   ORDER BY estimated_rows DESC;
   ```
2. Pick 2–3 queries to evaluate (examples in `validation.sql`). Run `EXPLAIN (ANALYZE, BUFFERS)` for each and save results.
3. Capture baseline metrics: execution time, rows returned, and if possible simple timing with `\timing` in `psql`.

## 3) Create a backup and restore to target
1. Create a dump:
   ```bash
   docker exec -i local_postgres pg_dump -Fc -U appuser -d pagila -f /var/lib/postgresql/data/pagila.dump
   docker cp local_postgres:/var/lib/postgresql/data/pagila.dump ./pagila.dump
   ```
2. Create a target Postgres (cloud or second local container). Get a connection string.
3. Restore:
   ```bash
   pg_restore -h <target_host> -U <target_user> -d <target_db> -j 4 ./pagila.dump
   ```
4. Run `validation.sql` against the target to confirm parity (row counts, sample aggregates).

## 4) Optimize queries and indexing
1. Identify slow queries (from your baseline).
2. Create indexes (see `optimization.sql`) then re-run `EXPLAIN (ANALYZE, BUFFERS)`:
   - Compare execution times before vs. after.
   - Ensure the planner is using the new index (look for `Index Scan`).
3. Optional: use `CREATE INDEX CONCURRENTLY` on larger instances to avoid write locks.

## 5) Basic Postgres config tuning (optional)
- `shared_buffers`: ~25% of RAM
- `effective_cache_size`: ~50–75% of RAM
- `work_mem`: enough for sorts/hashes (careful: per-operation)
- After changes, re-run your test queries and note any improvements.

## 6) Wrap up and document
- Capture before/after metrics
- Note indexes added and why
- Save `EXPLAIN` plans before and after
- Record any config changes

## Deliverables
- `pagila.dump` (backup file you created)
- `validation.sql` results before/after migration
- `optimization.sql` changes and the resulting performance gains
- A short write-up with your learnings

## Next steps
- Try logical replication (publications/subscriptions) for low-downtime sync
- Explore partitioning on large time-based tables
- Practice point-in-time recovery (PITR)
````

```sql name=validation.sql
-- Basic data parity checks and baseline EXPLAINs

-- Row counts per table
SELECT schemaname, relname AS table, n_live_tup AS estimated_rows
FROM pg_stat_user_tables
ORDER BY estimated_rows DESC;

-- Example aggregate parity check
SELECT COUNT(*) AS films, MIN(release_year) AS min_year, MAX(release_year) AS max_year FROM film;

-- Example workload queries (run EXPLAIN ANALYZE before/after)
EXPLAIN (ANALYZE, BUFFERS)
SELECT f.title, c.name AS category, r.rental_date
FROM film f
JOIN film_category fc ON fc.film_id = f.film_id
JOIN category c ON c.category_id = fc.category_id
JOIN inventory i ON i.film_id = f.film_id
JOIN rental r ON r.inventory_id = i.inventory_id
WHERE c.name = 'Action'
ORDER BY r.rental_date DESC
LIMIT 50;

EXPLAIN (ANALYZE, BUFFERS)
SELECT a.first_name, a.last_name, COUNT(*) AS films
FROM actor a
JOIN film_actor fa ON fa.actor_id = a.actor_id
GROUP BY a.actor_id
ORDER BY films DESC
LIMIT 20;
```

```sql name=optimization.sql
-- Indexes to improve common joins, filters, and sorts

-- Speeds up category filter + join
CREATE INDEX IF NOT EXISTS idx_category_name ON category (name);

-- Speeds up film_category joins
CREATE INDEX IF NOT EXISTS idx_film_category_film_id ON film_category (film_id);
CREATE INDEX IF NOT EXISTS idx_film_category_category_id ON film_category (category_id);

-- Speeds up inventory join by film_id
CREATE INDEX IF NOT EXISTS idx_inventory_film_id ON inventory (film_id);

-- Speeds up rental date ordering
CREATE INDEX IF NOT EXISTS idx_rental_inventory_id_date ON rental (inventory_id, rental_date DESC);

-- After creating indexes, re-run EXPLAIN (ANALYZE, BUFFERS) for target queries
```

What to do step-by-step right now
1. Clone this into a new folder and save the files above.
2. Put the Pagila schema/data SQL files into ./scripts/ so they load on startup.
3. Run docker compose up -d.
4. Baseline: run validation.sql locally and save results.
5. Create pagila.dump and restore to your target database.
6. Run validation.sql on the target. Confirm parity.
7. Apply optimization.sql on the target. Measure improvements.
8. Write down before/after timings and what changed.

If you prefer MySQL or a different path
- MySQL starter: Use the Sakila dataset. Migrate local → managed MySQL via mysqldump/restore, then enable the slow query log and create indexes based on EXPLAIN FORMAT=JSON output.
- Cross-engine starter: Use pgloader to migrate Sakila (MySQL) → Postgres, fix type mappings, validate row counts, then optimize on Postgres.

Want me to turn this into GitHub issues or a PR in your repo so you can track tasks? Share your preferred database (Postgres/MySQL), target environment, and the repository owner/name, and I’ll structure it for you.