-- SQL script to create database and check connection
-- Run this in DBeaver or psql

-- 1. Create database (if not exists)
CREATE DATABASE mauvanban_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 2. Connect to the database
\c mauvanban_db

-- 3. Check connection
SELECT current_database();

-- 4. Check PostgreSQL version
SELECT version();

-- 5. List all tables (will be empty initially)
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
