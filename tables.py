import re
from typing import Union

from sql_adapter import Adapter
from data_matrix import DataMatrixReader


class Table:
    def __init__(self, adapter: Adapter, table_name: str, column_names: Union[list, tuple],
                 column_headings: Union[list, tuple], var_attrs_indexes: Union[tuple, list] = None,
                 related_table=None,
                 var_attrs_indexes_from_rel_table: Union[tuple, list] = None):

        self.var_attrs_indexes_from_rel_table = var_attrs_indexes_from_rel_table
        self.var_attrs_indexes = var_attrs_indexes
        self.column_headings = column_headings
        self.column_names = column_names
        self.related_table = related_table
        self.adapter = adapter
        self.table_name = table_name
        self.columns_var_attrs = self._fill_column_unique_attrs()

    def _fill_column_unique_attrs(self):
        columns_var_attrs = {}
        if not self.var_attrs_indexes:
            return
        for i in self.var_attrs_indexes:
            column = self.column_names[i]
            columns_var_attrs[column] = [item[0] for item in
                                         self.adapter.select(self.table_name, (column,), distinct=True,
                                                             conditions=f'{column} IS NOT NULL')]
        if not self.var_attrs_indexes_from_rel_table:
            return columns_var_attrs
        for i in self.var_attrs_indexes_from_rel_table:
            column = self.column_names[i[0]]
            rel_column = self.related_table.column_names[i[1]]
            columns_var_attrs[column] = [item[0] for item in
                                         self.adapter.select(self.related_table.table_name, (rel_column,),
                                                             distinct=True,
                                                             conditions=f'{rel_column} IS NOT NULL')]
        return columns_var_attrs

    def edit_one(self, column_name: str, value, rec_id: str):
        return self.adapter.update(self.table_name, column_name, value, rec_id, self.column_names[0])

    def edit_all(self, column_name: str, value):
        return self.adapter.update(self.table_name, column_name, value)

    def select_last(self, column_name: str):
        return self.adapter.select(self.table_name, order=(False, column_name), limit=1)[0]

    def select_last_id(self):
        return self.select_last(self.column_names[0])

    def add(self, data_list: Union[list, tuple]):
        return self.adapter.insert(self.table_name, data_list)

    def remove(self, attr: str, value: str):
        self.adapter.delete(self.table_name, attr, value)

    def select_all(self):
        return self.adapter.select(self.table_name)

    def find_id(self, attrs: Union[list, tuple]):
        conditions = ''
        for i, attr in enumerate(attrs):
            if re.match('\d{4}-\d{2}-\d{2}', attr):
                conditions += f"{self.column_names[i + 1]} = '{attr}'"
            elif re.match('\d+', attr):
                conditions += f"{self.column_names[i + 1]} = {attr}"
            else:
                conditions += f"{self.column_names[i + 1]} = '{attr}'"
            if i < len(attrs) - 1:
                conditions += ' AND '
        return self.adapter.select(self.table_name, (self.column_names[0],), conditions=conditions,limit=1)[0][0]

    def select_columns(self, columns: tuple):
        return self.adapter.select(self.table_name, columns)

    def select_where(self, columns: tuple, conditions: str):
        return self.adapter.select(self.table_name, columns, conditions=conditions)

    def update_var_attrs(self, values: Union[list, tuple]):
        for i in range(1, len(self.column_names)):
            column = self.column_names[i]
            if column in self.columns_var_attrs and values[i - 1] \
                    not in self.columns_var_attrs[column]:
                self.columns_var_attrs[column].append(values[i - 1])


class EmployeesTable(Table):
    def __init__(self, adapter: Adapter):
        super().__init__(adapter, 'employees',
                         ('employee_id', 'employee_name'),
                         ('ID', 'Имя'), var_attrs_indexes=[1]
                         )

    def add(self, data_list):
        return self.adapter.insert(self.table_name, data_list,
                                   column_order=self.column_names[1:])

    def name_to_id(self, employee_name):
        if not employee_name:
            raise NameError
        res_id = self.select_where((self.column_names[0],), f"{self.column_names[1]} = '{employee_name}'")
        if not res_id:
            self.add((employee_name,))
            self.update_var_attrs((employee_name,))
            res_id = self.select_where((self.column_names[0],), f"{self.column_names[1]} = '{employee_name}'")
        return res_id[0][0]

    def id_to_name(self, employee_id):
        return self.select_where((self.column_names[1],), f"{self.column_names[0]} = '{employee_id}'")[0][0]


class ProductsTable(Table):
    def __init__(self, adapter: Adapter, related_table: EmployeesTable):
        super().__init__(adapter, 'products',
                         ('product_id', 'product_size', 'product_type', 'product_subtype', 'product_color',
                          'product_date_stored', 'laid_by', 'rolled_by'),
                         ('ID', 'Размер', 'Тип', 'Подтип', 'Цвет', 'Дата', 'Закл', 'Катка'),
                         var_attrs_indexes=[1, 2, 3, 4],
                         var_attrs_indexes_from_rel_table=[(6, 1), (7, 1)],
                         related_table=related_table)

    def add(self, data_list):
        DataMatrixReader.create_matrix(data_list)
        return self.adapter.insert(self.table_name, data_list,
                                   column_order=self.column_names[1:])

    def select_all(self):
        data = self.adapter.select(self.table_name)
        res_data = []
        for rec in data:
            rec = self.emp_id_to_name(rec)
            res_data.append(rec)
        return res_data

    def select_last_id(self):
        data = self.select_last(self.column_names[0])
        self.emp_id_to_name(data)
        return data

    def emp_name_to_id(self, data: Union[tuple, list]):
        if type(data) == tuple:
            data = [i for i in data]
        if len(data) == 8:
            data[6] = self.related_table.name_to_id(data[6])
            data[7] = self.related_table.name_to_id(data[7])
        elif len(data) == 7:
            data[5] = self.related_table.name_to_id(data[5])
            data[6] = self.related_table.name_to_id(data[6])
        return data

    def emp_id_to_name(self, data: Union[tuple, list]):
        if type(data) == tuple:
            data = [i for i in data]
        if len(data) == 8:
            data[6] = self.related_table.id_to_name(data[6])
            data[7] = self.related_table.id_to_name(data[7])
        elif len(data) == 7:
            data[5] = self.related_table.id_to_name(data[5])
            data[6] = self.related_table.id_to_name(data[6])
        return data
