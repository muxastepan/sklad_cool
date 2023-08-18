
import tkinter.filedialog

import win32print

from misc import SettingsFileManager
from widgets import *
import customtkinter as ctk


class PrinterDialogue(ctk.CTkToplevel):
    def __init__(self, paths, data):
        super().__init__()
        self.title('Печать матриц')
        self.data = data
        self.paths = paths
        self.cur = 0
        self.text_var = tk.StringVar()
        self.select_printer_cmb = ctk.CTkOptionMenu(self, values=[i[2] for i in win32print.EnumPrinters(2)],
                                                    fg_color=BTN_STANDARD,
                                                    button_hover_color=BTN_HOVER,
                                                    dropdown_hover_color=BTN_HOVER,
                                                    dropdown_fg_color=FRAME_COLOR,
                                                    text_color=TEXT_COLOR,
                                                    button_color=BTN_STANDARD
                                                    )
        self.select_printer_cmb.set(win32print.GetDefaultPrinter())
        self.update_text()

        self.label = ctk.CTkLabel(self, textvariable=self.text_var)
        self.next_btn = StandardButton(self, text='Следующая матрица', command=self.next)
        self.prev_btn = StandardButton(self, text='Предыдущая матрица', command=self.prev)
        self.print_button = SuccessButton(self, text="Печать", command=self.print)

        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')
        self.rowconfigure(2, weight=1, uniform='a')

        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.columnconfigure(2, weight=1, uniform='a')

        self.focus()

    def update_text(self):
        if not self.data:
            return
        text = f"Вы собираетесь напечатать: {' '.join(str(i) for i in self.data[self.cur][1:-2])}"
        self.text_var.set(text)

    def prev(self):
        if self.cur > 0:
            self.cur -= 1
            self.update_text()
        else:
            return

    def print(self):
        try:
            win32print.SetDefaultPrinter(self.select_printer_cmb.get())
        except SystemError:
            MessageBox('ОШИБКА: Возможно выбранного принтера не существует', 'ERROR')
            return
        DataMatrixReader.print_matrix(self.paths[self.cur])

    def show(self):
        ctk.CTkLabel(self, text='Принтер:').grid(row=0, column=0, sticky='e', padx=10)
        self.select_printer_cmb.grid(row=0, column=1, sticky='w')
        self.label.grid(row=1, column=0, columnspan=3, sticky='w', padx=10)
        self.next_btn.grid(row=2, column=2, padx=10, pady=5)
        self.print_button.grid(row=2, column=1, padx=10, pady=5)
        self.prev_btn.grid(row=2, column=0, padx=10, pady=5)

    def next(self):
        if self.cur < len(self.paths) - 1:
            self.cur += 1
            self.update_text()
        else:
            self.destroy()


class AddDBRecordDialogue(ctk.CTkToplevel):
    def __init__(self, parent, table: Table, straight_mode: bool = True, temp_var_attrs: list = None):
        super().__init__(parent)
        self.straight_mode = straight_mode
        self.temp_var_attrs = temp_var_attrs
        self.parent = parent
        self.table = table
        self.submit_button = SuccessButton(self, text='Отправить', command=self.submit_close)
        self.value_entries = self._build()
        self.bind('<Return>', self.submit_close_k_enter)
        self.focus()

    def submit_close_k_enter(self, event):
        self.submit_close()

    def _build(self):
        value_entries = []
        if self.straight_mode:
            var_attrs = self.table.var_attrs
        else:
            var_attrs = self.temp_var_attrs
        for i in range(len(self.table.column_names)):
            entry = AutoCompletionCombobox(self, values=[item[0] for item in var_attrs[i]] if var_attrs else None)
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
                MessageBox(ex, 'ERROR')
                self.table.rollback()
        else:
            self.parent.data_grid.add_row(data)
        self.destroy()

    def show(self):
        for i in range(len(self.table.column_headings)):
            ctk.CTkLabel(self, text=self.table.column_headings[i], text_color=TEXT_COLOR).pack()
            self.value_entries[i].pack(padx=10, pady=5)
        self.submit_button.pack(padx=10, pady=5)
        self.focus()


