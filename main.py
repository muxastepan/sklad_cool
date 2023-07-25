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


class Menu(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)
        settings_menu = tk.Menu(self, tearoff=0)
        settings_menu.add_command(label='Окно...', command=self.show_window_settings)
        settings_menu.add_command(label='SQL...',command=self.show_sql_settings)
        self.add_cascade(label='Настройки', menu=settings_menu)

    def show_window_settings(self):
        WindowSettingsDialogue(self).show()

    def show_sql_settings(self):
        SQLSEttingsDialogue(self).show()


class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sql_adapter = Adapter('testdb')
        self.employees_table = EmployeesTable(self.sql_adapter)
        self.product_table = ProductsTable(self.sql_adapter, self.employees_table)

        self._build()

    def _build(self):
        self.menu = Menu(self)
        self.config(menu=self.menu)

        self.tabs = ttk.Notebook(self)
        self.storage_tab = StorageTabFrame(self.tabs, self.sql_adapter, self.product_table)
        self.employees_tab = EmployeeTabFrame(self.tabs, self.sql_adapter, self.employees_table)

    def run(self):
        self.storage_tab.show()
        self.employees_tab.show()
        self.tabs.add(self.storage_tab, text='Склад')
        self.tabs.add(self.employees_tab, text='Сотрудники')
        self.tabs.pack(fill=tk.BOTH)
        self.mainloop()


if __name__ == '__main__':
    app = MainFrame()
    app.run()
