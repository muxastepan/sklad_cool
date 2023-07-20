import re
import tkinter as tk
from abc import ABC
from tkinter import ttk
from sql_adapter import Adapter
import datetime


class AddDBRecordDialogue(ABC):
    def __init__(self, adapter: Adapter):
        pass

    def submit_close(self):
        pass

    def show(self):
        pass


class AddProductRecordDialogue(AddDBRecordDialogue, tk.Toplevel):
    def __init__(self, adapter: Adapter):
        super().__init__()
        self.adapter = adapter
        self.submit_button = tk.Button(self, text='Отправить', command=self.submit_close)
        self.size_entry = ttk.Combobox(self, values=self.adapter.unique_values_from_products('product_size'))
        self.type_entry = ttk.Combobox(self, values=self.adapter.unique_values_from_products('product_type'))
        self.subtype_entry = ttk.Combobox(self, values=self.adapter.unique_values_from_products('product_subtype'))
        self.color_entry = ttk.Combobox(self, values=self.adapter.unique_values_from_products('product_color'))
        self.date_entry = tk.Entry(self)
        self.date_entry.insert(0, str(datetime.datetime.now().date()))
        self.laid_by_entry = ttk.Combobox(self, values=self.adapter.unique_values_from_products('laid_by'))
        self.rolled_by_entry = ttk.Combobox(self, values=self.adapter.unique_values_from_products('rolled_by'))
        self.article_entry = ttk.Combobox(self, values=self.adapter.unique_values_from_products('article'))

    def submit_close(self):
        data_list = [
            self.size_entry.get(),
            self.type_entry.get(),
            self.subtype_entry.get(),
            self.color_entry.get(),
            self.date_entry.get(),
            self.laid_by_entry.get(),
            self.rolled_by_entry.get(),
            self.article_entry.get()
        ]
        self.adapter.add_product(data_list)
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


class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sql_adapter = Adapter('testdb')
        self.add_product_button = tk.Button(text='Добавить продукт', command=self.show_add_product_dialogue)
        self.add_employee_button = tk.Button(text='Добавить сотрудника', command=self.show_add_employee_dialogue)
        self.add_window = None

    def show_add_product_dialogue(self):
        self.add_window = AddProductRecordDialogue(self.sql_adapter)
        self.add_window.show()

    def show_add_employee_dialogue(self):
        self.add_window = AddProductRecordDialogue(self.sql_adapter)
        self.add_window.show()

    def run(self):
        self.add_product_button.pack()
        self.add_employee_button.pack()
        self.mainloop()


if __name__ == '__main__':
    app = MainFrame()
    app.run()
