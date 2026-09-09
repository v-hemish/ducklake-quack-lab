import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb

    return duckdb, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The central idea around ducklake is to seperate compute, metadata and actual data. (duckdb + postgres + minio)
    """)
    return


@app.cell
def _(duckdb):
    # Connect to duckdb client
    q = duckdb.connect()
    return (q,)


@app.cell
def _(q):
    q.sql("""
    INSTALL quack;
    LOAD quack;
    """)
    return


@app.cell
def _(q):
    # Creating a quack secret (9494 is the default port for quack)
    q.sql("""
    CREATE OR REPLACE SECRET quack_secret (
        TYPE quack, 
        TOKEN 'ducklake-local-secret', 
        SCOPE 'quack:localhost:9494'
    );
    """)
    return


@app.cell
def _(q):
    # naming the attached source to this session and naming it remote
    # disabling ssl for local testing, flip it in production if needed. 
    q.sql("""
    ATTACH 'quack:localhost:9494'
    AS remote (
        TYPE quack,
        DISABLE_SSL true
    );
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Commands to setup ducklake, from the remote duckdb (quack is used to connect to the db server, in this case, we are using it to create our ducklake instance as well)
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        INSTALL ducklake;
        LOAD ducklake;

        INSTALL postgres;
        LOAD postgres;

        INSTALL httpfs;
        LOAD httpfs;

        SELECT ''Extensions loaded successfully'' AS status;
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's configure our S3/MinIO creds as well
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        CREATE OR REPLACE SECRET minio_secret (
            TYPE s3,
            KEY_ID ''minioadmin'',
            SECRET ''minioadmin'',
            REGION ''us-east-1'',
            ENDPOINT ''minio:9000'',
            USE_SSL false,
            URL_STYLE ''path''
        );

        SELECT ''MinIO configured successfully'' AS status;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Configuring connection to the catalog which is postgres here

    q.sql("""
    FROM remote.query(
        '
        CREATE OR REPLACE SECRET pg_secret (
            TYPE postgres,
            HOST ''postgres'',
            PORT 5432,
            DATABASE ''ducklake_catalog'',
            USER ''ducklake'',
            PASSWORD ''ducklake''
        );

        SELECT ''PostgreSQL configured successfully'' AS status;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Configuring ducklake to use minio for data and postgres for catalog

    q.sql("""
    FROM remote.query(
        '
        CREATE OR REPLACE SECRET ducklake_secret (
            TYPE ducklake,
            METADATA_PATH '''',
            DATA_PATH ''s3://ducklake/data/'',
            METADATA_PARAMETERS MAP {
                ''TYPE'': ''postgres'',
                ''SECRET'': ''pg_secret''
            }
        );

        SELECT ''DuckLake configuration created'' AS status;
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(q):
    # Run if needed to attach ducklake 
    q.sql("""
    FROM remote.query(
        '
        ATTACH ''ducklake:ducklake_secret'' AS lake;

        SELECT ''DuckLake attached successfully'' AS status;
        '
    )
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        'SHOW DATABASES'
    )
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;
        SELECT current_database() AS current_database;
        '
    )
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;
        SHOW TABLES;
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is all it takes to configure the existing setup. Now, lets do some CRUD operations on this architecture.
    """)
    return


@app.cell
def _(q):
    # Insert some dummy starter data, after creating an events table
    # Create a table named events
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        CREATE TABLE events (
            event_id INTEGER,
            user_id VARCHAR,
            event_type VARCHAR,
            score DOUBLE,
            event_time TIMESTAMP
        );

        SELECT ''events table created'' AS status;
        '
    )
    """)


    return


@app.cell
def _(q):
    # Insert command
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        -- Small human-readable dataset
        INSERT INTO events VALUES
            (1, ''user_1'', ''search'', 0.81, CURRENT_TIMESTAMP),
            (2, ''user_2'', ''social'', 0.62, CURRENT_TIMESTAMP),
            (3, ''user_3'', ''direct'', 0.91, CURRENT_TIMESTAMP),
            (4, ''user_1'', ''search'', 0.44, CURRENT_TIMESTAMP),
            (5, ''user_4'', ''social'', 0.73, CURRENT_TIMESTAMP);

        -- Larger dataset to force DuckLake to write real Parquet data
        INSERT INTO events
        SELECT
            1000 + i AS event_id,
            ''user_'' || CAST(i % 1000 AS VARCHAR) AS user_id,

            CASE
                WHEN i % 4 = 0 THEN ''search''
                WHEN i % 4 = 1 THEN ''social''
                WHEN i % 4 = 2 THEN ''direct''
                ELSE ''other''
            END AS event_type,

            random() AS score,

            CURRENT_TIMESTAMP
                - (i % 10000) * INTERVAL ''1 second''
                AS event_time

        FROM range(100000) t(i);

        SELECT COUNT(*) AS total_rows
        FROM events;
        '
    )
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;
        SHOW TABLES;
        '
    )
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM events
        ORDER BY event_id;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Update table 'events'
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        UPDATE events
        SET
            event_type = ''search'',
            score = 0.95
        WHERE event_id = 2;

        SELECT ''event 2 updated'' AS status;
        '
    )
    """)
    return


@app.cell
def _(q):

    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM events
        WHERE event_id = 2;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Delete a record 

    q.sql("""
    FROM remote.query(
        '
        USE lake;

        DELETE FROM events
        WHERE event_id = 3;

        SELECT ''event 3 deleted'' AS status;
        '
    )
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM events
        ORDER BY event_id;
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, lets check some snapshots around the state of the lake
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM lake.snapshots()
        ORDER BY snapshot_id;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Snapshot changes

    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT
            snapshot_id,
            snapshot_time,
            schema_version,
            changes
        FROM lake.snapshots()
        ORDER BY snapshot_id;
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Time travel
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM events
        ORDER BY event_id;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Table at snapshot version 7
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM events
        AT (VERSION => 5)
        ORDER BY event_id;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Table at snapshot version 8
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM events
        AT (VERSION => 8)
        ORDER BY event_id;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Row counts across different snapshots
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT
            (SELECT COUNT(*) FROM events AT (VERSION => 5)) AS snapshot_5_rows,
            (SELECT COUNT(*) FROM events AT (VERSION => 7)) AS snapshot_7_rows,
            (SELECT COUNT(*) FROM events AT (VERSION => 8)) AS snapshot_8_rows,
            (SELECT COUNT(*) FROM events) AS current_rows;
        '
    )
    """)
    return


@app.cell
def _(q):
    # Snapshot timeline

    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT
            snapshot_id,
            snapshot_time,
            schema_version,
            changes
        FROM lake.snapshots()
        ORDER BY snapshot_id;
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note: Data Inlining: For tiny writes, instead of creating a new parquet, ducklake saves it in postgres to flush later, which avoids the problem of creating many small files.
    """)
    return


@app.cell
def _(q):
    # Physical parquet location
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        FROM ducklake_list_files(''lake'', ''events'');
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, let's check how schema evolution works here
    """)
    return


app._unparsable_cell(
    """
    # Current Schema
    .sql(\"\"\"
    FROM remote.query(
        '
        USE lake;

        DESCRIBE events;
        '
    )
    \"\"\")
    """,
    name="_"
)


@app.cell
def _(q):
    # Adding a new column, which shoukd create a new snapshot and increment into a new schema version
    q.execute("""
    SELECT *
    FROM remote.query(
        '
        USE lake;

        ALTER TABLE events
        ADD COLUMN source_system VARCHAR DEFAULT ''web'';

        SELECT ''source_system column added'' AS status;
        '
    )
    """).fetchall()
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        DESCRIBE events;
        '
    )
    """)
    return


@app.cell
def _(q):
    q.execute("""
    SELECT *
    FROM remote.query(
        '
        USE lake;

        INSERT INTO events (
            event_id,
            user_id,
            event_type,
            score,
            event_time,
            source_system
        )
        SELECT
            600000 + i AS event_id,
            ''new_user_'' || CAST(i % 5000 AS VARCHAR) AS user_id,

            CASE
                WHEN i % 4 = 0 THEN ''search''
                WHEN i % 4 = 1 THEN ''social''
                WHEN i % 4 = 2 THEN ''direct''
                ELSE ''other''
            END AS event_type,

            random() AS score,

            CURRENT_TIMESTAMP
                - (i % 20000) * INTERVAL ''1 second''
                AS event_time,

            CASE
                WHEN i % 3 = 0 THEN ''mobile''
                WHEN i % 3 = 1 THEN ''web''
                ELSE ''api''
            END AS source_system

        FROM range(100000) t(i);

        SELECT COUNT(*) AS total_rows
        FROM events;
        '
    )
    """).fetchall()
    return


@app.cell
def _(q):
    # Data from new schema
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT
            event_id,
            user_id,
            event_type,
            source_system
        FROM events
        WHERE event_id >= 600000
        ORDER BY event_id
        LIMIT 20;
        '
    )
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM events
        ORDER BY event_id
        LIMIT 50;
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Partitioning + Pruning
    """)
    return


@app.cell
def _(q):
    # Enabling partitioning for this table on year and month
    q.execute("""
    SELECT *
    FROM remote.query(
        '
        USE lake;

        ALTER TABLE events
        SET PARTITIONED BY (
            year(event_time),
            month(event_time)
        );

        SELECT ''Partitioning enabled'' AS status;
        '
    )
    """).fetchall()
    return


@app.cell
def _(q):
    # Doing a large insert with timestamps across several months
    q.execute("""
    SELECT *
    FROM remote.query(
        '
        USE lake;

        INSERT INTO events (
            event_id,
            user_id,
            event_type,
            score,
            event_time,
            source_system
        )
        SELECT
            800000 + i,
            ''partition_user_'' || CAST(i % 5000 AS VARCHAR),

            CASE
                WHEN i % 4 = 0 THEN ''search''
                WHEN i % 4 = 1 THEN ''social''
                WHEN i % 4 = 2 THEN ''direct''
                ELSE ''other''
            END,

            random(),

            TIMESTAMP ''2026-01-01''
                + (i % 240) * INTERVAL ''1 day'',

            CASE
                WHEN i % 3 = 0 THEN ''mobile''
                WHEN i % 3 = 1 THEN ''web''
                ELSE ''api''
            END

        FROM range(200000) t(i);

        SELECT ''200k partitioned rows inserted'' AS status;
        '
    )
    """).fetchall()
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        FROM ducklake_list_files(''lake'', ''events'');
        '
    )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note: To inspect DuckLake’s physical Parquet files and partitions, open the MinIO console at http://localhost:9001, log in with the credentials from docker-compose.yml, and browse the ducklake/data/ path.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For data compaction, flush inlined rows, expire snapshots, merge small files, rewriet heavily deleted files, clearn old files and remove orphaned files, we use the CHECKPOINT command.
    """)
    return


@app.cell
def _(q):
    q.execute("""
    SELECT *
    FROM remote.query(
        '
        USE lake;

        CHECKPOINT;

        SELECT ''Checkpoint completed'' AS status;
        '
    )
    """).fetchall()
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        FROM ducklake_list_files(''lake'', ''events'');
        '
    )
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Data Change Feed: Using table_changes(), we can inspect row level changes between different snapshots
    """)
    return


@app.cell
def _(q):
    q.sql("""
    FROM remote.query(
        '
        USE lake;

        SELECT *
        FROM lake.table_changes(
            ''events'',
            5,
            8
        )
        ORDER BY snapshot_id, rowid;
        '
    )
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
