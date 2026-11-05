# E-Commerce Customer 360° Analytics & Intelligent Retention Strategy

## 1. Executive Summary

This project analyses the Olist Brazilian e-commerce dataset to understand business performance, customer purchasing behaviour, product revenue, customer retention, and delivery operations.

The objective is to transform raw transactional data into actionable business insights using Python, MySQL, and Power BI.

The analysis covers approximately 96,000 delivered orders and 93,000 unique customers, with a focus on identifying opportunities to improve customer retention, revenue generation, and operational efficiency.

## 2. Business Objectives

- Analyse overall sales and revenue performance.
- Identify high-performing product categories.
- Understand customer purchasing and repeat-purchase behaviour.
- Segment customers using RFM analysis.
- Evaluate customer retention and delivery performance.
- Develop data-driven business recommendations.

## 3. Key Performance Indicators

| Metric | Result |
|---|---:|
| Total Revenue | 13.22 million |
| Total Orders | 96,000 |
| Total Customers | 93,000 |
| Average Order Value | 137.04 |
| Repeat Customer Rate | 3.00% |
| Repeat Customers | 3,000 |
| One-Time Customers | 91,000 |
| Average Delivery Time | 12.50 days |
| Late Delivery Orders | 8,000 |
| Late Delivery Rate | 8.11% |
| Average Review Score | 4.09 / 5 |

*Note: Revenue and average order value are in the dataset's original currency, BRL, unless separately converted. Dashboard figures are rounded.*

## 4. Key Business Findings

### 4.1 Revenue and Sales Performance

- Total delivered-order revenue is approximately 13.22 million.
- Approximately 96,000 delivered orders were analysed.
- Revenue increased during the earlier period and subsequently fluctuated.
- November 2017 and May 2018 were identified as peak revenue months.

### 4.2 Product Category Performance

The five leading product categories by revenue were:

1. Health & Beauty
2. Watches & Gifts
3. Bed, Bath & Table
4. Sports & Leisure
5. Computers & Accessories

Health & Beauty was the leading revenue-generating category.

### 4.3 Customer Retention Analysis

- Approximately 93,000 unique customers were identified.
- Only around 3% were repeat customers.
- Approximately 91,000 customers were classified as one-time customers.
- The low repeat-purchase rate indicates a major opportunity for customer retention initiatives.

### 4.4 RFM Customer Segmentation

Customers were segmented using Recency, Frequency, and Monetary value.

The six identified customer segments were:

- Champions
- Loyal Customers
- Potential Loyalists
- New Customers
- Need Attention
- At Risk

The At Risk segment represented the largest customer group.

This suggests that customer re-engagement should be a major business priority.

### 4.5 Delivery Performance

- Average delivery time was approximately 12.5 days.
- Around 8,000 delivered orders were late.
- Late delivery rate was approximately 8.11%.
- Late deliveries showed a decreasing trend over time.

Roraima (RR) had the highest average delivery time, while São Paulo (SP) had the lowest among the states analysed.

### 4.6 Customer Satisfaction

- Average review score was 4.09 out of 5.
- Five-star reviews represented the largest review-score category.

Overall, the review distribution indicates positive customer feedback, although lower-rated reviews should be investigated.

## 5. Business Recommendations

### Recommendation 1: Improve Customer Retention

Introduce loyalty programmes, personalized discounts, and targeted re-engagement campaigns to encourage repeat purchases.

### Recommendation 2: Target At Risk Customers

Use RFM segmentation to identify inactive customers and create targeted campaigns based on their historical purchase behaviour.

### Recommendation 3: Focus on High-Performing Categories

Prioritize inventory planning, marketing campaigns, and seller partnerships in Health & Beauty and Watches & Gifts.

### Recommendation 4: Improve Regional Logistics

Investigate logistics operations in regions with longer delivery times, particularly Roraima. Evaluate shipping routes, seller locations, and delivery partners.

### Recommendation 5: Maintain Customer Satisfaction

Analyse negative reviews to identify recurring complaints and continue improving delivery reliability and customer service.

## 6. Technology Stack

| Technology | Application |
|---|---|
| Python | Data cleaning and exploratory analysis |
| Pandas & NumPy | Data manipulation |
| Matplotlib & Seaborn | Data visualization |
| MySQL | Data storage and advanced SQL analysis |
| SQL | Joins, CTEs, window functions, RFM and cohort analysis |
| Power BI | Interactive dashboards and DAX |
| Git & GitHub | Version control and project documentation |

## 7. Project Limitations

- RFM segmentation uses rule-based scoring rather than a trained machine-learning model.
- Churn risk categories are heuristic classifications based on customer inactivity.
- Revenue analysis uses item prices and excludes freight charges.
- Historical findings do not guarantee future customer behaviour.
- Delivery and review relationships are descriptive and do not establish causation.

## 8. Conclusion

The project demonstrates how multiple data sources can be integrated into a customer-centric analytical solution.

The most important finding is the low repeat-purchase rate, combined with a large At Risk customer segment. These findings highlight the importance of customer retention alongside new customer acquisition.

By combining Python, SQL, customer segmentation, and Power BI, this project provides a structured approach to understanding business performance and supporting data-driven decisions.

## 9. Future Improvements

- Develop a machine-learning-based customer churn prediction model.
- Build a customer lifetime value prediction model.
- Implement product recommendation algorithms.
- Perform customer cohort retention analysis in Power BI.
- Develop automated reporting and monitoring pipelines.