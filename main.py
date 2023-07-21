import re
import tkinter as tk
from abc import ABC
from tkinter import ttk
from typing import Union

from sql_adapter import Adapter, ProductsTable, EmployeesTable
import datetime


class DataGridView:
    def __init__(self, column_names: Union[list, tuple]):
        self.name_labels, self.value_entries = self._build(column_names)

    def _build(self, column_names):
        name_labels = []
        value_entries = []
        for name in column_names:
            name_labels.append(tk.Label(text=name))
            value_entries.append(tk.Entry())
        return name_labels, value_entries

    def show(self):
        for i in range(len(self.name_labels)):
            self.name_labels[i].grid(row=1, column=i)
            self.value_entries[i].grid(row=2, column=i)


class AutoCompletionCombobox(ttk.Combobox):
    def __init__(self, root, values=None):
        super().__init__(root, values=values)
        self.bind('<KeyRelease>', self.check_input)
        self.bind('<FocusIn>', self.check_input)
        self.old_values = self['values']

    def check_input(self, event):
        value = self.get()

        if value != '':
            data = []
            for item in self.old_values:
                if value in item:
                    data.append(item)
            self['values'] = data


class AddProductRecordDialogue(tk.Toplevel):
    def __init__(self, products_table: ProductsTable, employees_table: EmployeesTable):
        super().__init__()
        self.employees_table = employees_table
        self.products_table = products_table
        self.submit_button = tk.Button(self, text='Отправить', command=self.submit_close)
        self.size_entry = AutoCompletionCombobox(self, values=self.products_table.column_unique_attrs['product_size'])
        self.type_entry = AutoCompletionCombobox(self, values=self.products_table.column_unique_attrs['product_type'])
        self.subtype_entry = AutoCompletionCombobox(self,
                                                    values=self.products_table.column_unique_attrs['product_subtype'])
        self.color_entry = AutoCompletionCombobox(self, values=self.products_table.column_unique_attrs['product_color'])
        self.date_entry = tk.Entry(self)
        self.date_entry.insert(0, str(datetime.datetime.now().date()))
        self.laid_by_entry = AutoCompletionCombobox(self,
                                                    values=self.employees_table.column_unique_attrs['employee_name'])
        self.rolled_by_entry = AutoCompletionCombobox(self,
                                                      values=self.employees_table.column_unique_attrs['employee_name'])
        self.article_entry = ttk.Entry(self)

    def submit_close(self):
        size = self.size_entry.get()
        p_type = self.type_entry.get()
        p_subtype = self.subtype_entry.get()
        color = self.color_entry.get()
        date = self.date_entry.get()
        laid_by = self.employees_table.name_to_id(self.laid_by_entry.get())
        rolled_by = self.employees_table.name_to_id(self.rolled_by_entry.get())
        article = self.article_entry.get()
        data_list = [
            size,
            p_type,
            p_subtype,
            color,
            date,
            laid_by,
            rolled_by,
            article
        ]
        self.products_table.add(data_list)
        self.products_table.update_unique_attrs(data_list[:4])
        self.destroy()

    def show(self):
        tk.Label(self, text='Размер').pack()
        self.size_entry.pack()
        tk.Label(self, text='Тип').pack()
        self.type_entry.pack()
        tk.Label(self, text='Подтип').pack()
        self.subtype_entry.pack()
        tk.Label(self, text='Цвет').pack()
        self.color_entry.pack()
        tk.Label(self, text='Дата поступления на склад').pack()
        self.date_entry.pack()
        tk.Label(self, text='Закладка').pack()
        self.laid_by_entry.pack()
        tk.Label(self, text='Катка').pack()
        self.rolled_by_entry.pack()
        tk.Label(self, text='Артикул').pack()
        self.article_entry.pack()

        self.submit_button.pack()


class AddEmployeeRecordDialogue(tk.Toplevel):
    def __init__(self, employees_table: EmployeesTable):
        super().__init__()
        self.employees_table = employees_table
        self.submit_button = tk.Button(self, text='Отправить', command=self.submit_close)
        self.name_entry = AutoCompletionCombobox(self, values=employees_table.column_unique_attrs['employee_name'])

    def submit_close(self):
        data_list = [
            self.name_entry.get()
        ]
        self.employees_table.add(data_list)
        self.destroy()

    def show(self):
        tk.Label(self, text='Имя').pack()
        self.name_entry.pack()
        self.submit_button.pack()


class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sql_adapter = Adapter('testdb')
        self.product_table = ProductsTable(self.sql_adapter)
        self.employees_table = EmployeesTable(self.sql_adapter)
        self.add_product_button = tk.Button(text='Добавить продукт', command=self.show_add_product_dialogue)
        self.add_employee_button = tk.Button(text='Добавить сотрудника', command=self.show_add_employee_dialogue)
        self.add_window = None
        self.data_grid = DataGridView(('Размер', 'Тип', 'Подтип', 'Цвет', 'Дата', 'Закл', 'Катка', 'Артикул'))

    def show_add_product_dialogue(self):
        self.add_window = AddProductRecordDialogue(self.product_table, self.employees_table)
        self.add_window.show()

    def show_add_employee_dialogue(self):
        self.add_window = AddEmployeeRecordDialogue(self.employees_table)
        self.add_window.show()

    def run(self):
        self.add_product_button.grid(row=0, column=0, sticky=tk.EW)
        self.add_employee_button.grid(row=0, column=1, sticky=tk.EW)
        self.data_grid.show()
        self.mainloop()


if __name__ == '__main__':
    app = MainFrame()
    app.run()
