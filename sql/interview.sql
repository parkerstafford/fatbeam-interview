CREATE TABLE territories (
    territory_id VARCHAR(20) PRIMARY KEY,
    territory_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    country VARCHAR(50) DEFAULT 'USA',
    quota_monthly DECIMAL(12,2),
    active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_reps (
    rep_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    territory_id VARCHAR(20),
    hire_date DATE NOT NULL,
    role VARCHAR(50) DEFAULT 'Account Executive',
    quota_annual DECIMAL(12,2),
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (territory_id) REFERENCES territories(territory_id)
);

CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    product_category VARCHAR(50),
    unit_price DECIMAL(10,2),
    recurring BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE accounts (
    account_id VARCHAR(20) PRIMARY KEY,
    account_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    territory_id VARCHAR(20),
    annual_revenue DECIMAL(15,2),
    website VARCHAR(200),
    primary_contact_name VARCHAR(100),
    primary_contact_email VARCHAR(100),
    account_status VARCHAR(50) DEFAULT 'Active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (territory_id) REFERENCES territories(territory_id)
);


CREATE TABLE opportunities (
    opportunity_id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) NOT NULL,
    rep_id VARCHAR(20) NOT NULL,
    opportunity_name VARCHAR(200) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    product_id VARCHAR(20),
    amount DECIMAL(12,2) NOT NULL,
    probability INT CHECK (probability >= 0 AND probability <= 100),
    expected_revenue DECIMAL(12,2),
    close_date DATE NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    days_in_stage INT,
    previous_stage VARCHAR(50),
    stage_change_date TIMESTAMP,
    lead_source VARCHAR(100),
    next_step TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (rep_id) REFERENCES sales_reps(rep_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE activities (
    activity_id VARCHAR(20) PRIMARY KEY,
    opportunity_id VARCHAR(20),
    account_id VARCHAR(20),
    rep_id VARCHAR(20) NOT NULL,
    activity_type VARCHAR(50) NOT NULL, 
    activity_date TIMESTAMP NOT NULL,
    duration_minutes INT,
    outcome VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (rep_id) REFERENCES sales_reps(rep_id)
);

CREATE TABLE stage_history (
    history_id SERIAL PRIMARY KEY,
    opportunity_id VARCHAR(20) NOT NULL,
    from_stage VARCHAR(50),
    to_stage VARCHAR(50) NOT NULL,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    days_in_previous_stage INT,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id)
);


CREATE INDEX idx_opp_stage ON opportunities(stage);
CREATE INDEX idx_opp_close_date ON opportunities(close_date);
CREATE INDEX idx_opp_rep ON opportunities(rep_id);
CREATE INDEX idx_opp_account ON opportunities(account_id);
CREATE INDEX idx_opp_created ON opportunities(created_date);
CREATE INDEX idx_activities_date ON activities(activity_date);
CREATE INDEX idx_activities_opp ON activities(opportunity_id);
CREATE INDEX idx_stage_history_opp ON stage_history(opportunity_id);

CREATE VIEW v_current_pipeline AS
SELECT 
    o.opportunity_id,
    o.opportunity_name,
    a.account_name,
    o.stage,
    o.amount,
    o.probability,
    o.expected_revenue,
    o.close_date,
    o.created_date,
    o.days_in_stage,
    p.product_name,
    p.product_category,
    sr.first_name || ' ' || sr.last_name AS rep_name,
    sr.rep_id,
    t.territory_name,
    t.region,
    DATEDIFF(o.close_date, CURRENT_DATE) AS days_until_close,
    DATEDIFF(CURRENT_DATE, o.created_date) AS opportunity_age_days
FROM opportunities o
JOIN accounts a ON o.account_id = a.account_id
JOIN sales_reps sr ON o.rep_id = sr.rep_id
JOIN territories t ON sr.territory_id = t.territory_id
LEFT JOIN products p ON o.product_id = p.product_id
WHERE o.stage NOT IN ('Closed Won', 'Closed Lost');

CREATE VIEW v_rep_performance AS
SELECT 
    sr.rep_id,
    sr.first_name || ' ' || sr.last_name AS rep_name,
    t.territory_name,
    t.region,
    COUNT(CASE WHEN o.stage NOT IN ('Closed Won', 'Closed Lost') THEN 1 END) AS open_opps,
    SUM(CASE WHEN o.stage NOT IN ('Closed Won', 'Closed Lost') THEN o.amount ELSE 0 END) AS pipeline_value,
    SUM(CASE WHEN o.stage NOT IN ('Closed Won', 'Closed Lost') THEN o.expected_revenue ELSE 0 END) AS weighted_pipeline,
    COUNT(CASE WHEN o.stage = 'Closed Won' THEN 1 END) AS won_deals,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) AS total_revenue,
    COUNT(CASE WHEN o.stage = 'Closed Lost' THEN 1 END) AS lost_deals,
    CASE 
        WHEN COUNT(CASE WHEN o.stage IN ('Closed Won', 'Closed Lost') THEN 1 END) > 0
        THEN ROUND(100.0 * COUNT(CASE WHEN o.stage = 'Closed Won' THEN 1 END) / 
             COUNT(CASE WHEN o.stage IN ('Closed Won', 'Closed Lost') THEN 1 END), 2)
        ELSE 0 
    END AS win_rate_pct,
    AVG(CASE WHEN o.stage = 'Closed Won' THEN o.amount END) AS avg_deal_size
