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

        landscape = horzres > vertres

        if landscape:
            if img.size[1] > img.size[0]:
                img = img.rotate(90, expand=True)
        else:
            if img.size[1] < img.size[0]:
                img = img.rotate(90, expand=True)

        img_width = img.size[0]
        img_height = img.size[1]

        if landscape:
            ratio = vertres / horzres
            max_width = img_width
            max_height = (int)(img_width * ratio)
        else:
            ratio = horzres / vertres
            max_height = img_height
            max_width = (int)(max_height * ratio)

        hdc.SetMapMode(win32con.MM_ISOTROPIC)
        hdc.SetViewportExt((horzres, vertres))
        hdc.SetWindowExt((max_width, max_height))

        offset_x = (int)((max_width - img_width) / 2)
        offset_y = (int)((max_height - img_height) / 2)
        hdc.SetWindowOrg((-offset_x, -offset_y))

        try:
            hdc.StartDoc('Result')
        except win32ui.error:
            return
        hdc.StartPage()

        dib = ImageWin.Dib(img)
        dib.draw(hdc.GetHandleOutput(), (0, 0, img_width, img_height))

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
