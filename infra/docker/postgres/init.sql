-- Script de inicialização do banco PostgreSQL para Licitrix

-- Cria o banco principal se não existir
SELECT 'CREATE DATABASE licitrix' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'licitrix')\gexec

-- Cria o banco para Unleash (feature flags) se não existir
SELECT 'CREATE DATABASE unleash' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'unleash')\gexec

-- Conecta ao banco principal
\c licitrix;

-- Cria extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Cria usuário para o aplicativo se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'licitrix') THEN
        CREATE USER licitrix WITH PASSWORD 'licitrix';
    END IF;
END
$$;

-- Concede permissões
GRANT ALL PRIVILEGES ON DATABASE licitrix TO licitrix;
GRANT ALL PRIVILEGES ON SCHEMA public TO licitrix;

-- Conecta ao banco Unleash
\c unleash;

-- Cria usuário para Unleash se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'unleash') THEN
        CREATE USER unleash WITH PASSWORD 'unleash';
    END IF;
END
$$;

-- Concede permissões
GRANT ALL PRIVILEGES ON DATABASE unleash TO unleash;
GRANT ALL PRIVILEGES ON SCHEMA public TO unleash;
