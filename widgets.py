import datetime
import tkinter as tk
from tkinter import ttk
from typing import Callable

from data_matrix import DataMatrixReader
from misc import TypeIdentifier
from tables import Table, ProductsTable


class RestartQuestionBox(tk.Toplevel):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.parent = parent
        tk.Label(self, text=text).pack(side=tk.TOP)
        tk.Button(self, text='Нет', command=self.destroy, width=20).pack(side=tk.LEFT, padx=20)
        tk.Button(self, text='Да', command=self.restart, width=20).pack(side=tk.RIGHT, padx=20)

    def restart(self):
        self.parent.restart()


class MessageBox(tk.Toplevel):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.focus()
        tk.Label(self, text=text).pack()
        tk.Button(self, text='OK', command=self.destroy).pack()
        self.bind('<Return>', self.close_event)

    def close_event(self, event: tk.Event):
        self.destroy()


class DataGridView(tk.Frame):

    def __init__(self, parent, table: Table, printer_func: Callable = None):
        super().__init__(parent)
        self.printer_func = printer_func
        self.table = table
        self.data = self.table.select_all()
        self.y_scroll_bar = tk.Scrollbar(self)
        self.x_scroll_bar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.table_gui = ttk.Treeview(self)
        self._build_table()

    def show_rec_menu(self, event: tk.Event):
        def edit():
            self.set_cell_value(event)

        def delete():
            self.delete_record(event)

        menu = tk.Menu(self.table_gui, tearoff=0)
        menu.add_command(label='Изменить', command=edit)
        menu.add_command(label='Удалить', command=delete)
        menu.add_command(label='Печать', command=self.print_selected_items)
        menu.post(event.x_root, event.y_root)

    def print_selected_items(self):
        items = self.table_gui.selection()
        if not items:
            return
        if not self.printer_func:
            MessageBox(self, text='Метод печати не реализован для этой таблицы')
            return
        paths = []
        for item in items:
            data = self.table_gui.item(item)['values'][1:]
            if self.table.table_name == 'products':
                data = self.table.emp_name_to_id(data)
                data[4] = datetime.datetime.strptime(data[4], '%d.%m.%Y').date()

            path = f"matrix\\{''.join(str(i) for i in data)}.png"
            paths.append(path)
        self.printer_func(paths)

    def set_cell_value(self, event: tk.Event):
        items = self.table_gui.selection()
        if not items:
            return
        edit_frame = tk.Toplevel(self)
        edit_entry = tk.Entry(edit_frame)
        edit_entry.focus()
        edit_entry.pack()
        column = int(self.table_gui.identify_column(event.x).replace('#', '')) - 1

        def save_edit():
            for item in items:
                data = edit_entry.get()
                if not data:
                    data = None
                rec_id = self.table_gui.item(item, 'values')[0]
                old_rec = self.table.select_id(rec_id, self.table.column_names[1:])
                _, last_prod = self.table.find_id(old_rec)
                db_edit = self.table.edit_one(self.table.column_names[column], data, rec_id)
                if not db_edit:
                    MessageBox(self, 'Введенные данные имеют неверный формат')
                    break
                else:
                    self.table_gui.set(item, column=column, value=data if data else 'None')
                    rec = self.table.select_id(rec_id, self.table.column_names[1:])
                    DataMatrixReader.create_matrix(rec)
                    if last_prod:
                        path = f"matrix\\{''.join(str(i) for i in old_rec)}.png"
                        try:
                            DataMatrixReader.delete_matrix(path)
                        except FileNotFoundError:
                            MessageBox(self, f'Матрицы {path} не существует')
            edit_frame.destroy()

        def save_edit_return(event: tk.Event):
            return save_edit()

        submit_button = tk.Button(edit_frame, text='OK', command=save_edit)
        edit_entry.bind('<Return>', save_edit_return)
        submit_button.pack()

    def sort_data(self, col, reverse):
        data = [(self.table_gui.set(child, col), child) for child in self.table_gui.get_children('')]
        data.sort(reverse=reverse, key=lambda x: TypeIdentifier.identify_parse(x[0]))
        for index, (val, child) in enumerate(data):
            self.table_gui.move(child, '', index)

        self.table_gui.heading(col, command=lambda: self.sort_data(col, not reverse))

    def _build_table(self):
        self.table_gui['columns'] = self.table.column_headings
        self.table_gui.column('#0', width=0, stretch=tk.NO)
        for i, heading in enumerate(self.table.column_headings):
            self.table_gui.column(heading, anchor=tk.W, width=100)
            self.table_gui.heading(heading, text=heading, anchor=tk.W,
                                   command=lambda col=heading: self.sort_data(col, False))

        self._row_count = 0
        for row in self.data:
            self.table_gui.insert('', tk.END, values=row)
            self._row_count += 1

        self.y_scroll_bar.configure(command=self.table_gui.yview)
        self.y_scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.x_scroll_bar.configure(command=self.table_gui.xview)
        self.x_scroll_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.table_gui.bind("<Double-Button-1>", self.set_cell_value)
        self.table_gui.bind("<Button-3>", self.show_rec_menu)
        self.table_gui.pack(fill=tk.BOTH)

    def delete_record(self, event: tk.Event):
        items = self.table_gui.selection()
        if not items:
            return
        for item in items:
            data = self.table_gui.item(item)['values'][1:]
            if self.table.table_name == 'products':
                data = self.table.emp_name_to_id(data)
                data[4] = datetime.datetime.strptime(data[4], '%d.%m.%Y').date()
                id_to_del, last_prod = self.table.find_id(data)
                if last_prod:
                    path = f"matrix\\{''.join(str(i) for i in data)}.png"
                    try:
                        DataMatrixReader.delete_matrix(path)
                    except FileNotFoundError:
                        MessageBox(self, f'Матрицы {path} не существует')
            elif self.table.table_name == 'employees':
                id_to_del, _ = self.table.find_id(data)
            else:
                raise NotImplementedError

            self.table.remove(self.table.column_names[0], id_to_del)
            self.delete_row(id_to_del)

    def add_row(self, data):
        self._row_count += 1
        self.table_gui.insert('', tk.END, values=data)

    def delete_row(self, data):
        self._row_count -= 1
        rows = self.table_gui.get_children()
        for row in rows:
            if self.table_gui.item(row)['values'][0] == data:
                self.table_gui.delete(row)


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
        else:
            self['values'] = self.old_values
