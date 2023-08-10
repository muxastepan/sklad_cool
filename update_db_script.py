import psycopg2
import tkinter as tk


class Page(tk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        """Some widgets here"""

    def show(self):
        """Pack widgets and self"""


class StartPage(Page):
    def __init__(self, parent):
        super().__init__(parent)
        self.text = tk.Label(self,
                             text='Вас приветсвует мастер обновления базы данных СКЛАД.\nВыберите метод установки:',
                             justify=tk.LEFT)
        self.ch_var = tk.BooleanVar(value=False)
        self.create = tk.Radiobutton(self,
                                     text='Создать БД или очистить существующую\n(ОСТОРОЖНО! Данные БД будут удалены навсегда)',
                                     variable=self.ch_var, value=True,
                                     justify=tk.LEFT)
        self.update = tk.Radiobutton(self, text='Обновить существующую БД', variable=self.ch_var, value=False, justify=tk.LEFT)

    def show(self):
        self.text.pack()
        self.update.pack()
        self.create.pack()
        self.grid(row=0, column=0, columnspan=2)


class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Обновление БД')
        self.next_btn = tk.Button(text='Далее', command=self.next_page)
        self.pages = [StartPage(self)]
        self.cur = 0

    def next_page(self):
        self.pages[self.cur].destroy()

    def run(self):
        self.next_btn.grid(row=1, column=1)
        self.pages[0].show()
        self.mainloop()


if __name__ == '__main__':
    app = MainFrame()
    app.run()
# conn = psycopg2.connect(dbname="postgres", user="postgres", password="12345")
# dbname = 'testdb'
# cur = conn.cursor()
# conn.autocommit = True
# cur.execute(f'''
# CREATE DATABASE {dbname}
#     WITH
#     OWNER = postgres
#     ENCODING = 'UTF8'
#     LC_COLLATE = 'Russian_Russia.1251'
#     LC_CTYPE = 'Russian_Russia.1251'
#     TABLESPACE = pg_default
#     CONNECTION LIMIT = -1
#     IS_TEMPLATE = False;
# ''')
# conn.autocommit = False
# conn.close()
#
# conn = psycopg2.connect(dbname=dbname, user="postgres", password="12345")
# cur = conn.cursor()
# cur.execute('''
# CREATE TABLE IF NOT EXISTS products_sizes
# (
#     sizes INT,
#     PRIMARY KEY(sizes)
# );'''
#             )
# cur.execute('''
# CREATE TABLE IF NOT EXISTS products_types
# (
#     types VARCHAR,
#     PRIMARY KEY(types),
#     CONSTRAINT check_types CHECK
#     (types SIMILAR TO
#     '[а-яА-Я]*')
# );'''
#             )
# cur.execute('''
# CREATE TABLE IF NOT EXISTS products_subtypes
# (
#     subtypes VARCHAR,
#     PRIMARY KEY(subtypes),
#     CONSTRAINT check_subtypes CHECK
#     (subtypes SIMILAR TO
#     '[а-яА-Я]*')
# );'''
#             )
# cur.execute('''
# CREATE TABLE IF NOT EXISTS products_colors
# (
#     colors VARCHAR,
#     PRIMARY KEY(colors),
#     CONSTRAINT check_colors CHECK
#     (colors SIMILAR TO
#     '[а-яА-Я]*')
#
# );'''
#             )
# cur.execute('''
# CREATE TABLE IF NOT EXISTS employees
# (
#     employee_name VARCHAR NOT NULL,
#     PRIMARY KEY(employee_name),
#     CONSTRAINT check_name CHECK
#     (employee_name SIMILAR TO
#     '[а-яА-Я]*')
#
# )''')
# cur.execute('''
# CREATE TABLE IF NOT EXISTS products
# (
#     product_id SERIAL,
#     product_size INT NOT NULL,
#     product_type VARCHAR NOT NULL,
#     product_subtype VARCHAR,
#     product_color VARCHAR NOT NULL,
#     product_date_stored DATE NOT NULL,
#     laid_by VARCHAR NOT NULL,
#     rolled_by VARCHAR NOT NULL,
#     matrix_dir VARCHAR NOT NULL,
#     PRIMARY KEY(product_id),
#     CONSTRAINT fk_product_size
#         FOREIGN KEY(product_size)
#         REFERENCES products_sizes(sizes),
#     CONSTRAINT fk_product_type
#         FOREIGN KEY(product_type)
#         REFERENCES products_types(types),
#     CONSTRAINT fk_product_subtype
#         FOREIGN KEY(product_subtype)
#         REFERENCES products_subtypes(subtypes),
#     CONSTRAINT fk_product_color
#         FOREIGN KEY(product_color)
#         REFERENCES products_colors(colors),
#     CONSTRAINT fk_laid_name
#         FOREIGN KEY(laid_by)
#         REFERENCES employees(employee_name),
#     CONSTRAINT fk_rolled_name
#         FOREIGN KEY(rolled_by)
#         REFERENCES employees(employee_name),
#     CONSTRAINT check_type CHECK
#     (product_type SIMILAR TO
#     '[а-яА-Я]*'),
#     CONSTRAINT check_subtype CHECK
#     (product_subtype SIMILAR TO
#     '[а-яА-Я]*'),
#     CONSTRAINT check_color CHECK
#     (product_color SIMILAR TO
#     '[а-яА-Я]*')
# );'''
#             )
#
# conn.commit()
