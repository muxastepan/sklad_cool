import tkinter as tk
import win32api

from data_matrix import DataMatrixReaderException, DataMatrixReader
from misc import SettingsFileManager
from tables import *
from widgets import AutoCompletionCombobox, MessageBox, RestartQuestionBox


# TODO Обработка исключений
class AddDBRecordDialogue(tk.Toplevel):
    def __init__(self, parent, table: Table, straight_mode: bool = True, temp_var_attrs: list = None):
        super().__init__(parent)
        self.straight_mode = straight_mode
        self.temp_var_attrs = temp_var_attrs
        self.focus()
        self.parent = parent
        self.table = table
        self.submit_button = tk.Button(self, text='Отправить', command=self.submit_close)
        self.value_entries = self._build()
        self.bind('<Return>', self.submit_close_k_enter)

    def submit_close_k_enter(self, event):
        self.submit_close()

    def _build(self):
        value_entries = []
        if self.straight_mode:
            var_attrs = self.table.var_attrs
        else:
            var_attrs = self.temp_var_attrs
        for i in range(len(self.table.column_names)):
            entry = AutoCompletionCombobox(self, values=var_attrs[i] if var_attrs else None)
            value_entries.append(entry)
        return value_entries

    def submit_close(self):
        data = []
        for entry in self.value_entries:
            inp = entry.get()
            if inp:
                data.append(entry.get())
            else:
                data.append(None)
        if self.straight_mode:
            try:
                self.table.add(data)
                self.parent.data_grid.add_row(data)
                self.table.update_var_attrs()
                self.table.commit()
            except AdapterException as ex:
                MessageBox(self.parent, ex)
                self.table.rollback()
        else:
            self.parent.data_grid.add_row(data)
        self.destroy()

    def show(self):
        for i in range(len(self.table.column_headings)):
            tk.Label(self, text=self.table.column_headings[i]).pack()
            self.value_entries[i].pack()
        self.submit_button.pack()


class AddProductRecordDialogue(AddDBRecordDialogue):
    def __init__(self, parent, products_table: ProductsTable, temp_var_attrs: list):
        super().__init__(parent, products_table, straight_mode=False, temp_var_attrs=temp_var_attrs)

    def submit_close(self):
        super().submit_close()
        self.parent.update_temp_var_attrs()


class AddEmployeeRecordDialogue(AddDBRecordDialogue):
    def __init__(self, parent, employees_table: EmployeesTable):
        super().__init__(parent, employees_table)


