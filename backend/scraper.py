#!/usr/bin/env python3
"""
Scraper de imagens do Yupoo para o Craque Do Jogo Store.
Baixa imagens organizadas por time/categoria para /opt/craque-do-jogo/uploads/
"""
import os
import re
import time
import hashlib
import requests
from urllib.parse import urlparse

UPLOAD_DIR = "/opt/craque-do-jogo/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Referer": "https://camisetafutbol.x.yupoo.com/",
})

# Times que queremos
TARGET_TERMS = [
    "Flamengo", "Corinthians", "Palmeiras", "São Paulo", "Cruzeiro", "Atlético",
    "Santos", "Vasco", "Grêmio", "Internacional", "Botafogo", "Fluminense",
    "Bahia", "Sport", "Ceará", "Athletico",
    "Real Madrid", "Barcelona", "Liverpool", "Manchester", "PSG", "Bayern",
    "Juventus", "Chelsea", "Arsenal", "Milan", "Inter Milan", "Benfica", "Porto",
    "Brasil", "Argentina", "França", "Alemanha", "Italia", "Portugal", "Espanha",
    "Inglaterra", "Holanda", "Uruguai",
    "Lakers", "Celtics", "Warriors", "Bulls", "Heat", "Nets", "Knicks", "Suns",
    "Mavericks", "Bucks", "Nuggets", "Clippers",
    "Yankees", "Dodgers", "Red Sox", "Cubs", "Astros", "Giants",
]

def slug(text: str) -> str:
    text = re.sub(r"[^\w\s]", "", text.lower())
    text = re.sub(r"[\s]+", "-", text.strip())
    return text[:40]

def make_unique_name(url: str, page: int, idx: int) -> str:
    # Cria nome único baseado no hash da URL
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    ext = url.split(".")[-1] if "." in url else "jpg"
    return f"{page:03d}_{idx:03d}_{h}.{ext}"

def get_page(url: str, retries=3):
    for i in range(retries):
        try:
            resp = SESSION.get(url, timeout=20)
            if resp.status_code == 200:
                return resp.text
            time.sleep(2)
        except Exception as e:
            print(f"  Retry {i+1}: {e}")
            time.sleep(3)
    return ""

def extract_images(html: str) -> list[str]:
    """Extrai URLs de imagem do Yupoo."""
    # Padrão: photo.yupoo.com com /small.jpg ou /medium.jpg
    pattern = re.compile(r'src="(https://photo\.yupoo\.com/[^"]+\.(?:jpg|jpeg|png))"')
    urls = []
    seen = set()
    for match in pattern.finditer(html):
        url = match.group(1).replace("/small.jpg", "/medium.jpg").replace("/thumbs/", "/")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls

def should_keep(name: str, team: str) -> bool:
    """Filtra se deve baixar basedo no time."""
    name_lower = (name + " " + team).lower()
    for term in TARGET_TERMS:
        if term.lower() in name_lower:
            return True
    return False

def download_image(url: str, dest: str, retries=2) -> bool:
    for attempt in range(retries):
        try:
            resp = SESSION.get(url, timeout=30, stream=True)
            if resp.status_code == 200:
                content = resp.content
                if len(content) > 5000:  # filtro de imagens mínimas
                    with open(dest, "wb") as f:
                        f.write(content)
                    return True
        except Exception as e:
            print(f"    Erro {attempt+1}: {e}")
        time.sleep(1)
    return False

def scrape_page(page: int) -> list[str]:
    url = f"https://camisetafutbol.x.yupoo.com/albums?tab=gallery&page={page}"
    print(f"\n[{page}/20] {url}")
    html = get_page(url)
    if not html:
        print("  Falha ao carregar")
        return []
    return extract_images(html)

def run():
    print("=== Scraper Yupoo - Craque Do Jogo Store ===\n")
    all_urls = []

    for page in range(1, 21):
        images = scrape_page(page)
        all_urls.extend(images)
        print(f"  -> {len(images)} imagens nesta página")
        time.sleep(1.5)

    print(f"\nTotal coletado: {len(all_urls)} imagens\n")

    # Download
    downloaded = 0
    skipped = 0
    for i, url in enumerate(all_urls):
        filename = make_unique_name(url, (i // 40) + 1, i % 40)
        dest = os.path.join(UPLOAD_DIR, filename)

        if os.path.exists(dest) and os.path.getsize(dest) > 5000:
            skipped += 1
            if (i+1) % 50 == 0:
                print(f"  [{i+1}/{len(all_urls)}] Já existe: {filename}")
            continue

        ok = download_image(url, dest)
        if ok:
            downloaded += 1
            size = os.path.getsize(dest) / 1024
            print(f"  [{i+1}/{len(all_urls)}] ✓ {filename} ({size:.0f}KB)")
        else:
            print(f"  [{i+1}/{len(all_urls)}] ✗ {url[:60]}...")

        if (i+1) % 20 == 0:
            time.sleep(2)

    print(f"\n\n=== Download concluído ===")
    print(f"  Novas: {downloaded}")
    print(f"  Puladas: {skipped}")
    print(f"  Pasta: {UPLOAD_DIR}")

if __name__ == "__main__":
    run()