
# NiFi ETL Pipeline Description

## Pipeline Overview

The ETL pipeline extracts data from MySQL TPCH database,

transforms it into a star schema, and loads it as files.

## Processors Used

### 1. GenerateTableFetch

- Connects to MySQL via DBCPConnectionPool

- Generates SELECT queries in batches of 10,000 rows

- Prevents out-of-memory errors for large tables

- Used for: fact_lineitem (6 million rows)

### 2. ExecuteSQL

- Executes SQL queries against MySQL TPCH database

- Performs JOIN operations to pre-join dimension tables

- dim_supplier: JOINs supplier + nation

- dim_customer: JOINs customer + nation

- fact_lineitem: JOINs lineitem + orders

### 3. PutFile

- Saves output flowfiles to local filesystem

- Each table saved to separate directory

- Output format: JSON (dim_supplier) and Avro (others)

## Controller Services

### DBCPConnectionPool

- Manages MySQL database connections

- URL: jdbc:mysql://localhost:3306/tpch

- Handles connection pooling for efficiency

### AvroReader

- Reads Avro format flowfiles

- Used by ConvertRecord processor

### JsonRecordSetWriter

- Writes output in JSON format

- Used by ConvertRecord processor

## Data Flow

```

MySQL TPCH DB

     │

     ▼

GenerateTableFetch ──► ExecuteSQL ──► PutFile ──► /nifi-output/

     │

     ├── dim_supplier  (supplier JOIN nation)

     ├── dim_customer  (customer JOIN nation)

     └── fact_lineitem (lineitem JOIN orders)

```

