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
            MessageBox(ex, 'ERROR')
            SQLSettingsDialogue(self, self.settings).show()
            self.mainloop()
        self._build()

    @staticmethod
    def restart():
        program = sys.executable
        os.execl(program, program, *sys.argv)

    def _build(self):
        self.employees_table = EmployeesTable(self.sql_adapter)
        self.salary_per_size_table = SalaryPerSizeTable(self.sql_adapter)
        self.product_table = ProductsTable(self.sql_adapter)
        self.salary_table = SalaryTable(self.sql_adapter)
        self.adv_salary_table = AdvancedSalaryTable(self.sql_adapter)

        self.menu = Menu(self, ('Настройки', 'Архив товаров'), SettingsMenu(self, self.settings),
                         ProdArchiveMenu(self, self.product_table))
        self.config(menu=self.menu)

        self.tabs = TabScroll(self)
        self.storage_tab = TabFrame(self.tabs)
        self.storage_tab.fill_data_frames(
            ProductDataFrame(self.storage_tab, self.product_table, self.settings['prod_table_settings']['editable'],
                             self.settings['prod_table_settings']['deletable']))

        self.salary_tab = SalaryTabFrame(self.tabs)
        self.salary_tab.fill_data_frames(
            DataFrame(self.salary_tab, self.salary_per_size_table, editable=True, deletable=True,
                      preload_from_table=True, straight_mode=True),
            DataFrame(self.salary_tab, self.adv_salary_table, can_add=False, preload_from_table=True),
            DataFrame(self.salary_tab, self.salary_table, can_add=False, preload_from_table=True)
        )

    def run(self):
        self.storage_tab.show()
        self.salary_tab.show()
        self.tabs.add(self.storage_tab, text='Склад')
        self.tabs.add(self.salary_tab, text='Расчёт зарплаты')
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
