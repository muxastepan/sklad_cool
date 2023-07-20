import psycopg2


class Adapter:
    def __init__(self, dbname: str, user='postgres', password='12345'):
        self.con = psycopg2.connect(dbname=dbname, user=user, password=password)
        self.cur = self.con.cursor()

    def add_employee(self, name: str):
        self.cur.execute("INSERT INTO employees (employee_name) VALUES (%s)", (name,))
        self.con.commit()

    def add_product(self, data_list: list):
        self.cur.execute(
            "INSERT INTO products(product_size,product_type, product_subtype,"
            "product_color ,product_date_storaged, laid_by,rolled_by,article)"
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", data_list
        )
        self.con.commit()

    def close(self):
        self.con.close()
        self.cur.close()

    def remove_employee(self, employee_id):
        self.cur.execute(
            "DELETE FROM employees WHERE employee_id = (%s)", (employee_id,)
        )
        self.con.commit()

    def remove_product(self, product_id):
        self.cur.execute(
            "DELETE FROM products WHERE product_id = (%s)", (product_id,)
        )
        self.con.commit()

    def unique_values_from_products(self, column):
        self.cur.execute('''
        SELECT DISTINCT %s FROM products
        ''', (column,))
        self.con.commit()

    def unique_values_from_employees(self, column):
        self.cur.execute('''
        SELECT DISTINCT %s FROM employees
        ''', (column,))
        self.con.commit()


