import psycopg2
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class ProgressFrame(tk.Frame):
    def __init__(self, parent, pw: str, dbname: str, create: bool):
        super().__init__(parent)
        self.create = create
        self.dbname = dbname
        self.pw = pw
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=100, value=0)
        self.parent = parent

    def show(self):
        self.grid(row=4, column=0,
                  sticky=tk.NE)
        self.progress_bar.pack()
        self.__run_main_script()

    def __run_create_script(self):
        conn = psycopg2.connect(dbname="postgres", user="postgres", password=self.pw)
        cur = conn.cursor()
        conn.autocommit = True
        cur.execute(f'''
        CREATE DATABASE {self.dbname}
            WITH
            OWNER = postgres
            ENCODING = 'UTF8'
            LC_COLLATE = 'Russian_Russia.1251'
            LC_CTYPE = 'Russian_Russia.1251'
            TABLESPACE = pg_default
            CONNECTION LIMIT = -1
            IS_TEMPLATE = False;
        ''')
        conn.autocommit = False
        conn.close()

    def __run_main_script(self):
        self.progress_bar['value'] = 0
        try:
            if self.create:
                self.__run_create_script()
            self.progress_bar['value'] += 8.34
            conn = psycopg2.connect(dbname=self.dbname, user="postgres", password=self.pw)
            cur = conn.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS products_sizes
            (
                sizes INT,
                PRIMARY KEY(sizes)
            );'''
                        )

            self.progress_bar['value'] += 8.34
            cur.execute('''
            CREATE TABLE IF NOT EXISTS salary_per_size
            (
                size INT,
                salary INT NOT NULL,
                CONSTRAINT fk_size
                    FOREIGN KEY(size)
                    REFERENCES products_sizes(sizes)
            );
            ''')

            self.progress_bar['value'] += 8.34
            cur.execute('''
            CREATE TABLE IF NOT EXISTS products_types
            (
                types VARCHAR,
                PRIMARY KEY(types),
                CONSTRAINT check_types CHECK
                (types SIMILAR TO
                '[а-яА-Я]*')
            );'''
                        )

            self.progress_bar['value'] += 8.34
            cur.execute('''
            CREATE TABLE IF NOT EXISTS products_subtypes
            (
                subtypes VARCHAR,
                PRIMARY KEY(subtypes),
                CONSTRAINT check_subtypes CHECK
                (subtypes SIMILAR TO
                '[а-яА-Я]*')
            );'''
                        )

            self.progress_bar['value'] += 8.34
            cur.execute('''
            CREATE TABLE IF NOT EXISTS products_colors
            (
                colors VARCHAR,
                PRIMARY KEY(colors),
                CONSTRAINT check_colors CHECK
                (colors SIMILAR TO
                '[а-яА-Я]*')

            );'''
                        )

            self.progress_bar['value'] += 8.34
            cur.execute('''
            CREATE TABLE IF NOT EXISTS employees
            (
                employee_name VARCHAR NOT NULL,
                PRIMARY KEY(employee_name),
                CONSTRAINT check_name CHECK
                (employee_name SIMILAR TO
                '[а-яА-Я ]*')

            )''')

            self.progress_bar['value'] += 8.34
            cur.execute('''
            CREATE TABLE IF NOT EXISTS products
            (
                product_id SERIAL,
                product_size INT NOT NULL,
                product_type VARCHAR NOT NULL,
                product_subtype VARCHAR,
                product_color VARCHAR NOT NULL,
                product_date_stored DATE NOT NULL,
                laid_by VARCHAR NOT NULL,
                rolled_by VARCHAR NOT NULL,
                matrix_dir VARCHAR NOT NULL,
                sold BOOLEAN,
                PRIMARY KEY(product_id),
                CONSTRAINT fk_product_size
                    FOREIGN KEY(product_size)
                    REFERENCES products_sizes(sizes),
                CONSTRAINT fk_product_type
                    FOREIGN KEY(product_type)
                    REFERENCES products_types(types),
                CONSTRAINT fk_product_subtype
                    FOREIGN KEY(product_subtype)
                    REFERENCES products_subtypes(subtypes),
                CONSTRAINT fk_product_color
                    FOREIGN KEY(product_color)
                    REFERENCES products_colors(colors),
                CONSTRAINT fk_laid_name
                    FOREIGN KEY(laid_by)
                    REFERENCES employees(employee_name),
                CONSTRAINT fk_rolled_name
                    FOREIGN KEY(rolled_by)
                    REFERENCES employees(employee_name),
                CONSTRAINT check_type CHECK
                (product_type SIMILAR TO
                '[а-яА-Я]*'),
                CONSTRAINT check_subtype CHECK
                (product_subtype SIMILAR TO
                '[а-яА-Я]*'),
                CONSTRAINT check_color CHECK
                (product_color SIMILAR TO
                '[а-яА-Я]*')
            );'''
                        )

            self.progress_bar['value'] += 8.34
            cur.execute('''
            CREATE OR REPLACE function f_add_col(_tbl regclass, _col  text, _type regtype)
                  RETURNS bool
                  LANGUAGE plpgsql AS
                $func$
                BEGIN
                   IF EXISTS (SELECT FROM pg_attribute
                              WHERE  attrelid = _tbl
                              AND    attname  = _col
                              AND    NOT attisdropped) THEN
                      RETURN false;
                   ELSE
                      EXECUTE format('ALTER TABLE %s ADD COLUMN %I %s', _tbl, _col, _type);
                      RETURN true;
                   END IF;
                END
                $func$;
            SELECT f_add_col('salary_per_size','type','varchar');            

            ALTER TABLE salary_per_size DROP CONSTRAINT IF EXISTS  salary_per_size_type_fkey; 

            ALTER TABLE IF EXISTS salary_per_size
                ADD CONSTRAINT salary_per_size_type_fkey
                FOREIGN KEY (type)
                REFERENCES products_types(types);
            ALTER TABLE salary_per_size DROP CONSTRAINT IF EXISTS  salary_per_size_type_size_unique; 
            ALTER TABLE IF EXISTS salary_per_size
                ADD CONSTRAINT salary_per_size_type_size_unique
                UNIQUE (type,size);
            ''')

            self.progress_bar['value'] += 8.34
            cur.execute('''
                        CREATE OR REPLACE VIEW emp_names
                            AS SELECT employee_name FROM employees
                        ''')

            self.progress_bar['value'] += 8.34
            cur.execute('''
            SELECT f_add_col('employees','payment','int');
            SELECT f_add_col('employees','tax','int');
            SELECT f_add_col('employees','bonus','int');            
            ''')

            self.progress_bar['value'] += 8.34
            cur.execute('''
                            DROP VIEW  IF EXISTS by_recs CASCADE;
                            CREATE OR REPLACE VIEW by_recs
                            AS SELECT product_size, product_type,
                            laid_by,rolled_by,
                            product_date_stored,
                            salary*0.55 as l_salary,
                            salary*0.45 as r_salary
                            FROM products
                            LEFT JOIN salary_per_size
                            ON (products.product_size,products.product_type)=(salary_per_size.size,salary_per_size.type);
                        ''')

            self.progress_bar['value'] += 8.34
            cur.execute('''                           
                            CREATE OR REPLACE VIEW all_recs_by_emp
                            AS SELECT product_date_stored,product_size,product_type,laid_by as emp_name,l_salary as salary
                            FROM by_recs
                            UNION ALL
                            SELECT product_date_stored,product_size,product_type,rolled_by,r_salary
                            FROM by_recs;
                        ''')

            conn.commit()
            conn.close()
        except Exception as ex:
            ex = repr(ex)
            tk.messagebox.showerror(ex, ex)
            self.destroy()
            return

        tk.messagebox.showinfo('Завершено', 'Программа завершена')
        self.destroy()
        self.parent.destroy()


class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Обновление БД')
        self.pw_entry = tk.Entry(self)
        self.name_entry = tk.Entry(self)
        self.create_var = tk.BooleanVar(value=False)
        self.create_radio_btn = tk.Radiobutton(text='Создать БД', variable=self.create_var, value=True)
        self.update_radio_btn = tk.Radiobutton(text='БД уже есть', variable=self.create_var, value=False)
        self.submit_btn = tk.Button(text='Старт', command=self.run)

    def run(self):
        ProgressFrame(self, self.pw_entry.get(), self.name_entry.get(), self.create_var.get()).show()

    def show(self):
        tk.Label(text='Пароль:').grid(row=0, column=0)
        self.pw_entry.grid(row=1, column=0)
        tk.Label(text='Имя:').grid(row=2, column=0)
        self.name_entry.grid(row=3, column=0)

        self.update_radio_btn.grid(row=1, column=1)
        self.create_radio_btn.grid(row=2, column=1)
        self.submit_btn.grid(row=3, column=1)

        self.mainloop()


if __name__ == '__main__':
    app = Root()
    app.show()