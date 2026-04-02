# OLAP
TPCH OLAP Lab - CSE-4E3 Alexandria University
# TPCH OLAP Lab — CSE-4E3
## Designing Data Intensive Applications
Alexandria University — Faculty of Engineering

# Overview
ETL pipeline converting the TPCH relational (OLTP) schema
into a Star Schema (OLAP), using:
- MySQL as the source OLTP database
- Apache NiFi for ETL (Extract, Transform, Load)
- Apache Parquet as the columnar storage format
- Apache Spark as the OLAP query engine

---

# Project Structure

tpch-olap-lab

 1_data_generation     # TPCH data generation steps + screenshots

 2_mysql_setup         # DDL, data loading scripts, screenshots

 3_star_schema         # Star schema design, DDL, diagram

 4_nifi_etl            # NiFi flow template + processor descriptions

 5_spark_queries       # Spark query scripts + results

 6_benchmark           # Timing table (16 runs)

 7-docs                   


---

# Tech Stack
| Tool | Version | Purpose |
|------|---------|---------|
| MySQL | 8.x | Source OLTP database |
| Apache NiFi | 2.2.0 | ETL pipeline |
| Apache Spark | 3.x | OLAP query engine |
| Java | 21 | Required for NiFi |
| Parquet | — | Columnar storage format |

---
