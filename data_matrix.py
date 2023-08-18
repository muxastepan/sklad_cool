import os

from typing import Union

import pylibdmtx.pylibdmtx as dmtx
import win32con
import win32print
import win32ui
from PIL import Image, ImageWin


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
    def print_matrix(path):
        img = Image.open(path, 'r')

        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(win32print.GetDefaultPrinter())

        horzres = hdc.GetDeviceCaps(win32con.HORZRES)
        vertres = hdc.GetDeviceCaps(win32con.VERTRES)

        img_width = img.size[0]
        img_height = img.size[1]

        hdc.SetMapMode(win32con.MM_ISOTROPIC)
        hdc.SetWindowExt((img_width, img_height))
        hdc.SetViewportExt((horzres, vertres))

        hdc.SetWindowOrg((0, 0))

        try:
            hdc.StartDoc('Result')
        except win32ui.error:
            return
        hdc.StartPage()

        dib = ImageWin.Dib(img)
        dib.draw(hdc.GetHandleOutput(), (15, 5, 45, 35))

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()

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
        return os.startfile(path, "print")


