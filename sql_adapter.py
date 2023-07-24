from typing import Union, Dict

import psycopg2


class Adapter:
    def __init__(self, dbname: str, user='postgres', password='12345'):
        self.con = psycopg2.connect(dbname=dbname, user=user, password=password)
        self.cur = self.con.cursor()

    def insert(self, table_name: str, data_list: Union[list, tuple], column_order: str = None):
        values_placeholder = f"({'%s,' * (len(data_list) - 1) + '%s'})"
        if not column_order:
            column_order_placeholder = ''
        else:
            column_order_placeholder = column_order + ' '
        self.cur.execute(f"INSERT INTO {table_name} {column_order_placeholder}VALUES {values_placeholder}", data_list)
        self.con.commit()

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


class Table:
    def __init__(self, adapter: Adapter, table_name: str, column_unique_attrs: Dict[str, list], related_table=None):
        self.related_table = related_table
        self.column_unique_attrs = column_unique_attrs
        self.table_name = table_name
        self.adapter = adapter

    def select_last(self, column_name):
        return self.adapter.select(self.table_name, order=(False, column_name), limit=1)

    def add(self, data_list):
        self.adapter.insert(self.table_name, data_list)

    def remove(self, attr: str, value: str):
        self.adapter.delete(self.table_name, attr, value)

    def select_all(self):
        return self.adapter.select(self.table_name)

    def select_columns(self, columns: tuple):
        return self.adapter.select(self.table_name, columns)

    def select_where(self, columns: tuple, conditions: str):
        return self.adapter.select(self.table_name, columns, conditions=conditions)

    def update_unique_attrs(self, values: Union[list, tuple]):
        i = 0
        for attr, old_values in self.column_unique_attrs.items():
            if values[i] not in old_values:
                old_values.append(values[i])
            i += 1


class EmployeesTable(Table):
    def __init__(self, adapter: Adapter):
        super().__init__(adapter, 'employees',
                         column_unique_attrs={
                             'employee_name':
                                 [item[0] for item in
                                  adapter.select('employees', ('employee_name',), distinct=True)],
                         }
                         )

    def select_last_id(self):
        self.select_last('employee_id')

    def add(self, data_list):
        self.adapter.insert(self.table_name, data_list,
                            column_order="(employee_name)")

    def name_to_id(self, employee_name):
        res_id = self.select_where(('employee_id',), f"employee_name = '{employee_name}'")
        if not res_id:
            self.add((employee_name,))
            self.update_unique_attrs((employee_name,))
            res_id = self.select_where(('employee_id',), f"employee_name = '{employee_name}'")
        return res_id[0]

    def id_to_name(self, employee_id):
        return self.select_where(('employee_name',), f"employee_id = '{employee_id}'")[0]


class ProductsTable(Table):
    def __init__(self, adapter: Adapter, related_table: EmployeesTable):
        super().__init__(adapter, 'products',
                         column_unique_attrs={
                             'product_size':
                                 [item[0] for item in
                                  adapter.select('products', ('product_size',), distinct=True)],
                             'product_type':
                                 [item[0] for item in
                                  adapter.select('products', ('product_type',), distinct=True)],
                             'product_subtype':
                                 [item[0] for item in
                                  adapter.select('products', ('product_subtype',), distinct=True)],
                             'product_color':
                                 [item[0] for item in
                                  adapter.select('products', ('product_color',), distinct=True)]
                         },
                         related_table=related_table)

    def add(self, data_list):
        self.adapter.insert(self.table_name, data_list,
                            column_order="(product_size,product_type, product_subtype,product_color,"
                                         "product_date_stored, laid_by,rolled_by,article)")

    def select_last_id(self):
        return self.select_last('product_id')

    def select_all(self):
        data = self.adapter.select(self.table_name)
        res_data = []
        for rec in data:
            laid_by = self.related_table.id_to_name(rec[6])
            rolled_by = self.related_table.id_to_name(rec[7])
            res_rec = rec[:6] + laid_by + rolled_by + rec[8:]
            res_data.append(res_rec)
        return res_data
