# Project File Report

This report summarizes the files currently present in the repository, excluding `venv/` and `liboqs/` as requested.
Each item below explains what the file is for in plain, short terms.

## Root Files

`/.env`  
Stores environment-specific settings like database URLs or local configuration values. It is used at runtime and should usually stay private.

`/.gitignore`  
Tells Git which generated or local-only files should not be committed. It helps keep the repository clean.

`/README.md`  
Intended to describe the project, setup steps, and usage instructions. It is currently empty and acts like a placeholder.

`/requirements.txt`  
Lists the Python dependencies needed to run the API, database layer, and crypto features. It is used when setting up the environment.

## App Entry And Utilities

`/app/main.py`  
Main FastAPI application entry point. It builds the app, registers error handlers, and mounts all API route modules.

`/app/benchmark.py`  
Runs performance measurements for KEM and DSA algorithms. It writes benchmark output so algorithm speed can be compared.

`/app/pqc_performance_metrics.csv`  
Stores recorded benchmark results for post-quantum crypto operations. It is useful for analysis or reporting.

`/app/test_apikey.py`  
Simple script for creating API keys through the repository layer. It looks like a quick manual test or local seeding helper.

`/app/test_crypto_KEM.py`  
Manual test script for KEM functionality. It is used to exercise encapsulation-related crypto flows outside the API.

`/app/test_crypto_DSA.py`  
Manual test script for DSA functionality. It is used to check signing and verification behavior locally.

## Core Configuration

`/app/core/config.py`  
Defines application settings using `BaseSettings`. It centralizes values like API metadata and environment-driven config.

`/app/core/database.py`  
Creates the SQLAlchemy engine, session factory, and declarative base. It is the foundation for all model and repository database access.

`/app/core/dependencies.py`  
Holds shared FastAPI dependency helpers. It is typically used for request validation such as API key or header checks.

`/app/core/exceptions.py`  
Defines custom exception response helpers and handlers. It keeps API error output consistent across endpoints.

## Crypto Layer

`/app/crypto/__init__.py`  
Initializes crypto package behavior, especially around locating the `liboqs` library. It prepares the runtime environment for PQC operations.

`/app/crypto/_oqs_loader.py`  
Contains the low-level logic that finds and loads shared `liboqs` binaries. It is the bridge between Python code and the native crypto library.

`/app/crypto/registry.py`  
Provides algorithm lookup and metadata helper logic. It acts like a central place for available algorithm information.

`/app/crypto/kem.py`  
Implements the KEM manager and wraps key encapsulation operations. It exposes the core encrypt/decrypt-style PQC primitives to the app.

`/app/crypto/dsa.py`  
Implements the DSA manager and wraps signature operations. It exposes signing and verification features using PQC algorithms.

## Data Models

`/app/models/algorithm.py`  
SQLAlchemy model for stored algorithm metadata. It likely tracks names, identifiers, and related descriptive fields.

`/app/models/api_key.py`  
SQLAlchemy model for API key records. It represents stored key ownership, status, and audit-related timestamps.

`/app/models/api_usage.py`  
SQLAlchemy model for API usage tracking. It is meant for counting requests, quota usage, or endpoint activity.

`/app/models/audit_log.py`  
SQLAlchemy model for audit log entries. It is used to record important events for traceability and review.

`/app/models/key.py`  
SQLAlchemy model for generated or stored keys. It likely supports persisting key material metadata in the database.

`/app/models/user.py`  
SQLAlchemy model for user records. It is the base data structure for application users or API consumers.

## Repository Layer

`/app/repositories/algorithm_repo.py`  
Repository for CRUD-style algorithm database access. It keeps query logic separate from route and service code.

`/app/repositories/api_key_repo.py`  
Repository for creating, fetching, revoking, and deleting API keys. It is the main database access layer for API key management.

`/app/repositories/api_usage_repo.py`  
Repository for API usage records. It is used to insert or retrieve usage statistics from the database.

`/app/repositories/audit_log_repo.py`  
Repository for audit log operations. It handles storing and retrieving event history data.

`/app/repositories/key_repo.py`  
Repository for key-related database operations. It keeps key persistence logic organized away from endpoints.

`/app/repositories/user_repo.py`  
Repository for user-related database operations. It manages user reads and writes through SQLAlchemy sessions.

## API Schemas

`/app/schemas/algorithms.py`  
Pydantic response models for algorithm endpoints. It shapes how algorithm data is returned by the API.

`/app/schemas/dsa.py`  
Pydantic request and response models for DSA operations. It validates signing and verification payloads.

`/app/schemas/health.py`  
Pydantic schema for health-check responses. It keeps the status endpoint response structure consistent.

`/app/schemas/kem.py`  
Pydantic request and response models for KEM operations. It validates encapsulation and decapsulation payloads.

## Service Layer

`/app/services/algorithm_service.py`  
Business logic for reading algorithm information. It connects repository data to API-facing response schemas.

`/app/services/dsa_services.py`  
Business logic for DSA requests. It converts validated API input into crypto manager operations and response objects.

`/app/services/health_service.py`  
Business logic for the health endpoint. It returns service status and app metadata in a clean response model.

`/app/services/kem_services.py`  
Business logic for KEM requests. It coordinates request parsing, crypto execution, and response shaping.

## Route Modules

`/app/routes/algorithms.py`  
FastAPI routes for listing algorithms and fetching one by name. It exposes the algorithm service to HTTP clients.

`/app/routes/api_keys.py`  
FastAPI routes for API key actions using mock in-memory data. It currently looks more like a placeholder than a full DB-backed route.

`/app/routes/audit_logs.py`  
FastAPI route module for returning audit logs. It currently appears to expose mocked or simplified data structures.

`/app/routes/dsa.py`  
FastAPI routes for signature and verification operations. It maps HTTP requests to the DSA service layer.

`/app/routes/health.py`  
FastAPI health-check route module. It gives clients a quick way to confirm the service is running.

`/app/routes/kem.py`  
FastAPI routes for KEM encapsulation and decapsulation. It maps HTTP requests to the KEM service layer.

`/app/routes/keygen.py`  
FastAPI route module for generic key generation requests. It appears to provide a simpler or mock-oriented key generation API.

`/app/routes/usage.py`  
FastAPI route module for usage statistics. It currently appears to serve example or placeholder usage data.

## Documentation

`/app/docs/workflow.md`  
Internal project documentation for workflow or process notes. It likely explains how the team expects the app or development flow to work.
