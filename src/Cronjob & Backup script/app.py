import subprocess, requests, os, json, time
from flask import Flask, render_template, request, jsonify, Response
from apscheduler.schedulers.background import BackgroundScheduler
from cron_descriptor import get_description

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# --- AYARLAR ---
TELEGRAM_TOKEN = "TOKEN"
CHAT_ID = "Chat ID"
# ---------------

jobs_log = []

def send_telegram_backup(user, status, zip_path):
    """Telegram üzerinden zip dosyasını ve bilgi mesajını iletir."""
    msg = f"📦 *Yeni Yedekleme Paketi*\n👤 *Sorumlu:* {user}\n📊 *Durum:* {status}\n📅 *Tarih:* {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Mesaj gönder
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})

    # Zip dosyasını gönder ve sonra temizle (opsiyonel)
    if os.path.exists(zip_path):
        with open(zip_path, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", 
                          data={'chat_id': CHAT_ID}, files={'document': f})
        # Gönderdikten sonra sunucuda yer kaplamaması için silebilirsin:
        # os.remove(zip_path)

def backup_worker(user, file_path):
    # Bash scriptini çalıştır
    process = subprocess.run(['./backup.sh', user, file_path], capture_output=True, text=True)
    output = process.stdout
    
    # Script çıktısından zip dosyasının adını ayıkla
    zip_file = ""
    for line in output.split("\n"):
        if "ZIP_DOSYASI:" in line:
            zip_file = line.split(":")[1]

    if "DURUM:BASARILI" in output:
        status = "Başarıyla Zipledi ve Gönderdi"
        send_telegram_backup(user, status, zip_file)
    else:
        status = "HATA: Dosya bulunamadı"

    # Canlı log verisi oluştur
    log_entry = {"user": user, "task": file_path, "status": status, "time": time.strftime('%H:%M:%S')}
    jobs_log.append(log_entry)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/add_job', methods=['POST'])
def add_job():
    data = request.json
    cron_str = data.get('cron', '').strip()
    
    try:
        # Cron geçerli mi kontrol et ve dile çevir
        readable = get_description(cron_str)
        
        parts = cron_str.split()
        if len(parts) < 5:
            raise ValueError("Eksik cron parçası")

        # Zamanlayıcıya ekle
        scheduler.add_job(
            backup_worker, 
            'cron', 
            minute=parts[0], 
            hour=parts[1], 
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
            args=[data['user'], data['file_path']]
        )
        
        return jsonify({"message": "Görev Zamanlandı", "readable": readable})

    except Exception as e:
        # Hata durumunda 400 hatası döndür, sunucu çökmesin
        return jsonify({"message": "Hata: Geçersiz Cron Formatı!", "error": str(e)}), 400

@app.route('/stream-logs')
def stream_logs():
    def gen():
        last = 0
        while True:
            if len(jobs_log) > last:
                for i in range(last, len(jobs_log)):
                    yield f"data: {json.dumps(jobs_log[i])}\n\n"
                last = len(jobs_log)
            time.sleep(1)
    return Response(gen(), mimetype='text/event-stream')

if __name__ == '__main__':

    app.run(debug=True, port=5000)
