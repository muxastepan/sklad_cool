import tkinter as tk
from tkinter import ttk
from typing import Union
import re
from sql_adapter import Adapter, ProductsTable, EmployeesTable
import datetime


class DataGridView(tk.Frame):
    def __init__(self, column_names: Union[list, tuple], data):
        super().__init__()

        self.column_names = column_names
        self.data = data
        self.scroll_bar = tk.Scrollbar(self)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table = ttk.Treeview(self)
        self.scroll_bar.configure(command=self.table.yview)
        self._build_table()
        self.table.pack()

    def sort_data(self, col, reverse):
        data = [(self.table.set(child, col), child) for child in self.table.get_children('')]
        data_vals = [x[0] for x in data]

        if all(re.match('\d{4}-\d{2}-\d{2}', i) for i in data_vals):
            data.sort(reverse=reverse, key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d'))
        elif all(re.match('\d+', i) for i in data_vals):
            data.sort(reverse=reverse, key=lambda x: int(x[0]))
        else:
            data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            self.table.move(child, '', index)

        self.table.heading(col, command=lambda: self.sort_data(col, not reverse))

    def _build_table(self):
        self.table['columns'] = self.column_names
        self.table.column('#0', width=0, stretch=tk.NO)
        for i, heading in enumerate(self.column_names):
            self.table.column(heading, anchor=tk.W, width=100)
            self.table.heading(heading, text=heading, anchor=tk.W,
                               command=lambda col=heading: self.sort_data(col, False))

        self._row_count = 0
        for row in self.data:
            self.table.insert('', tk.END, values=row)
            self._row_count += 1

    def add_row(self, data):
        self._row_count += 1
        self.table.insert('', tk.END, values=data[0])


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


class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()

        self.sql_adapter = Adapter('testdb')
        self.employees_table = EmployeesTable(self.sql_adapter)
        self.product_table = ProductsTable(self.sql_adapter, self.employees_table)
        self.add_product_button = tk.Button(text='Добавить продукт', command=self.show_add_product_dialogue)
        self.add_employee_button = tk.Button(text='Добавить сотрудника', command=self.show_add_employee_dialogue)
        data_for_grid = self.product_table.select_all()
        self.data_grid = DataGridView(('ID', 'Размер', 'Тип', 'Подтип', 'Цвет', 'Дата', 'Закл', 'Катка', 'Артикул'),
                                      self.product_table.select_all())
        # self.show_db_button = tk.Button(text='show', command=self.show_db)

    def show_db(self):
        self.data_grid.add_row(self.product_table.select_last_id())

    def show_add_product_dialogue(self):
        add_window = AddProductRecordDialogue(self, self.product_table, self.employees_table)
        add_window.show()

    def show_add_employee_dialogue(self):
        add_window = AddEmployeeRecordDialogue(self, self.employees_table)
        add_window.show()

    def run(self):
        self.add_product_button.grid(row=0, column=0, sticky=tk.EW)
        self.add_employee_button.grid(row=0, column=1, sticky=tk.EW)
        # self.show_db_button.grid(row=0, column=2, sticky=tk.EW)
        self.data_grid.grid(row=1, column=0, columnspan=2, sticky=tk.NS)
        self.mainloop()


class AddProductRecordDialogue(tk.Toplevel):
    def __init__(self, parent: MainFrame, products_table: ProductsTable, employees_table: EmployeesTable):
        super().__init__()
        self.parent = parent
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
        data = [
            size,
            p_type,
            p_subtype,
            color,
            date,
            laid_by,
            rolled_by,
            article
        ]
        self.products_table.add(data)
        self.products_table.update_unique_attrs(data[:4])
        self.parent.data_grid.add_row(self.products_table.select_last_id())
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
    def __init__(self, parent: MainFrame, employees_table: EmployeesTable):
        super().__init__()
        self.parent = parent
        self.employees_table = employees_table
        self.submit_button = tk.Button(self, text='Отправить', command=self.submit_close)
        self.name_entry = AutoCompletionCombobox(self, values=employees_table.column_unique_attrs['employee_name'])

    def submit_close(self):
        data_list = [
            self.name_entry.get()
        ]
        self.employees_table.add(data_list)
        self.parent.data_grid.add_row(self.employees_table.select_last_id())
        self.destroy()

    def show(self):
        tk.Label(self, text='Имя').pack()
        self.name_entry.pack()
        self.submit_button.pack()


if __name__ == '__main__':
    app = MainFrame()
    app.run()
