
/*
PURPOSE: Calculate historical customer value and classify
         customer inactivity / churn risk.
DATABASE: ecommerce_customer_360
COMPATIBILITY: MySQL 8.0+

DEFINITIONS:
- Historical CLV: Sum of delivered order item prices per customer.
- Average order value: Average delivered-order item revenue.
- Inactivity: Days since the customer's latest delivered order,
  measured against the latest delivered order date in the dataset.
- Active: 0-90 inactive days.
- At Risk: 91-180 inactive days.
- High Risk: More than 180 inactive days.

IMPORTANT:
These inactivity bands are heuristic business rules. They are
not predictions from a trained machine-learning model.
Freight charges are excluded from revenue.
*/

USE ecommerce_customer_360;

-- ============================================================
-- QUERY 01: HISTORICAL CUSTOMER LIFETIME VALUE (CLV)
-- BUSINESS QUESTION: Which customers generate the highest
--                    historical delivered-order revenue?
-- OUTPUT: One row per customer_unique_id.
-- ============================================================

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        SUM(oi.price) AS order_revenue
    FROM customers AS c
    JOIN orders AS o
        ON c.customer_id = o.customer_id
    JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp
),
customer_clv AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(order_revenue) AS lifetime_revenue,
        AVG(order_revenue) AS average_order_value,
        MIN(order_purchase_timestamp) AS first_purchase_date,
        MAX(order_purchase_timestamp) AS last_purchase_date
    FROM customer_orders
    GROUP BY customer_unique_id
)
SELECT
    customer_unique_id,
    total_orders,
    ROUND(lifetime_revenue, 2) AS historical_clv,
    ROUND(average_order_value, 2) AS average_order_value,
    first_purchase_date,
    last_purchase_date
FROM customer_clv
ORDER BY historical_clv DESC;


-- ============================================================
-- QUERY 02: CUSTOMER-LEVEL INACTIVITY AND CHURN RISK
-- BUSINESS QUESTION: How recently did each customer purchase,
--                    and which inactivity band do they belong to?
-- OUTPUT: One row per customer_unique_id.
-- ============================================================

WITH customer_last_purchase AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.price) AS lifetime_revenue
    FROM customers AS c
    JOIN orders AS o
        ON c.customer_id = o.customer_id
    JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
analysis_date AS (
    SELECT
        MAX(order_purchase_timestamp) AS snapshot_date
    FROM orders
    WHERE order_status = 'delivered'
)
SELECT
    clp.customer_unique_id,
    clp.total_orders,
    ROUND(clp.lifetime_revenue, 2) AS lifetime_revenue,
    clp.last_purchase_date,
    DATEDIFF(
        ad.snapshot_date,
        clp.last_purchase_date
    ) AS inactive_days,
    CASE
        WHEN DATEDIFF(
            ad.snapshot_date,
            clp.last_purchase_date
        ) <= 90
            THEN 'Active'
        WHEN DATEDIFF(
            ad.snapshot_date,
            clp.last_purchase_date
        ) <= 180
            THEN 'At Risk'
        ELSE 'High Risk'
    END AS churn_risk
FROM customer_last_purchase AS clp
CROSS JOIN analysis_date AS ad
ORDER BY inactive_days DESC;


-- ============================================================
-- QUERY 03: CHURN RISK BUSINESS SUMMARY
-- BUSINESS QUESTION: How many customers and how much
--                    historical revenue are in each risk group?
-- ============================================================

WITH customer_metrics AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.price) AS lifetime_revenue
    FROM customers AS c
    JOIN orders AS o
        ON c.customer_id = o.customer_id
    JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
snapshot AS (
    SELECT
        MAX(order_purchase_timestamp) AS snapshot_date
    FROM orders
    WHERE order_status = 'delivered'
),
risk_classification AS (
    SELECT
        cm.customer_unique_id,
        cm.last_purchase_date,
        cm.total_orders,
        cm.lifetime_revenue,
        DATEDIFF(
            s.snapshot_date,
            cm.last_purchase_date
        ) AS inactive_days,
        CASE
            WHEN DATEDIFF(
                s.snapshot_date,
                cm.last_purchase_date
            ) <= 90
                THEN 'Active'
            WHEN DATEDIFF(
                s.snapshot_date,
                cm.last_purchase_date
            ) <= 180
                THEN 'At Risk'
            ELSE 'High Risk'
        END AS churn_risk
    FROM customer_metrics AS cm
    CROSS JOIN snapshot AS s
)
SELECT
    churn_risk,
    COUNT(*) AS total_customers,
    ROUND(AVG(lifetime_revenue), 2) AS avg_customer_revenue,
    ROUND(SUM(lifetime_revenue), 2) AS total_revenue,
    ROUND(AVG(total_orders), 2) AS avg_orders_per_customer,
    ROUND(AVG(inactive_days), 2) AS avg_inactive_days
FROM risk_classification
GROUP BY churn_risk
ORDER BY
    CASE churn_risk
        WHEN 'High Risk' THEN 1
        WHEN 'At Risk' THEN 2
        WHEN 'Active' THEN 3
    END;
