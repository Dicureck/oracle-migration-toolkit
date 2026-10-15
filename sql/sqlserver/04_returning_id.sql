-- Case 03 / SQL Server. Transaction will be rolled back.
-- Identity retrieval after INSERT is demonstrated using OUTPUT inserted.
BEGIN TRANSACTION;
INSERT INTO dbo.demo_customers (display_name, segment)
OUTPUT INSERTED.customer_id
VALUES (N'Synthetic Review Record', N'SMB');
ROLLBACK TRANSACTION;