class SettingsDialogue(tk.Toplevel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.parent = parent
        self.settings = settings
        self.cancel_button = tk.Button(self, text='Отмена', command=self.cancel)
        self.save_button = tk.Button(self, text='Применить', command=self.submit)
        self.save_close_button = tk.Button(self, text='Применить и выйти', command=self.submit_close)

    def show(self):
        self.save_button.pack(fill=tk.X)
        self.save_close_button.pack(fill=tk.X)
        self.cancel_button.pack(fill=tk.X)

    def submit_close(self):
        self.submit()
        self.destroy()

    def submit(self):
        pass

    def cancel(self):
        self.destroy()


class MatrixFolderPathDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.path = tk.StringVar(value=self.settings['matrix_folder_path'])
        self.frame = tk.LabelFrame(self)
        self.entry = tk.Entry(self.frame, textvariable=self.path)

    def show(self):
        self.frame.pack(padx=10, pady=10)
        tk.Label(self.frame, text='Путь к папке с матрицами:').pack(padx=10, pady=10)
        self.entry.pack(padx=10, pady=10)
        super().show()

    def submit(self):
        path = self.path.get()
        self.settings['matrix_folder_path'] = path
        SettingsFileManager.write_settings('settings', self.settings)
        self.parent.matrix_path = path


class WindowSettingsDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.width = tk.StringVar(value=self.settings['window_settings']['width'])
        self.height = tk.StringVar(value=self.settings['window_settings']['height'])
        self.width_frame = tk.LabelFrame(self)
        self.height_frame = tk.LabelFrame(self)
        self.height_entry = tk.Entry(self.height_frame, textvariable=self.height)
        self.width_entry = tk.Entry(self.width_frame, textvariable=self.width)

    def show(self):
        self.width_frame.pack()
        self.height_frame.pack()
        tk.Label(self.height_frame, text='Высота').pack()
        self.height_entry.pack(pady=10, padx=10)
        tk.Label(self.width_frame, text='Ширина').pack()
        self.width_entry.pack(pady=10, padx=10)
        super().show()

    def submit(self):
        width = self.width.get()
        height = self.height.get()
        self.settings['window_settings']['width'] = width
        self.settings['window_settings']['height'] = height
        SettingsFileManager.write_settings('settings', self.settings)
        self.parent.geometry(f'{width}x{height}')


class SQLSettingsDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.dbname = tk.StringVar(value=self.settings['sql_settings']['db_name'])
        self.host = tk.StringVar(value=self.settings['sql_settings']['host'])
        self.port = tk.StringVar(value=self.settings['sql_settings']['port'])
        self.user_name = tk.StringVar(value=self.settings['sql_settings']['user_name'])
        self.password = tk.StringVar(value=self.settings['sql_settings']['password'])

        self.db_frame = tk.LabelFrame(self)
        self.user_frame = tk.LabelFrame(self)
        self.dbname_entry = tk.Entry(self.db_frame, textvariable=self.dbname)
        self.host_entry = tk.Entry(self.db_frame, textvariable=self.host)
        self.port_entry = tk.Entry(self.db_frame, textvariable=self.port)
        self.user_name_entry = tk.Entry(self.user_frame, textvariable=self.user_name)
        self.user_password_entry = tk.Entry(self.user_frame, textvariable=self.password)

    def submit(self):
        host = self.host.get()
        port = self.port.get()
        user = self.user_name.get()
        password = self.password.get()
        dbname = self.dbname.get()

        self.settings['sql_settings']['host'] = host
        self.settings['sql_settings']['port'] = port
        self.settings['sql_settings']['user'] = user
        self.settings['sql_settings']['password'] = password
        self.settings['sql_settings']['db_name'] = dbname

        SettingsFileManager.write_settings('settings', self.settings)

        RestartQuestionBox(self.parent, 'Изменения вступят в силу после перезапуска приложения.\n Перезапустить?')

    def show(self):
        self.user_frame.pack()
        tk.Label(self.user_frame, text='Имя пользователя').pack()
        self.user_name_entry.pack(padx=10, pady=10)
        tk.Label(self.user_frame, text='Пароль').pack()
        self.user_password_entry.pack(padx=10, pady=10)

        self.db_frame.pack()
        tk.Label(self.db_frame, text='Имя БД').pack()
        self.dbname_entry.pack(padx=10, pady=10)
        tk.Label(self.db_frame, text='Хост').pack()
        self.host_entry.pack(padx=10, pady=10)
        tk.Label(self.db_frame, text='Порт').pack()
        self.port_entry.pack(padx=10, pady=10)

        super().show()


class TableAttrsSettingsDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.state = tk.BooleanVar(value=self.settings['add_attrs_if_not_exists'])
        self.frame = tk.LabelFrame(self)
        self.check = tk.Checkbutton(self.frame, variable=self.state)

    def show(self):
        self.frame.pack(padx=10, pady=10)
        tk.Label(self.frame, text='Добавлять аттрибут, если его не существует:').pack(padx=10, pady=10, side=tk.LEFT)
        self.check.pack(padx=10, pady=10, side=tk.RIGHT)
        super().show()

    def submit(self):
        res_state = self.state.get()
        self.settings['add_attrs_if_not_exists'] = res_state
        SettingsFileManager.write_settings('settings', self.settings)


class ProdTableSettingsDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.deletable = tk.BooleanVar(value=self.settings['prod_table_settings']['deletable'])
        self.editable = tk.BooleanVar(value=self.settings['prod_table_settings']['editable'])
        self.del_frame = tk.LabelFrame(self)
        self.edit_frame = tk.LabelFrame(self)
        self.del_check = tk.Checkbutton(self.del_frame, variable=self.deletable)
        self.edit_check = tk.Checkbutton(self.edit_frame, variable=self.editable)

    def show(self):
        self.del_frame.pack(padx=10, pady=10, fill=tk.X)
        self.edit_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(self.edit_frame, text='Разрешить редактирование:').pack(padx=10, pady=10, side=tk.LEFT)
        self.edit_check.pack(padx=10, pady=10, side=tk.RIGHT)

        tk.Label(self.del_frame, text='Разрешить удаление:').pack(padx=10, pady=10, side=tk.LEFT)
        self.del_check.pack(padx=10, pady=10, side=tk.RIGHT)
        super().show()

    def submit(self):
        del_state = self.deletable.get()
        ed_state = self.editable.get()
        self.settings['prod_table_settings']['deletable'] = del_state
        self.settings['prod_table_settings']['editable'] = ed_state
        self.parent.storage_tab.data_grid.deletable = del_state
        self.parent.storage_tab.data_grid.editable = ed_state
        SettingsFileManager.write_settings('settings', self.settings)


class ReadBarCodeDialogue(tk.Toplevel):
    def __init__(self, parent, table: ProductsTable):
        super().__init__(parent)
        win32api.LoadKeyboardLayout('00000409', 1)
        self.parent = parent
        self.table = table
        self.bar_code_entry = tk.Entry(self)
        self.bind('<Return>', self.submit)

    def delete(self):
        data = self.bar_code_entry.get()
        try:
            attrs = DataMatrixReader.read(data)
        except DataMatrixReaderException as ex:
            MessageBox(self.parent, ex)
            return
        try:
            self.table.remove(self.table.column_names[0], attrs[0])
            self.table.commit()
        except AdapterException as ex:
            self.table.rollback()
            MessageBox(self.parent, ex)
            return
        self.parent.data_grid.delete_row(attrs[0])

    def submit(self, event):
        self.delete()
        self.destroy()

    def show(self):
        tk.Label(self, text='После ввода нажмите клавишу Enter').pack()
        self.bar_code_entry.pack()
        self.bar_code_entry.focus()
