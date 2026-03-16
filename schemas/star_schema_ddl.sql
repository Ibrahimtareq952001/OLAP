
-- Dimension: Supplier (pre-joined with Nation)

CREATE TABLE dim_supplier (

  supplier_key  INT PRIMARY KEY,

  s_name        VARCHAR(100),

  s_address     VARCHAR(200),

  s_phone       VARCHAR(20),

  s_acctbal     DECIMAL(10,2),

  n_name        VARCHAR(100),

  n_regionkey   INT

);

-- Dimension: Customer (pre-joined with Nation)

CREATE TABLE dim_customer (

  customer_key  INT PRIMARY KEY,

  c_name        VARCHAR(100),

  c_address     VARCHAR(200),

  c_phone       VARCHAR(20),

  c_acctbal     DECIMAL(10,2),

  c_mktsegment  VARCHAR(50),

  n_name        VARCHAR(100)

);

-- Dimension: Date

CREATE TABLE dim_date (

  date_key   INT PRIMARY KEY,

  full_date  DATE,

  year       INT,

  month      INT,

  day        INT,

  quarter    INT

);

-- Fact Table

CREATE TABLE fact_lineitem (

  lineitem_id     INT PRIMARY KEY,

  supplier_key    INT,

  customer_key    INT,

  date_key        INT,

  l_quantity      DECIMAL(10,2),

  l_extendedprice DECIMAL(10,2),

  l_discount      DECIMAL(5,2),

  l_tax           DECIMAL(5,2),

  l_returnflag    CHAR(1),

  l_linestatus    CHAR(1)

);

