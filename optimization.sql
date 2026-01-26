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