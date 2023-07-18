import re
import tkinter as tk
from tkinter import ttk
from sql_adapter import Adapter


class AddWindow(tk.Toplevel):
    def __init__(self, adapter: Adapter, table_name: str):
        super().__init__()
        self.adapter = adapter
        self.table_name = table_name
        self.submit_button = tk.Button(self, text='Отправить', command=self.submit_close)
        self.data_columns = self.adapter.fetch_column_names(self.table_name)
        self.combo_boxes = []

    def submit_close(self):
        data_list = []
        for combo_box in self.combo_boxes:
            data = combo_box.get()
            data_list.append(data)
        if self.table_name == 'products':
            self.adapter.add_product(data_list)
        elif self.table_name == 'employees':
            self.adapter.add_employee(data_list[0])
        self.destroy()

    def show(self):
        for column in self.data_columns:
            cur_name = column[0].replace('_', ' ')
            combo_box = ttk.Combobox(self)
            combo_box['values'] = column[1]
            self.combo_boxes.append(combo_box)
            tk.Label(self, text=cur_name).pack()
            combo_box.pack()
        self.submit_button.pack()


class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sql_adapter = Adapter('testdb')
        self.add_product_button = tk.Button(text='Добавить запись', command=self.show_add_product_dialogue)
        self.add_employee_button = tk.Button(text='Добавить запись', command=self.show_add_employee_dialogue)
        self.add_window = None

    def show_add_product_dialogue(self):
        self.add_window = AddWindow(self.sql_adapter, 'products')
        self.add_window.show()

    def show_add_employee_dialogue(self):
        self.add_window = AddWindow(self.sql_adapter, 'employees')
        self.add_window.show()

    def run(self):
        self.add_product_button.pack()
        self.add_employee_button.pack()
        self.mainloop()


if __name__ == '__main__':
    app = MainFrame()
    app.run()
