-- Synthetic demo schema. SQL Server 2019+; run in a disposable database only.
-- This script is illustrative DDL. Do not run on corporate infrastructure.
CREATE TABLE dbo.demo_customers (
    customer_id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    display_name NVARCHAR(120) NOT NULL,
    segment NVARCHAR(30) NOT NULL
);
GO
CREATE TABLE dbo.demo_orders (
    order_id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES dbo.demo_customers(customer_id),
    created_at DATETIME2(0) NOT NULL,
    status VARCHAR(12) NOT NULL CHECK (status IN ('COMPLETED', 'VOID')),
    amount DECIMAL(18,2) NOT NULL CHECK (amount >= 0)
);
GO
CREATE INDEX ix_demo_orders_period
    ON dbo.demo_orders(created_at, status, customer_id)
    INCLUDE (amount);
GO
