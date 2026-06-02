<p align="center">
  <img src="xpose-logo.jpg" width="60" alt="X-POSE logo">
</p>

<h1 align="center">X-POSE</h1>

<p align="center">
  <em>AI-powered Twitter personality analyzer — savage, sharable, screenshot-worthy.</em>
</p>

<p align="center">
  <a href="./README.zh.md">中文版</a>
</p>

---

## Overview

X-POSE is a single-user Twitter personality analyzer. Enter a username → scrape their profile & latest tweets → DeepSeek V4 Pro AI generates a 15-dimension personality report with cards, roast, strengths, weaknesses, and more.

Inspired by [Wordware](https://wordware.ai)'s viral Twitter personality project.

## Features

- **Scrape** — fetches profile info + latest tweets via Playwright/CloakBrowser
- **Analyze** — sends profile + tweets to DeepSeek V4 Pro and returns structured JSON
- **15 Report Cards** — about, roast, strengths, weaknesses, love life, money, health, and more
- **Download as Image** — one-click PNG screenshot via html2canvas
- **Share to X** — pre-filled tweet with your report
- **Bilingual UI** — Simplified Chinese / English toggle
- **1-Click Concurrency Limit** — prevents server overload on Streamlit Cloud

## Quick Start

### Try it online

👉 **[xpose7.streamlit.app](https://xpose7.streamlit.app)**

### Run locally

```bash
# 1. Clone
git clone https://github.com/gokuscraper/x-pose.git
cd x-pose

# 2. Install Python deps
pip install -r requirements.txt

# 3. Install Playwright browsers (required by CloakBrowser)
playwright install chromium

# 4. Configure API key
# Create .streamlit/secrets.toml with:
# SILICON_API_KEY = "sk-your-key-here"

# 5. Run
streamlit run streamlit_app.py
```

### API Key

X-POSE uses [SiliconFlow](https://siliconflow.cn) DeepSeek V4 Pro. Get your API key from [SiliconFlow Console](https://cloud.siliconflow.cn).

## Project Structure

```
x-pose/
├── streamlit_app.py        # Home page — username input → scrape
├── pages/
│   └── 1_Analysis.py       # Analysis report page
├── lib/
│   ├── ai.py               # AI prompt & API call
│   ├── tweet_utils.py      # Tweet formatting & stats
│   └── sidebar.py          # Sidebar navigation
├── scraper/
│   ├── worker.py           # Subprocess entry point (avoids event-loop conflict)
│   ├── subprocess_client.py# Subprocess communication
│   ├── client.py           # CloakBrowser wrapper
│   ├── fetcher.py          # Fetch user + tweets
│   ├── parser.py           # Parse raw API data → models
│   ├── models.py           # TwitterUser, Tweet dataclasses
│   ├── storage.py          # Local JSON caching
│   └── config.py           # API endpoints config
├── locales/
│   ├── zh.json             # Chinese UI strings
│   └── en.json             # English UI strings
├── i18n.py                 # i18n helper
├── requirements.txt
└── packages.txt            # System deps for Streamlit Cloud
```

## How It Works

```mermaid
flowchart LR
    A[User Input] --> B[Playwright Subprocess]
    B --> C[Profile JSON + Tweets]
    C --> D[DeepSeek V4 Pro]
    D --> E[15-Field JSON Report]
    E --> F[Card Grid UI]
    F --> G[Download PNG / Share to X]
```

1. **Input** — username (supports `@user`, `https://x.com/user`, bare name)
2. **Scrape** — subprocess runs Playwright via CloakBrowser to bypass Vercel challenges
3. **Analyze** — profile + tweets sent to DeepSeek V4 Pro with a savage, witty prompt
4. **Report** — 15 cards rendered in a responsive grid
5. **Share** — download as PNG or share to X with pre-filled text

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) (single-page app) |
| AI Model | [DeepSeek V4 Pro](https://platform.deepseek.ai) via SiliconFlow API |
| Scraper | [CloakBrowser](https://cloakbrowser.com) (Playwright-based) |
| Deployment | [Streamlit Cloud](https://streamlit.io/cloud) |
| License | Apache 2.0 |

## License

[Apache 2.0](LICENSE)
