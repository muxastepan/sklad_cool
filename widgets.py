import tkinter as tk
from tkinter import ttk
from typing import Callable, Literal
from tkinter import messagebox
from tables import *
import customtkinter as ctk
from gui_colors import *


class StandardButton(ctk.CTkButton):
    def __init__(self, parent, text, command):
        super().__init__(parent, text=text, command=command,
                         fg_color=BTN_STANDARD,
                         hover_color=BTN_HOVER,
                         text_color=TEXT_COLOR
                         )


class FailButton(ctk.CTkButton):
    def __init__(self, parent, text, command):
        super().__init__(parent, text=text, command=command,
                         fg_color=FAIL_STANDARD,
                         hover_color=FAIL_HOVER,
                         text_color=TEXT_COLOR
                         )


class SuccessButton(ctk.CTkButton):
    def __init__(self, parent, text, command):
        super().__init__(parent, text=text, command=command,
                         fg_color=SUCCESS_STANDARD,
                         hover_color=SUCCESS_HOVER,
                         text_color=TEXT_COLOR
                         )


class DateSelector(ctk.CTkFrame):
    MONTHS = {
        'Январь': ('01', '31'),
        'Февраль': ('02', '28'),
        'Март': ('03', '31'),
        'Апрель': ('04', '30'),
        'Май': ('05', '31'),
        'Июнь': ('06', '30'),
        'Июль': ('07', '31'),
        'Август': ('08', '31'),
        'Сентябрь': ('09', '30'),
        'Октябрь': ('10', '31'),
        'Ноябрь': ('11', '30'),
        'Декабрь': ('12', '31')
    }

    def __init__(self, parent, *con_data_frames):
        super().__init__(parent, fg_color=FRAME_COLOR)
        self.con_data_frames = con_data_frames
        self.parent = parent
        self.month_entry = ctk.CTkOptionMenu(self, values=[month for month in DateSelector.MONTHS.keys()],
                                             fg_color=BTN_STANDARD,
                                             button_hover_color=BTN_HOVER,
                                             dropdown_hover_color=BTN_HOVER,
                                             dropdown_fg_color=FRAME_COLOR,
                                             text_color=TEXT_COLOR,
                                             button_color=BTN_STANDARD)
        self.year = tk.StringVar(value=str(datetime.date.today().year))
        self.year_entry = ctk.CTkEntry(self, textvariable=self.year, border_color=BTN_STANDARD)
        self.btn = StandardButton(self, text='Поиск', command=self.search_by_date)

        self.rowconfigure(0, weight=1, uniform='a')
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.columnconfigure(2, weight=1, uniform='a')

    def search_by_date(self):
        year = self.year.get()
        month = DateSelector.MONTHS[self.month_entry.get()][0]
        last_day = DateSelector.MONTHS[self.month_entry.get()][1]
        beg = f'01.{month}.{year}'
        end = f'{last_day}.{month}.{year}'
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
            data_frame.update_table_with_data(res_data[i])

    def show(self, row=0, column=0, columnspan=1):
        self.grid(row=row, column=column, columnspan=columnspan, sticky=tk.NSEW)
        self.month_entry.grid(row=0, column=0, sticky=tk.W)
        self.year_entry.grid(row=0, column=1, sticky=tk.W)
        self.btn.grid(row=0, column=2, padx=10, sticky=tk.W)


class QuestionBox(ctk.CTkToplevel):
    def __init__(self, parent, text: str, callback: Callable, *args, title: str = None):
        super().__init__(parent)
        if title:
            self.title(title)
        self.callback = callback
        self.args = args
        self.parent = parent
        ctk.CTkLabel(self, text=text).pack(side=tk.TOP, pady=10, padx=10)
        FailButton(self, text='Нет', command=self.destroy).pack(side=tk.LEFT, padx=20, pady=10)
        SuccessButton(self, text='Да', command=self.run_callback).pack(side=tk.RIGHT, padx=20, pady=10)
        self.grab_set()

    def run_callback(self):
        if self.args:
            self.callback(*self.args)
        else:
            self.callback()
        self.destroy()


class RestartQuestionBox(QuestionBox):
    def __init__(self, parent, text):
        super().__init__(parent, text, parent.restart, title='Перезапуск')


class AddAttrQuestionBox(QuestionBox):
    def __init__(self, parent, text, column_ind, *args):
        if column_ind == 5 or column_ind == 6:
            callback = parent.table.attr_tables[-1].add
        else:
            callback = parent.table.attr_tables[column_ind].add
        super().__init__(parent, text, callback, *args, title='Добавление аттрибута')

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


