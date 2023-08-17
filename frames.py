import os.path
import tkinter

from dialogues import *
from widgets import *
from tables import *
import customtkinter as ctk
from gui_colors import *


class TabScroll(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color='#b3d4ff')
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=4, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')
        self.choose_frame = ctk.CTkFrame(self, fg_color=TAB_SCROLL,
                                         background_corner_colors=(TAB_SCROLL, TAB_SCROLL, TAB_SCROLL, TAB_SCROLL))
        self.choose_frame.columnconfigure(0, weight=1, uniform='a')
        self.btns = []
        self.tabs_count = 0
        self.tabs = {}
        self.sel_tab = None

    def add(self, name: str, frame: ctk.CTkFrame):
        self.tabs[name] = frame
        btn = ctk.CTkButton(
            self.choose_frame,
            fg_color=BTN_STANDARD,
            hover_color=BTN_HOVER,
            text_color=TEXT_COLOR,
            text=name)
        btn.bind('<Button-1>', self.on_tab_change)
        self.btns.append(btn)
        self.choose_frame.rowconfigure(self.tabs_count, weight=1, uniform='a')
        self.tabs_count += 1

    def show(self, row=0, column=0, columnspan=1, rowspan=1):
        self.choose_frame.rowconfigure(self.tabs_count + 1, weight=10, uniform='a')
        name = self.btns[0].cget('text')
        self.sel_tab = self.tabs[name]
        self.grid(row=row, column=column, columnspan=columnspan, sticky=tk.NSEW, rowspan=rowspan)
        self.choose_frame.grid(row=0, column=0, sticky='nsew')
        for i, btn in enumerate(self.btns):
            btn.grid(row=i, column=0, sticky='nsew', pady=(0, 10), padx=10)
        self.sel_tab.show(row=0, column=1)

    def on_tab_change(self, event: tk.Event):
        name = event.widget.master.cget('text')
        self.sel_tab.grid_forget()
        self.sel_tab = self.tabs[name]
        self.sel_tab.show(row=0, column=1)
        for data_frame in self.sel_tab.data_frames:
            data_frame.data_grid.update_table_gui_from_table()


class ProdArchiveMenu(tk.Menu):
    def __init__(self, parent, table: ProductsTable):
        super().__init__(parent, tearoff=0)
        self.table = table
        self.parent = parent
        self.add_command(label='Архив товаров', command=self.show_archive_frame)

    def show_archive_frame(self):
        ProdArchiveFrame(self, self.table).show()


class SalaryPerSizeMenu(tk.Menu):
    def __init__(self, parent, table: SalaryPerSizeTable):
        super().__init__(parent, tearoff=0)
        self.table = table
        self.parent = parent
        self.add_command(label='Оплата за размер', command=self.show_salary_per_size_frame)

    def show_salary_per_size_frame(self):
        SalaryPerSizeFrame(self, self.table).show()


