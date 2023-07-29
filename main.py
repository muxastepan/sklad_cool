import os
import sys

import psycopg2

from frames import *
from misc import SettingsFileManager
from tables import *


class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.exception = None
        self.settings = SettingsFileManager.read_settings('settings')
        self.geometry(f"{self.settings['window_settings']['width']}x{self.settings['window_settings']['height']}")
        try:
            self.sql_adapter = Adapter(dbname=self.settings['sql_settings']["db_name"],
                                       host=self.settings['sql_settings']["host"],
                                       port=self.settings['sql_settings']["port"],
                                       user=self.settings['sql_settings']["user_name"],
                                       password=self.settings['sql_settings']["password"])

            self.employees_table = EmployeesTable(self.sql_adapter)
            self.product_table = ProductsTable(self.sql_adapter, self.employees_table)
            self._build()
        except psycopg2.OperationalError as ex:
            self.exception = ex

    def restart(self):
        program = sys.executable
        os.execl(program, program, *sys.argv)

    def _build(self):
        self.menu = Menu(self, SettingsMenu(self, self.settings))
        self.config(menu=self.menu)

        self.tabs = ttk.Notebook(self)
        self.storage_tab = StorageTabFrame(self.tabs, self.sql_adapter, self.product_table)
        self.employees_tab = EmployeeTabFrame(self.tabs, self.sql_adapter, self.employees_table)

    def run(self):
        if self.exception:
            MessageBox(self, 'Не удалось подключиться к базе данных, проверьте настройки')
            SQLSettingsDialogue(self, self.settings).show()
            self.mainloop()
            return
        self.storage_tab.show()
        self.employees_tab.show()
        self.tabs.add(self.storage_tab, text='Склад')
        self.tabs.add(self.employees_tab, text='Сотрудники')
        self.tabs.pack(fill=tk.BOTH)
        self.mainloop()


if __name__ == '__main__':
    app = MainFrame()
    app.run()
# TODO удаление на пкм в таблице(меню)
# TODO замена матрицы при изменении записи доделать
# TODO Обработать исключения протестировать
# TODO Засунуть проект в exe файл
