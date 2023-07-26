import psycopg2

from dialogues import *
from widgets import *
from tables import *


class TabFrame(tk.Frame):
    def __init__(self, parent, adapter: Adapter, table: Table):
        super().__init__(parent)
        self.table = table
        self.adapter = adapter
        self.add_btn = tk.Button(self, text='Добавить', command=self.show_add_dialogue)
        self.data_grid = DataGridView(self, self.table)

    def show_add_dialogue(self):
        AddDBRecordDialogue(self, self.table).show()

    def show(self):
        self.add_btn.pack(fill=tk.X)
        self.data_grid.pack(side=tk.LEFT, fill=tk.BOTH)
        self.pack(fill=tk.BOTH)


class StorageTabFrame(TabFrame):
    def __init__(self, parent, adapter: Adapter, table: ProductsTable):
        super().__init__(parent, adapter, table)

    def show_add_dialogue(self):
        AddProductRecordDialogue(self, self.table).show()


class EmployeeTabFrame(TabFrame):
    def __init__(self, parent, adapter: Adapter, table: EmployeesTable):
        super().__init__(parent, adapter, table)

    def show_add_dialogue(self):
        AddEmployeeRecordDialogue(self, self.table).show()


class SettingsMenu(tk.Menu):
    def __init__(self, parent, settings):
        super().__init__(parent, tearoff=0)
        self.parent = parent
        self.settings = settings
        self.add_command(label='Окно...', command=self.show_window_settings)
        self.add_command(label='SQL...', command=self.show_sql_settings)

    def show_window_settings(self):
        WindowSettingsDialogue(self.parent, self.settings).show()

    def show_sql_settings(self):
        SQLSettingsDialogue(self.parent, self.settings).show()


class Menu(tk.Menu):
    def __init__(self, parent, settings_menu: SettingsMenu):
        super().__init__(parent)
        self.settings_menu = settings_menu
        self.add_cascade(label='Настройки', menu=self.settings_menu)