class SalaryPerSizeFrame(ctk.CTkToplevel):
    def __init__(self, parent, table):
        super().__init__(parent)
        self.title('Оплата за размер')
        self.table = table
        self.data_frame = DataFrame(self, self.table, editable=True, deletable=True, preload_from_table=True)

        self.columnconfigure(0, weight=1, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')
        self.focus()

    def show(self):
        self.data_frame.show()


class SettingsMenu(tk.Menu):
    def __init__(self, parent, settings):
        super().__init__(parent, tearoff=0)
        self.parent = parent
        self.settings = settings
        self.add_command(label='Окно...', command=self.show_window_settings)
        self.add_command(label='SQL...', command=self.show_sql_settings)
        self.add_command(label='Путь к папке с матрицами', command=self.show_matrix_path_settings)
        self.add_command(label='Аттрибуты таблицы...', command=self.show_table_attrs_settings)
        self.add_command(label='Таблица склада...', command=self.show_prod_table_settings)

    def show_prod_table_settings(self):
        ProdTableSettingsDialogue(self.parent, self.settings).show()

    def show_table_attrs_settings(self):
        TableAttrsSettingsDialogue(self.parent, self.settings).show()

    def show_matrix_path_settings(self):
        MatrixFolderPathDialogue(self.parent, self.settings).show()

    def show_window_settings(self):
        WindowSettingsDialogue(self.parent, self.settings).show()

    def show_sql_settings(self):
        SQLSettingsDialogue(self.parent, self.settings).show()


class Menu(tk.Menu):
    def __init__(self, parent, headings: tuple, *child_menus: tk.Menu):
        super().__init__(parent)
        for i, child_menu in enumerate(child_menus):
            self.add_cascade(label=headings[i], menu=child_menu)


class DataFrame(ctk.CTkFrame):
    def __init__(self, parent, table, can_add=True, editable: bool = False, deletable: bool = False,
                 preload_from_table: bool = False, straight_mode: bool = True, spec_ops: Dict[str, Callable] = None,
                 select_func: Callable = None):
        super().__init__(parent, fg_color=FRAME_COLOR)
        self.parent = parent
        self.can_add = can_add
        self.table = table
        self.data_grid = DataGridView(self, table, editable, deletable, preload_from_table, straight_mode, spec_ops,
                                      select_func)
        self.add_btn = StandardButton(self, text='Добавить', command=self.show_add_dialogue)

        self.columnconfigure(0, weight=2, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=20, uniform='a')

    def show_add_dialogue(self):
        AddDBRecordDialogue(self, self.table).show()

    def show(self, row=0, column=0, columnspan=1, rowspan=1, padx=0, pady=0):
        self.grid(row=row, column=column, columnspan=columnspan, sticky=tk.NSEW, rowspan=rowspan, padx=padx, pady=pady)
        if self.can_add:
            self.add_btn.grid(row=0, column=0, sticky=tk.NSEW)
            self.data_grid.grid(row=1, column=0, sticky=tkinter.NSEW)
        else:
            self.data_grid.grid(row=1, column=0, sticky=tkinter.NSEW)


class ProductDataFrame(DataFrame):
    def __init__(self, parent, table, editable: bool = False, deletable: bool = False):
        super().__init__(parent, table, editable=editable, deletable=deletable,
                         preload_from_table=True, straight_mode=True, spec_ops={'Печать': self.show_matrix},
                         select_func=table.select_all_not_sold)
        self.delete_bar_code_btn = FailButton(self, text='Пробить товар',
                                              command=self.show_delete_bar_code_dialogue)
        self.show_attrs_frame_btn = StandardButton(self, text='Аттрибуты', command=self.show_attrs_frame)
        self.table = table
        self.columnconfigure(1, weight=1, uniform='a')
        self.columnconfigure(2, weight=1, uniform='a')

    def show_matrix(self):
        table = self.data_grid.table_gui
        items = table.selection()
        if not items:
            return
        for item in items:
            rec_id = table.item(item)['values'][0]
            path = self.table.select_matrix(rec_id)[0]
            DataMatrixReader.open_matrix(path)

    def show_attrs_frame(self):
        AttrFrame(self, self.table).show()

    def show_add_dialogue(self):
        AddProductFrame(self, self.table, self).show()

    def show_delete_bar_code_dialogue(self):
        ReadBarCodeDialogue(self, self.table).show()

    def show(self, row=0, column=0, columnspan=1, rowspan=1, padx=0, pady=0):
        super().show(row, column, columnspan, rowspan)
        self.show_attrs_frame_btn.grid(row=0, column=1, sticky=tk.NSEW, padx=(10, 5))
        self.delete_bar_code_btn.grid(row=0, column=2, sticky=tk.NSEW, padx=5)
        self.data_grid.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)


class AddDataFrame(DataFrame):
    def __init__(self, parent, table, con_data_frame: DataFrame):
        super().__init__(parent, table, can_add=True, editable=True, deletable=True, straight_mode=False)
        self.con_data_frame = con_data_frame
        self.submit_btn = StandardButton(self, text='Сохранить и вывести на печать', command=self.submit_print_close)
        self.columnconfigure(1, weight=1, uniform='a')

    def submit_print_close(self):
        rows = self.data_grid.table_gui.get_children()
        parsed_values = []
        for row in rows:
            values = [TypeIdentifier.identify_parse(val) for val in self.data_grid.table_gui.item(row)['values']]
            parsed_values.append(values)
            try:
                self.table.add(values)
            except AdapterException as ex:
                MessageBox(ex, 'ERROR')
                self.table.rollback()
                return
        self.table.update_var_attrs()
        self.table.commit()
        for values in parsed_values:
            self.con_data_frame.data_grid.add_row(values)

        self.destroy()

    def show(self, row=0, column=0, columnspan=1, rowspan=1, pady=0, padx=0):
        super().show(row, column, columnspan, rowspan)
        self.add_btn.grid(row=0, column=0, sticky=tk.NSEW)
        self.submit_btn.grid(row=0, column=1, sticky=tk.NSEW)
        self.data_grid.grid(row=1, column=0, columnspan=2)


