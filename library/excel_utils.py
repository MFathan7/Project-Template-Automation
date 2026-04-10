import os
import logging
import pandas as pd
import xlwings as xw

logger = logging.getLogger(__name__)

class ExcelApplicationScope:
    def __init__(self, file_path: str, visible: bool = False, create_new_file: bool = True, save_changes: bool = True):
        self.file_path = os.path.abspath(file_path)
        self.visible = visible
        self.create_new_file = create_new_file
        self.save_changes = save_changes
        self.app = None
        self.wb = None

    def __enter__(self):
        #logger.info(f"Excel Application Scope: {self.file_path}")
        
        # Buka instance aplikasi Excel
        self.app = xw.App(visible=self.visible, add_book=False)
        
        # Cek apakah file ada
        if not os.path.exists(self.file_path):
            if self.create_new_file:
                #logger.info("File tidak ditemukan. Membuat file Excel baru...")
                self.wb = self.app.books.add()
                self.wb.save(self.file_path)
            else:
                self.app.quit()
                raise FileNotFoundError(f"File {self.file_path} is not found (create_new_file=False)")
        else:
            self.wb = self.app.books.open(self.file_path)
            
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.wb:
            if self.save_changes:
                self.wb.save()
                #logger.info("Perubahan pada Excel berhasil disimpan.")
            self.wb.close()
            
        if self.app:
            self.app.quit()
            #logger.info("Excel Application Scope ditutup.")

    # ==========================================
    # ACTIVITIES: Read Range & Write Range
    # ==========================================
    def read_range(self, sheet_name: str, range_address: str = "A1", has_headers: bool = True) -> pd.DataFrame:
        
        if sheet_name in [sheet.name for sheet in self.wb.sheets]:
            sheet = self.wb.sheets[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' tidak ditemukan!")

        if range_address == "":
            # Baca seluruh Used Range (mengabaikan putusnya tabel akibat baris kosong)
            df = sheet.used_range.options(pd.DataFrame, index=False, header=has_headers).value
        elif ":" in range_address:
            # Baca spesifik range
            df = sheet.range(range_address).options(pd.DataFrame, index=False, header=has_headers).value
        else:
            # Baca dengan expand (berhenti jika ada baris/kolom kosong total)
            df = sheet.range(range_address).options(pd.DataFrame, index=False, header=has_headers, expand='table').value
        
        # Jika file kosong, return dataframe kosong
        if df is None or df.empty:
            return pd.DataFrame()
            
        return df

    def write_range(self, sheet_name: str, data: pd.DataFrame, start_cell: str = "A1", add_headers: bool = True):
        #logger.info(f"Menulis data ke sheet '{sheet_name}' mulai dari cell '{start_cell}'")
        
        # Buat sheet baru jika belum ada
        sheet_names = [sheet.name for sheet in self.wb.sheets]
        if sheet_name not in sheet_names:
            sheet = self.wb.sheets.add(sheet_name)
        else:
            sheet = self.wb.sheets[sheet_name]

        sheet.range(start_cell).options(index=False, header=add_headers).value = data