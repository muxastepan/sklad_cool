from data_matrix import DataMatrixReader
from dialogues import *
from widgets import *
from tables import *

class TabScroll(ttk.Notebook):
    def __init__(self,parent):
        super().__init__(parent)
        self.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def on_tab_change(self,event:tk.Event):
        for tab in self.children.values():
            tab.data_grid.update_table_gui()

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
    def __init__(self, parent, child_menu: tk.Menu, text: str):
        super().__init__(parent)
        self.child_menu = child_menu
        self.add_cascade(label=text, menu=self.child_menu)


class TabFrame(tk.Frame):
    def __init__(self, parent, table):
        super().__init__(parent)
        self.table = table
        self.add_btn = tk.Button(self, text='Добавить', command=self.show_add_dialogue)
        self.data_grid = DataGridView(self, self.table, preload_from_table=True)

    def show_add_dialogue(self):
        AddFrame(self, self.table).show()

    def show(self):
        self.add_btn.pack(fill=tk.X)
        self.data_grid.pack(side=tk.LEFT, fill=tk.BOTH)
        self.pack(fill=tk.BOTH)


class StorageTabFrame(TabFrame):
    def __init__(self, parent, table: ProductsTable):
        super().__init__(parent, table)
        self.settings = SettingsFileManager.read_settings('settings')['prod_table_settings']
        self.data_grid.deletable = self.settings['deletable']
        self.data_grid.editable = self.settings['editable']
        self.delete_bar_code_btn = tk.Button(self, text='Пробить товар',
                                             command=self.show_delete_bar_code_dialogue)
        self.show_attrs_frame_btn = tk.Button(self, text='Аттрибуты', command=self.show_attrs_frame)

    def show_attrs_frame(self):
        AttrFrame(self, self.table).show()

    def show_add_dialogue(self):
        AddProductFrame(self, self.table).show()

    def show_delete_bar_code_dialogue(self):
        ReadBarCodeDialogue(self, self.table).show()

    def show(self):
        self.show_attrs_frame_btn.pack(fill=tk.X)
        self.delete_bar_code_btn.pack(fill=tk.X)
        super().show()


class EmployeeTabFrame(TabFrame):
    def __init__(self, parent, table: EmployeesTable):
        super().__init__(parent, table)
        self.data_grid = DataGridView(self, self.table, preload_from_table=True, editable=True, deletable=True)

    def show_add_dialogue(self):
        AddEmployeeRecordDialogue(self, self.table).show()


class AddFrame(tk.Toplevel):
    def __init__(self, parent: TabFrame, table):
        super().__init__(parent)
        self.parent = parent
        self.table = table
        self.add_btn = tk.Button(self, text='Добавить', command=self.show_add_dialogue)
        self.submit_btn = tk.Button(self, text='Сохранить и вывести на печать', command=self.submit_print_close)
        self.data_grid = DataGridView(self, self.table, editable=True, deletable=True, straight_mode=False)

    def submit_print_close(self):
        rows = self.data_grid.table_gui.get_children()
        parsed_values = []
        for row in rows:
            values = [TypeIdentifier.identify_parse(val) for val in self.data_grid.table_gui.item(row)['values']]
            parsed_values.append(values)
            try:
                self.table.add(values)
            except AdapterException as ex:
                MessageBox(self, ex)
                self.table.rollback()
                return
        self.table.update_var_attrs()
        self.table.commit()
        for values in parsed_values:
            self.parent.data_grid.add_row(values)
        self.destroy()

    def show_add_dialogue(self):
        AddDBRecordDialogue(self, self.table).show()

    def show(self):
        self.add_btn.pack(fill=tk.X)
        self.submit_btn.pack(fill=tk.X)
        self.data_grid.pack(side=tk.LEFT, fill=tk.BOTH)


class AddProductFrame(AddFrame):
    def __init__(self, parent, table: ProductsTable):
        super().__init__(parent, table)
        self.settings = SettingsFileManager.read_settings('settings')
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
        for row in rows:
            values = [TypeIdentifier.identify_parse(val) for val in self.data_grid.table_gui.item(row)['values']]
            parsed_values.append(values)
            try:
                if self.settings['add_attrs_if_not_exists']:
                    self.table.add_to_attrs_tables(values)
                    self.table.commit()
                self.table.add(values)
            except AdapterException as ex:
                MessageBox(self, ex)
                self.table.rollback()
                return
            except TableException as ex:
                MessageBox(self, ex)
                self.table.rollback()
                return
        self.table.update_var_attrs()
        self.table.commit()
        for values in parsed_values:
            self.parent.data_grid.add_row(values)
            DataMatrixReader.create_matrix(values)

        self.table.commit()
        DataMatrixReader.print_matrix(self.settings['matrix_folder_path'])
        self.destroy()

    def show(self):
        super().show()
        try:
            DataMatrixReader.clear_matrix(self.settings['matrix_folder_path'])
        except FileNotFoundError as ex:
            MessageBox(self.parent, ex)
            self.destroy()

    def show_add_dialogue(self):
        AddProductRecordDialogue(self, self.table, self.temp_var_attrs).show()


class AttrGrid(TabFrame):
    def __init__(self, parent, table):
        super().__init__(parent, table)
        self.data_grid = DataGridView(self, self.table, preload_from_table=True, deletable=True, editable=True)

    def show_add_dialogue(self):
        AddDBRecordDialogue(self, self.table).show()


class AttrFrame(tk.Toplevel):
    def __init__(self, parent, table):
        super().__init__(parent)
        self.table = table

    def show(self):
        for i, attr_table in enumerate(self.table.attr_tables):
            frame = tk.LabelFrame(self)
            frame.grid(row=1, column=i)
            AttrGrid(frame, attr_table).show()