class AddProductDataFrame(AddDataFrame):
    def __init__(self, parent, table: ProductsTable, con_data_frame):
        super().__init__(parent, table, con_data_frame)
        self.settings = SettingsFileManager.read_settings()
        self.table.update_var_attrs()
        self.temp_var_attrs = self.table.var_attrs

    def update_temp_var_attrs(self):
        self.temp_var_attrs[0] = self.table.next_id()
        rows = self.data_grid.table_gui.get_children()
        for row in rows:
            values = [(i,) for i in self.data_grid.table_gui.item(row)['values']]
            for c in range(1, len(values)):
                if values[c] != ('None',) and values[c] not in self.temp_var_attrs[c]:
                    self.temp_var_attrs[c].append(values[c])

    def submit_print_close(self):
        rows = self.data_grid.table_gui.get_children()
        parsed_values = []
        matrix_folder_path = os.path.normpath(self.settings['matrix_folder_path'])
        print_paths = []
        for row in rows:
            values = [TypeIdentifier.identify_parse(val) for val in self.data_grid.table_gui.item(row)['values']]

            matrix_name = f"{''.join(str(i) for i in values)}.png"
            matrix_path = os.path.join(matrix_folder_path, matrix_name)
            print_paths.append(matrix_path)
            parsed_values.append(values)
            try:
                try:
                    DataMatrixReader.create_matrix(values[0], matrix_path)
                except FileNotFoundError as ex:
                    MessageBox(ex, 'ERROR')
                    MatrixFolderPathDialogue(self, self.settings).show()
                    return
                if self.settings['add_attrs_if_not_exists']:
                    self.table.add_to_attrs_tables(values)
                    self.table.commit()

                values.append(matrix_path)
                values.append(False)
                self.table.add(values)
            except AdapterException as ex:
                DataMatrixReader.delete_matrix(matrix_path)
                print_paths.remove(matrix_path)

                MessageBox(ex, 'ERROR')
                self.table.rollback()
                return
            except TableException as ex:
                DataMatrixReader.delete_matrix(matrix_path)
                print_paths.remove(matrix_path)

                MessageBox(ex, 'ERROR')
                self.table.rollback()
                return
        self.table.update_var_attrs()
        self.table.commit()
        for values in parsed_values:
            self.con_data_frame.data_grid.add_row(values)
        if parsed_values:
            PrinterDialogue(print_paths, parsed_values).show()

        self.parent.destroy()

    def show_add_dialogue(self):
        AddProductRecordDialogue(self, self.table, self.temp_var_attrs).show()


class TabFrame(ctk.CTkFrame):
    def __init__(self, parent, caption: str):
        super().__init__(parent, fg_color=FRAME_COLOR)
        self.caption = caption
        self.data_frames = []
        self.parent = parent
        self.rowconfigure(0, weight=1, uniform='a')

    def fill_data_frames(self, *data_frames: DataFrame):
        for data_frame in data_frames:
            self.data_frames.append(data_frame)
        for i in range(len(self.data_frames)):
            self.columnconfigure(i, weight=1, uniform='a')
        return self

    def show(self, row=0, column=0, columnspan=1, rowspan=1):
        self.grid(row=row, column=column, columnspan=columnspan, sticky=tk.NSEW, rowspan=rowspan)
        for i, data_frame in enumerate(self.data_frames):
            data_frame.show(row=0, column=i)


class SalaryTabFrame(TabFrame):
    def __init__(self, parent, caption: str):
        super().__init__(parent, caption)
        self.print_btn = StandardButton(self, text='Печать', command=self.print_doc)
        self.date_select = None
        self.rowconfigure(0, weight=1, uniform='a')
        self.columnconfigure(0, weight=3, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')

    def fill_data_frames(self, *data_frames: DataFrame):
        for data_frame in data_frames:
            self.data_frames.append(data_frame)
        for i in range(len(self.data_frames)):
            self.rowconfigure(i + 1, weight=10, uniform='a')
        self.date_select = DateSelector(self, *data_frames)
        return self

    def print_doc(self):
        pass

    def show(self, row=0, column=0, columnspan=1, rowspan=1):
        self.grid(row=row, column=column, columnspan=columnspan, sticky=tk.NSEW, rowspan=rowspan)
        self.date_select.show()
        self.print_btn.grid(row=0, column=1)
        for i, data_frame in enumerate(self.data_frames):
            data_frame.show(row=i + 1, column=0, columnspan=2)


class AddFrame(ctk.CTkToplevel):
    def __init__(self, parent, table, con_data_frame: DataFrame):
        super().__init__(parent)
        self.data_frame = AddDataFrame(self, table, con_data_frame)
        self.focus()

    def show(self):
        self.data_frame.show()


class AddProductFrame(AddFrame):
    def __init__(self, parent, table, con_data_frame):
        super().__init__(parent, table, con_data_frame)
        self.title('Приём товара')
        self.data_frame = AddProductDataFrame(self, table, con_data_frame)


class AttrFrame(ctk.CTkToplevel):
    def __init__(self, parent, table):
        super().__init__(parent)
        self.title('Таблицы аттрибутов')
        self.table = table
        for i in range(len(self.table.attr_tables)):
            self.columnconfigure(i, weight=1, uniform='a', minsize=200)
        self.focus()

    def show(self):
        for i, attr_table in enumerate(self.table.attr_tables):
            DataFrame(self, attr_table, editable=True, deletable=True, preload_from_table=True).show(row=0, column=i,
                                                                                                     padx=10, pady=10)


class ProdArchiveFrame(ctk.CTkToplevel):
    def __init__(self, parent, table: ProductsTable):
        super().__init__(parent)
        self.title('Архив товаров')
        self.table = table
        self.select_date = DateSelector(self, self)
        self.data_grid = DataGridView(self, self.table, editable=True, deletable=True, preload_from_table=True)
        self.select_date.search_by_date()
        self.columnconfigure(0, weight=1, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=20, uniform='a')
        self.focus()

    def show(self):
        self.data_grid.grid(row=1, column=0, sticky=tk.NSEW)
        self.select_date.show()
