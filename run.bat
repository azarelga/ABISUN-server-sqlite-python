@echo off
title ABISUN: Alat Bantu Edukasi Resusitasi Jantung Paru - Instalasi

echo =====================================================
echo  ABISUN: Alat Bantu Edukasi Resusitasi Jantung Paru
echo =====================================================
echo.

:: Langkah 1: Periksa Instalasi Python
echo Memeriksa instalasi Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Python tidak terinstal di sistem Anda.
    echo Silakan instal Python 3.8+ dari https://www.python.org/downloads/ dan jalankan skrip ini lagi.
    pause
    exit /b 1
)
echo Python terinstal.
echo.

:: Langkah 2: Instal Dependensi
echo Menginstal dependensi yang diperlukan...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo Gagal menginstal dependensi yang diperlukan.
    echo Pastikan Anda memiliki koneksi internet yang aktif dan coba lagi.
    pause
    exit /b 1
)
echo Dependensi berhasil diinstal.
echo.

:: Langkah 3: Menjalankan Server dan Aplikasi
echo Menjalankan server dan aplikasi...
cd app
start python server.py
timeout /t 5
start python -m streamlit run app.py
timeout /t 5

:: Langkah 4: Membuka Aplikasi di Browser
echo Membuka aplikasi di browser Anda...
start "" "http://localhost:8501"

echo.
echo =====================================================
echo      Instalasi selesai! ABISUN sekarang berjalan.
echo   Jangan tutup window ini untuk membiarkan berjalan.
echo =====================================================
echo.

pause
exit /b 0

