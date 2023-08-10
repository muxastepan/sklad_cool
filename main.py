import os
import sys

from frames import *
from misc import SettingsFileManager, resource_path
from tables import *
import logging


class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = SettingsFileManager.read_settings()
        self.title('СкладУчет')
        self.geometry(f"{self.settings['window_settings']['width']}x{self.settings['window_settings']['height']}")
        try:
            self.sql_adapter = Adapter(dbname=self.settings['sql_settings']["db_name"],
                                       host=self.settings['sql_settings']["host"],
                                       port=self.settings['sql_settings']["port"],
                                       user=self.settings['sql_settings']["user_name"],
                                       password=self.settings['sql_settings']["password"])
        except AdapterException as ex:
            MessageBox(self, ex)
            SQLSettingsDialogue(self, self.settings).show()
            self.mainloop()
        self.employees_table = EmployeesTable(self.sql_adapter)
        self.product_table = ProductsTable(self.sql_adapter)
        self._build()

    @staticmethod
    def restart():
        program = sys.executable
        os.execl(program, program, *sys.argv)

    def _build(self):

        self.menu = Menu(self, SettingsMenu(self, self.settings), 'Настройки')
        self.config(menu=self.menu)

        self.tabs = TabScroll(self)
        self.storage_tab = StorageTabFrame(self.tabs, self.product_table)
        self.employees_tab = EmployeeTabFrame(self.tabs, self.employees_table)

    def run(self):
        self.storage_tab.show()
        self.employees_tab.show()
        self.tabs.add(self.storage_tab, text='Склад')
        self.tabs.add(self.employees_tab, text='Сотрудники')
        self.tabs.pack(fill=tk.BOTH)
        self.mainloop()


if __name__ == '__main__':
    open(resource_path('crashlog.txt'), 'w').close()
    logging.basicConfig(filename='crashlog.txt', level=logging.DEBUG)
    try:
        app = MainFrame()
        app.run()
    except Exception:
        logging.exception('Exception')
        raise
