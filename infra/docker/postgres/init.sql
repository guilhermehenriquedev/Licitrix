-- Script de inicialização do banco PostgreSQL para Licitrix

-- Cria o banco principal
CREATE DATABASE licitrix;

-- Cria o banco para Unleash (feature flags)
CREATE DATABASE unleash;

-- Conecta ao banco principal
\c licitrix;

-- Cria extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Cria usuário para o aplicativo
CREATE USER licitrix WITH PASSWORD 'licitrix';

-- Concede permissões
GRANT ALL PRIVILEGES ON DATABASE licitrix TO licitrix;
GRANT ALL PRIVILEGES ON SCHEMA public TO licitrix;

-- Conecta ao banco Unleash
\c unleash;

-- Cria usuário para Unleash
CREATE USER unleash WITH PASSWORD 'unleash';

-- Concede permissões
GRANT ALL PRIVILEGES ON DATABASE unleash TO unleash;
GRANT ALL PRIVILEGES ON SCHEMA public TO unleash;
