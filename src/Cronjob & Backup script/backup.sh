#!/bin/bash

# 1. GEREKLİ PAKETLERİ OTOMATİK KUR (Sadece ilk çalıştırmada veya eksikse)
echo "Sistem kontrolleri yapılıyor..."
pip install flask apscheduler cron-descriptor requests urllib3 flask-cors --quiet
sudo apt update && sudo apt install zip -y

# 2. PARAMETRELERİ AL
USER_NAME=$1
FILE_PATH=$2
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ZIP_NAME="yedek_${TIMESTAMP}.zip"

# 3. YEDEKLEME VE ZİPLEME İŞLEMİ
if [ -f "$FILE_PATH" ]; then
    # Dosyayı zip formatında sıkıştır
    zip -r "$ZIP_NAME" "$FILE_PATH" > /dev/null
    
    # Python'un anlaması için çıktı üret
    echo "DURUM:BASARILI"
    echo "ZIP_DOSYASI:$ZIP_NAME"
else
    echo "DURUM:HATA (Dosya bulunamadı)"
fi