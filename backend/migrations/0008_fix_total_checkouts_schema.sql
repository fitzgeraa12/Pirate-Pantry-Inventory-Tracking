-- Fix total_checkouts table to allow multiple products per checkout
-- Create a new table with the correct schema
CREATE TABLE IF NOT EXISTS total_checkouts_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkout_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    brand TEXT NOT NULL DEFAULT '',
    num_checked_out INTEGER NOT NULL,
    checkout_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(checkout_id, product_id)
);

-- Copy existing data if any
INSERT INTO total_checkouts_new (checkout_id, product_id, name, brand, num_checked_out, checkout_time)
SELECT checkout_id, id, name, brand, num_checked_out, checkout_time FROM total_checkouts;

-- Drop old table and rename new one
DROP TABLE total_checkouts;
ALTER TABLE total_checkouts_new RENAME TO total_checkouts;