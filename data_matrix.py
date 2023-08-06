import os
import re

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
    def print_matrix(folder_path):
        os.startfile(folder_path)
        # root = Image.new('RGB', (550, 400), '#FFFFFF')
        # x = 50
        # y = 50
        # for path in paths:
        #     im = Image.open(path)
        #     norm_img = im.resize((30, 30))
        #     root.paste(norm_img, (x, y))
        #     x += 40
        #     if x >= 500:
        #         x = 0
        #         y += 40
        #
        # root.save('root.png')
        # os.startfile('root.png', 'print')

    @staticmethod
    def create_matrix(data: Union[list, tuple]):
        # Вариант с полными данными
        # code = ''
        #
        # for i in data:
        #     code += f'{str(i)}.'
        # code = translit(code, 'ru', reversed=True)
        # encoded = dmtx.encode(code.encode('utf-8'))
        # im = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
        # im.save(f"matrix\\{''.join(str(i) for i in data)}.png")

        # Вариант с ID
        code = str(data[0])

        encoded = dmtx.encode(code.encode('utf-8'))
        im = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
        im.save(f"matrix\\{''.join(str(i) for i in data)}.png")

    @staticmethod
    def clear_matrix(folder_path):
        for fp in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, fp))