class DataGridView(ctk.CTkFrame):

    def __init__(self, parent, table: Table, editable: bool = False, deletable: bool = False,
                 preload_from_table: bool = False, straight_mode: bool = True, spec_ops: Dict[str, Callable] = None,
                 select_func: Callable = None, have_sum_row=False):
        super().__init__(parent, fg_color=FRAME_COLOR)
        self.have_sum_row = have_sum_row
        self.columnconfigure(0, weight=1, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')

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

        self.table_gui = ttk.Treeview(self, show='headings')
        self.check_theme()
        self.y_scroll_bar = ctk.CTkScrollbar(self, command=self.table_gui.yview, fg_color=FRAME_COLOR,
                                             button_color=BTN_STANDARD,
                                             button_hover_color=BTN_HOVER)
        self.table_gui.configure(yscrollcommand=self.y_scroll_bar.set)
        self.__editable = editable
        self._build_table()

    def check_theme(self):
        mode = ctk.get_appearance_mode()
        if mode == 'Dark':
            ind = 1
        else:
            ind = 0
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview.Heading', background=BTN_STANDARD[ind], foreground='white' if ind == 1 else 'black',
                        font=('Calibri', 11))
        style.configure("Treeview",
                        background=FRAME_COLOR[ind],
                        rowheight=25,
                        foreground='white' if ind == 1 else 'black',
                        fieldbackground='white'
                        )
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style.map('Treeview', background=[('selected', BTN_STANDARD[ind])],
                  foreground=[('selected', 'white' if ind == 1 else 'black')])
        style.map('Treeview.Heading', background=[('selected', BTN_HOVER[ind])])
        self.table_gui.tag_configure('odd', background=DATA_GRID_ODD[ind])
        self.table_gui.tag_configure('even', background=DATA_GRID_EVEN[ind])

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
        self.delete_rows(self.table_gui.get_children())
        self.data = data
        for row in self.data:
            self.add_row(row)

    def update_table_gui_from_table(self):
        self.delete_rows(self.table_gui.get_children())
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
                                            values=[self.table_gui.item(item)['values'][column]],
                                            width=self.table_gui.column(column)['width'], height=25)
        edit_entry.focus()
        edit_entry.place(x=column * self.table_gui.column(column)['width'], y=20 + (event.y // 25 - 1) * 25)

        def save_edit():
            data = TypeIdentifier.identify_parse(edit_entry.get())
            if data != 0 and not data:
                data = None
            if self.straight_mode:
                row_data = self.table_gui.item(item, 'values')
                rec_id = row_data[0]

                try:
                    self.table.edit(self.table.column_names[column], data, rec_id,
                                    {self.table.column_names[i]: row_data[i] for i in
                                     range(len(self.table.column_names)) if
                                     i != column})
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

            self.table_gui.set(item, column=column, value=data if not data is None else 'Пусто')

            edit_entry.destroy()

        def save_edit_return(event: tk.Event):
            return save_edit()

        edit_entry.bind('<Return>', save_edit_return)

    def sort_data(self, col, reverse):
        data = [(self.table_gui.set(child, col), child) for child in self.table_gui.get_children('')]
        if self.have_sum_row:
            data.pop()
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

        self.y_scroll_bar.grid(row=0, column=1, rowspan=2, sticky=tk.NS)

        if self.editable:
            self.table_gui.bind("<Double-Button-1>", self.set_cell_value)
        self.table_gui.bind("<Button-3>", self.show_rec_menu)
        self.table_gui.grid(row=0, column=0, sticky=tk.NSEW)

    def delete_record(self, event: tk.Event):
        items = self.table_gui.selection()
        if not items:
            return
        for item in items:
            data = self.table_gui.item(item)['values']
            p_key = data[0]
            p_name = self.table.p_key_column_name
            other_columns = {self.table.column_names[i]: data[i] for i in range(len(self.table.column_names))}
            if self.straight_mode:
                try:
                    self.table.remove(p_name, p_key, other_columns)
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
        self.table.commit()

        self.delete_rows(items)

    def add_row(self, data):
        data = list(data)
        self._row_count += 1
        for i, val in enumerate(data):
            if type(val) == bool:
                continue
            if val is None:
                data[i] = 'Пусто'
        self.table_gui.insert('', tk.END, values=data, tags=('odd',) if self._row_count % 2 == 1 else ('even',))

    def delete_rows(self, items: Union[tuple, list]):
        for item in items:
            self._row_count -= 1
            self.table_gui.delete(item)


class AutoCompletionCombobox(ctk.CTkComboBox):
    def __init__(self, root, width=None, height=None, values=None):
        super().__init__(root, values=[str(i) for i in values if i] if values else [],
                         fg_color=FRAME_COLOR,
                         button_color=BTN_STANDARD,
                         button_hover_color=BTN_HOVER,
                         dropdown_fg_color=FRAME_COLOR,
                         border_color=BTN_STANDARD,
                         dropdown_hover_color=BTN_HOVER,
                         dropdown_text_color=TEXT_COLOR,
                         text_color=TEXT_COLOR,
                         corner_radius=0
                         )
        if width:
            self.configure(width=width)
        if height:
            self.configure(height=height)
        self.configure(command=self.check_input)
        self.old_values = self.cget('values')
        if self.old_values:
            self.set(self.old_values[0])
        else:
            self.set('Пусто')

    def check_input(self, value):

        if value != '':
            data = []
            for item in self.old_values:
                if value in item:
                    data.append(item)
            self.configure(values=data)
        else:
            self.configure(values=self.old_values)
