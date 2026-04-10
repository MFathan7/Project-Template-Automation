import logging
import pandas as pd

logger = logging.getLogger(__name__)

# ==========================================
# DATATABLE ACTIVITIES
# Note: Selalu assign (timpa) return value ke variabel asal.
# Contoh: dt = filter_datatable(dt, ...)
# ==========================================

def filter_datatable(df: pd.DataFrame, column_name: str, operator: str, value: any) -> pd.DataFrame:
    """
    Operator yang didukung: "==", "!=", ">", "<", ">=", "<=", "contains"
    """
    #logger.info(f"🗃️ FILTER DATATABLE: Menyaring kolom '{column_name}' {operator} '{value}'")
    
    try:
        if operator == "==":
            return df[df[column_name] == value].copy()
        elif operator == "!=":
            return df[df[column_name] != value].copy()
        elif operator == ">":
            return df[df[column_name] > value].copy()
        elif operator == "<":
            return df[df[column_name] < value].copy()
        elif operator == ">=":
            return df[df[column_name] >= value].copy()
        elif operator == "<=":
            return df[df[column_name] <= value].copy()
        elif operator.lower() == "contains":
            # Bikin case-insensitive contain
            return df[df[column_name].astype(str).str.contains(str(value), case=False, na=False)].copy()
        else:
            raise ValueError(f"Operator '{operator}' tidak didukung.")
    except KeyError:
        logger.error(f"❌ FILTER GAGAL: Kolom '{column_name}' tidak ditemukan.")
        raise

def sort_datatable(df: pd.DataFrame, column_name: str, ascending: bool = True) -> pd.DataFrame:
    order_str = "Ascending" if ascending else "Descending"
    #logger.info(f"🗃️ SORT DATATABLE: Mengurutkan kolom '{column_name}' secara {order_str}")
    
    return df.sort_values(by=column_name, ascending=ascending, ignore_index=True).copy()

def add_data_row(df: pd.DataFrame, row_data: list) -> pd.DataFrame:
    """
    row_data adalah list berisi nilai per kolom (contoh: ["Budi", "Aktif", 5000]).
    """
    #logger.info(f"🗃️ ADD DATA ROW: Menambahkan baris baru {row_data}")
    
    if len(row_data) != len(df.columns):
        raise ValueError("Jumlah data tidak sesuai dengan jumlah kolom di DataTable.")
    
    df.loc[len(df)] = row_data
    return df

def remove_data_row(df: pd.DataFrame, row_index: int) -> pd.DataFrame:
    #logger.info(f"🗃️ REMOVE DATA ROW: Menghapus baris ke-{row_index}")
    
    if row_index < 0 or row_index >= len(df):
        raise IndexError(f"Index baris {row_index} di luar batas tabel.")
        
    df_new = df.drop(index=row_index).reset_index(drop=True)
    return df_new

def clear_datatable(df: pd.DataFrame) -> pd.DataFrame:
    #logger.info("🗃️ CLEAR DATATABLE: Mengosongkan isi tabel")
    # Mengembalikan dataframe kosong dengan struktur kolom yang sama
    return df.iloc[0:0].copy()

def merge_datatable(df_destination: pd.DataFrame, df_source: pd.DataFrame) -> pd.DataFrame:
    #logger.info("🗃️ MERGE DATATABLE: Menggabungkan dua tabel")
    # ignore_index=True mereset nomor urut agar tidak berantakan
    return pd.concat([df_destination, df_source], ignore_index=True)