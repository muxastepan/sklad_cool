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

    def select(self, table_name, columns: Union[list, tuple] = None, distinct=False, conditions: str = None):
        if columns:
            columns_placeholder = ','.join(columns)
        else:
            columns_placeholder = '*'
        if distinct:
            distinct_placeholder = ' DISTINCT'
        else:
            distinct_placeholder = ''
        if conditions:
            conditions_placeholder = f' WHERE {conditions}'
        else:
            conditions_placeholder = f''
        self.cur.execute(
            f"SELECT{distinct_placeholder} {columns_placeholder} FROM {table_name}{conditions_placeholder}")
        data = self.cur.fetchall()
        self.con.commit()
        return data

    def delete(self, table_name: str, column_name: str, column_value: str):
        self.cur.execute(
            f"DELETE FROM {table_name} WHERE {column_name} = (%s)", (column_value,)
        )
        self.con.commit()


class Table:
    def __init__(self, adapter: Adapter, table_name: str, column_unique_attrs: Dict[str, list]):
        self.column_unique_attrs = column_unique_attrs
        self.table_name = table_name
        self.adapter = adapter

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

    def update_unique_attrs(self, values: Union[list,tuple]):
        i = 0
        for attr, old_values in self.column_unique_attrs.items():
            if values[i] not in old_values:
                old_values.append(values[i])
            i += 1


class ProductsTable(Table):
    def __init__(self, adapter: Adapter):
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
                         })

    def add(self, data_list):
        self.adapter.insert(self.table_name, data_list,
                            column_order="(product_size,product_type, product_subtype,product_color,"
                                         "product_date_stored, laid_by,rolled_by,article)")


class EmployeesTable(Table):
    def __init__(self, adapter: Adapter):
        super().__init__(adapter, 'employees',
                         column_unique_attrs={
                             'employee_name':
                                 [item[0] for item in
                                  adapter.select('employees', ('employee_name',), distinct=True)],
                         }
                         )

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
