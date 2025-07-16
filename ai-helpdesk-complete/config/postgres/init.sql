-- Initialize AI Service database
\c ai_service;

-- Create chat interactions table
CREATE TABLE IF NOT EXISTS chat_interactions (
    id SERIAL PRIMARY KEY,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    department VARCHAR(50),
    priority VARCHAR(20),
    confidence FLOAT,
    created_ticket BOOLEAN DEFAULT FALSE,
    ticket_id VARCHAR(50),
    knowledge_articles JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create knowledge sync table
CREATE TABLE IF NOT EXISTS knowledge_sync (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE,
    UNIQUE(source, source_id)
);

-- Create indexes
CREATE INDEX idx_chat_interactions_created_at ON chat_interactions(created_at);
CREATE INDEX idx_chat_interactions_department ON chat_interactions(department);
CREATE INDEX idx_knowledge_sync_source ON knowledge_sync(source);
CREATE INDEX idx_knowledge_sync_updated ON knowledge_sync(last_updated);