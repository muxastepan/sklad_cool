import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Literal
from tkinter import messagebox
from tables import *
from tkcalendar import DateEntry


class DateSelector(tk.Frame):
    def __init__(self, parent, *con_data_frames):
        super().__init__(parent)
        self.con_data_frames = con_data_frames
        self.parent = parent
        self.date_start = DateEntry(self, locale='ru_RU')
        self.date_end = DateEntry(self, locale='ru_RU')
        self.btn = tk.Button(self, text='Поиск', command=self.search_by_date)

    def search_by_date(self):
        try:
            beg = datetime.datetime.strptime(self.date_start.get(), '%d.%m.%Y').date()
            end = datetime.datetime.strptime(self.date_end.get(), '%d.%m.%Y').date()
        except ValueError:
            MessageBox('ОШИБКА: Дата введена неверно', 'ERROR')
            return
        res_data = []
        for data_frame in self.con_data_frames:
            try:
                res_data.append(data_frame.table.select_by_date(beg, end))
            except AdapterException as ex:
                MessageBox(ex, 'ERROR')
                for data_frame_to_rollback in self.con_data_frames:
                    data_frame_to_rollback.table.rollback()
                return
        for i, data_frame in enumerate(self.con_data_frames):
            data_frame.table.commit()
            data_frame.data_grid.update_table_gui_with_data(res_data[i])


    def show(self, row=0, column=0, columnspan=1):
        self.grid(row=row, column=column, columnspan=columnspan)
        tk.Label(self, text='Начало периода:').grid(row=0, column=0)
        self.date_start.grid(row=0, column=1)
        tk.Label(self, text='Конец периода:').grid(row=0, column=2)
        self.date_end.grid(row=0, column=3)
        self.btn.grid(row=0, column=4, padx=10)


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
            callback = parent.table.attr_tables[-1].add
        else:
            callback = parent.table.attr_tables[column_ind].add
        super().__init__(parent, text, callback, *args)

    def run_callback(self):
        try:
            super().run_callback()
        except AdapterException as ex:
            MessageBox(ex, 'ERROR')
            self.destroy()


class MessageBox:
    def __init__(self, text: Union[str, Exception], level: Literal['INFO', 'WARNING', 'ERROR']):
        super().__init__()
        self.level = level
        if level == 'INFO':
            tk.messagebox.showinfo(text, text)
        elif level == 'WARNING':
            tk.messagebox.showwarning(text, text)
        elif level == 'ERROR':
            tk.messagebox.showerror(text, text)


class DataGridView(tk.Frame):

    def __init__(self, parent, table: Table, editable: bool = False, deletable: bool = False,
                 preload_from_table: bool = False, straight_mode: bool = True, spec_ops: Dict[str, Callable] = None,
                 select_func: Callable = None):
        super().__init__(parent)
        self.select_func = select_func
        self.spec_ops = spec_ops
        self.straight_mode = straight_mode
        self.preload_from_table = preload_from_table
        self.deletable = deletable
        self.table = table
        if not select_func:
            self.select_func = self.table.select_all
        if self.preload_from_table:
            self.data = self.select_func()
        else:
            self.data = []
        self.y_scroll_bar = tk.Scrollbar(self)
        self.x_scroll_bar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.table_gui = ttk.Treeview(self)
        self.__editable = editable
        self._build_table()

    @property
    def editable(self):
        return self.__editable

    @editable.setter
    def editable(self, val):
        if val:
            self.table_gui.bind("<Double-Button-1>", self.set_cell_value)
        else:
            self.table_gui.unbind("<Double-Button-1>")
        self.__editable = val

    def update_table_gui_with_data(self, data: list):
        for row in self.data:
            self.delete_row(row[0])
        self.data = data
        for row in self.data:
            self.add_row(row)

    def update_table_gui_from_table(self):
        for row in self.data:
            self.delete_row(row[0])
        if self.preload_from_table:
            self.data = self.select_func()
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
        item = self.table_gui.selection()
        if not item:
            return
        else:
            item = item[0]
        column = int(self.table_gui.identify_column(event.x).replace('#', '')) - 1
        edit_entry = AutoCompletionCombobox(self.table_gui,
                                            values=[self.table_gui.item(item)['values'][column]])
        edit_entry.focus()
        edit_entry.place(x=column * 100, y=25 + (event.y // 20 - 1) * 20, width=self.table_gui.column(column)['width'])

        def save_edit():
            data = TypeIdentifier.identify_parse(edit_entry.get())
            if not data:
                data = None
            if self.straight_mode:
                rec_id = self.table_gui.item(item, 'values')[0]

                try:
                    self.table.edit(self.table.column_names[column], data, rec_id)
                except AdapterException as ex:
                    edit_entry.destroy()
                    MessageBox(ex, 'ERROR')
                    self.table.rollback()
                    return
                except ProdTableAttrNotFoundException as ex:
                    edit_entry.destroy()
                    self.table.rollback()
                    AddAttrQuestionBox(self, f"{ex}\nДобавить этот аттрибут?", column - 1, (data,))
                    return
                except ProdTableEditIdException as ex:
                    edit_entry.destroy()
                    MessageBox(ex, 'WARNING')
                    self.table.rollback()
                    return
                except TableException as ex:
                    edit_entry.destroy()
                    MessageBox(ex, 'ERROR')
                    self.table.rollback()
                    return
                self.table.commit()
                self.table.update_var_attrs()

            self.table_gui.set(item, column=column, value=data if data else 'Пусто')

            edit_entry.destroy()

        def save_edit_return(event: tk.Event):
            return save_edit()

        edit_entry.bind('<Return>', save_edit_return)

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
                    MessageBox(ex, 'ERROR')
                    self.table.rollback()
                    return
                except ProdTableMatrixNotFoundWarning as ex:
                    MessageBox(ex, 'ERROR')
                except TableException as ex:
                    MessageBox(ex, 'ERROR')
                    self.table.rollback()
                    return

                self.table.update_var_attrs()
            self.delete_row(p_key)

    def add_row(self, data):
        self._row_count += 1
        for i, val in enumerate(data):
            if type(val) == bool:
                continue
            if not val:
                data[i] = 'Пусто'
        self.table_gui.insert('', tk.END, values=data)

    def delete_row(self, rec_id: Union[int, str]):
        self._row_count -= 1
        rows = self.table_gui.get_children()
        for row in rows:
            if self.table_gui.item(row)['values'][0] == rec_id:
                self.table_gui.delete(row)


class AutoCompletionCombobox(ttk.Combobox):
    def __init__(self, root, values=None):
        super().__init__(root, values=values)
        self.bind('<KeyRelease>', self.check_input)
        self.old_values = self['values']
        if self.old_values:
            self.set(self.old_values[0])

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
