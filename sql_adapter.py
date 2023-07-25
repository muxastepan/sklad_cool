from typing import Union
import psycopg2


class Adapter:
    def __init__(self, dbname: str, user='postgres', password='12345'):
        self.con = psycopg2.connect(dbname=dbname, user=user, password=password)
        self.cur = self.con.cursor()

    def insert(self, table_name: str, data_list: Union[list, tuple], column_order: tuple = None):
        values_placeholder = f"({'%s,' * (len(data_list) - 1) + '%s'})"
        if not column_order:
            column_order_placeholder = ''
        else:
            if len(column_order) == 1:
                column_order_placeholder = f"({column_order[0]}) "
            else:
                column_order_placeholder = f"({','.join(column_order)}) "
        try:
            self.cur.execute(f"INSERT INTO {table_name} {column_order_placeholder}VALUES {values_placeholder}", data_list)
        except psycopg2.Error as ex:
            print(ex)
            self.con.rollback()
            return False
        self.con.commit()
        return True

    def select(self, table_name, columns: Union[list, tuple] = None, distinct=False, conditions: str = None,
               order: Union[list, tuple] = None, limit=None):
        query = "SELECT "
        if distinct:
            query += 'DISTINCT '
        if columns:
            query += ','.join(columns) + ' '
        else:
            query += '* '

        query += f'FROM {table_name}'

        if conditions:
            query += f' WHERE {conditions}'

        if order:
            query += f' ORDER BY {order[1]}'
            if order[0]:
                query += ' ASC'
            else:
                query += ' DESC'
        if limit:
            query += f' LIMIT {limit}'
        self.cur.execute(query)
        data = self.cur.fetchall()
        self.con.commit()
        return data

    def delete(self, table_name: str, column_name: str, column_value: str):
        self.cur.execute(
            f"DELETE FROM {table_name} WHERE {column_name} = (%s)", (column_value,)
        )
        self.con.commit()

    def update(self, table_name: str, column_name: str, column_value: str, rec_id: str = None,
               column_id_name: str = None):
        query = f"UPDATE {table_name} SET {column_name}=%s"
        if rec_id and column_id_name:
            query += f" WHERE {column_id_name} = {rec_id}"
        try:
            self.cur.execute(query, (column_value,))
        except psycopg2.Error as ex:
            print(ex)
            self.con.rollback()
            return False
        self.con.commit()
        return True
