import psycopg2


class Adapter:
    def __init__(self, dbname: str, user='postgres', password='12345'):
        self.con = psycopg2.connect(dbname=dbname, user=user, password=password)
        self.cur = self.con.cursor()

    def add_employee(self, name: str):
        self.cur.execute("INSERT INTO employees (Имя_работника) VALUES (%s)", (name,))
        self.con.commit()

    def add_product(self, data_list: list):
        self.cur.execute(
            "INSERT INTO products(Размер_продукта,Дата_поступления_на_склад, Закладка,"
            "Катка ,Артикл, Тип_продукта,Подтип_продукта,Цвет_продукта)"
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", data_list
        )
        self.con.commit()

    def close(self):
        self.con.close()
        self.cur.close()

    def remove_product(self, product_id):
        self.cur.execute(
            "DELETE FROM products WHERE product_id = (%s)", (product_id,)
        )
        self.con.commit()

    def fetch_column_names(self, table_name):
        self.cur.execute('''
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME=%s AND NOT COLUMN_NAME LIKE '%%id%%'
        ''', (table_name,))
        fetched_data = self.cur.fetchall()
        self.con.commit()
        columns = []
        for data in fetched_data:
            column_name = data[0]
            query = f'''
            SELECT DISTINCT {column_name}
            FROM {table_name}
            '''
            mogrified_query = self.cur.mogrify(query)
            self.cur.execute(mogrified_query)
            column_values = self.cur.fetchall()
            columns.append((column_name, [item[0] for item in column_values]))
        self.con.commit()
        return columns
