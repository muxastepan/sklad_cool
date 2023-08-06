import psycopg2

conn = psycopg2.connect(dbname="testdb", user="postgres", password="12345")

cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS products_sizes
(
    sizes INT,
    PRIMARY KEY(sizes)
);'''
            )
cur.execute('''
CREATE TABLE IF NOT EXISTS products_types
(
    types VARCHAR,
    PRIMARY KEY(types),
    CONSTRAINT check_types CHECK
    (types SIMILAR TO 
    '[а-яА-Я]*')
);'''
            )
cur.execute('''
CREATE TABLE IF NOT EXISTS products_subtypes
(
    subtypes VARCHAR,
    PRIMARY KEY(subtypes),
    CONSTRAINT check_subtypes CHECK
    (subtypes SIMILAR TO 
    '[а-яА-Я]*')
);'''
            )
cur.execute('''
CREATE TABLE IF NOT EXISTS products_colors
(
    colors VARCHAR,
    PRIMARY KEY(colors),
    CONSTRAINT check_colors CHECK
    (colors SIMILAR TO 
    '[а-яА-Я]*')
    
);'''
            )
cur.execute('''
CREATE TABLE IF NOT EXISTS employees
(    
    employee_name VARCHAR NOT NULL,
    PRIMARY KEY(employee_name),
    CONSTRAINT check_name CHECK
    (employee_name SIMILAR TO 
    '[а-яА-Я]*')
    
)''')
cur.execute('''
CREATE TABLE IF NOT EXISTS products
(
    product_id SERIAL,
    product_size INT NOT NULL,
    product_type VARCHAR NOT NULL,
    product_subtype VARCHAR,
    product_color VARCHAR NOT NULL,
    product_date_stored DATE NOT NULL,
    laid_by VARCHAR NOT NULL, 	
    rolled_by VARCHAR NOT NULL,    
    PRIMARY KEY(product_id),
    CONSTRAINT fk_product_size
        FOREIGN KEY(product_size) 
        REFERENCES products_sizes(sizes),
    CONSTRAINT fk_product_type
        FOREIGN KEY(product_type) 
        REFERENCES products_types(types),
    CONSTRAINT fk_product_subtype
        FOREIGN KEY(product_subtype) 
        REFERENCES products_subtypes(subtypes),
    CONSTRAINT fk_product_color
        FOREIGN KEY(product_color) 
        REFERENCES products_colors(colors),
    CONSTRAINT fk_laid_name
        FOREIGN KEY(laid_by) 
        REFERENCES employees(employee_name),
    CONSTRAINT fk_rolled_name
        FOREIGN KEY(rolled_by) 
        REFERENCES employees(employee_name),
    CONSTRAINT check_type CHECK
    (product_type SIMILAR TO 
    '[а-яА-Я]*'),
    CONSTRAINT check_subtype CHECK
    (product_subtype SIMILAR TO 
    '[а-яА-Я]*'),
    CONSTRAINT check_color CHECK
    (product_color SIMILAR TO 
    '[а-яА-Я]*')        
);'''
            )

conn.commit()
