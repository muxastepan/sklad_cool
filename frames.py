import os.path
import tkinter

from dialogues import *
from widgets import *
from tables import *


class TabScroll(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def on_tab_change(self, event: tk.Event):
        tab = self.children[self.select().replace(f"{self}.", '')]
        for data_frame in tab.data_frames:
            data_frame.data_grid.update_table_gui_from_table()


class ProdArchiveMenu(tk.Menu):
    def __init__(self, parent, table: ProductsTable):
        super().__init__(parent, tearoff=0)
        self.table = table
        self.parent = parent
        self.add_command(label='Архив товаров', command=self.show_archive_frame)

    def show_archive_frame(self):
        ProdArchiveFrame(self, self.table).show()


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


class DataFrame(tk.Frame):
    def __init__(self, parent, table, can_add=True, editable: bool = False, deletable: bool = False,
                 preload_from_table: bool = False, straight_mode: bool = True, spec_ops: Dict[str, Callable] = None,
                 select_func: Callable = None):
        super().__init__(parent)
        self.parent = parent
        self.can_add = can_add
        self.table = table
        self.data_grid = DataGridView(self, table, editable, deletable, preload_from_table, straight_mode, spec_ops,
                                      select_func)
        self.add_btn = tk.Button(self, text='Добавить', command=self.show_add_dialogue)

    def show_add_dialogue(self):
        AddDBRecordDialogue(self, self.table).show()

    def show(self, row=0, column=0, columnspan=1):
        self.grid(row=row, column=column, columnspan=columnspan, sticky=tk.NSEW)
        if self.can_add:
            self.add_btn.grid(row=0, column=0, sticky=tk.EW)
        else:
            tk.Button(self, state='disabled').grid(row=0, column=0, sticky=tk.EW)
        self.data_grid.grid(row=1, column=0, sticky=tkinter.NSEW)


class ProductDataFrame(DataFrame):
    def __init__(self, parent, table, editable: bool = False, deletable: bool = False):
        super().__init__(parent, table, editable=editable, deletable=deletable,
                         preload_from_table=True, straight_mode=True, spec_ops={'Печать': self.show_matrix},
                         select_func=table.select_all_not_sold)
        self.delete_bar_code_btn = tk.Button(self, text='Пробить товар',
                                             command=self.show_delete_bar_code_dialogue)
        self.show_attrs_frame_btn = tk.Button(self, text='Аттрибуты', command=self.show_attrs_frame)
        self.table = table

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

    def show(self, row=0, column=0, columnspan=1):
        super().show(row, column, columnspan)
        self.show_attrs_frame_btn.grid(row=0, column=1, sticky=tk.EW)
        self.delete_bar_code_btn.grid(row=0, column=2, sticky=tk.EW)
        self.data_grid.grid(row=1, column=0, columnspan=3)


class AddDataFrame(DataFrame):
    def __init__(self, parent, table, con_data_frame: DataFrame):
        super().__init__(parent, table, can_add=True, editable=True, deletable=True, straight_mode=False)
        self.con_data_frame = con_data_frame
        self.add_btn = tk.Button(self, text='Добавить', command=self.show_add_dialogue)
        self.submit_btn = tk.Button(self, text='Сохранить и вывести на печать', command=self.submit_print_close)

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

    def show(self, row=0, column=0, columnspan=1):
        super().show(row, column, columnspan)
        self.add_btn.grid(row=0, column=0, sticky=tk.EW)
        self.submit_btn.grid(row=0, column=1, sticky=tk.EW)
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
                    self.destroy()
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


class TabFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.data_frames = []
        self.parent = parent

    def fill_data_frames(self, *data_frames: DataFrame):
        for data_frame in data_frames:
            self.data_frames.append(data_frame)
        return self

    def show(self, row=0, column=0, columnspan=1):
        self.grid(row=row, column=column, columnspan=columnspan)
        for i, data_frame in enumerate(self.data_frames):
            data_frame.show(row=1, column=i)


class SalaryTabFrame(TabFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.date_select = None
        self.cnt_sum_btn = tk.Button(self, text='Рассчитать сумму к оплате', command=self.count_salary_payment)

    def fill_data_frames(self, *data_frames: DataFrame):
        super().fill_data_frames(*data_frames)
        self.date_select = DateSelector(self, data_frames[1], data_frames[2])

    def count_salary_payment(self):
        def on_exit(event: tk.Event):
            sum_view.destroy()

        sum_var = tk.DoubleVar(value=sum([item[1] for item in self.data_frames[2].data_grid.data]))
        sum_view = tk.Toplevel()
        ok_btn = tk.Button(sum_view, text='OK', command=sum_view.destroy)
        sum_entry = tk.Entry(sum_view, textvariable=sum_var)
        sum_entry.focus()
        sum_entry.bind('<Return>', on_exit)

        ok_btn.grid(row=1, column=0, columnspan=2)
        tk.Label(sum_view, text='К оплате:').grid(row=0, column=0)
        sum_entry.grid(row=0, column=1)

    def show(self, row=0, column=0, columnspan=1):
        super().show()
        if self.date_select:
            self.date_select.show(columnspan=2)
            self.cnt_sum_btn.grid(row=0, column=2, sticky=tk.EW)


class AddFrame(tk.Toplevel):
    def __init__(self, parent, table, con_data_frame: DataFrame):
        super().__init__(parent)
        self.data_frame = AddDataFrame(self, table, con_data_frame)

    def show(self):
        self.data_frame.show()


class AddProductFrame(AddFrame):
    def __init__(self, parent, table, con_data_frame):
        super().__init__(parent, table, con_data_frame)
        self.data_frame = AddProductDataFrame(self, table, con_data_frame)


class AttrFrame(tk.Toplevel):
    def __init__(self, parent, table):
        super().__init__(parent)
        self.table = table

    def show(self):
        for i, attr_table in enumerate(self.table.attr_tables):
            frame = tk.LabelFrame(self)
            frame.grid(row=1, column=i)
            DataFrame(frame, attr_table, editable=True, deletable=True, preload_from_table=True).show()


class ProdArchiveFrame(tk.Toplevel):
    def __init__(self, parent, table: ProductsTable):
        super().__init__(parent)
        self.table = table
        self.select_date = DateSelector(self, self)
        self.data_grid = DataGridView(self, self.table, editable=True, deletable=True, preload_from_table=True)
        self.select_date.search_by_date()

    def show(self):
        self.data_grid.grid(row=1, column=0, columnspan=25)
        self.select_date.show()
