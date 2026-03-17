# TPCH OLAP Lab Report
## Alexandria University - CSE-4E3
## Designing Data Intensive Applications

---

## 1. TPC-H Data Generation Steps

### Step 1 - Clone and compile dbgen
```bash
git clone https://github.com/electrum/tpch-dbgen.git
cd tpch-dbgen
make
```

### Step 2 - Generate data with scale factor 1
```bash
./dbgen -s 1
```

### Step 3 - Verify generated files
```bash
ls *.tbl
# Output: customer.tbl lineitem.tbl nation.tbl orders.tbl
#         part.tbl partsupp.tbl region.tbl supplier.tbl
```

---

## 2. Data Insertion into MySQL

### Step 1 - Create database and tables
```sql
CREATE DATABASE tpch;
USE tpch;
```

### Step 2 - Enable local infile
```sql
SET GLOBAL local_infile=1;
```

### Step 3 - Load all tables
```sql
LOAD DATA LOCAL INFILE '~/tpch-dbgen/nation.tbl'
INTO TABLE nation FIELDS TERMINATED BY '|';
-- repeated for all 8 tables
```

### Verified Row Counts
| Table | Rows |
|-------|------|
| nation | 25 |
| supplier | 10,000 |
| customer | 150,000 |
| partsupp | 800,000 |
| orders | 1,500,000 |
| lineitem | 6,000,000 |

---

## 3. OLTP Schema DDL
See file: schemas/oltp_schema_ddl.sql

---

## 4. Star Schema DDL
See file: schemas/star_schema_ddl.sql

### Star Schema Design
```
          dim_date
             │
dim_customer─┼─► fact_lineitem ◄─── dim_supplier
             │   (center)
```

### Design Decisions
- dim_supplier: pre-joins supplier + nation
- dim_customer: pre-joins customer + nation
- fact_lineitem: contains all measurable data
- Original 6-table join reduced to 3-table join

---

## 5. NiFi ETL Pipeline

### Pipeline Flow
```
MySQL TPCH DB
      │
      ▼
GenerateTableFetch → ExecuteSQL → PutFile → /nifi-output/
```

### Processor Descriptions

#### GenerateTableFetch
- Generates batched SELECT queries (10,000 rows per batch)
- Prevents OutOfMemoryError for large tables
- Required for fact_lineitem (6 million rows)

#### ExecuteSQL
- Executes JOIN queries against MySQL
- Transforms OLTP to star schema by pre-joining tables
- dim_supplier query: JOIN supplier + nation
- dim_customer query: JOIN customer + nation
- fact_lineitem query: JOIN lineitem + orders

#### PutFile
- Saves output to local filesystem
- Each table saved to separate directory

### Controller Services
- DBCPConnectionPool: manages MySQL connections
- AvroReader: reads Avro format data
- JsonRecordSetWriter: writes JSON format data

---

## 6. Known Issues and Simplifications

### Issue 1 - Duplicate Data in Parquet Files
**What happened:** NiFi pipeline was run multiple times
during debugging. This caused duplicate records in output.

**Impact:**
| Table | Expected | Actual in Parquet |
|-------|----------|-------------------|
| dim_supplier | 10,000 | 6,080,000 |
| dim_customer | 150,000 | 96,300,000 |
| fact_lineitem | ~5,700,000 | 5,690,000 |

**Root cause:** NiFi PutFile does not check for existing
data. Each pipeline run appended new files to output folder.

**Fix applied:** Used dropDuplicates() in Spark:
```python
dim_supplier = dim_supplier.dropDuplicates(["supplier_key"])
dim_customer = dim_customer.dropDuplicates(["customer_key"])
```
After deduplication, correct counts were restored:
- dim_supplier: 10,000 rows
- dim_customer: 150,000 rows

**Proper production fix:** Clear output directories before
each pipeline run, or configure NiFi PutFile with
"Conflict Resolution = replace".

---

### Issue 2 - Mixed File Formats
**What happened:** dim_supplier saved as JSON, others as Avro.
This happened because pipeline was rebuilt mid-way and
ConvertRecord processor configuration changed.

**Fix applied:** Python script handles both formats
automatically - tries Avro first, falls back to JSON.

---

### Issue 3 - OutOfMemoryError in Spark
**What happened:** Due to Issue 1, dim_customer had
96 million duplicate rows causing Java heap OOM error.

**Fix applied:** dropDuplicates() reduced dim_customer
back to correct 150,000 rows. Also increased Spark
driver memory to 8GB.

---

### Issue 4 - MySQL Authentication
**What happened:** NiFi could not connect as root user
because mysql_native_password plugin was removed in MySQL 9.x.

**Fix applied:** Created dedicated NiFi user:
```sql
CREATE USER 'nifi'@'localhost' IDENTIFIED BY 'nifi123';
GRANT ALL PRIVILEGES ON tpch.* TO 'nifi'@'localhost';
```

---

### Issue 5 - PutParquet Not Available
**What happened:** NiFi 2.2.0 does not include PutParquet
processor in standard installation.

**Fix applied:** Used PutFile to save in native format,
then converted to Parquet using Python with pyarrow.

---

## 7. Performance Comparison

### MySQL Results (OLTP - 6 table joins)
| Run | Time (seconds) |
|-----|---------------|
| 1   | 108.247 |
| 2   | 136.199 |
| 3   | 137.161 |
| 4   | 132.834 |
| 5   | 142.135 |
| 6   | 149.637 |
| 7   | 126.655 |
| 8   | 128.429 |
| **Average** | **132.662** |

### Spark Results (Star Schema - Parquet)
| Run | Time (seconds) |
|-----|---------------|
| 1   | 6.871 |
| 2   | 6.324 |
| 3   | 6.218 |
| 4   | 6.013 |
| 5   | 6.614 |
| 6   | 7.111 |
| 7   | 7.422 |
| 8   | 7.819 |
| **Average** | **6.799** |

### Performance Summary
| System | Average Time | Speedup |
|--------|-------------|---------|
| MySQL (OLTP) | 132.662 seconds | 1x baseline |
| Spark (Star Schema) | 6.799 seconds | **19.5x faster** |

### Note on Spark Results
Results obtained after deduplication using dropDuplicates().
Query ran on correct ~150,000 customer rows and ~10,000
supplier rows after fix was applied.

### Why Spark is 19.5x Faster
1. **Columnar Parquet format:** reads only needed columns
   from disk instead of entire rows
2. **Fewer joins:** star schema has 3 joins vs 6 in OLTP
3. **Parallel processing:** Spark uses all CPU cores
   simultaneously while MySQL runs single-threaded
4. **Pre-joined dimensions:** ETL (NiFi) did the expensive
   join work once during loading, not at query time

---

## 8. Conclusion
The ETL pipeline successfully demonstrated conversion from
a normalized OLTP schema to an OLAP star schema.

Despite technical challenges including NiFi version
compatibility issues, MySQL 9.x authentication changes,
memory constraints, and data duplication from multiple
pipeline runs, the pipeline was completed successfully.

The performance results clearly demonstrate the value of
OLAP optimization:
- Spark with star schema: 6.799 seconds average
- MySQL with OLTP schema: 132.662 seconds average
- Performance improvement: 19.5x faster

This confirms that for analytical workloads involving
large table scans and aggregations, OLAP-optimized
star schemas with columnar storage significantly
outperform traditional normalized OLTP databases.
