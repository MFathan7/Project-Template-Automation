import logging, re
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class DatabaseScope:
    """
        db_type: 'sqlserver', 'mysql', 'postgresql', 'sqlite', atau 'custom'
        Untuk SQL Server Windows Auth, cukup kosongkan username & password.
    """
    def __init__(self, db_type: str = "custom", server: str = "", database: str = "", 
                 username: str = "", password: str = "", connection_string: str = "", 
                 driver: str = "ODBC Driver 17 for SQL Server"): # <-- Update Default Driver ke versi modern
        self.db_type = db_type.lower()
        self.engine = None
        self.connection = None

        safe_password = urllib.parse.quote_plus(password) if password else ""

        if self.db_type == "custom":
            if not connection_string:
                raise ValueError("Untuk db_type 'custom', parameter connection_string wajib diisi.")
            self.connection_string = connection_string
        elif self.db_type == "sqlite":
            if not database:
                raise ValueError("Untuk SQLite, parameter 'database' (path file) wajib diisi.")
            self.connection_string = f"sqlite:///{database}"
        elif self.db_type == "sqlserver":
            driver_fmt = driver.replace(" ", "+")
            if username and password:
                self.connection_string = f"mssql+pyodbc://{username}:{safe_password}@{server}/{database}?driver={driver_fmt}"
            else:
                self.connection_string = f"mssql+pyodbc://@{server}/{database}?driver={driver_fmt}&Trusted_Connection=yes"
        elif self.db_type == "mysql":
            self.connection_string = f"mysql+pymysql://{username}:{safe_password}@{server}/{database}"
        elif self.db_type in ["postgresql", "postgres"]:
            self.connection_string = f"postgresql://{username}:{safe_password}@{server}/{database}"
        else:
            raise ValueError(f"Tipe database '{db_type}' tidak didukung.")

    def connect(self):
        """Membuka koneksi database."""
        if self.connection is not None:
            logger.warning("Koneksi sudah terbuka.")
            return self
            
        #logger.info(f"🛢️ CONNECT DATABASE: Membuka koneksi ke {self.db_type.upper()}...")
        try:
            # Tambahkan kwargs khusus untuk performa Bulk Insert di SQL Server
            engine_kwargs = {}
            if self.db_type == "sqlserver":
                engine_kwargs["fast_executemany"] = True # <-- Rahasia kecepatan Bulk Insert
                
            self.engine = create_engine(self.connection_string, **engine_kwargs)
            self.connection = self.engine.connect()
            #logger.info("   ↳ Koneksi berhasil ✅")
            return self
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal connect database: {e}")
            raise

    def disconnect(self):
        """Menutup koneksi database."""
        #logger.info("🛑 DISCONNECT DATABASE: Menutup koneksi database.")
        if self.connection:
            self.connection.close()
            self.connection = None
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # ==========================================
    # DATABASE ACTIVITIES
    # ==========================================
    def run_query(self, query: str, parameters: dict = None) -> pd.DataFrame:
        """Menjalankan SELECT dan mengembalikan DataFrame / Datatable."""
        if not self.connection:
            raise ConnectionError("Koneksi belum dibuka! Panggil .connect() terlebih dahulu.")
            
        try:
            df = pd.read_sql_query(text(query), self.connection, params=parameters)
            #logger.info(f"   ↳ Berhasil mengambil {len(df)} baris data ✅")
            return df
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal eksekusi query: {e}")
            raise

    def execute_non_query(self, query: str, parameters: dict = None) -> int:
        """Menjalankan INSERT/UPDATE/DELETE (satu perintah) dan mengembalikan rowcount."""
        if not self.connection:
            raise ConnectionError("Koneksi belum dibuka! Panggil .connect() terlebih dahulu.")
            
        try:
            result = self.connection.execute(text(query), parameters or {})
            self.connection.commit()
            rowcount = result.rowcount
            #logger.info(f"   ↳ Eksekusi sukses! Baris terdampak: {rowcount} ✅")
            return rowcount
        except Exception as e:
            self.connection.rollback()
            logger.error(f"   ↳ ❌ Gagal eksekusi non-query: {e}")
            raise

    def insert_datatable(self, table_name: str, data: pd.DataFrame, behavior: str = 'append'):
        """Memasukkan seluruh isi DataFrame ke tabel SQL secara massal.
        Gunakan behavior append untuk tambah data, atau replace untuk mereset tabel lama.
        """
        if not self.connection:
            raise ConnectionError("Koneksi belum dibuka! Panggil .connect() terlebih dahulu.")
            
        try:
            data_clean = data.where(pd.notnull(data), None)
            con_to_use = self.connection if self.connection else self.engine
            data_clean.to_sql(name=table_name, con=con_to_use, if_exists=behavior, index=False)
            #logger.info("   ↳ Bulk insert selesai ✅")
        except Exception as e:
            logger.error(f"   ↳ ❌ Gagal bulk insert: {e}")
            raise

    def bulk_update(self, table_name: str, data: pd.DataFrame, match_columns: list) -> int:
        """
        Memperbarui banyak baris sekaligus berdasarkan kolom kunci (match_columns).
        Pastikan DataFrame 'data' berisi kolom yang ingin diubah + kolom kunci.
        """
        if not self.connection:
            raise ConnectionError("Koneksi belum dibuka! Panggil .connect() terlebih dahulu.")
            
        if data.empty:
            logger.warning("   ↳ DataTable kosong. Eksekusi dilewati.")
            return 0
            
        update_cols = [col for col in data.columns if col not in match_columns]
        
        if not update_cols:
            raise ValueError("Dataframe tidak memiliki kolom sisa untuk di-update selain dari match_columns.")
        
        q_start, q_end = ('[', ']') if self.db_type == 'sqlserver' else (('`', '`') if self.db_type == 'mysql' else ('"', '"'))
        def safe_param(name):
            return re.sub(r'[^a-zA-Z0-9_]', '_', str(name))

        set_clause = ", ".join([f"{q_start}{col}{q_end} = :{safe_param(col)}" for col in update_cols])
        where_clause = " AND ".join([f"{q_start}{col}{q_end} = :{safe_param(col)}" for col in match_columns])
        query = f"UPDATE {q_start}{table_name}{q_end} SET {set_clause} WHERE {where_clause}"
        
        try:
            records = data.to_dict('records')
            safe_records = []
            for row in records:
                safe_records.append({safe_param(k): v for k, v in row.items()})
            
            #logger.info("   ↳ Bulk update selesai ✅")
            result = self.connection.execute(text(query), safe_records)
            self.connection.commit()
            return result.rowcount if result.rowcount > 0 else len(data)
        except Exception as e:
            self.connection.rollback()
            logger.error(f"   ↳ ❌ Gagal bulk update: {e}")
            raise