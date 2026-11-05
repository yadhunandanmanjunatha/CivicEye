-- Runs once when the database volume is first created.
CREATE DATABASE civicflow_test OWNER civic;
\c civicflow
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
\c civicflow_test
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
