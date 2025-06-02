-- Add these to your bin_status table
ALTER TABLE bin_status ADD COLUMN IF NOT EXISTS battery_level DECIMAL(5,2);
ALTER TABLE bin_status ADD COLUMN IF NOT EXISTS status VARCHAR(20);

-- Create a materialized view for dashboard data
CREATE MATERIALIZED VIEW IF NOT EXISTS bin_summary AS
SELECT 
    bin_id,
    AVG(fill_level) as avg_fill,
    MAX(temperature) as max_temp,
    COUNT(*) as readings
FROM bin_status
GROUP BY bin_id;