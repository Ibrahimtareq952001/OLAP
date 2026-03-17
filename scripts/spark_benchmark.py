from pyspark.sql import SparkSession
import time
import csv

# Create Spark session
spark = SparkSession.builder \
    .appName("TPCH OLAP Benchmark") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("Loading Parquet files...")

# Load star schema parquet files
dim_supplier = spark.read.parquet(
    "/Users/ibrahimtarek/nifi-output/dim_supplier.parquet"
)
dim_customer = spark.read.parquet(
    "/Users/ibrahimtarek/nifi-output/dim_customer.parquet"
)
fact_lineitem = spark.read.parquet(
    "/Users/ibrahimtarek/nifi-output/fact_lineitem.parquet"
)

# Register as temp views for SQL
dim_supplier.createOrReplaceTempView("dim_supplier")
dim_customer.createOrReplaceTempView("dim_customer")
fact_lineitem.createOrReplaceTempView("fact_lineitem")

print("Tables loaded successfully!")
print(f"fact_lineitem rows: {fact_lineitem.count()}")
print(f"dim_supplier rows: {dim_supplier.count()}")
print(f"dim_customer rows: {dim_customer.count()}")

# The OLAP query on star schema
query = """
SELECT
    ds.n_name,
    ds.s_name,
    sum(f.l_quantity)                                    as sum_qty,
    sum(f.l_extendedprice)                               as sum_base_price,
    sum(f.l_extendedprice * (1 - f.l_discount))          as sum_disc_price,
    sum(f.l_extendedprice * (1 - f.l_discount) * (1 + f.l_tax)) as sum_charge,
    avg(f.l_quantity)                                    as avg_qty,
    avg(f.l_extendedprice)                               as avg_price,
    avg(f.l_discount)                                    as avg_disc,
    count(*)                                             as count_order
FROM fact_lineitem f
JOIN dim_supplier ds ON f.supplier_key = ds.supplier_key
JOIN dim_customer dc ON f.customer_key = dc.customer_key
GROUP BY ds.n_name, ds.s_name
"""

print("\nStarting 8 benchmark runs...")
times = []

for i in range(1, 9):
    print(f"Run {i}...")
    start = time.time()
    result = spark.sql(query)
    result.collect()
    end = time.time()
    elapsed = round(end - start, 3)
    times.append(elapsed)
    print(f"Run {i}: {elapsed} seconds")

# Save results
with open('/Users/ibrahimtarek/spark_times.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Run', 'Time(seconds)'])
    for i, t in enumerate(times, 1):
        writer.writerow([i, t])

avg_time = sum(times) / len(times)
print(f"\nAll runs complete!")
print(f"Average Spark time: {avg_time:.3f} seconds")
print(f"Results saved to ~/spark_times.csv")

spark.stop()
