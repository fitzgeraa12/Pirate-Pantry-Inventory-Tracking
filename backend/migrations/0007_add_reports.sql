CREATE TABLE IF NOT EXISTS reports (
    id          TEXT PRIMARY KEY,
    user_id     TEXT REFERENCES users(id) ON DELETE CASCADE,
    user_email  TEXT NOT NULL,
    message     TEXT NOT NULL,
    created_at  INTEGER NOT NULL,
    resolved    INTEGER NOT NULL DEFAULT 0 -- 0 = unresolved, 1 = resolved
);