class AddProductRecordDialogue(AddDBRecordDialogue):
    def __init__(self, parent, products_table: ProductsTable, temp_var_attrs: list):
        super().__init__(parent, products_table, straight_mode=False, temp_var_attrs=temp_var_attrs)
        self.title('Добавление товара')

    def _build(self):
        value_entries = []
        if self.straight_mode:
            var_attrs = self.table.var_attrs
        else:
            var_attrs = self.temp_var_attrs

        for i in range(len(self.table.column_names)):
            if i == 0:
                entry = ctk.CTkEntry(self, textvariable=tk.StringVar(value=var_attrs[i]), border_color=BTN_STANDARD)
            elif i == 5:
                entry = ctk.CTkEntry(self, textvariable=tk.StringVar(value=var_attrs[i][0]), border_color=BTN_STANDARD)
            else:
                entry = AutoCompletionCombobox(self, values=[item[0] for item in var_attrs[i]] if var_attrs else None)
            value_entries.append(entry)
        return value_entries

    def submit_close(self):
        super().submit_close()
        self.parent.update_temp_var_attrs()


class AddEmployeeRecordDialogue(AddDBRecordDialogue):
    def __init__(self, parent, employees_table: EmployeesTable):
        super().__init__(parent, employees_table)
        self.title('Добавить сотрудника')
        self.focus()


