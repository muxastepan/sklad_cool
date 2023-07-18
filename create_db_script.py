import psycopg2

conn = psycopg2.connect(dbname="testdb", user="postgres", password="12345")

cur = conn.cursor()
cur.execute('''
DROP TABLE IF EXISTS employees CASCADE;
''')
cur.execute('''
DROP TABLE IF EXISTS products;
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS employees
(
    id_работника INT GENERATED ALWAYS AS IDENTITY,
    Имя_работника VARCHAR,
    PRIMARY KEY(id_работника)
);
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS products
(
    id_продукта INT GENERATED ALWAYS AS IDENTITY,
    Размер_продукта INT,
    Тип_продукта VARCHAR,
    Подтип_продукта VARCHAR,
    Цвет_продукта VARCHAR,
    Дата_поступления_на_склад DATE,
    Закладка INT, 	
    Катка INT,
    Артикл VARCHAR,
    PRIMARY KEY(id_продукта),
    CONSTRAINT fk_layed_id
        FOREIGN KEY(Закладка) 
        REFERENCES employees(id_работника),
    CONSTRAINT fk_rolled_id
        FOREIGN KEY(Катка) 
        REFERENCES employees(id_работника)
);'''
            )
conn.commit()
