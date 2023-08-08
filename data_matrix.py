import os
import re
import subprocess
import threading

from typing import Union

import pylibdmtx.pylibdmtx as dmtx
from PIL import Image
from transliterate import translit

from misc import TypeIdentifier


class DataMatrixReaderException(Exception):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text


class InvalidMatrixValueException(DataMatrixReaderException):
    def __init__(self):
        super().__init__("ОШИБКА: Код неверный")


class DataMatrixReader:

    @staticmethod
    def read(data: str):
        re_mask = re.compile(r'(.+?)\.(.+?)\.(.+?)\.(.+?)\.(.+?)\.(\d{2}\.\d{2}\.\d{4})\.(.+?)\.(.+?)\.')
        tr_data = translit(data, 'ru').replace('Ноне', 'None')
        try:
            attrs = re.findall(re_mask, tr_data)[0]
            attrs = [TypeIdentifier.identify_parse(i) for i in attrs]
        except IndexError:
            raise InvalidMatrixValueException
        return attrs

    @staticmethod
    def print_matrix(path):
        return os.startfile(path, "print")

    @staticmethod
    def create_matrix(rec_id: Union[int, str], path: str):
        code = str(rec_id)

        encoded = dmtx.encode(code.encode('utf-8'))
        im = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
        im.save(path)

    @staticmethod
    def clear_matrix_folder(folder_path):
        for fp in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, fp))

    @staticmethod
    def delete_matrix(path):
        os.remove(path)

    @staticmethod
    def open_matrix(path):
        os.startfile(path)
