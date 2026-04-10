# Python REFramework Template 🤖

Template ini adalah adaptasi dari **Robotic Enterprise Framework (REFramework)** milik UiPath, dibangun menggunakan Python murni. Framework ini dirancang untuk kestabilan, *error recovery*, dan kemudahan penggunaan bagi RPA Developer.

## 📁 Struktur Folder

* **`main.py`** : *State Machine* utama (Jangan diubah kecuali perlu!).
* **`framework/`** : Berisi *lifecycle* robot (`InitAllSettings`, `GetTransactionData`, `Process`, `CloseAllApplications`).
* **`library/`** : Kumpulan fungsi *reusable* (Web Automation pakai Playwright, Excel pakai xlwings, dll).
* **`Example/`** : Berisi file contoh penggunaan tiap *library* yang bisa langsung di-*run*.
* **`Data/`** : Tempat menyimpan `Config.xlsx` dan file data.

## 🚀 Cara Menggunakan

1. **Install Dependencies:** Buka terminal dan jalankan:
   pip install -r requirements.txt
   playwright install

2. **Atur Config:** Buka `Data/Config.xlsx` dan atur parameter yang dibutuhkan (misal: `MaxConsecutiveSystemExceptions`).

3. **Tulis Logic:** Buka `framework/Process.py` dan tulis alur bisnismu di sana. Gunakan *custom activities* dari folder `library/` agar rapi.

4. **Jalankan:** Run file `main.py`.