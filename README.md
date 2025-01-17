# Crawl4AI Web Crawler & Chat

Bu proje, web sitelerini kazıyıp içeriklerini vektör veritabanında saklayan ve bu içerikler üzerinde sohbet imkanı sunan bir uygulamadır.

## Özellikler

- 🕷️ Web sitelerini otomatik kazıma
- 💾 İçerikleri Supabase'de saklama
- 🔍 Vektör tabanlı benzerlik araması
- 💬 Kazınan içerikler üzerinde sohbet
- 🎯 OpenAI entegrasyonu
- 🌐 Streamlit web arayüzü

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyasını düzenleyin:
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Crawler Configuration
MAX_PAGES=100
```

3. Supabase veritabanını hazırlayın:
- Supabase projenizi oluşturun
- `schema.sql` dosyasındaki SQL komutlarını Supabase SQL editöründe çalıştırın

## Kullanım

1. Streamlit uygulamasını başlatın:
```bash
streamlit run app.py
```

2. Web tarayıcınızda `http://localhost:8501` adresine gidin

3. "Crawler" sekmesinde:
   - Kazımak istediğiniz URL'yi girin
   - "Start Crawling" butonuna tıklayın
   - İşlem tamamlanana kadar bekleyin

4. "Chat" sekmesinde:
   - Kazınan içerikler hakkında sorular sorun
   - AI destekli yanıtları alın

## Teknik Detaylar

- Web kazıma: Crawl4AI
- Vektör veritabanı: Supabase + pgvector
- Embedding modeli: all-MiniLM-L6-v2
- Sohbet modeli: OpenAI GPT
- Web arayüzü: Streamlit

## Lisans

MIT 