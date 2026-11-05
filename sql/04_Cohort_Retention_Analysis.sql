
/*
PURPOSE: Measure customer retention by first-purchase cohort.
DATABASE: ecommerce_customer_360
COMPATIBILITY: MySQL 8.0+

DEFINITIONS:
- Cohort month: Month of the customer's first delivered order.
- Month number 0: The customer's first-purchase month.
- Retained customers: Distinct customers with a delivered order
  in the cohort month number.
- Retention percentage: Retained customers / original cohort size.
*/

USE ecommerce_customer_360;

-- ============================================================
-- QUERY 01: MONTHLY CUSTOMER COHORT RETENTION
-- BUSINESS QUESTION: What percentage of each customer cohort
--                    returns in subsequent months?
-- ============================================================

WITH customer_orders AS (
    SELECT DISTINCT
        c.customer_unique_id,
        o.order_id,
        DATE_FORMAT(
            o.order_purchase_timestamp,
            '%Y-%m-01'
        ) AS order_month
    FROM customers AS c
    JOIN orders AS o
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
),
first_purchase AS (
    SELECT
        customer_unique_id,
        MIN(order_month) AS cohort_month
    FROM customer_orders
    GROUP BY customer_unique_id
),
cohort_data AS (
    SELECT
        co.customer_unique_id,
        fp.cohort_month,
        co.order_month,
        PERIOD_DIFF(
            REPLACE(co.order_month, '-', ''),
            REPLACE(fp.cohort_month, '-', '')
        ) AS month_number
    FROM customer_orders AS co
    JOIN first_purchase AS fp
        ON co.customer_unique_id = fp.customer_unique_id
),
cohort_counts AS (
    SELECT
        cohort_month,
        month_number,
        COUNT(DISTINCT customer_unique_id) AS retained_customers
    FROM cohort_data
    GROUP BY cohort_month, month_number
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_unique_id) AS cohort_size
    FROM first_purchase
    GROUP BY cohort_month
)
SELECT
    cc.cohort_month,
    cc.month_number,
    cs.cohort_size,
    cc.retained_customers,
    ROUND(
        cc.retained_customers * 100.0 / cs.cohort_size,
        2
    ) AS retention_percentage
FROM cohort_counts AS cc
JOIN cohort_sizes AS cs
    ON cc.cohort_month = cs.cohort_month
ORDER BY cc.cohort_month, cc.month_number;
