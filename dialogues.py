from tables import *
from widgets import *


class AddDBRecordDialogue(tk.Toplevel):
    def __init__(self, parent, table: Table):
        super().__init__(parent)
        self.parent = parent
        self.table = table
        self.submit_button = tk.Button(self, text='Отправить', command=self.submit_close)
        self.value_entries = self._build()

    def _build(self):
        value_entries = []
        for i in range(1, len(self.table.column_names)):
            column = self.table.column_names[i]
            entry = AutoCompletionCombobox(self, values=self.table.columns_var_attrs[
                column] if column in self.table.columns_var_attrs else None)
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
        db_add = self.table.add(data)
        if db_add:
            self.table.update_var_attrs(data)
            self.parent.data_grid.add_row(self.table.select_last_id())
        else:
            MessageBox(self.parent, 'Введенные данные имеют неверный формат')
        self.destroy()

    def show(self):
        for i in range(1, len(self.table.column_headings)):
            tk.Label(self, text=self.table.column_headings[i]).pack()
            self.value_entries[i - 1].pack()
        self.submit_button.pack()


class AddProductRecordDialogue(AddDBRecordDialogue):
    def __init__(self, parent, products_table: ProductsTable):
        super().__init__(parent, products_table)

    def submit_close(self):
        data = []
        for i, entry in enumerate(self.value_entries):
            inp = entry.get()
            if inp:
                data.append(entry.get())
            else:
                data.append(None)
        try:
            laid_id = self.table.related_table.name_to_id(data[5])
            rolled_id = self.table.related_table.name_to_id(data[6])
        except NameError as ex:
            print(ex)
            MessageBox(self.parent, 'Поля не заполнены')
            self.destroy()
            return

        db_add = self.table.add(data[:5] + [laid_id, rolled_id] + data[7:])
        if db_add:
            self.parent.data_grid.add_row(self.table.select_last_id())
            self.table.update_var_attrs(data)
        else:
            MessageBox(self.parent, 'Введенные данные имеют неверный формат или не заполнены поля')
        self.destroy()

    def _build(self):
        value_entries = []
        for i in range(1, len(self.table.column_names)):
            entry = None
            column = self.table.column_names[i]
            if i != 5 and i != 8:
                if column in self.table.columns_var_attrs:
                    entry = AutoCompletionCombobox(self, values=[item for item in self.table.columns_var_attrs[
                        column] if item])
                else:
                    entry = AutoCompletionCombobox(self)
            elif i == 5:
                date = tk.StringVar(value=str(datetime.date.today()))
                entry = tk.Entry(self, textvariable=date)
            elif i == 8:
                art = tk.StringVar(value='test')
                entry = tk.Entry(self, textvariable=art)
            value_entries.append(entry)
        return value_entries


class AddEmployeeRecordDialogue(AddDBRecordDialogue):
    def __init__(self, parent, employees_table: EmployeesTable):
        super().__init__(parent, employees_table)


class SettingsDialogue(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.cancel_button = tk.Button(self, text='Отмена', command=self.cancel)
        self.save_button = tk.Button(self, text='Применить', command=self.submit)

    def show(self):
        self.save_button.pack(fill=tk.X)
        self.cancel_button.pack(fill=tk.X)

    def submit(self):
        pass

    def cancel(self):
        self.destroy()


class WindowSettingsDialogue(SettingsDialogue):
    def __init__(self, parent):
        super().__init__(parent)
        self.width_frame = tk.LabelFrame(self)
        self.height_frame = tk.LabelFrame(self)
        self.height_entry = tk.Entry(self.height_frame)
        self.width_entry = tk.Entry(self.width_frame)

    def show(self):
        self.width_frame.pack()
        self.height_frame.pack()
        tk.Label(self.height_frame, text='Высота').pack()
        self.height_entry.pack(pady=10, padx=10)
        tk.Label(self.width_frame, text='Ширина').pack()
        self.width_entry.pack(pady=10, padx=10)
        super().show()


class SQLSEttingsDialogue(SettingsDialogue):
    def __init__(self, parent):
        super().__init__(parent)
        self.db_frame = tk.LabelFrame(self)
        self.user_frame = tk.LabelFrame(self)
        self.dbname = tk.Entry(self.db_frame)
        self.host = tk.Entry(self.db_frame)
        self.port = tk.Entry(self.db_frame)
        self.user_name = tk.Entry(self.user_frame)
        self.user_password = tk.Entry(self.user_frame)

    def show(self):
        self.user_frame.pack()
        tk.Label(self.user_frame, text='Имя пользователя').pack()
        self.user_name.pack(padx=10, pady=10)
        tk.Label(self.user_frame, text='Пароль').pack()
        self.user_password.pack(padx=10, pady=10)

        self.db_frame.pack()
        tk.Label(self.db_frame, text='Имя БД').pack()
        self.dbname.pack(padx=10, pady=10)
        tk.Label(self.db_frame, text='Хост').pack()
        self.host.pack(padx=10, pady=10)
        tk.Label(self.db_frame, text='Порт').pack()
        self.port.pack(padx=10, pady=10)

        super().show()
