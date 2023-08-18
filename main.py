import os
import sys

from frames import *
from misc import SettingsFileManager, resource_path
from tables import *
import logging
import customtkinter as ctk


class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=FRAME_COLOR)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.settings = SettingsFileManager.read_settings()
        self.title('СкладУчет')
        self.geometry(f"{self.settings['window_settings']['width']}x{self.settings['window_settings']['height']}")
        ctk.set_appearance_mode(self.settings['window_settings']['theme'])
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
        self.salary_per_size_table = SalaryPerSizeTable(self.sql_adapter)
        self.product_table = ProductsTable(self.sql_adapter)
        self.salary_table = SalaryTable(self.sql_adapter)
        self.adv_salary_table = AdvancedSalaryTable(self.sql_adapter)
        self.employee_table = EmployeesTable(self.sql_adapter)

        self.menu = Menu(self, ('Настройки', 'Архив товаров', 'Оплата за размер'), SettingsMenu(self, self.settings),
                         ProdArchiveMenu(self, self.product_table), SalaryPerSizeMenu(self, self.salary_per_size_table))
        self.config(menu=self.menu)
        self.tabs = TabScroll(self)
        self.storage_tab = TabFrame(self.tabs, 'Склад')
        self.storage_tab.fill_data_frames(
            ProductDataFrame(self.storage_tab, self.product_table, self.settings['prod_table_settings']['editable'],
                             self.settings['prod_table_settings']['deletable']))

        self.salary_tab = SalaryTabFrame(self.tabs, "Расчет зарплаты")
        self.salary_tab.fill_data_frames(
            AdvSalaryDataFrame(self.salary_tab, self.adv_salary_table),
            SalaryDataFrame(self.salary_tab, self.salary_table)
        )
        self.employee_tab = TabFrame(self.tabs, 'Сотрудники')
        self.employee_tab.fill_data_frames(
            DataFrame(self.employee_tab, self.employee_table, can_add=True, preload_from_table=True, editable=True,
                      deletable=True)
        )

        self.tabs.add(self.storage_tab.caption, self.storage_tab)
        self.tabs.add(self.salary_tab.caption, self.salary_tab)
        self.tabs.add(self.employee_tab.caption, self.employee_tab)

    def run(self):
        self.tabs.show()
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
