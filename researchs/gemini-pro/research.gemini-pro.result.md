# Research Result for gemini-pro


# Teknik Rapor: Cronjobs & Backup Scripts

Bu rapor, Unix/Linux tabanlı sistemlerde zamanlanmış görevler (Cron) ve veri yedekleme otomasyonunun çalışma prensiplerini, güvenlik risklerini ve endüstri standartlarını incelemektedir.

## 1. Temel Çalışma Prensipleri

Bu sistemin temel amacı **otomasyondur**. İnsan müdahalesine gerek kalmadan belirli periyotlarda belirli komutların işletilmesini sağlar.

### Cron (Chronograph - Zamanlayıcı)

Cron, arka planda çalışan bir daemon (servis) sürecidir (`crond`). Genellikle sistem açılışında başlar ve dakikada bir uyanarak yapılandırma dosyalarını (`crontab`) kontrol eder.

* **Daemon Döngüsü:** `crond` her dakika yapılandırma dosyalarının değiştirilme zamanını (modtime) kontrol eder. Değişiklik varsa yeni görevleri belleğe yükler.
* **Syntax (Söz Dizimi):** Cron, 5 yıldızlı bir zamanlama formatı kullanır:
`* * * * * /komut/yolu`
(Sırasıyla: Dakika, Saat, Ayın Günü, Ay, Haftanın Günü)

### Backup Scripts (Yedekleme Senaryoları)

Yedekleme scriptleri genellikle Shell (Bash), Python veya Perl ile yazılır. Temel akış şöyledir:

1. **Toplama (Collection):** Veritabanı dump'ı alma veya dosya dizinlerini listeleme.
2. **Sıkıştırma (Compression):** Veriyi `tar`, `gzip` veya `zstd` ile sıkıştırma.
3. **Şifreleme (Encryption):** Verinin güvenliği için (örn: GPG) şifreleme.
4. **Transfer:** Veriyi uzak sunucuya (FTP, SSH/SCP, AWS S3) taşıma.
5. **Temizlik (Rotation):** Eski yedekleri silme (Retention Policy).

---

## 2. En İyi Uygulama Yöntemleri (Best Practices) ve Endüstri Standartları

Sektörde kabul görmüş "Best Practice" kuralları, veri kaybını önlemek ve sistemin kararlı çalışmasını sağlamak için kritiktir.

### 3-2-1 Yedekleme Kuralı

Endüstri standardı olan bu kural şunları emreder:

* **3** adet veri kopyanız olmalı (1 canlı veri + 2 yedek).
* **2** farklı depolama medyası kullanılmalı (Örn: Disk + Tape veya Disk + Cloud).
* **1** kopya mutlaka **ofis/lokasyon dışında (off-site)** saklanmalı.

### Cronjob Best Practices

* **Mutlak Yollar (Absolute Paths):** Script içinde `tar` yerine `/usr/bin/tar` kullanın. Cron'un çevre değişkenleri (PATH) kullanıcı shell'inden farklıdır.
* **Çıktı Yönlendirme ve Loglama:** Cron çıktısını asla boşluğa (`/dev/null`) atmayın; en azından hataları loglayın.
* *Kötü:* `0 0 * * * /backup.sh > /dev/null 2>&1`
* *İyi:* `0 0 * * * /backup.sh >> /var/log/backup.log 2>&1`


* **Monitoring (İzleme):** Cron'un çalıştığını varsaymayın. **Dead Man's Snitch** veya **Healthchecks.io** gibi servislerle "heartbeat" takibi yapın.

### Backup Script Best Practices

* **Atomik İşlemler:** Yedekleme sırasında dosya bütünlüğü bozulmamalıdır. Veritabanları için `transaction logs` veya `lock` mekanizmaları kullanılmalıdır.
* **Yedekten Geri Dönüş Testi:** Geri yüklenemeyen bir yedek, yedek değildir. Düzenli olarak "Restore" tatbikatı yapılmalıdır.
* **Hata Yönetimi (Error Handling):** Scriptler `set -e` (hata durumunda dur) ve `set -o pipefail` (pipe zincirindeki hatayı yakala) modunda çalıştırılmalıdır.

---

## 3. Benzer Açık Kaynak Projeler ve Rakipler

Manuel script yazmak yerine kullanılan modern araçlar ve alternatifler:

### Cron Alternatifleri

| Teknoloji | Açıklama | Avantajı |
| --- | --- | --- |
| **Systemd Timers** | Modern Linux sistemlerinin yerleşik zamanlayıcısı. | Daha iyi loglama, bağımlılık yönetimi ve hata ayıklama. |
| **Anacron** | Sürekli açık olmayan bilgisayarlar (laptoplar) için. | Bilgisayar kapalıyken kaçan görevleri açılınca çalıştırır. |
| **Kubernetes CronJobs** | Konteyner orkestrasyonu için. | Cloud-native uygulamalar için ölçeklenebilir yapı. |
| **Airflow / Jenkins** | Karmaşık iş akışları için. | Görsel arayüz, pipeline yönetimi ve hata durumunda tekrar deneme. |

### Yedekleme Araçları (Script Alternatifleri)

* **Restic:** Go ile yazılmış, hızlı, güvenli ve verimli (deduplication destekli) yedekleme aracı.
* **BorgBackup:** Veri tekilleştirme (deduplication) konusunda çok başarılıdır, disk alanından tasarruf sağlar.
* **Duplicity:** Yedekleri şifreleyerek bulut depolama alanlarına yükler.

---

