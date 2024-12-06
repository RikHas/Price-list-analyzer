import os
import csv
from operator import itemgetter
import chardet  # Для определения кодировки


class PriceList:
    def __init__(self):
        self.data = []  # Список для хранения данных из всех файлов
        self.result = ''  # Результаты поиска
        self.name_length = 0  # Длина самого длинного названия товара для форматирования вывода

    def _detect_encoding(self, file_path):
        """
        Определяет кодировку файла.
        """
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)  # Читаем первые 10 KB файла
        result = chardet.detect(raw_data)
        return result['encoding']

    def _detect_delimiter(self, file_path, encoding):
        """
        Определяет разделитель (`,` или `;`) в файле CSV.
        """
        with open(file_path, encoding=encoding) as file:
            sample = file.readline()
        if ';' in sample and ',' not in sample:
            return ';'
        return ','

    def load_prices(self, file_path=''):
        """
        Сканирует указанный каталог. Ищет файлы со словом price в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        """
        for file_name in os.listdir(file_path):
            if "price" in file_name and file_name.endswith(".csv"):
                file_full_path = os.path.join(file_path, file_name)
                try:
                    encoding = self._detect_encoding(file_full_path)  # Определяем кодировку файла
                    delimiter = self._detect_delimiter(file_full_path, encoding)
                    with open(file_full_path, encoding=encoding) as file:
                        reader = csv.reader(file, delimiter=delimiter)
                        headers = next(reader)

                        # Определяем столбцы
                        col_name, col_price, col_weight = self._search_product_price_weight(headers)
                        if col_name is not None and col_price is not None and col_weight is not None:
                            for row in reader:
                                try:
                                    name = row[col_name]
                                    price = float(row[col_price])
                                    weight = float(row[col_weight])
                                    price_per_kg = price / weight
                                    self.data.append({
                                        "name": name,
                                        "price": price,
                                        "weight": weight,
                                        "file": file_name,
                                        "price_per_kg": price_per_kg
                                    })
                                    self.name_length = max(self.name_length, len(name))
                                except (ValueError, IndexError):
                                    continue
                except Exception as e:
                    print(f"Ошибка при обработке файла {file_name}: {e}")

    def _search_product_price_weight(self, headers):
        """
        Возвращает индексы столбцов для названия, цены и веса.
        """
        name_columns = {"товар", "название", "наименование", "продукт"}
        price_columns = {"цена", "розница"}
        weight_columns = {"вес", "масса", "фасовка"}

        col_name = col_price = col_weight = None
        for i, header in enumerate(headers):
            header = header.strip().lower()
            if header in name_columns:
                col_name = i
            elif header in price_columns:
                col_price = i
            elif header in weight_columns:
                col_weight = i
        return col_name, col_price, col_weight

    def export_to_html(self, fname='output.html'):
        """
        Экспортирует данные в HTML-файл.
        """
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table border="1">
                <tr>
                    <th>№</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Вес</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for idx, item in enumerate(self.data, start=1):
            html_content += f'''
                <tr>
                    <td>{idx}</td>
                    <td>{item["name"]}</td>
                    <td>{item["price"]}</td>
                    <td>{item["weight"]}</td>
                    <td>{item["file"]}</td>
                    <td>{item["price_per_kg"]:.2f}</td>
                </tr>
            '''
        html_content += '''
            </table>
        </body>
        </html>
        '''
        with open(fname, "w", encoding="utf-8") as file:
            file.write(html_content)

    def find_text(self, text):
        """
        Поиск товаров по тексту с сортировкой по цене за килограмм.
        """
        result = [item for item in self.data if text.lower() in item["name"].lower()]
        result = sorted(result, key=itemgetter("price_per_kg"))
        return result


if __name__ == "__main__":
    pm = PriceList()
    pm.load_prices(
        file_path="D:\\PythonProject\\pythonProjectPZ\\Практическое задание _Анализатор прайс-листов._"
    )  # Путь к папке с файлами

    while True:
        search_text = input("Введите текст для поиска (или 'exit' для выхода): ")
        if search_text.lower() == "exit":
            print("Работа завершена.")
            break
        search_results = pm.find_text(search_text)
        if not search_results:
            print("Ничего не найдено.")
        else:
            print(f"\n{'№':<4}{'Наименование':<{pm.name_length + 2}}"
                  f"{'Цена':<8}{'Вес':<8}{'Файл':<20}{'Цена за кг.':<10}")
            for idx, item in enumerate(search_results, start=1):
                print(f"{idx:<4}{item['name']:<{pm.name_length + 2}}"
                      f"{item['price']:<8}{item['weight']:<8}"
                      f"{item['file']:<20}{item['price_per_kg']:<10.2f}")

    pm.export_to_html()
