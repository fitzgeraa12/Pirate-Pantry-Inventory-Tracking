CREATE TABLE IF NOT EXISTS total_checkouts (
    checkout_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
    id         INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    brand      TEXT    NOT NULL DEFAULT '',
    num_checked_out   INTEGER NOT NULL,
    checkout_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
