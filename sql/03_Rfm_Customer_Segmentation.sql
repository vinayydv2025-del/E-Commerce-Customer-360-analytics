
/*
PURPOSE: Calculate customer-level RFM scores and assign
         actionable customer segments.
DATABASE: ecommerce_customer_360
         COMPATIBILITY: MySQL 8.0+

RFM DEFINITIONS:
- Recency: Days since the customer's latest delivered order.
  Lower recency is better.
- Frequency: Number of distinct delivered orders.
  Higher frequency is better.
- Monetary: Sum of delivered order item prices.
  Higher monetary value is better.

IMPORTANT:
- Revenue uses order_items.price and excludes freight.
- NTILE(5) creates relative quintile scores from 1 to 5.
- Ties may be split across NTILE buckets.
- These are rule-based segments, not ML churn predictions.
*/

USE ecommerce_customer_360;

-- ============================================================
-- QUERY 01: CUSTOMER-LEVEL RFM SEGMENTATION
-- PURPOSE: Export this result to CSV for Power BI.
-- OUTPUT: One row per customer_unique_id, including all RFM
--         metrics, scores, and the customer segment.
-- ============================================================

WITH customer_metrics AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price) AS monetary
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
rfm AS (
    SELECT
        cm.customer_unique_id,
        DATEDIFF(s.snapshot_date, cm.last_purchase_date) AS recency,
        cm.frequency,
        cm.monetary
    FROM customer_metrics AS cm
    CROSS JOIN snapshot AS s
),
rfm_scores AS (
    SELECT
        customer_unique_id,
        recency,
        frequency,
        monetary,

        -- Lower recency is better, so DESC gives the lowest
        -- recency values the highest NTILE score (5).
        NTILE(5) OVER (ORDER BY recency DESC) AS recency_score,

        -- Higher frequency and monetary value are better.
        -- ASC gives the highest values the highest score (5).
        NTILE(5) OVER (ORDER BY frequency ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS monetary_score
    FROM rfm
),
segments AS (
    SELECT
        customer_unique_id,
        recency,
        frequency,
        monetary,
        recency_score,
        frequency_score,
        monetary_score,
        CONCAT(
            recency_score,
            frequency_score,
            monetary_score
        ) AS rfm_score,
        CASE
            WHEN recency_score >= 4
                 AND frequency_score >= 4
                 AND monetary_score >= 4
                THEN 'Champions'

            WHEN recency_score >= 3
                 AND frequency_score >= 4
                THEN 'Loyal Customers'

            WHEN recency_score >= 4
                 AND frequency_score BETWEEN 2 AND 3
                THEN 'Potential Loyalists'

            WHEN recency_score >= 4
                 AND frequency_score <= 2
                THEN 'New Customers'

            WHEN recency_score BETWEEN 2 AND 3
                 AND frequency_score BETWEEN 2 AND 3
                THEN 'Need Attention'

            WHEN recency_score <= 2
                 AND frequency_score >= 3
                THEN 'At Risk'

            WHEN recency_score <= 2
                 AND frequency_score <= 2
                THEN 'Lost Customers'

            ELSE 'Others'
        END AS customer_segment
    FROM rfm_scores
)

SELECT
    customer_unique_id,
    recency,
    frequency,
    ROUND(monetary, 2) AS monetary,
    recency_score,
    frequency_score,
    monetary_score,
    rfm_score,
    customer_segment
FROM segments
ORDER BY recency_score DESC, frequency_score DESC, monetary_score DESC;


-- ============================================================
-- QUERY 02: RFM SEGMENT BUSINESS SUMMARY
-- BUSINESS QUESTION: How many customers and how much revenue
--                    belong to each RFM segment?
-- ============================================================

WITH customer_metrics AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price) AS monetary
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
rfm AS (
    SELECT
        cm.customer_unique_id,
        DATEDIFF(s.snapshot_date, cm.last_purchase_date) AS recency,
        cm.frequency,
        cm.monetary
    FROM customer_metrics AS cm
    CROSS JOIN snapshot AS s
),
rfm_scores AS (
    SELECT
        customer_unique_id,
        recency,
        frequency,
        monetary,

        -- Lower recency is better, so DESC gives the lowest
        -- recency values the highest NTILE score (5).
        NTILE(5) OVER (ORDER BY recency DESC) AS recency_score,

        -- Higher frequency and monetary value are better.
        -- ASC gives the highest values the highest score (5).
        NTILE(5) OVER (ORDER BY frequency ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS monetary_score
    FROM rfm
),
segments AS (
    SELECT
        customer_unique_id,
        recency,
        frequency,
        monetary,
        recency_score,
        frequency_score,
        monetary_score,
        CONCAT(
            recency_score,
            frequency_score,
            monetary_score
        ) AS rfm_score,
        CASE
            WHEN recency_score >= 4
                 AND frequency_score >= 4
                 AND monetary_score >= 4
                THEN 'Champions'

            WHEN recency_score >= 3
                 AND frequency_score >= 4
                THEN 'Loyal Customers'

            WHEN recency_score >= 4
                 AND frequency_score BETWEEN 2 AND 3
                THEN 'Potential Loyalists'

            WHEN recency_score >= 4
                 AND frequency_score <= 2
                THEN 'New Customers'

            WHEN recency_score BETWEEN 2 AND 3
                 AND frequency_score BETWEEN 2 AND 3
                THEN 'Need Attention'

            WHEN recency_score <= 2
                 AND frequency_score >= 3
                THEN 'At Risk'

            WHEN recency_score <= 2
                 AND frequency_score <= 2
                THEN 'Lost Customers'

            ELSE 'Others'
        END AS customer_segment
    FROM rfm_scores
)

SELECT
    customer_segment,
    COUNT(*) AS total_customers,
    ROUND(AVG(monetary), 2) AS average_customer_spend,
    ROUND(SUM(monetary), 2) AS segment_revenue
FROM segments
GROUP BY customer_segment
ORDER BY total_customers DESC;
