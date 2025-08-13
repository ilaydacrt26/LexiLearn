# LexiLearn

LexiLearn, kullanıcıların dil becerilerini geliştirmelerine yardımcı olmak için tasarlanmış yenilikçi bir dil öğrenme platformudur. Büyük Dil Modelleri (LLM'ler) ve yapay zeka destekli araçlar kullanarak, kullanıcıların sohbet partnerleriyle etkileşim kurmasını, seviye testleri çözmesini, dinleme ve telaffuz egzersizleri yapmasını ve çeşitli senaryolarla pratik yapmasını sağlar.

## Canlı Demoyu Görüntüle

Uygulamanın çalışan hali Streamlit Cloud üzerinde aşağıdaki linkten erişilebilir:

https://lexilearn-urvjsappfy9v9u8clntfzxh.streamlit.app/

## Kurulum

LexiLearn'i kendi yerel ortamınızda kurmak ve çalıştırmak için aşağıdaki adımları takip edin:

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/KullaniciAdiniz/LexiLearn.git # Kendi depo URL'nizi buraya ekleyin
cd LexiLearn
```

### 2. Sanal Ortam Oluşturun ve Aktifleştirin

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

Sanal ortamı aktifleştirdikten sonra, gerekli tüm Python bağımlılıklarını yükleyin:

```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenlerini Ayarlayın

Proje, API anahtarları veya diğer hassas bilgiler için `.env` dosyası kullanabilir. Eğer varsa, proje kök dizininde `.env` adında bir dosya oluşturun ve gerekli değişkenleri içine ekleyin.

```
# .env dosyası örneği
# GOOGLE_API_KEY=sizin_api_anahtarınız
```

### 5. Uygulamayı Çalıştırın

Tüm bağımlılıklar yüklendikten sonra, uygulamayı başlatabilirsiniz:

```bash
streamlit run app.py
```

Uygulama, varsayılan olarak `http://localhost:8501` adresinde tarayıcınızda açılacaktır.

## Proje Yapısı

LexiLearn projesi, anlaşılır ve bakımı kolay bir yapıya sahiptir. İşte ana dizinler ve dosyaların açıklamaları:

```
LexiLearn/
├── _pages/
│   ├── _chat_partner.py     # Yapay zeka sohbet partneri ile etkileşim sayfası
│   ├── _daily_tasks.py      # Günlük dil öğrenme görevleri ve alıştırmaları
│   ├── _level_test.py       # Kullanıcının dil seviyesini belirleyen test sayfası
│   ├── _listening.py        # Dinleme becerilerini geliştirmeye yönelik egzersizler
│   ├── _login.py            # Kullanıcı giriş/kayıt sayfası
│   ├── _profile.py          # Kullanıcı profilini ve ilerlemesini gösteren sayfa
│   ├── _pronunciation.py    # Telaffuz pratiği ve geri bildirim sayfası
│   └── _scenarios.py        # Çeşitli gerçek hayat senaryolarında dil pratiği
├── app.py                   # Streamlit uygulamasının ana giriş noktası
├── data/
│   ├── level_test_questions.py # Seviye testi için soru verileri
│   ├── listening_data.py    # Dinleme egzersizleri için veriler
│   ├── scenarios_data.py    # Senaryo tabanlı pratik için veriler
│   └── vocabulary_data.py   # Kelime bilgisi verileri
├── database/
│   ├── __init__.py          # Veritabanı paketini başlatır
│   └── models.py            # Veritabanı modelleri (örneğin, kullanıcılar, ilerleme vb.)
├── duckdb_db/
│   └── lexilearn.duckdb     # DuckDB veritabanı dosyası
├── lexilearn.db             # SQLite veritabanı dosyası
├── README.md                # Proje hakkında bilgiler ve kurulum talimatları
├── requirements.txt         # Projenin tüm Python bağımlılıkları
└── utils/
    ├── audio_handler.py     # Ses işleme ve kaydetme ile ilgili yardımcı fonksiyonlar
    ├── level_calculator.py  # Kullanıcının dil seviyesini hesaplama mantığı
    ├── llm_handler.py       # Büyük Dil Modelleri (LLM) ile etkileşimleri yönetir
    └── rag_system.py        # Retrieval Augmented Generation (RAG) sistemi uygulaması
```

## Kullanılan Teknolojiler

LexiLearn projesi, modern web geliştirme ve yapay zeka teknolojilerini bir araya getirir:

*   **Streamlit:** Python ile hızlı ve kolay web uygulamaları oluşturmak için kullanılır.
*   **Langchain:** Büyük Dil Modelleri uygulamaları geliştirmek için modüler bir çerçeve.
*   **Google Generative AI:** Google'ın üretken yapay zeka modelleri ile entegrasyon.
*   **DuckDB:** Hızlı ve gömülü analitik veritabanı.
*   **SQLite/PostgreSQL (psycopg2-binary, db-sqlite3):** Uygulama verilerini depolamak için veritabanı çözümleri.
*   **SpeechRecognition & gTTS:** Konuşma tanıma ve metin okuma yetenekleri sağlar.
*   **Pandas & Plotly:** Veri işleme ve görselleştirme için kullanılır.
*   **Streamlit Audio Components:** Streamlit içinde ses kaydı ve oynatma işlevselliği sunar.
*   **Python-Dotenv:** Ortam değişkenlerinin güvenli bir şekilde yönetilmesi.

