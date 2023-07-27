import tkinter as tk
from tkinter import ttk

import re
import datetime

from tables import Table


class RestartQuestionBox(tk.Toplevel):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.parent = parent
        tk.Label(self, text=text).pack(side=tk.TOP)
        tk.Button(self, text='Нет', command=self.destroy,width=20).pack(side=tk.LEFT, padx=20)
        tk.Button(self, text='Да', command=self.restart,width=20).pack(side=tk.RIGHT, padx=20)

    def restart(self):
        self.parent.restart()


class MessageBox(tk.Toplevel):
    def __init__(self, parent, text):
        super().__init__(parent)
        tk.Label(self, text=text).pack()
        tk.Button(self, text='OK', command=self.destroy).pack()


class DataGridView(tk.Frame):
    def __init__(self, parent, table: Table):
        super().__init__(parent)
        self.table = table
        self.data = self.table.select_all()
        self.y_scroll_bar = tk.Scrollbar(self)
        self.x_scroll_bar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.table_gui = ttk.Treeview(self)
        self._build_table()

    def set_cell_value(self, event: tk.Event):
        item = self.table_gui.selection()
        if not item:
            return
        else:
            item = item[0]
        column = int(self.table_gui.identify_column(event.x).replace('#', '')) - 1
        edit_frame = tk.Toplevel(self)
        edit_entry = tk.Entry(edit_frame)
        edit_entry.pack()

        def save_edit():
            data = edit_entry.get()
            if data:
                rec_id = self.table_gui.item(item, 'values')[0]
                db_edit = self.table.edit_one(self.table.column_names[column], data, rec_id)
                if not db_edit:
                    MessageBox(self, 'Введенные данные имеют неверный формат')
                else:
                    self.table_gui.set(item, column=column, value=data)

            edit_frame.destroy()

        def save_edit_return(event):
            return save_edit()

        submit_button = tk.Button(edit_frame, text='OK', command=save_edit)
        edit_entry.bind('<Return>', save_edit_return)
        submit_button.pack()

    def sort_data(self, col, reverse):
        data = [(self.table_gui.set(child, col), child) for child in self.table_gui.get_children('')]
        data_vals = [x[0] for x in data]

        if all(re.match('\d{4}-\d{2}-\d{2}', i) for i in data_vals):
            data.sort(reverse=reverse, key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d'))
        elif all(re.match('\d+', i) for i in data_vals):
            data.sort(reverse=reverse, key=lambda x: int(x[0]))
        else:
            data.sort(reverse=reverse)
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
        self.table_gui.pack(fill=tk.BOTH)

    def add_row(self, data):
        self._row_count += 1
        self.table_gui.insert('', tk.END, values=data)

    def delete_row(self,data):
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