class SettingsDialogue(ctk.CTkToplevel):
    def __init__(self, parent, settings):
        super().__init__(parent, fg_color=FRAME_COLOR)

        self.parent = parent
        self.settings = settings
        self.cancel_button = FailButton(self, text='Отмена', command=self.cancel)
        self.save_button = SuccessButton(self, text='Применить', command=self.submit_close)
        self.window_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR)
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.rowconfigure(0, weight=5, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')
        self.focus()

    def show(self):
        self.window_frame.grid(row=0, column=0, columnspan=3, sticky='nsew')
        self.save_button.grid(row=1, column=1, pady=5, padx=10, sticky='w')
        self.cancel_button.grid(row=1, column=0, pady=5, padx=10, sticky='w')

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
        self.title('Путь к папке с матрицами')
        self.path = tk.StringVar(value=self.settings['matrix_folder_path'])
        self.entry = ctk.CTkEntry(self.window_frame, textvariable=self.path, border_color=BTN_STANDARD)
        self.open_dir_dialogue_btn = StandardButton(self.window_frame, text='Выбрать...',
                                                    command=self.dir_dialogue)

        self.rowconfigure(0, weight=1, uniform='a')
        self.columnconfigure(0, weight=3, uniform='a')
        self.window_frame.columnconfigure(0, weight=3, uniform='a')
        self.window_frame.columnconfigure(1, weight=1, uniform='a')
        self.window_frame.rowconfigure(0, weight=1, uniform='a')

    def dir_dialogue(self):
        self.path.set(tkinter.filedialog.askdirectory())

    def show(self):
        self.entry.grid(row=0, column=0, padx=(10, 0), sticky='ew')
        self.open_dir_dialogue_btn.grid(row=0, column=1, sticky='w', padx=10)
        super().show()

    def submit(self):
        path = self.path.get()
        self.settings['matrix_folder_path'] = path
        SettingsFileManager.write_settings(self.settings)
        self.parent.matrix_path = path


class WindowSettingsDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.title('Настройки окна')
        self.width = tk.StringVar(value=self.settings['window_settings']['width'])
        self.height = tk.StringVar(value=self.settings['window_settings']['height'])
        self.theme = tk.BooleanVar(value=True if self.settings['window_settings']['theme'] == 'light' else False)

        self.light_btn = ctk.CTkRadioButton(self.window_frame, value=True, variable=self.theme, text='Светлая',
                                            fg_color=BTN_STANDARD,
                                            hover_color=BTN_HOVER)
        self.dark_btn = ctk.CTkRadioButton(self.window_frame, value=False, variable=self.theme, text='Темная',
                                           fg_color=BTN_STANDARD,
                                           hover_color=BTN_HOVER
                                           )
        self.height_entry = ctk.CTkEntry(self.window_frame, textvariable=self.height, border_color=BTN_STANDARD)
        self.width_entry = ctk.CTkEntry(self.window_frame, textvariable=self.width, border_color=BTN_STANDARD)

        self.window_frame.columnconfigure(0, weight=1, uniform='a')
        self.window_frame.columnconfigure(1, weight=1, uniform='a')
        self.window_frame.rowconfigure(0, weight=1, uniform='a')
        self.window_frame.rowconfigure(1, weight=1, uniform='a')
        self.window_frame.rowconfigure(2, weight=1, uniform='a')
        self.window_frame.rowconfigure(3, weight=1, uniform='a')

    def show(self):

        ctk.CTkLabel(self.window_frame, text='Высота').grid(column=0, row=0, sticky='w', padx=10)
        self.height_entry.grid(pady=10, padx=10, column=0, row=1, sticky='w')
        ctk.CTkLabel(self.window_frame, text='Ширина').grid(column=0, row=2, sticky='w', padx=10)
        self.width_entry.grid(pady=10, padx=10, column=0, row=3, sticky='w')
        ctk.CTkLabel(self.window_frame, text='Тема').grid(column=1, row=0, sticky='w', padx=10)
        self.light_btn.grid(column=1, row=1, sticky='w', padx=10)
        self.dark_btn.grid(column=1, row=3, sticky='w', padx=10)
        super().show()

    def submit(self):
        width = self.width.get()
        height = self.height.get()
        theme_var = self.theme.get()
        if theme_var:
            theme = 'light'
        else:
            theme = 'dark'
        theme_changed = theme != self.settings['window_settings']['theme']
        try:
            self.parent.geometry(f'{width}x{height}')
            ctk.set_appearance_mode(theme)
        except tk.TclError:
            MessageBox('Неверный формат', 'ERROR')
            return
        self.settings['window_settings']['width'] = width
        self.settings['window_settings']['height'] = height
        self.settings['window_settings']['theme'] = theme
        SettingsFileManager.write_settings(self.settings)
        if theme_changed:
            RestartQuestionBox(self.parent, 'Изменения вступят в силу после перезапуска приложения.\n Перезапустить?')


class SQLSettingsDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.title('Настройки SQL')
        self.dbname = tk.StringVar(value=self.settings['sql_settings']['db_name'])
        self.host = tk.StringVar(value=self.settings['sql_settings']['host'])
        self.port = tk.StringVar(value=self.settings['sql_settings']['port'])
        self.user_name = tk.StringVar(value=self.settings['sql_settings']['user_name'])
        self.password = tk.StringVar(value=self.settings['sql_settings']['password'])

        self.dbname_entry = ctk.CTkEntry(self.window_frame, textvariable=self.dbname,
                                         border_color=BTN_STANDARD)
        self.host_entry = ctk.CTkEntry(self.window_frame, textvariable=self.host,
                                       border_color=BTN_STANDARD)
        self.port_entry = ctk.CTkEntry(self.window_frame, textvariable=self.port,
                                       border_color=BTN_STANDARD)
        self.user_name_entry = ctk.CTkEntry(self.window_frame, textvariable=self.user_name,
                                            border_color=BTN_STANDARD)
        self.user_password_entry = ctk.CTkEntry(self.window_frame, textvariable=self.password,
                                                border_color=BTN_STANDARD)

        self.window_frame.rowconfigure(0, weight=1, uniform='a')
        self.window_frame.rowconfigure(1, weight=1, uniform='a')
        self.window_frame.rowconfigure(2, weight=1, uniform='a')
        self.window_frame.rowconfigure(3, weight=1, uniform='a')
        self.window_frame.rowconfigure(4, weight=1, uniform='a')
        self.window_frame.rowconfigure(5, weight=1, uniform='a')
        self.window_frame.columnconfigure(0, weight=1, uniform='a')
        self.window_frame.columnconfigure(1, weight=1, uniform='a')

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

        SettingsFileManager.write_settings(self.settings)

        RestartQuestionBox(self.parent, 'Изменения вступят в силу после перезапуска приложения.\n Перезапустить?')

    def show(self):
        ctk.CTkLabel(self.window_frame, text='Имя пользователя').grid(row=0, column=0, sticky='w', padx=10)
        self.user_name_entry.grid(padx=10, pady=5, row=1, column=0, sticky='w')
        ctk.CTkLabel(self.window_frame, text='Пароль').grid(row=2, column=0, sticky='w', padx=10)
        self.user_password_entry.grid(padx=10, pady=5, row=3, column=0, sticky='w')

        ctk.CTkLabel(self.window_frame, text='Имя БД').grid(row=4, column=0, sticky='w', padx=10)
        self.dbname_entry.grid(padx=10, pady=5, row=5, column=0, sticky='w')
        ctk.CTkLabel(self.window_frame, text='Хост').grid(row=0, column=1, sticky='w', padx=10)
        self.host_entry.grid(padx=10, pady=5, row=1, column=1, sticky='w')
        ctk.CTkLabel(self.window_frame, text='Порт').grid(row=2, column=1, sticky='w', padx=10)
        self.port_entry.grid(padx=10, pady=5, row=3, column=1, sticky='w')

        super().show()


class TableAttrsSettingsDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.title('Настройки аттрибутов')
        self.check_box_state = tk.BooleanVar(value=self.settings['add_attrs_if_not_exists'])
        self.check = ctk.CTkCheckBox(self.window_frame, variable=self.check_box_state,
                                     text='Добавлять аттрибут, если его не существует',
                                     fg_color=BTN_STANDARD,
                                     hover_color=BTN_HOVER, onvalue=True, offvalue=False)
        self.rowconfigure(0, weight=1, uniform='a')
        self.window_frame.columnconfigure(0, weight=1, uniform='a')
        self.window_frame.rowconfigure(0, weight=1, uniform='a')

    def show(self):
        self.check.grid(padx=10, pady=10, sticky='w', row=0, column=0)
        super().show()

    def submit(self):
        res_state = self.check_box_state.get()
        self.settings['add_attrs_if_not_exists'] = res_state
        SettingsFileManager.write_settings(self.settings)


class ProdTableSettingsDialogue(SettingsDialogue):
    def __init__(self, parent, settings):
        super().__init__(parent, settings)
        self.title('Настройки таблицы товаров')
        self.deletable = tk.BooleanVar(value=self.settings['prod_table_settings']['deletable'])
        self.editable = tk.BooleanVar(value=self.settings['prod_table_settings']['editable'])
        self.del_check = ctk.CTkCheckBox(self.window_frame, variable=self.deletable,
                                         fg_color=BTN_STANDARD,
                                         hover_color=BTN_HOVER, onvalue=True, offvalue=False,
                                         text='Разрешить удаление'
                                         )
        self.edit_check = ctk.CTkCheckBox(self.window_frame, variable=self.editable,
                                          fg_color=BTN_STANDARD,
                                          hover_color=BTN_HOVER, onvalue=True, offvalue=False,
                                          text='Разрешить редактирование'
                                          )
        self.rowconfigure(0, weight=2, uniform='a')
        self.window_frame.columnconfigure(0, weight=1, uniform='a')
        self.window_frame.rowconfigure(0, weight=1, uniform='a')
        self.window_frame.rowconfigure(1, weight=1, uniform='a')

    def show(self):
        self.edit_check.grid(padx=10, pady=10, row=0, column=0, sticky='w')
        self.del_check.grid(padx=10, pady=10, row=1, column=0, sticky='w')
        super().show()

    def submit(self):
        del_state = self.deletable.get()
        ed_state = self.editable.get()
        self.settings['prod_table_settings']['deletable'] = del_state
        self.settings['prod_table_settings']['editable'] = ed_state
        self.parent.storage_tab.data_frames[0].data_grid.deletable = del_state
        self.parent.storage_tab.data_frames[0].data_grid.editable = ed_state
        SettingsFileManager.write_settings(self.settings)


class ReadBarCodeDialogue(ctk.CTkToplevel):
    def __init__(self, parent, table: ProductsTable):
        super().__init__(parent)
        self.title('Пробить товар')
        self.parent = parent
        self.table = table
        self.bar_code_entry = ctk.CTkEntry(self, border_color=BTN_STANDARD)
        self.bind('<Return>', self.submit)
        self.grab_set()



    def delete(self):
        data = self.bar_code_entry.get()
        try:
            self.table.edit('sold', True, data)
            self.table.commit()
        except AdapterException as ex:
            self.table.rollback()
            MessageBox(ex, 'ERROR')
            return
        self.parent.data_grid.delete_row(int(data))

    def submit(self, event):
        self.delete()
        self.destroy()

    def show(self):
        ctk.CTkLabel(self, text='После ввода нажмите клавишу Enter').pack()
        self.bar_code_entry.pack()
        self.bar_code_entry.focus_force()

