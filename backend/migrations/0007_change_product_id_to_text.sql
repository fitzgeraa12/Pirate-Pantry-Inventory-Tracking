-- Migration to change product id from INTEGER to TEXT to preserve leading zeros

-- Drop old tables if they exist (in case of partial run)
DROP TABLE IF EXISTS products_old;
DROP TABLE IF EXISTS product_tags_old;
DROP TABLE IF EXISTS total_checkouts_old;

-- Rename tables to old
ALTER TABLE products RENAME TO products_old;
ALTER TABLE product_tags RENAME TO product_tags_old;
ALTER TABLE total_checkouts RENAME TO total_checkouts_old;

-- Create new products table with TEXT id
CREATE TABLE products (
    id         TEXT PRIMARY KEY,
    name       TEXT    NOT NULL COLLATE NOCASE,
    brand      TEXT    DEFAULT NULL REFERENCES brands(name) ON DELETE SET NULL,
    quantity   INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    image_link TEXT    DEFAULT NULL REFERENCES image_links(path) ON DELETE SET NULL
);

-- Create new product_tags table with TEXT product_id
CREATE TABLE product_tags (
    product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    tag_label  TEXT NOT NULL REFERENCES tags(label) ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_label)
);

-- Create new total_checkouts table with TEXT id
CREATE TABLE total_checkouts (
    checkout_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
    id         TEXT NOT NULL,
    name       TEXT NOT NULL,
    brand      TEXT,
    num_checked_out INTEGER NOT NULL,
    checkout_time INTEGER NOT NULL
);

-- Copy data, converting ids to TEXT
INSERT INTO products (id, name, brand, quantity, image_link)
SELECT CAST(id AS TEXT), name, brand, quantity, image_link FROM products_old;

INSERT INTO product_tags (product_id, tag_label)
SELECT CAST(pt.product_id AS TEXT), pt.tag_label FROM product_tags_old pt;

INSERT INTO total_checkouts (checkout_id, id, name, brand, num_checked_out, checkout_time)
SELECT checkout_id, CAST(id AS TEXT), name, brand, num_checked_out, checkout_time FROM total_checkouts_old;

-- Drop old tables
DROP TABLE products_old;
DROP TABLE product_tags_old;
DROP TABLE total_checkouts_old;