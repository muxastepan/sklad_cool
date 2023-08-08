import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict

from sql_adapter import *
from misc import TypeIdentifier
from tables import Table, TableException, ProdTableAttrNotFoundException, ProdTableMatrixNotFoundWarning


class QuestionBox(tk.Toplevel):
    def __init__(self, parent, text: str, callback: Callable, *args):
        super().__init__(parent)
        self.callback = callback
        self.args = args
        self.parent = parent
        tk.Label(self, text=text).pack(side=tk.TOP)
        tk.Button(self, text='Нет', command=self.destroy, width=20).pack(side=tk.LEFT, padx=20)
        tk.Button(self, text='Да', command=self.run_callback, width=20).pack(side=tk.RIGHT, padx=20)

    def run_callback(self):
        if self.args:
            self.callback(self.args)
        else:
            self.callback()
        self.destroy()


class RestartQuestionBox(QuestionBox):
    def __init__(self, parent, text):
        super().__init__(parent, text, parent.restart)


class AddAttrQuestionBox(QuestionBox):
    def __init__(self, parent, text, column_ind, *args):
        if column_ind == 5 or column_ind == 6:
            callback = parent.table.related_table.add
        else:
            callback = parent.table.attr_tables[column_ind].add
        super().__init__(parent, text, callback, *args)

    def run_callback(self):
        try:
            super().run_callback()
        except AdapterException as ex:
            MessageBox(self.parent, ex)
            self.destroy()


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

    def __init__(self, parent, table: Table, editable: bool = False, deletable: bool = False,
                 preload_from_table: bool = False, straight_mode: bool = True, spec_ops: Dict[str, Callable] = None):
        super().__init__(parent)
        self.spec_ops = spec_ops
        self.straight_mode = straight_mode
        self.preload_from_table = preload_from_table
        self.deletable = deletable
        self.editable = editable
        self.table = table
        if self.preload_from_table:
            self.data = self.table.select_all()
        else:
            self.data = []
        self.y_scroll_bar = tk.Scrollbar(self)
        self.x_scroll_bar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.table_gui = ttk.Treeview(self)
        self._build_table()

    def update_table_gui(self):
        for row in self.data:
            self.delete_row(row[0])
        if self.preload_from_table:
            self.data = self.table.select_all()
        else:
            self.data = []
        for row in self.data:
            self.add_row(row)

    def show_rec_menu(self, event: tk.Event):
        def edit():
            self.set_cell_value(event)

        def delete():
            self.delete_record(event)

        menu = tk.Menu(self.table_gui, tearoff=0)

        if self.editable:
            menu.add_command(label='Изменить', command=edit)
        if self.deletable:
            menu.add_command(label='Удалить', command=delete)
        if self.spec_ops:
            for label, command in self.spec_ops.items():
                menu.add_command(label=label, command=command)
        menu.post(event.x_root, event.y_root)

    def set_cell_value(self, event: tk.Event):
        items = self.table_gui.selection()
        if not items:
            return
        column = int(self.table_gui.identify_column(event.x).replace('#', '')) - 1
        edit_frame = tk.Toplevel(self)
        edit_entry = AutoCompletionCombobox(edit_frame,
                                            values=[self.table_gui.item(item)['values'][column] for item in items])
        edit_entry.focus()
        edit_entry.pack()

        def save_edit():
            data = TypeIdentifier.identify_parse(edit_entry.get())
            if not data:
                data = None
            if self.straight_mode:
                for item in items:
                    rec_id = self.table_gui.item(item, 'values')[0]

                    try:
                        self.table.edit(self.table.column_names[column], data, rec_id)
                    except AdapterException as ex:
                        MessageBox(self, ex)
                        self.table.rollback()
                        return
                    except ProdTableAttrNotFoundException as ex:
                        self.table.rollback()
                        AddAttrQuestionBox(self, f"{ex}\nДобавить этот аттрибут?", column - 1, (data,))
                        return
                    except TableException as ex:
                        MessageBox(self, ex)
                        self.table.rollback()
                        return
                self.table.commit()
                self.table.update_var_attrs()

            for item in items:
                self.table_gui.set(item, column=column, value=data if data else 'Пусто')

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
            self.add_row(row)

        self.y_scroll_bar.configure(command=self.table_gui.yview)
        self.y_scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.x_scroll_bar.configure(command=self.table_gui.xview)
        self.x_scroll_bar.pack(side=tk.BOTTOM, fill=tk.X)

        if self.editable:
            self.table_gui.bind("<Double-Button-1>", self.set_cell_value)
        self.table_gui.bind("<Button-3>", self.show_rec_menu)
        self.table_gui.pack(fill=tk.BOTH)

    def delete_record(self, event: tk.Event):
        items = self.table_gui.selection()
        if not items:
            return
        for item in items:
            data = self.table_gui.item(item)['values']
            p_key = data[0]
            if self.straight_mode:
                try:
                    self.table.remove(self.table.p_key_column_name, p_key)
                except AdapterException as ex:
                    MessageBox(self, ex)
                    self.table.rollback()
                    return
                except ProdTableMatrixNotFoundWarning as ex:
                    MessageBox(self, ex)
                except TableException as ex:
                    MessageBox(self, ex)
                    self.table.rollback()
                    return

                self.table.update_var_attrs()
            self.delete_row(p_key)

    def add_row(self, data):
        self._row_count += 1
        for i, val in enumerate(data):
            if not val:
                data[i] = 'Пусто'
        self.table_gui.insert('', tk.END, values=data)

    def delete_row(self, rec_id: int):
        self._row_count -= 1
        rows = self.table_gui.get_children()
        for row in rows:
            if self.table_gui.item(row)['values'][0] == rec_id:
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
