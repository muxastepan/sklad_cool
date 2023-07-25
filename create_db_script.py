import psycopg2

conn = psycopg2.connect(dbname="testdb", user="postgres", password="12345")

cur = conn.cursor()


cur.execute('''
CREATE TABLE IF NOT EXISTS employees
(
    employee_id INT GENERATED ALWAYS AS IDENTITY,
    employee_name VARCHAR NOT NULL,
    PRIMARY KEY(employee_id)
);
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS products
(
    product_id INT GENERATED ALWAYS AS IDENTITY,
    product_size INT NOT NULL,
    product_type VARCHAR NOT NULL,
    product_subtype VARCHAR,
    product_color VARCHAR NOT NULL,
    product_date_stored DATE NOT NULL,
    laid_by INT NOT NULL, 	
    rolled_by INT NOT NULL,
    article VARCHAR NOT NULL,
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
