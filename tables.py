import datetime

from data_matrix import DataMatrixReader
from misc import TypeIdentifier
from sql_adapter import *


class TableException(Exception):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text


class ProdTableEditIdException(TableException):
    def __init__(self):
        super().__init__('ОШИБКА: Менять ID товара запрещено')


class ProdTableAttrNotFoundException(TableException):
    def __init__(self, value=None):
        super().__init__(
            f"ОШИБКА: Значение {value if value else ''} отсутствует в таблице аттрибутов или в таблице сотрудников.")


class ProdTableMatrixNotFoundWarning(TableException):
    def __init__(self):
        super().__init__(
            f"ПРЕДУПРЕЖДЕНИЕ: Матрица не найдена. Запись удалена.")


class EmpTableValUsedInOtherTable(TableException):
    def __init__(self):
        super().__init__(f"ОШИБКА: Имя сотрудника используется в другой таблице")


class Table:
    def __init__(self, adapter: Adapter, table_name: str, column_names: Union[list, tuple],
                 column_headings: Union[list, tuple], p_key_column_name: str, var_attrs=None,
                 attr_tables: Union[list, tuple] = None, date_column: str = None):
        self.date_column = date_column
        self.attr_tables = attr_tables
        self.p_key_column_name = p_key_column_name
        if var_attrs is None:
            var_attrs = []
        self.var_attrs = var_attrs
        self.column_headings = column_headings
        self.column_names = column_names
        self.adapter = adapter
        self.table_name = table_name

    def _fill_attr_tables(self):
        """Create tables with attributes,
            KEEP THE COLUMN ORDER FROM __init__
        """
        pass

    def rollback(self):
        self.adapter.rollback()

    def commit(self):
        self.adapter.commit()

    def edit(self, column_name: str, value, rec_id: str):
        self.adapter.update(self.table_name, column_name, value, rec_id, self.column_names[0])

    def add(self, data_list: Union[list, tuple], if_not_exist: bool = False):
        self.adapter.insert(self.table_name, data_list, if_not_exist=if_not_exist)

    def remove(self, attr: str, value: str):
        self.adapter.delete(self.table_name, attr, value)

    def select_all(self):
        try:
            data = self.adapter.select(self.table_name)
        except AdapterRecNotExistException:
            print('Warning: DB is empty')
            return []
        self.commit()
        return data

    def select_columns(self, columns: tuple):
        try:
            data = self.adapter.select(self.table_name, columns)
        except AdapterRecNotExistException:
            print('Warning: DB is empty')
            return []
        self.commit()
        return data

    def select_id(self, rec_id: str, columns: tuple):
        data = self.adapter.select(self.table_name, columns=columns, conditions=f'{self.column_names[0]} = {rec_id}')[0]
        self.commit()
        return data

    def select_by_date(self, date_start, date_end):
        data = \
            self.adapter.select(self.table_name,
                                conditions=f"{self.date_column} BETWEEN '{date_start}' AND '{date_end}'")
        self.commit()
        res_data = []
        for rec in data:
            res_data.append([TypeIdentifier.identify_parse(val) for val in rec])
        return res_data

    def update_var_attrs(self):
        self.select_all()


class AttrTable(Table):
    def __init__(self, adapter: Adapter, table_name: str, column_name: str, heading: str):
        super().__init__(adapter, table_name, (column_name,), (heading,), column_name)
        self.update_var_attrs()

    def add(self, data: Union[tuple, list], if_not_exist=True):
        self.adapter.insert(self.table_name, data, if_not_exist=if_not_exist)

    def update_var_attrs(self):
        self.var_attrs = [self.select_all()]


class EmployeesTable(AttrTable):
    def __init__(self, adapter: Adapter):
        super().__init__(adapter, 'employees',
                         'employee_name',
                         'Имя')

    def remove(self, attr: str, value: str):
        try:
            super().remove(attr, value)
        except AdapterFKException:
            raise EmpTableValUsedInOtherTable

    def edit(self, column_name: str, value, rec_id: str):
        try:
            super().edit(column_name, value, rec_id)
        except AdapterFKException:
            raise EmpTableValUsedInOtherTable


