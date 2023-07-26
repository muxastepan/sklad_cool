
from barcode import EAN13
from barcode.writer import ImageWriter

# Создаем объект штрих-кода
writer = ImageWriter()
code = '5901234123457'  # Текст, который нужно закодировать
ean = EAN13(code,writer=writer)

# Генерируем штрих-код и сохраняем его в файл
filename = ean.save('ean13_barcode')
print(f"Штрих-код сгенерирован и сохранен в файл {filename}")