#!/bin/bash
set -e

# Create multiple databases for different services
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE zammad;
    CREATE DATABASE bookstack;  
    CREATE DATABASE ai_service;
    
    GRANT ALL PRIVILEGES ON DATABASE zammad TO postgres;
    GRANT ALL PRIVILEGES ON DATABASE bookstack TO postgres;
    GRANT ALL PRIVILEGES ON DATABASE ai_service TO postgres;
EOSQL