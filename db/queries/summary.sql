-- calculate the total amount of money for each user name
select author_name, SUM(amount_value) as total_amount
from livechat_data
group by author_name;

-- create a summary table
create table if not exists author_total (
    author_name VARCHAR(255) PRIMARY KEY,
    total_amount NUMERIC
);

-- insert the calculated data into the table
insert into author_total (author_name, total_amount)
VALUES (%s, %s) 
ON CONFLICT (author_name) DO UPDATE SET total_amount = EXCLUDED.total_amount;
