-- Validation SQL Script
-- Row counts per table
SELECT schemaname, relname AS table_name, n_live_tup AS estimated_rows
FROM pg_stat_user_tables
WHERE schemaname = 'public'
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
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY films DESC
LIMIT 20;