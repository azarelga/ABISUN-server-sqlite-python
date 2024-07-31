#!/bin/bash
echo "====================================================="
echo " ABISUN: Alat Bantu Edukasi Resusitasi Jantung Paru"
echo "====================================================="
echo

# Langkah 1: Periksa Instalasi Python
echo "Memeriksa instalasi Python..."
if ! command -v python3 &>/dev/null; then
  echo
  echo "Python tidak terinstal di sistem Anda."
  echo "Silakan instal Python 3.8+ dari https://www.python.org/downloads/ dan jalankan skrip ini lagi."
  read -p "Tekan enter untuk keluar..."
  exit 1
fi
echo "Python terinstal."
echo

# Langkah 2: Instal Dependensi
echo "Menginstal dependensi yang diperlukan..."
python3 -m pip install --upgrade pip
if [ $? -ne 0 ]; then
  echo
  echo "Gagal menginstal pip."
  echo "Pastikan Anda memiliki koneksi internet yang aktif dan coba lagi."
  read -p "Tekan enter untuk keluar..."
  exit 1
fi

python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
  echo
  echo "Gagal menginstal dependensi yang diperlukan."
  echo "Pastikan Anda memiliki koneksi internet yang aktif dan coba lagi."
  read -p "Tekan enter untuk keluar..."
  exit 1
fi
echo "Dependensi berhasil diinstal."
echo

# Langkah 3: Menjalankan Server dan Aplikasi
echo "Menjalankan server dan aplikasi..."
cd app
python3 server.py &
sleep 5
streamlit run app.py &
sleep 5

echo
echo "====================================================="
echo "     Instalasi selesai! ABISUN sekarang berjalan."
echo "  Jangan tutup terminal ini untuk membiarkan berjalan."
echo "====================================================="
echo

read -p "Tekan enter untuk keluar..."
