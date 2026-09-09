# DuckLake + Quack Lab

A local environment for exploring **DuckLake** with **DuckDB, Quack, PostgreSQL, MinIO, and marimo**.

## Architecture

- **DuckDB**: query / compute engine
- **DuckLake**: lakehouse metadata and transaction layer
- **PostgreSQL**: DuckLake catalog and metadata
- **MinIO**: S3-compatible storage for Parquet files
- **Quack**: remote access to DuckDB

```text
Marimo Notebook
      |
Local DuckDB Client
      |
    Quack
      |
Remote DuckDB
      |
   DuckLake
   /      \
Postgres  MinIO
Catalog   Parquet
```

## What the Notebook Covers

The `quack_exploration.py` notebook explores:

- DuckLake architecture
- Remote DuckDB access through Quack
- CRUD operations
- Data inlining and Parquet-backed writes
- Snapshots
- Time travel
- Data Change Feed
- Schema evolution
- Partitioning
- Partition and file pruning
- Maintenance and compaction concepts

## Prerequisites

Install:

- Docker
- Docker Compose
- Python 3.11+
- `uv`

## Setup

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd ducklake-local-lab
```

Install Python dependencies:

```bash
uv sync
```

Start the local services:

```bash
docker compose up -d --build
```

Check that the services are running:

```bash
docker compose ps
```

## Docker Compose Services

### PostgreSQL

Stores the DuckLake catalog and metadata.

Local port:

```text
5432
```

### MinIO

Provides S3-compatible object storage for DuckLake Parquet files.

- S3 API: `http://localhost:9000`
- Web console: `http://localhost:9001`

The `minio-init` service creates the `ducklake` bucket automatically.

DuckLake data is stored under:

```text
s3://ducklake/data/
```

### Quack

Runs the remote DuckDB service used by the notebook.

Local port:

```text
9494
```

## Run the Notebook

From the repository root:

```bash
cd notebooks
uv run marimo edit quack_exploration.py --host 'data-hveeraboina'
```

If you are running this on a different machine, replace `data-hveeraboina` with the hostname or interface you want marimo to bind to.

## Inspect Parquet Files

Open the MinIO console:

```text
http://localhost:9001
```

Then browse:

```text
ducklake/data/
```

This lets you inspect the physical Parquet files and partition layout created by DuckLake.

## Reset the Environment

Stop the containers while keeping existing data:

```bash
docker compose down
```

Delete the PostgreSQL and MinIO volumes and start from scratch:

```bash
docker compose down -v
docker compose up -d --build
```

## Notes

This repository is intended for local experimentation and learning rather than production deployment.



