CREATE TABLE IF NOT EXISTS products (
    id         TEXT PRIMARY KEY,
    name       TEXT    NOT NULL COLLATE NOCASE,
    brand      TEXT    DEFAULT NULL REFERENCES brands(name) ON DELETE SET NULL,
    quantity   INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    image_link TEXT    DEFAULT NULL REFERENCES image_links(path) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tags (
    label TEXT PRIMARY KEY COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS brands (
    name TEXT PRIMARY KEY COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS image_links (
    path TEXT PRIMARY KEY COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS product_tags (
    product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    tag_label  TEXT    NOT NULL REFERENCES tags(label)  ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_label)
);

CREATE TABLE IF NOT EXISTS users (
    id           TEXT PRIMARY KEY,
    email        TEXT UNIQUE NOT NULL,
    access_level TEXT NOT NULL CHECK(access_level IN ('trusted', 'admin'))
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id            TEXT PRIMARY KEY,
    user_id       TEXT REFERENCES users(id) ON DELETE CASCADE,
    google_sub    TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at    INTEGER NOT NULL,
    created_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_codes (
    code       TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    expires_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS total_checkouts (
    checkout_id TEXT PRIMARY KEY, --unique per checkout
    id         INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    brand      TEXT    NOT NULL DEFAULT '',
    num_checked_out   INTEGER NOT NULL,
    checkout_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
<<<<<<< HEAD


=======
>>>>>>> 6a412d85544acdd9b01645e2a9567e7b86000683
