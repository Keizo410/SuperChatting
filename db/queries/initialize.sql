 CREATE TABLE transactions (
            id SERIAL PRIMARY KEY,
            transaction_time TIMESTAMP,
            name VARCHAR(255),
            amount NUMERIC(10, 2)
            );


-- Insert sample data into the transactions table
INSERT INTO transactions (transaction_time, name, amount) VALUES
('2024-08-08 12:00:00', 'John Doe', 100.00),
('2024-08-08 13:00:00', 'Jane Smith', 150.50),
('2024-08-08 14:00:00', 'Alice Johnson', 200.75),
('2024-08-08 15:00:00', 'Bob Brown', 50.25);
