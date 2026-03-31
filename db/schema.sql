-- Stores Kroger location info
CREATE TABLE IF NOT EXISTS stores (
    location_id     VARCHAR(20) PRIMARY KEY,
    name            VARCHAR(255),
    address         VARCHAR(255),
    city            VARCHAR(100),
    state           VARCHAR(50),
    zip_code        VARCHAR(10)
);

-- Stores every product price snapshot
CREATE TABLE IF NOT EXISTS prices (
    id              SERIAL PRIMARY KEY,
    product_id      VARCHAR(50),
    search_term     VARCHAR(100),
    description     VARCHAR(255),
    brand           VARCHAR(100),
    size            VARCHAR(50),
    price           NUMERIC(10, 2),
    location_id     VARCHAR(20) REFERENCES stores(location_id),
    fetched_at      TIMESTAMP DEFAULT NOW()
);

-- Index for fast time-series queries per product
CREATE INDEX IF NOT EXISTS idx_prices_product_id  ON prices(product_id);
CREATE INDEX IF NOT EXISTS idx_prices_fetched_at  ON prices(fetched_at);
CREATE INDEX IF NOT EXISTS idx_prices_search_term ON prices(search_term);