
/*
PURPOSE: Advanced SQL analysis using CTEs and window functions.
DATABASE: ecommerce_customer_360
COMPATIBILITY: MySQL 8.0+
*/

USE ecommerce_customer_360;

-- ============================================================
-- QUERY 01: REPEAT CUSTOMER ANALYSIS USING A CTE
-- BUSINESS QUESTION: How can repeat customers be isolated
--                    using a Common Table Expression (CTE)?
-- ============================================================

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS total_delivered_orders
    FROM customers AS c
    JOIN orders AS o
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT
    customer_unique_id,
    total_delivered_orders
FROM customer_orders
WHERE total_delivered_orders > 1
ORDER BY total_delivered_orders DESC;


-- ============================================================
-- QUERY 02: RANK PRODUCT CATEGORIES BY REVENUE
-- BUSINESS QUESTION: What is the revenue rank of each
--                    product category?
-- SQL CONCEPT: CTE + RANK()
-- ============================================================

WITH category_revenue AS (
    SELECT
        COALESCE(
            ct.product_category_name_english,
            p.product_category_name
        ) AS category,
        SUM(oi.price) AS revenue
    FROM order_items AS oi
    JOIN orders AS o
        ON oi.order_id = o.order_id
    JOIN products AS p
        ON oi.product_id = p.product_id
    LEFT JOIN category_translation AS ct
        ON p.product_category_name = ct.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY category
)
SELECT
    category,
    ROUND(revenue, 2) AS revenue,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM category_revenue
ORDER BY revenue_rank;


-- ============================================================
-- QUERY 03: COMPARE RANK, DENSE_RANK, AND ROW_NUMBER
-- BUSINESS QUESTION: How do payment methods rank by total
--                    payment value, including ties?
-- ============================================================

SELECT
    payment_type,
    ROUND(SUM(payment_value), 2) AS total_payment,
    RANK() OVER (
        ORDER BY SUM(payment_value) DESC
    ) AS rank_position,
    DENSE_RANK() OVER (
        ORDER BY SUM(payment_value) DESC
    ) AS dense_rank_position,
    ROW_NUMBER() OVER (
        ORDER BY SUM(payment_value) DESC, payment_type
    ) AS row_position
FROM order_payments
GROUP BY payment_type;


-- ============================================================
-- QUERY 04: MONTH-OVER-MONTH REVENUE COMPARISON
-- BUSINESS QUESTION: How does monthly delivered revenue
--                    compare with the previous month?
-- SQL CONCEPT: CTE + LAG()
-- ============================================================

WITH monthly_revenue AS (
    SELECT
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS sales_month,
        SUM(oi.price) AS revenue
    FROM orders AS o
    JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
)
SELECT
    sales_month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        LAG(revenue) OVER (ORDER BY sales_month),
        2
    ) AS previous_month_revenue,
    ROUND(
        revenue - LAG(revenue) OVER (ORDER BY sales_month),
        2
    ) AS revenue_difference
FROM monthly_revenue
ORDER BY sales_month;


-- ============================================================
-- QUERY 05: NEXT-MONTH ORDER COUNT USING LEAD()
-- BUSINESS QUESTION: How many delivered orders were placed
--                    in the following month?
-- SQL CONCEPT: CTE + LEAD()
-- ============================================================

WITH monthly_orders AS (
    SELECT
        DATE_FORMAT(order_purchase_timestamp, '%Y-%m') AS sales_month,
        COUNT(DISTINCT order_id) AS total_orders
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY DATE_FORMAT(order_purchase_timestamp, '%Y-%m')
)
SELECT
    sales_month,
    total_orders,
    LEAD(total_orders) OVER (
        ORDER BY sales_month
    ) AS next_month_orders
FROM monthly_orders
ORDER BY sales_month;
