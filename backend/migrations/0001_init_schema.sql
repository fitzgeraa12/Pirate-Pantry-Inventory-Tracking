-- Migration number: 0001 	 2026-03-09T23:39:38.348Z
CREATE TABLE IF NOT EXISTS products (
    id         INTEGER UNIQUE PRIMARY KEY NOT NULL,
    name       TEXT    NOT NULL,
    brand      TEXT    NOT NULL DEFAULT '',
    quantity   INTEGER NOT NULL DEFAULT 0,
    image_link TEXT
);

CREATE TABLE IF NOT EXISTS tags (
    label TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS product_tags (
    product_id INTEGER NOT NULL REFERENCES products(id)    ON DELETE CASCADE,
    tag_label  TEXT    NOT NULL REFERENCES tags(label)     ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_label)
);

CREATE TABLE IF NOT EXISTS perms (
    email TEXT PRIMARY KEY,
    type  TEXT NOT NULL CHECK(type IN ('admin', 'trusted'))
);

CREATE TABLE IF NOT EXISTS auth_cache (
    token      TEXT    PRIMARY KEY,  -- Google ID token (the key for lookup)
    email      TEXT    NOT NULL,     -- Verified email extracted from token
    expires_at INTEGER NOT NULL      -- Unix timestamp (from token's exp claim)
);

CREATE TABLE IF NOT EXISTS checkouts (
    id         INTEGER UNIQUE PRIMARY KEY NOT NULL,
    name       TEXT    NOT NULL,
    brand      TEXT    NOT NULL DEFAULT '',
    quantity   INTEGER NOT NULL,
    checked_out TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
