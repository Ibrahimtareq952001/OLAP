<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=20,24,30&height=180&section=header&text=TPC-H%20Data%20Warehouse&fontSize=38&fontColor=fff&animation=twinkling&fontAlignY=38&desc=OLTP%20%E2%86%92%20OLAP%20Pipeline%20%E2%80%94%2019.5%C3%97%20Query%20Speedup%20over%20MySQL%20Baseline&descAlignY=58&descSize=15&descColor=cbd5e1"/>

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=flat-square&logo=apache-spark&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Apache NiFi](https://img.shields.io/badge/Apache_NiFi-017CEE?style=flat-square&logo=apache&logoColor=white)
![Parquet](https://img.shields.io/badge/Apache_Parquet-50ABF1?style=flat-square&logo=apache&logoColor=white)

</div>

---

## Overview

An end-to-end **ELT data pipeline** that migrates the **TPC-H benchmark** (22 tables, 1 GB+) from a normalized MySQL OLTP schema into an optimized **star-schema OLAP warehouse**, using Apache NiFi for extraction and Apache Spark for transformation and analytical queries.

> **Result: ~19.5× query speedup** over the MySQL OLTP baseline on standard TPC-H analytical queries.

---

## Pipeline Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌─────────────────────┐
│   MySQL 8.x  │     │   Apache NiFi   │     │   Apache Parquet    │
│  (22 tables, │────►│  ETL Pipeline   │────►│  (Star Schema)      │
│   OLTP / 3NF)│     │  Extract +      │     │  Columnar Storage   │
│   TPC-H data │     │  Transform      │     └──────────┬──────────┘
└──────────────┘     └─────────────────┘                │
                                                         ▼
                                               ┌─────────────────────┐
                                               │   Apache Spark      │
                                               │   OLAP Query Engine │
                                               │   22 TPC-H queries  │
                                               └─────────────────────┘
```

### Star Schema Design

```
                    ┌──────────────┐
                    │  FACT_ORDERS │
                    │  (lineitem)  │
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ DIM_PART   │  │DIM_CUSTOMER│  │DIM_SUPPLIER│
    └────────────┘  └────────────┘  └────────────┘
           ┌───────────────┼
           ▼               ▼
    ┌────────────┐  ┌────────────┐
    │  DIM_DATE  │  │DIM_NATION  │
    └────────────┘  └────────────┘
```

---

## Benchmark Results

| Query Type | MySQL (OLTP) | Apache Spark (OLAP) | Speedup |
|-----------|-------------|---------------------|---------|
| Aggregation (Q1) | ~18s | ~0.9s | **20×** |
| Join-heavy (Q3) | ~35s | ~1.8s | **19.4×** |
| Group + filter (Q6) | ~12s | ~0.6s | **20×** |
| Multi-join (Q5) | ~42s | ~2.2s | **19.1×** |
| **Average** | — | — | **~19.5×** |

---

## Project Structure

```
OLAP/
├── scripts/
│   ├── convert_to_parquet.py   # OLTP → Parquet conversion
│   ├── mysql_benchmark.sh      # MySQL baseline timing
│   └── spark_benchmark.py      # Spark OLAP query runner
├── schemas/                    # Star schema DDL + diagrams
├── results/                    # Benchmark timing outputs
└── report/                     # Full lab report
```

---

## Getting Started

### Prerequisites
- MySQL 8.x
- Apache NiFi 2.2+
- Apache Spark 3.x
- Python 3.9+, Java 21

### Run the Pipeline

```bash
git clone https://github.com/Ibrahimtareq952001/OLAP.git
cd OLAP

# 1. Set up MySQL and load TPC-H data
#    Follow schemas/ DDL scripts

# 2. Run NiFi ETL to extract + load to Parquet
#    Import the NiFi flow template

# 3. Run Spark benchmark
python3 scripts/spark_benchmark.py

# 4. Run MySQL baseline benchmark
bash scripts/mysql_benchmark.sh
```

---

<div align="center">

*Data Engineering — Designing Data-Intensive Applications, Alexandria University 2025*

[![Resume](https://img.shields.io/badge/View_Resume-PDF-008080?style=flat-square&logo=latex&logoColor=white)](https://github.com/Ibrahimtareq952001/Resume/blob/main/resume.pdf)
[![Portfolio](https://img.shields.io/badge/GitHub-Ibrahimtareq952001-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Ibrahimtareq952001)

</div>

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=20,24,30&height=100&section=footer"/>
