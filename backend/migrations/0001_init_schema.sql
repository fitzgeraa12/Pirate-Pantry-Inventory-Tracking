CREATE TABLE IF NOT EXISTS products (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    brand      TEXT    NOT NULL DEFAULT '' REFERENCES brands(name) ON DELETE SET DEFAULT,
    quantity   INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    image_link TEXT    NOT NULL DEFAULT '' REFERENCES image_links(path) ON DELETE SET DEFAULT
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
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    tag_label  TEXT    NOT NULL REFERENCES tags(label)  ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_label)
);

CREATE TABLE IF NOT EXISTS users (
    email        TEXT PRIMARY KEY,
    access_level TEXT NOT NULL CHECK(access_level IN ('visitor', 'trusted', 'admin'))
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    access_token  TEXT    PRIMARY KEY,
    refresh_token TEXT    NOT NULL,
    email         TEXT, -- NULL for visitors
    expires_at    INTEGER NOT NULL -- Unix timestamp
);
