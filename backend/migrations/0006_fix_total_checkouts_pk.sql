-- checkout_id was incorrectly PRIMARY KEY, preventing multiple items per checkout.
-- Recreate with a proper auto-increment row id; checkout_id becomes a plain grouping column.
CREATE TABLE total_checkouts_new (
    row_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    checkout_id     INTEGER NOT NULL,
    id              INTEGER NOT NULL,
    name            TEXT    NOT NULL,
    brand           TEXT    NOT NULL DEFAULT '',
    num_checked_out INTEGER NOT NULL,
    checkout_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO total_checkouts_new (checkout_id, id, name, brand, num_checked_out, checkout_time)
SELECT checkout_id, id, name, brand, num_checked_out, checkout_time FROM total_checkouts;

DROP TABLE total_checkouts;
ALTER TABLE total_checkouts_new RENAME TO total_checkouts;