## 4. Kritik Yapılandırma Dosyaları ve Parametreleri

Bir Linux sisteminde bu süreci yöneten ana dosyalar şunlardır:

* `/etc/crontab`: Sistem genelindeki cron tablosu (Root yetkisi gerektirir).
* `/var/spool/cron/crontabs/`: Kullanıcılara özel cron dosyalarının bulunduğu dizin.
* `/etc/cron.d/`: Paketlerin veya uygulamaların kendi cron parçalarını bıraktığı dizin.
* `/etc/cron.allow` ve `/etc/cron.deny`: Hangi kullanıcıların cron kullanabileceğini belirleyen güvenlik dosyaları.

**Kritik Parametreler:**

* `SHELL`: Cron'un hangi kabuğu kullanacağını belirtir (Genelde `/bin/sh`).
* `PATH`: Komutların aranacağı dizinler.
* `MAILTO`: Cron çıktısının e-posta ile kime gönderileceği.

---

## 5. Güvenlik Açısından Dikkat Edilmesi Gereken Kritik Noktalar

Cron ve Backup scriptleri yüksek yetkilerle (genelde `root`) çalıştığı için saldırganların favori hedefidir.

1. **Dosya İzinleri (Permissions):** Script dosyaları sadece root tarafından yazılabilir (`chmod 700` veya `740`) olmalıdır. Eğer herkesin yazabildiği (`777`) bir script root olarak cron'da çalışırsa, herhangi bir kullanıcı scriptin içine zararlı kod ekleyerek root yetkisi kazanabilir (**Privilege Escalation**).
2. **Parola Güvenliği:** Backup scriptleri veritabanı şifrelerini içerebilir. Bu şifreler script içine "hardcode" edilmemeli, güvenli bir `config` dosyasından okunmalı (`.my.cnf` gibi) ve dosya izinleri kısıtlanmalıdır.
3. **Environment Injection:** Cron çevre değişkenleri sınırlıdır. Scriptler dışarıdan manipüle edilebilecek değişkenlere güvenmemelidir.
4. **Off-site Yedeklerin İzolasyonu:** Ransomware (Fidye yazılımı) saldırılarında, saldırganlar önce ağdaki yedekleri şifreler. Yedekleme sunucusu, ana sunucudan "çekme" (pull) yapmalıdır, ana sunucu yedeği "itmemelidir" (push). Böylece ana sunucu hacklense bile yedeklere erişemez.

---

## 6. Bu Konunun Var Olmasını Sağlayan Ana Sebepler

1. **İş Sürekliliği (Business Continuity):** Sistem çökmesi, veri silinmesi veya donanım arızası durumunda şirketin faaliyetlerine devam edebilmesi.
2. **İnsan Hatasını Önleme:** Manuel yapılan işlemler unutulabilir veya yanlış yapılabilir. Otomasyon tutarlılık sağlar.
3. **Kaynak Yönetimi:** Ağır işlemlerin (yedekleme, raporlama) sistemin en az kullanıldığı saatlerde (gece yarısı) yapılarak performans kaybının önlenmesi.
4. **Yasal Zorunluluklar:** KVKK, GDPR veya finansal regülasyonlar (BDDK, PCI-DSS) verilerin belirli süre saklanmasını zorunlu kılar.

---

## 7. Siber Saldırı Sırasında Cron/Backup Manipülasyonunun Etkileri

Bir siber saldırgan sisteme sızdığında, cronjob ve backup scriptleri ile oynaması **yıkıcı** sonuçlar doğurur.

### A. Yazılımcı/Sistem Yöneticisi Açısından Etkileri

* **Kalıcılık (Persistence) Sağlama:** Saldırgan, sistemi yeniden başlatsanız bile içeri tekrar sızabileceği bir "Backdoor" (arka kapı) komutunu cronjob'a ekler. Tespit edilmesi zordur çünkü meşru görevlerin arasına gizlenir.
* **Logic Bomb (Mantık Bombası):** Saldırgan, belirli bir tarihte tüm verileri silecek bir komutu cron'a zamanlayabilir. Bu, saldırgan sistemden atıldıktan aylar sonra bile tetiklenebilir.
* **Yanlış Güven Hissi:** Backup scripti değiştirilip `exit 0` (başarılı) döndürecek ama aslında yedek almayacak şekilde ayarlanabilir. Yönetici yedeklerin alındığını sanırken aslında aylar boyunca yedeksiz kalır.

### B. Şirket Açısından Etkileri

* **Ransomware (Fidye) Kabusu:** Modern fidye yazılımları, canlı veriyi şifrelemeden önce sessizce backup scriptlerini bozar veya bulut yedeklerini siler. Şirket fidye ödemeden veriyi kurtaramaz hale gelir.
* **Veri Sızıntısı (Exfiltration):** Backup scripti, veriyi şirketin sunucusu yerine saldırganın sunucusuna gönderecek şekilde değiştirilebilir. Bu, KVKK kapsamında devasa cezalara yol açar.
* **Operasyonel Felaket:** Kritik bir veritabanının yedeğinin bozuk olması, şirketin günlerce servis verememesi ve milyonlarca dolar zarar etmesi demektir.

---

### Referanslar ve Kaynaklar

* *Man pages:* `man 5 crontab`, `man 8 cron`.
* *NIST SP 800-34:* Contingency Planning Guide for Federal Information Systems (Yedekleme standartları).
* *OWASP:* Privilege Escalation via Cron (Güvenlik zafiyetleri).
* *Linux Foundation:* System Administration Guides.

