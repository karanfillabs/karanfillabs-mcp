# Karanfil Labs — Visual DNA MCP Server
[![karanfillabs/karanfillabs-mcp MCP server](https://glama.ai/mcp/servers/karanfillabs/karanfillabs-mcp/badges/score.svg)](https://glama.ai/mcp/servers/karanfillabs/karanfillabs-mcp)
[![Karanfil Labs Visual DNA MCP server – quality and maintenance score on Glama](https://glama.ai/mcp/servers/karanfillabs/karanfillabs-mcp/badges/card.svg)](https://glama.ai/mcp/servers/karanfillabs/karanfillabs-mcp)
![Karanfil Labs Visual DNA API](https://raw.githubusercontent.com/karanfillabs/visual-dna-quickstart/main/karanfillabs_cover.jpg)

Official **Model Context Protocol (MCP)** server for the **[Karanfil Labs Visual DNA API](https://karanfillabs.com)** — enabling **Claude Desktop**, **Cursor**, **Windsurf**, and any MCP-compatible AI agent to identify movies & TV episodes from video frames or search across **88M+ 768-d visual fingerprints** using plain-language prompts.

[🇬🇧 English Guide](#-english-guide) • [🇹🇷 Türkçe Kılavuz](#-türkçe-kılavuz) • [🌐 Live Demo & API Key](https://karanfillabs.com) • [📖 Swagger Docs](https://api.karanfillabs.com/docs)

---

## 🇬🇧 English Guide

### Available MCP Tools
1. **`identify_scene_from_image`** — Identify the movie or TV episode (`SxxExx`), release year, `tmdb_id`, and similarity confidence from any local screenshot file path (`PNG`, `JPG`, `WEBP`) or direct image URL (`POST /v1/identify`). Works even on cropped or subtitled frames.
2. **`search_scenes_by_text`** — Semantic text-to-scene discovery across millions of cinema and TV frames using natural English descriptions like *"rainy neon street car chase"* (`POST /v1/search`).
3. **`check_visual_dna_status`** — Keyless health check returning live server status and real-time indexed 768-d vector count (`GET /health`).

### Privacy & Catalog Note
* **Volatile RAM Processing:** Submitted image frames are converted into 768-d mathematical vectors strictly in volatile server RAM and discarded immediately — zero full images or copyrighted videos are hosted or written to disk.
* **Growing Catalog & Thresholds:** While 88M+ frame vectors are online (heavily covering TV series, anime, and feature films), not every movie ever made is indexed yet. True matches from indexed titles typically score **82% – 95%+**; scores below **80%** indicate closest visual similarity when a title is not yet in the index.

### 1. Get Your Free API Key (50 Free Credits)
Sign up in 15 seconds at **[karanfillabs.com/#portal](https://karanfillabs.com/#portal)** (no credit card required) to receive **50 free API test credits** and your `kl_live_...` key.

### 2. Quick Configuration (Claude Desktop / Cursor / Windsurf)

Requires [`uv`](https://docs.astral.sh/uv/) (`pip install uv` or `brew install uv`). Add the following block to your `claude_desktop_config.json` or `.cursor/mcp.json`:

**Option A — Run directly from GitHub (Works Immediately):**
```json
{
  "mcpServers": {
    "karanfillabs": {
      "command": "uvx",
      "args": [
        "--from",
        "git+[https://github.com/karanfillabs/karanfillabs-mcp](https://github.com/karanfillabs/karanfillabs-mcp)",
        "karanfillabs-mcp"
      ],
      "env": {
        "KARANFIL_API_KEY": "kl_live_your_api_key_here"
      }
    }
  }
}
```

**Option B — Run from PyPI (Once published on PyPI):**
```json
{
  "mcpServers": {
    "karanfillabs": {
      "command": "uvx",
      "args": ["karanfillabs-mcp"],
      "env": {
        "KARANFIL_API_KEY": "kl_live_your_api_key_here"
      }
    }
  }
}
```

### 3. Example Prompts in Claude or Cursor
* *"Check Karanfil Labs Visual DNA server status and how many vectors are online."*
* *"Identify the movie or series episode in `/Users/alex/Desktop/frame.jpg` using Karanfil Labs."*
* *"Search Karanfil Labs for cinema scenes matching 'spaceship approaching a black hole'."*

---

## 🇹🇷 Türkçe Kılavuz

**[Karanfil Labs Visual DNA API](https://karanfillabs.com)** için resmi **Model Context Protocol (MCP)** köprü paketi. Tek satır kod yazmadan **Claude Desktop**, **Cursor** ve **Windsurf** içerisinden bilgisayarınızdaki bir film/dizi karesini taratabilir veya **88M+ adet 768 boyutlu görsel parmak izi** arasında sahne araması yapabilirsiniz.

### Sunulan Araçlar (Tools)
1. **`identify_scene_from_image`** — Bilgisayarınızdaki bir ekran görüntüsü yolundan (`PNG`, `JPG`, `WEBP`) veya doğrudan görsel bağlantısından hangi film/dizi bölümü (`SxxExx`) olduğunu, yılını, `tmdb_id` bilgisini ve güven skorunu döndürür (`POST /v1/identify`).
2. **`search_scenes_by_text`** — Doğal dil sahne tarifleriyle milyonlarca sinema/dizi karesi içinde anlamsal sahne araması yapar (`POST /v1/search`). Türkçe yazsanız bile yapay zeka asistanınız tarifi otomatik İngilizceye çevirerek sorgular.
3. **`check_visual_dna_status`** — Anahtar gerektirmeden sunucu sağlık durumunu ve o an aktif olan canlı vektör sayısını döndürür (`GET /health`).

### Gizlilik ve Katalog Notu
* **Anlık RAM İşleme (KVKK / GDPR Uyumlu):** Gönderilen kareler yalnızca geçici sunucu belleğinde (RAM) 768 boyutlu vektöre çevrilip salisesinde silinir; diske ham görsel yazılmaz ve telifli video barındırılmaz.
* **Büyüyen Katalog ve Skor Eşiği:** Katalogda 88M+ kare vektörü aktif olsa da henüz tarihteki tüm filmler indekslenmemiştir. İndekste bulunan yapımlar genelde **%82 – %95+** bandında eşleşir; **%80** altındaki skorlar aranan yapımın henüz katalogda olmayabileceğini gösterir.

### 1. Ücretsiz API Anahtarı Alın (50 Hediye Kredi)
**[karanfillabs.com/#portal](https://karanfillabs.com/#portal)** adresinden kredi kartı gerekmeden ücretsiz hesap açarak **50 test kredisi** ve `kl_live_...` anahtarınızı hemen alabilirsiniz.

### 2. Kurulum (Claude Desktop / Cursor)
`claude_desktop_config.json` veya `.cursor/mcp.json` dosyanıza yukarıdaki **Option A** JSON bloğunu ekleyip `KARANFIL_API_KEY` kısmına kendi `kl_live_...` anahtarınızı yazmanız yeterlidir.

### 3. Örnek Kullanım Komutları
* *"Karanfil Labs sunucu durumunu ve aktif vektör sayısını kontrol et."*
* *"Masaüstümdeki `C:\Users\Kullanici\Desktop\sahne.png` karesinin hangi dizi ve bölüm olduğunu Karanfil Labs ile bul."*
* *"Yağmurlu bir gecede neon ışıklı sokakta geçen araba kovalamacası sahnelerini Karanfil Labs'te ara."*

---

## License
MIT © [Karanfil Labs Yazılım ve Teknoloji A.Ş.](https://karanfillabs.com)
