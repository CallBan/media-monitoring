import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


class ExcelGeneration:
    def __init__(self, data, file_name):
        self.file_name = file_name
        # Создание DataFrame
        df = pd.DataFrame(data)
        df.to_excel(self.file_name, index=False)
        self.__styles_excel()

    def __styles_excel(self):
        wb = load_workbook(self.file_name)
        ws = wb.active

        header_font = Font(bold=True)
        header_alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True)

        # Дефолтные ширины колонок (можно по номеру или по заголовку)
        default_widths = {
            1: 18,  # 'Дата публикации'
            2: 40,  # 'Заголовок'
            3: 50,  # 'Краткая суть'
            4: 20,  # 'Источник'
            5: 50,  # 'Ссылка'
        }

        for col_idx, cell in enumerate(ws[1], start=1):
            cell.font = header_font
            cell.alignment = header_alignment

            # Применяем дефолтную ширину или авторасчёт
            if col_idx in default_widths:
                ws.column_dimensions[get_column_letter(
                    col_idx)].width = default_widths[col_idx]
            else:
                max_length = max(
                    len(str(c.value)) if c.value else 0 for c in ws[get_column_letter(col_idx)])
                ws.column_dimensions[get_column_letter(
                    col_idx)].width = max_length + 5

        center_align = Alignment(vertical="top", wrap_text=True)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = center_align

        wb.save(self.file_name)
        print(f"Файл сохранён: {self.file_name}")
