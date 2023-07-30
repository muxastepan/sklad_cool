import os
import re
import threading

import pylibdmtx.pylibdmtx as dmtx
from PIL import Image
from tables import *
from transliterate import translit


class DataMatrixReader:

    @staticmethod
    def read(data: str):
        tr_data = translit(data, 'ru').replace('Ноне', 'None')
        attrs = re.findall(r'(.+?)\.', tr_data)
        if not attrs:
            raise ValueError
        return attrs

    @staticmethod
    def print_matrix(paths):
        root = Image.new('RGB', (550, 400), '#FFFFFF')
        x = 50
        y = 50
        for path in paths:
            im = Image.open(path)
            norm_img = im.resize((30, 30))
            root.paste(norm_img, (x, y))
            x += 40
            if x >= 500:
                x = 0
                y += 40

        root.save('root.png')
        os.startfile('root.png', 'print')

    @staticmethod
    def create_matrix(data: Union[list, tuple]):
        code = ''

        for i in data:
            code += f'{str(i)}.'
        code = translit(code, 'ru', reversed=True)
        encoded = dmtx.encode(code.encode('utf-8'))
        im = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
        im.save(f"matrix\\{''.join(str(i) for i in data)}.png")

    @staticmethod
    def delete_matrix(path):
        os.remove(path)
