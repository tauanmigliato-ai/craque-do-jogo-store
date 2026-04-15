#!/usr/bin/env python3
"""
Scraper para minkang.x.yupoo.com
Navega: categorias → times → álbuns → imagens
Salva imagens + metadata.json com dados corretos por produto.
"""
import os
import re
import time
import json
import hashlib
import requests
from typing import Optional

UPLOAD_DIR = "/opt/craque-do-jogo/uploads"
METADATA_PATH = os.path.join(UPLOAD_DIR, "metadata.json")
BASE_URL = "https://minkang.x.yupoo.com"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Referer": "https://minkang.x.yupoo.com/",
})

TARGET_LEAGUES = [
    {
        "name": "Copa do Mundo 2026",
        "slug": "copa-do-mundo",
        "keywords": ["copa do mundo", "world cup", "2026"],
        "category_id": None,
    },
    {
        "name": "Brasileirão",
        "slug": "brasileirao",
        "keywords": ["brasileiro", "brasileirão", "série a", "serie a"],
        "category_id": "680738",
    },
]

TYPE_PRIORITY = ["home", "away", "third"]

TYPE_KEYWORDS = {
    "home": ["home"],
    "away": ["away"],
    "third": ["third", "3rd"],
}

SKIP_KEYWORDS = ["kids", "children", "baby", "infant", "goalkeeper", "gk", "women", "female", "polo", "shorts", "socks", "jacket", "windbreaker", "training"]


def detect_type(album_title: str) -> Optional[str]:
    """Detecta o tipo (home/away/third) a partir do nome do álbum."""
    title_lower = album_title.lower()

    if any(kw in title_lower for kw in SKIP_KEYWORDS):
        return None

    for kit_type in TYPE_PRIORITY:
        for keyword in TYPE_KEYWORDS[kit_type]:
            if keyword in title_lower:
                return kit_type

    return None


def find_category_ids(html: str, keywords: list) -> list:
    """Encontra IDs de categorias cujo texto de link contenha alguma das keywords."""
    pattern = re.compile(r'href="/categories/(\d+)"[^>]*>([^<]+)<', re.IGNORECASE)
    results = []
    for match in pattern.finditer(html):
        cat_id, label = match.group(1), match.group(2).lower()
        if any(kw.lower() in label for kw in keywords):
            results.append(cat_id)
    return results


def parse_subcategories(html: str) -> list:
    """Extrai (nome, id) de subcategorias de time (?isSubCate=true)."""
    pattern = re.compile(r'href="/categories/(\d+)\?isSubCate=true"[^>]*>([^<]+)<', re.IGNORECASE)
    return [(m.group(2).strip(), m.group(1)) for m in pattern.finditer(html)]


def parse_albums(html: str) -> list:
    """Extrai (título, id) de álbuns da página de um time."""
    pattern = re.compile(r'href="/albums/(\d+)"[^>]*>([^<]+)<', re.IGNORECASE)
    seen = set()
    results = []
    for m in pattern.finditer(html):
        album_id, title = m.group(1), m.group(2).strip()
        if album_id not in seen and title:
            seen.add(album_id)
            results.append((title, album_id))
    return results


def parse_image_urls(html: str) -> list:
    """Extrai URLs de imagem do Yupoo, normalizando para /medium.jpg."""
    pattern = re.compile(r'src="(https://photo\.yupoo\.com/[^"]+\.(?:jpg|jpeg|png))"', re.IGNORECASE)
    seen = set()
    urls = []
    for m in pattern.finditer(html):
        url = m.group(1)
        url = re.sub(r'/small\.', '/medium.', url)
        url = re.sub(r'/thumbs/', '/', url)
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def make_filename(url: str) -> str:
    """Gera nome de arquivo determinístico a partir da URL."""
    h = hashlib.md5(url.encode()).hexdigest()[:12]
    ext = url.rsplit(".", 1)[-1].split("?")[0] if "." in url else "jpg"
    return f"{h}.{ext}"


def download_image(url: str, retries: int = 2) -> Optional[str]:
    """Baixa imagem para UPLOAD_DIR. Retorna filename ou None se falhar."""
    filename = make_filename(url)
    dest = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(dest) and os.path.getsize(dest) > 5000:
        return filename

    for attempt in range(retries):
        try:
            resp = SESSION.get(url, timeout=30, stream=True)
            if resp.status_code == 200 and len(resp.content) > 5000:
                with open(dest, "wb") as f:
                    f.write(resp.content)
                return filename
        except Exception as e:
            print(f"    [retry {attempt+1}] {e}")
        time.sleep(1)

    return None


def save_metadata(entries: list) -> None:
    """Grava metadata.json com todas as entradas coletadas."""
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"\nmetadata.json salvo: {len(entries)} produtos em {METADATA_PATH}")


def get_page(url: str, retries: int = 3) -> str:
    """Fetch HTML de uma URL com retry."""
    for i in range(retries):
        try:
            resp = SESSION.get(url, timeout=20)
            if resp.status_code == 200:
                return resp.text
            print(f"  HTTP {resp.status_code}: {url}")
        except Exception as e:
            print(f"  Erro (tentativa {i+1}): {e}")
        time.sleep(2)
    return ""


def scrape_league(league: dict) -> list:
    """Scrapa uma liga inteira. Retorna lista de entradas para metadata.json."""
    entries = []
    category_id = league["category_id"]

    if category_id is None:
        html = get_page(f"{BASE_URL}/categories")
        ids = find_category_ids(html, league["keywords"])
        if not ids:
            print(f"  [WARN] Liga não encontrada: {league['name']}")
            return []
        category_id = ids[0]
        print(f"  Liga '{league['name']}' encontrada: ID {category_id}")
        time.sleep(1.5)

    html = get_page(f"{BASE_URL}/categories/{category_id}")
    subcats = parse_subcategories(html)
    print(f"  {len(subcats)} times encontrados em {league['name']}")

    for team_name, team_id in subcats:
        time.sleep(1.5)
        html = get_page(f"{BASE_URL}/categories/{team_id}?isSubCate=true")
        albums = parse_albums(html)

        seen_types: dict = {}
        for album_title, album_id in albums:
            kit_type = detect_type(album_title)
            if kit_type is None or kit_type in seen_types:
                continue

            time.sleep(1.5)
            album_html = get_page(f"{BASE_URL}/albums/{album_id}")
            image_urls = parse_image_urls(album_html)

            if not image_urls:
                print(f"    [SKIP] Sem imagens: {album_title}")
                continue

            downloaded = []
            for img_url in image_urls:
                filename = download_image(img_url)
                if filename:
                    downloaded.append(filename)
                time.sleep(1)

            if not downloaded:
                print(f"    [SKIP] Download falhou: {album_title}")
                continue

            entries.append({
                "league": league["name"],
                "league_slug": league["slug"],
                "team": team_name,
                "type": kit_type,
                "album_name": album_title,
                "album_url": f"{BASE_URL}/albums/{album_id}",
                "images": downloaded,
            })
            seen_types[kit_type] = True
            print(f"    ✓ {team_name} {kit_type}: {len(downloaded)} imagens")

    return entries


def run():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print("=== Scraper Minkang — Craque Do Jogo Store ===\n")
    all_entries = []

    for league in TARGET_LEAGUES:
        print(f"\n[Liga] {league['name']}")
        entries = scrape_league(league)
        all_entries.extend(entries)
        print(f"  → {len(entries)} produtos coletados")

    save_metadata(all_entries)
    print(f"\n=== Concluído: {len(all_entries)} produtos no total ===")


if __name__ == "__main__":
    run()
