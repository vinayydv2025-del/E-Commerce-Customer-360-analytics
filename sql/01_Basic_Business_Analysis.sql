/*
PURPOSE: Core business analysis using the Olist dataset.
DATABASE: ecommerce_customer_360
REQUIRED TABLES: orders, customers, order_items, order_payments,
                 products, category_translation

NOTES:
- Revenue is calculated from order_items.price and excludes freight.
- Queries that analyse sales/customer purchasing use delivered orders.
- Payment analysis includes all payment records unless otherwise stated.
- Compatible with MySQL 8.0+.
*/

USE ecommerce_customer_360;

-- ============================================================
-- QUERY 01: ORDER STATUS DISTRIBUTION
-- BUSINESS QUESTION: How are orders distributed by status?
-- ============================================================

SELECT
    order_status,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders),
        2
    ) AS percentage_of_orders
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;


-- ============================================================
-- QUERY 02: MONTHLY DELIVERED REVENUE
-- BUSINESS QUESTION: How does delivered-order revenue change
--                    from month to month?
-- ============================================================

SELECT
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS sales_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM orders AS o
JOIN order_items AS oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
ORDER BY sales_month;


-- ============================================================
-- QUERY 03: TOP 10 PRODUCT CATEGORIES BY REVENUE
-- BUSINESS QUESTION: Which product categories generate the
--                    highest delivered-order revenue?
-- ============================================================

SELECT
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name
    ) AS category,
    COUNT(*) AS items_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM order_items AS oi
JOIN orders AS o
    ON oi.order_id = o.order_id
JOIN products AS p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation AS ct
    ON p.product_category_name = ct.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- QUERY 04: PAYMENT METHOD ANALYSIS
-- BUSINESS QUESTION: Which payment methods account for the
--                    highest payment value?
-- NOTE: Includes payment records across all order statuses.
-- ============================================================

SELECT
    payment_type,
    COUNT(*) AS payment_transactions,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS average_payment_value
FROM order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- ============================================================
-- QUERY 05: REPEAT CUSTOMER IDENTIFICATION
-- BUSINESS QUESTION: Which customers have placed more than
--                    one delivered order?
-- CUSTOMER GRAIN: customer_unique_id
-- ============================================================

SELECT
    c.customer_unique_id,
    COUNT(DISTINCT o.order_id) AS total_delivered_orders
FROM customers AS c
JOIN orders AS o
    ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id
HAVING COUNT(DISTINCT o.order_id) > 1
ORDER BY total_delivered_orders DESC;