import psycopg2

conn = psycopg2.connect(dbname="testdb", user="postgres", password="12345")

cur = conn.cursor()


cur.execute('''
CREATE TABLE IF NOT EXISTS employees
(
    employee_id INT GENERATED ALWAYS AS IDENTITY,
    employee_name VARCHAR,
    PRIMARY KEY(employee_id)
);
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS products
(
    product_id INT GENERATED ALWAYS AS IDENTITY,
    product_size INT,
    product_type VARCHAR,
    product_subtype VARCHAR,
    product_color VARCHAR,
    product_date_stored DATE,
    laid_by INT, 	
    rolled_by INT,
    article VARCHAR,
    PRIMARY KEY(product_id),
    CONSTRAINT fk_laid_id
        FOREIGN KEY(laid_by) 
        REFERENCES employees(employee_id),
    CONSTRAINT fk_rolled_id
        FOREIGN KEY(rolled_by) 
        REFERENCES employees(employee_id)
);'''
            )
conn.commit()
