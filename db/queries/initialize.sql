CREATE TABLE IF NOT EXISTS livechat_data (
    id SERIAL PRIMARY KEY,
    datetime TIMESTAMP,
    author_name VARCHAR(255),
    message TEXT,
    amount_value NUMERIC
);

-- Insert sample data into the transactions table
INSERT INTO livechat_data (datetime, author_name, message, amount_value) VALUES
('2024-08-08 12:00:00', 'John Doe', 'Hello',100.00),
('2024-08-08 13:00:00', 'Jane Smith', 'Hello',150.50),
('2024-08-08 14:00:00', 'Alice Johnson', 'This is hello',200.75),
('2024-08-08 15:00:00', 'Bob Brown','this is crazy' ,50.25),
('2024-08-08 15:00:00', 'Bob Brown','this is crazy' , 0);