class SalaryPerSizeTable(Table):
    def __init__(self, adapter: Adapter):
        super().__init__(adapter, 'salary_per_size',
                         ('size', 'salary'),
                         ('Размер', 'Оплата'),
                         'size')
        self.attr_tables = self._fill_attr_tables()
        self.update_var_attrs()

    def _fill_attr_tables(self):
        attr_tables = [AttrTable(self.adapter, 'products_sizes', 'sizes', 'Размеры')]
        return attr_tables

    def update_var_attrs(self):
        self.var_attrs.clear()
        for attr in self.attr_tables:
            self.var_attrs.append(attr.select_all())
        self.var_attrs.append(self.select_columns(('salary',)))


class ProductsTable(Table):
    def __init__(self, adapter: Adapter):
        super().__init__(adapter, 'products',
                         ('product_id', 'product_size', 'product_type', 'product_subtype', 'product_color',
                          'product_date_stored', 'laid_by', 'rolled_by'),
                         ('ID', 'Размер', 'Тип', 'Подтип', 'Цвет', 'Дата', 'Закл', 'Катка'),
                         'product_id', date_column='product_date_stored')
        self.attr_tables = self._fill_attr_tables()
        self.update_var_attrs()

    def _fill_attr_tables(self):
        attr_tables = [AttrTable(self.adapter, 'products_sizes', 'sizes', 'Размеры'),
                       AttrTable(self.adapter, 'products_types', 'types', 'Типы'),
                       AttrTable(self.adapter, 'products_subtypes', 'subtypes', 'Подтипы'),
                       AttrTable(self.adapter, 'products_colors', 'colors', 'Цвета'),
                       AttrTable(self.adapter, 'employees', 'employees', 'Сотрудники')]
        return attr_tables

    def next_id(self):
        return self.adapter.next_sequence('products_product_id_seq')

    def cur_id(self):
        return self.adapter.cur_sequence('products_product_id_seq')

    def add_to_attrs_tables(self, data_list):
        if not data_list[3]:
            data_list[3] = 'Пусто'
        for i, table in enumerate(self.attr_tables):
            self.attr_tables[i].add((data_list[i + 1],))
        self.attr_tables[-1].add((data_list[7],), if_not_exist=True)

    def add(self, data_list, if_not_exist=False):
        if data_list[3] == 'Пусто':
            data_list[3] = None
        try:
            self.adapter.insert(self.table_name, data_list)
        except AdapterFKException:
            raise ProdTableAttrNotFoundException()

    def select_matrix(self, rec_id):
        return self.select_id(rec_id, ('matrix_dir',))

    def remove(self, attr: str, value: str):
        matrix_path = self.select_matrix(value)[0]
        try:
            DataMatrixReader.delete_matrix(matrix_path)
        except FileNotFoundError:
            super().remove(attr, value)
            raise ProdTableMatrixNotFoundWarning
        super().remove(attr, value)

    def select_all(self):
        data = super().select_all()
        res_data = []
        for rec in data:
            res_data.append([TypeIdentifier.identify_parse(val) for val in rec])
        return res_data

    def select_all_not_sold(self):
        data = super().select_all()
        res_data = []
        for rec in data:
            if not rec[-1]:
                res_data.append([TypeIdentifier.identify_parse(val) for val in rec])
        return res_data

    def edit(self, column_name: str, value, rec_id: str):
        if column_name == self.column_names[0]:
            raise ProdTableEditIdException
        try:
            super().edit(column_name, value, rec_id)
        except AdapterFKException:
            raise ProdTableAttrNotFoundException(value)

    def update_var_attrs(self):
        self.var_attrs.clear()
        try:
            self.var_attrs.append(self.cur_id())
        except AdapterException:
            self.rollback()
            self.var_attrs.append(self.next_id())
        for i in range(len(self.attr_tables) - 1):
            self.var_attrs.append(self.attr_tables[i].select_all())

        date = [(datetime.date.today().strftime('%d.%m.%Y'),)]
        employees = self.attr_tables[-1].select_all()
        self.var_attrs.append(date)
        self.var_attrs.append(employees)
        self.var_attrs.append(employees)
