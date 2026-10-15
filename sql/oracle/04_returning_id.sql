-- Case 03 / Oracle Database 12c+. Transaction will be rolled back.
-- RETURNING INTO is scoped to the INSERT and avoids lookups for the new key.
SET SERVEROUTPUT ON;
DECLARE
    v_customer_id demo_customers.customer_id%TYPE;
BEGIN
    SAVEPOINT before_demo_insert;
    INSERT INTO demo_customers (display_name, segment)
    VALUES (N'Synthetic Review Record', N'SMB')
    RETURNING customer_id INTO v_customer_id;
    DBMS_OUTPUT.PUT_LINE('Generated synthetic customer id: ' || v_customer_id);
    ROLLBACK TO before_demo_insert;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK TO before_demo_insert;
        RAISE;
END;
/
