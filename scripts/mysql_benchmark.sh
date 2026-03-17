#!/bin/bash
echo "Starting MySQL benchmark - 8 runs"
echo "Run,Time(seconds)" > ~/mysql_times.csv

for i in {1..8}
do
    echo "Run $i..."
    START=$(date +%s%N)
    mysql -u nifi -pnifi123 tpch << 'SQLEOF'
SELECT
    n.n_name,
    s.s_name,
    sum(l.l_quantity) as sum_qty,
    sum(l.l_extendedprice) as sum_base_price,
    sum(l.l_extendedprice * (1 - l.l_discount)) as sum_disc_price,
    sum(l.l_extendedprice * (1 - l.l_discount) * (1 + l.l_tax)) as sum_charge,
    avg(l.l_quantity) as avg_qty,
    avg(l.l_extendedprice) as avg_price,
    avg(l.l_discount) as avg_disc,
    count(*) as count_order
FROM
    lineitem l,
    orders o,
    customer c,
    nation n,
    partsupp ps,
    supplier s
WHERE
    l.l_shipdate <= '1998-09-02'
    AND l.l_orderkey = o.o_orderkey
    AND o.o_custkey = c.c_custkey
    AND c.c_nationkey = n.n_nationkey
    AND l.l_partkey = ps.ps_partkey
    AND l.l_suppkey = ps.ps_suppkey
    AND ps.ps_suppkey = s.s_suppkey
GROUP BY
    n.n_name,
    s.s_name;
SQLEOF
    END=$(date +%s%N)
    ELAPSED=$(echo "scale=3; ($END - $START) / 1000000000" | bc)
    echo "Run $i: $ELAPSED seconds"
    echo "$i,$ELAPSED" >> ~/mysql_times.csv
done

echo "Done! Results saved to ~/mysql_times.csv"
cat ~/mysql_times.csv
