-- Total KPIs
SELECT SUM(revenue) AS revenue, COUNT(DISTINCT transaction_id) AS orders,
       SUM(revenue) / COUNT(DISTINCT transaction_id) AS aov, SUM(quantity) AS units
FROM v_sales;

-- Monthly trend
SELECT substr(order_date,1,7) AS month, SUM(revenue) AS revenue
FROM v_sales GROUP BY month ORDER BY month;

-- Top 10 products
SELECT product_name, SUM(revenue) AS revenue FROM v_sales
GROUP BY product_name ORDER BY revenue DESC LIMIT 10;

-- Bottom 5 products
SELECT product_name, SUM(revenue) AS revenue FROM v_sales
GROUP BY product_name ORDER BY revenue ASC LIMIT 5;

-- Revenue by region and city
SELECT region, city, SUM(revenue) AS revenue FROM v_sales
GROUP BY region, city ORDER BY revenue DESC;

-- Customer value (excluding unknown)
SELECT customer_id, customer_name, COUNT(DISTINCT transaction_id) AS orders, SUM(revenue) AS revenue
FROM v_sales WHERE customer_id <> 'UNKNOWN'
GROUP BY customer_id, customer_name ORDER BY revenue DESC;