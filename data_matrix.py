import re

import pylibdmtx.pylibdmtx as dmtx
from PIL import Image
from tables import *
from transliterate import translit


class DataMatrixReader:

    @staticmethod
    def read(data: str):
        tr_data = translit(data, 'ru').replace('Ноне', 'None')
        attrs = re.findall(r'(.+?)\.', tr_data)
        return attrs

    @staticmethod
    def create_matrix(data: Union[list, tuple]):
        code = ''

        for i in data:
            code += f'{str(i)}.'
        code = translit(code, 'ru', reversed=True)
        encoded = dmtx.encode(code.encode('utf-8'))
        im = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
        im.save(f"matrix\\{''.join(str(i) for i in data)}.png")
