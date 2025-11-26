CREATE TABLE IF NOT EXISTS c4_nodes (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    c4_type VARCHAR(50) NOT NULL,
    description TEXT,
    meta_data JSONB
);

CREATE TABLE IF NOT EXISTS c4_edges (
    source_id VARCHAR(64) REFERENCES c4_nodes(id),
    target_id VARCHAR(64) REFERENCES c4_nodes(id),
    label VARCHAR(255),
    PRIMARY KEY (source_id, target_id)
);