FROM sales_reps sr
JOIN territories t ON sr.territory_id = t.territory_id
LEFT JOIN opportunities o ON sr.rep_id = o.rep_id
WHERE sr.active = TRUE
GROUP BY sr.rep_id, sr.first_name, sr.last_name, t.territory_name, t.region;


WITH stage_durations AS (
    SELECT 
        sh.opportunity_id,
        sh.from_stage,
        sh.to_stage,
        sh.days_in_previous_stage,
        o.stage AS current_stage
    FROM stage_history sh
    JOIN opportunities o ON sh.opportunity_id = o.opportunity_id
)
SELECT 
    from_stage,
    COUNT(*) AS transitions,
    AVG(days_in_previous_stage) AS avg_days_in_stage,
    MIN(days_in_previous_stage) AS min_days,
    MAX(days_in_previous_stage) AS max_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY days_in_previous_stage) AS median_days
FROM stage_durations
WHERE from_stage IS NOT NULL
GROUP BY from_stage
ORDER BY avg_days_in_stage DESC;

SELECT 
    t.region,
    p.product_category,
    p.product_name,
    COUNT(CASE WHEN o.stage = 'Closed Won' THEN 1 END) AS won_count,
    COUNT(CASE WHEN o.stage = 'Closed Lost' THEN 1 END) AS lost_count,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) AS won_revenue,
    ROUND(100.0 * COUNT(CASE WHEN o.stage = 'Closed Won' THEN 1 END) / 
          NULLIF(COUNT(CASE WHEN o.stage IN ('Closed Won', 'Closed Lost') THEN 1 END), 0), 2) AS win_rate
FROM opportunities o
JOIN sales_reps sr ON o.rep_id = sr.rep_id
JOIN territories t ON sr.territory_id = t.territory_id
JOIN products p ON o.product_id = p.product_id
WHERE o.stage IN ('Closed Won', 'Closed Lost')
GROUP BY t.region, p.product_category, p.product_name
HAVING COUNT(*) >= 5
ORDER BY won_revenue DESC;

WITH monthly_forecasts AS (
    SELECT 
        DATE_TRUNC('month', close_date) AS forecast_month,
        SUM(expected_revenue) AS forecasted_revenue,
        SUM(CASE WHEN stage = 'Closed Won' THEN amount ELSE 0 END) AS actual_revenue
    FROM opportunities
    WHERE close_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '6 months')
    GROUP BY DATE_TRUNC('month', close_date)
)
SELECT 
    forecast_month,
    forecasted_revenue,
    actual_revenue,
    actual_revenue - forecasted_revenue AS variance,
    ROUND(100.0 * (actual_revenue - forecasted_revenue) / NULLIF(forecasted_revenue, 0), 2) AS variance_pct
FROM monthly_forecasts
ORDER BY forecast_month;

SELECT 
    a.account_name,
    o1.opportunity_id AS opp1,
    o2.opportunity_id AS opp2,
    o1.amount,
    o1.stage AS stage1,
    o2.stage AS stage2,
    o1.close_date AS close1,
    o2.close_date AS close2
FROM opportunities o1
JOIN opportunities o2 ON o1.account_id = o2.account_id 
    AND o1.opportunity_id < o2.opportunity_id
    AND ABS(o1.amount - o2.amount) < 1000
JOIN accounts a ON o1.account_id = a.account_id
WHERE o1.stage NOT IN ('Closed Won', 'Closed Lost')
  AND o2.stage NOT IN ('Closed Won', 'Closed Lost');


SELECT 
    'Missing Product' AS issue_type,
    COUNT(*) AS count
FROM opportunities
WHERE product_id IS NULL AND stage NOT IN ('Closed Lost')
UNION ALL
SELECT 
    'Past Close Date in Open Stage' AS issue_type,
    COUNT(*)
FROM opportunities
WHERE close_date < CURRENT_DATE AND stage NOT IN ('Closed Won', 'Closed Lost')
UNION ALL
SELECT 
    'Zero Amount' AS issue_type,
    COUNT(*)
FROM opportunities
WHERE amount = 0;
