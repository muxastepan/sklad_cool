from typing import Union
import psycopg2
import psycopg2.errors


class AdapterException(Exception):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text


class AdapterRecNotExistException(AdapterException):
    def __init__(self):
        super().__init__("ОШИБКА: Записи не существует")


class AdapterFKException(AdapterException):
    def __init__(self, text):
        super().__init__(text)


class AdapterCurSecException(AdapterException):
    def __init__(self):
        super().__init__("ОШИБКА:  текущее значение для последовательности ещё не определено в этом сеансе")


class AdapterConnectionException(AdapterException):
    def __init__(self):
        super().__init__("ОШИБКА: Не удалось подключиться к базе данных, проверьте настройки подключения")


class AdapterWrongInputException(AdapterException):
    def __init__(self):
        super().__init__("ОШИБКА: Введенные данные имеют неверный формат")


class AdapterNotNullException(AdapterException):
    def __init__(self):
        super().__init__("ОШИБКА: Поле не может быть пустым")


class AdapterUniqueValueException(AdapterException):
    def __init__(self):
        super().__init__("ОШИБКА: Поле должно содержать только уникальные значения")


class Adapter:
    def __init__(self, dbname: str, user='postgres', password='12345', port='5432', host='localhost'):
        try:
            self.con = psycopg2.connect(dbname=dbname, user=user, password=password, port=port, host=host)
        except psycopg2.OperationalError:
            raise AdapterConnectionException
        self.cur = self.con.cursor()

    def commit(self):
        self.con.commit()

    def rollback(self):
        self.con.rollback()

    def insert(self, table_name: str, data_list: Union[list, tuple], column_order: tuple = None,
               if_not_exist: bool = False):
        query = f"INSERT INTO {table_name} "
        if column_order:
            if len(column_order) == 1:
                query += f"({column_order[0]}) "
            else:
                query += f"({','.join(column_order)}) "

        values_placeholder = f"({'%s,' * (len(data_list) - 1) + '%s'})"
        query += f"VALUES {values_placeholder}"
        if if_not_exist:
            query += " ON CONFLICT DO NOTHING"
        try:
            self.cur.execute(query,
                             data_list)
        except psycopg2.errors.UniqueViolation as ex:
            raise AdapterUniqueValueException
        except psycopg2.errors.NotNullViolation:
            raise AdapterNotNullException
        except psycopg2.errors.CheckViolation as ex:
            print(ex)
            raise AdapterWrongInputException
        except psycopg2.errors.ForeignKeyViolation as ex:
            raise AdapterFKException(repr(ex))
        except psycopg2.errors.DatatypeMismatch:
            raise AdapterWrongInputException
        except psycopg2.DataError:
            raise AdapterWrongInputException

    def select(self, table_name, columns: Union[list, tuple] = None, distinct=False, conditions: str = None,
               order: Union[list, tuple] = None, limit=None):
        query = "SELECT "
        if distinct:
            query += 'DISTINCT '
        if columns:
            query += ','.join(columns) + ' '
        else:
            query += '* '

        query += f'FROM {table_name}'

        if conditions:
            query += f' WHERE {conditions}'

        if order:
            query += f' ORDER BY {order[1]}'
            if order[0]:
                query += ' ASC'
            else:
                query += ' DESC'
        if limit:
            query += f' LIMIT {limit}'
        try:
            self.cur.execute(query)
        except psycopg2.DataError:
            self.con.rollback()
            raise ValueError
        data = self.cur.fetchall()
        if not data:
            raise AdapterRecNotExistException
        return data

    def delete(self, table_name: str, p_key_name: str, p_key_value: str):
        try:
            self.cur.execute(
                f"DELETE FROM {table_name} WHERE {p_key_name} = (%s)", (p_key_value,)
            )
        except psycopg2.DataError:
            raise AdapterWrongInputException
        except psycopg2.errors.ForeignKeyViolation as ex:
            raise AdapterFKException(repr(ex))

    def update(self, table_name: str, column_name: str, column_value: str, rec_id: str = None,
               column_id_name: str = None):
        query = f"UPDATE {table_name} SET {column_name}=%s"
        if rec_id and column_id_name:
            query += f" WHERE {column_id_name} = %s"
        try:
            self.cur.execute(query, (column_value, rec_id))
        except psycopg2.errors.UniqueViolation:
            raise AdapterUniqueValueException
        except psycopg2.errors.NotNullViolation:
            raise AdapterNotNullException
        except psycopg2.errors.CheckViolation:
            raise AdapterWrongInputException
        except psycopg2.errors.ForeignKeyViolation as ex:
            raise AdapterFKException(repr(ex))
        except psycopg2.DataError:
            raise AdapterWrongInputException
        except psycopg2.errors.DatatypeMismatch:
            raise AdapterWrongInputException

    def next_sequence(self, seq_name):
        query = f"SELECT NEXTVAL('{seq_name}')"
        self.cur.execute(query)
        data = self.cur.fetchall()
        self.con.commit()
        return data[0][0]

    def cur_sequence(self, seq_name):
        query = f"SELECT CURRVAL('{seq_name}')"
        try:
            self.cur.execute(query)
        except psycopg2.errors.ObjectNotInPrerequisiteState:
            raise AdapterCurSecException
        data = self.cur.fetchall()
        self.con.commit()
        return data[0][0]
