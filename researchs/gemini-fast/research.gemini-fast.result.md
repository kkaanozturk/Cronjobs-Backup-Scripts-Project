# Research Result for gemini-fast


## Cronjobs ve Yedekleme Scriptleri Teknik Analiz Raporu

### 1. Çalışma Mantığı: Kavramsal ve Teknik Yaklaşım

**Kavramsal Olarak:**
Bir **Cronjob**, bilgisayarın belleğinde sürekli çalışan ve zamanı takip eden bir "alarm saati" gibidir. Belirlenen zaman geldiğinde, ilgili görevi (script) uyandırır ve çalıştırır. **Yedekleme Scripti** ise bu saatin çaldığında ne yapılacağını belirleyen "talimatlar listesidir".

**Teknik Olarak:**
Linux sistemlerde `crond` adı verilen bir **daemon** (arkaplan süreci) her dakika uyanarak `/etc/crontab` ve `/var/spool/cron/crontabs/` dizinlerini kontrol eder. Eğer o anki zaman dilimiyle eşleşen bir komut varsa, bu komutu ilgili kullanıcının yetkileriyle (UID/GID) alt süreç (child process) olarak başlatır.

---

### 2. Kabul Görmüş En Doğru Yöntemler (Best Practices)

Verimli bir sistem kurmak için şu prensipler uygulanmalıdır:

* **Mutlak Dosya Yolları (Absolute Paths):** Cron sınırlı bir `PATH` değişkeniyle çalışır. `/usr/bin/python3` gibi tam yollar kullanılmalıdır.
* **Loglama ve Hata Yönetimi:** Standart çıktı (stdout) ve hatalar (stderr) mutlaka bir dosyaya yönlendirilmelidir: `>> /var/log/backup.log 2>&1`.
* **3-2-1 Kuralı:** Verinin 3 kopyası olmalı, 2 farklı medya türünde saklanmalı ve en az 1 kopyası fiziksel olarak farklı bir konumda (off-site/cloud) durmalıdır.
* **Atomik İşlemler:** Yedekleme sırasında veri tutarlılığını sağlamak için veritabanı "dump" işlemleri kilitlenerek veya "snapshot" yöntemiyle yapılmalıdır.

---

### 3. Açık Kaynak Araçlar ve Alternatifler

| Araç Tipi | Popüler Araç | Alternatifler | Özellikleri |
| --- | --- | --- | --- |
| **Zamanlayıcı** | **Cron** | Systemd Timers, Anacron | Hafif, standart, her Linux'ta var. |
| **Yedekleme Motoru** | **Rsync** | Rclone, BorgBackup | Diferansiyel yedekleme, bant genişliği tasarrufu. |
| **Tam Çözüm** | **BorgBackup** | Restic, Bacula, Duplicati | Şifreleme, tekilleştirme (deduplication). |

---

### 4. Kritik Konfigürasyon Dosyaları ve Parametreler

1. **/etc/crontab:** Sistem geneli zamanlanmış görevleri tutar.
* `* * * * * user command`: (Dakika, Saat, Gün, Ay, Haftanın Günü).


2. **/etc/anacrontab:** Bilgisayar kapalıyken kaçırılan görevlerin telafisi için kullanılır.
3. **Script Yapılandırması (Örn: `.my.cnf` veya `.env`):**
* `DB_USER`, `DB_PASS`, `BACKUP_DIR`: Scriptin ihtiyaç duyduğu hassas parametreler.



---

### 5. Güvenlik Riskleri

* **Düz Metin Şifreler:** Script içine yazılan veritabanı şifreleri en büyük risktir.
* **Yazma İzinleri:** Yedekleme dizininin (backup directory) herkese açık olması, yedeğin çalınmasına veya manipüle edilmesine neden olur.
* **Eksik Doğrulama:** Yedek alınıyor gibi görünse de, yedeğin boş veya bozuk olması (silent failure) operasyonel bir risktir.

---

### 6. Neden Bu Sistemlere İhtiyaç Duyarız?

* **Süreklilik:** İnsan müdahalesine gerek kalmadan sistemin kendi kendini korumasını sağlar.
* **Felaket Kurtarma (DR):** Donanım arızası, fidye yazılımı (ransomware) veya yanlışlıkla silme durumlarında tek geri dönüş yoludur.
* **Kaynak Yönetimi:** Yedekleme gibi işlemci yükü yüksek işlerin, trafiğin az olduğu gece saatlerinde (off-peak hours) yapılmasını sağlar.

---

### 7. Bir Saldırgan Müdahale Ederse Ne Olur?

Saldırganlar için cronjob'lar "Kalıcılık" (Persistence) sağlamanın en favori yoludur:

1. **Privilege Escalation (Yetki Yükseltme):** Eğer bir cronjob `root` yetkisiyle çalışıyor ve script dosyası normal bir kullanıcı tarafından düzenlenebiliyorsa, saldırgan kendi komutunu ekleyerek tam yetki kazanır.
2. **Veri Sızıntısı:** Yedekleme scriptine eklenen bir satır ile tüm veritabanı saldırganın sunucusuna transfer edilebilir.
3. **Arka Kapı (Backdoor):** Saldırgan silinse bile, cronjob her saat başı saldırganın tekrar sisteme girmesini sağlayan bir "reverse shell" açabilir.

---

**Kaynaklar:**

* *The Linux Programming Interface (Michael Kerrisk)*
* *OWASP: Infrastructure Security Guidelines*
* *SANS Institute: Securing Linux Systems*
