import decimal
import json
import os
import re
import datetime
import sys
from typing import Union, List, Tuple


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class DocHtmlWriter:
    @staticmethod
    def write_res_doc_to_html(year: str, month: str, headings: Union[List[str], Tuple[str]], data: Union[list, tuple]):
        with open(resource_path('doc.html'), 'w', encoding='utf8') as f:
            f.write(
                '''
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <link rel="stylesheet" href="doc_table_style.css">
                    </head>
                ''')
            f.write(
                f'''                          
                    <body>
                        <h1>Сводная ведомость для начисления заработной платы</h1>
                        <h1>
                            за {month} {year} года
                        </h1>
                ''')
            f.write(
                '''
                        <table>
                            <tr>
                                <th>№</th>
                ''')
            f.writelines([f"<th>{heading}</th>" for heading in headings])
            f.write('''
                            <th>Подпись</th>
                            </tr>                            
            ''')

            for i in range(len(data) - 1):
                row = data[i]
                f.write(f'''<tr>
                            <td>{i + 1}</td>''')
                f.writelines([f"<td>{cell}</td>" for cell in row])
                f.write('''
                        <td></td>
                        </tr>''')
            f.write(f'''<tr>
                    <td colspan="2">{data[-1][0]}</td>''')
            f.writelines([f"<td>{data[-1][i]}</td>" for i in range(1, len(data[-1]))])
            f.write("<td></td>"
                    "</tr>")

            f.write('''
            </table>
            </body>
            </html>
            ''')
            os.startfile('doc.html')


class SettingsFileManager:
    @staticmethod
    def read_settings():
        with open(resource_path('settings'), 'r') as f:
            settings = json.load(f)
        return settings

    @staticmethod
    def write_settings(settings):
        with open(resource_path('settings'), 'w') as f:
            json.dump(settings, f)


class TypeIdentifier:
    @staticmethod
    def identify_parse(value):
        if type(value) == bool:
            return value
        if value is None:
            return None
        elif value == 'None':
            return None
        elif type(value) == int:
            return value
        elif type(value) == datetime.date:
            return value.strftime('%d.%m.%Y')
        elif type(value) == decimal.Decimal:
            if value < 0:
                return 0
            return round(value, 2)
        elif all(re.match(r'\d+', i) for i in value):
            return int(value)
        elif re.match(r'\d{2}\.\d{2}\.\d{4}', value):
            return value
        elif re.match(r'\d+\.\d{2}', value):
            return decimal.Decimal(value)
        else:
            return str(value)
