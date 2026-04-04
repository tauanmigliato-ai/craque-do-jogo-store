#!/usr/bin/env python3
"""
Scraper Yupoo — baixa TODAS as imagens do álbum (páginas 1-20).
Filtra apenas elementos muito pequenos (logos, ícones).
"""
import os, asyncio, hashlib, time
from pathlib import Path

UPLOAD_DIR = "/opt/craque-do-jogo/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MIN_SIZE = 20000  # 20KB — elimina logos/ícones

# Times brasileiros que queremos priorizar (para nome do arquivo)
TEAM_KEYWORDS = [
    "flamengo", "corinthians", "palmeiras", "sao paulo", "cruzeiro", "atletico",
    "santos", "vasco", "gremio", "internacional", "botafogo", "fluminense",
    "bahia", "sport", "ceara", "athletico",
    "real madrid", "barcelona", "liverpool", "manchester", "psg", "bayern",
    "juventus", "chelsea", "arsenal", "milan", "inter", "benfica", "porto",
    "brasil", "argentina", "franca", "alemanha", "italia", "portugal", "espanha",
    "inglaterra", "holanda", "uruguai",
    "lakers", "celtics", "warriors", "bulls", "heat", "nets", "knicks", "suns",
    "mavericks", "bucks", "nuggets", "clippers",
    "yankees", "dodgers", "red sox", "cubs", "astros", "giants",
]

def make_filename(url: str, page: int, idx: int) -> str:
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    ext = url.split(".")[-1] if "." in url else "jpg"
    return f"p{page:03d}_{idx:03d}_{h}.{ext}"

def download(url: str, dest: str) -> bool:
    import requests
    try:
        resp = requests.get(url, timeout=25,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
                "Referer": "https://camisetafutbol.x.yupoo.com/",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            },
            stream=True)
        if resp.status_code == 200:
            content = resp.content
            if len(content) >= MIN_SIZE:
                with open(dest, "wb") as f:
                    f.write(content)
                return True
    except Exception as e:
        print(f"  Erro: {e}")
    return False


async def scrape_page(page_num: int, browser):
    url = f"https://camisetafutbol.x.yupoo.com/albums?tab=gallery&page={page_num}"
    print(f"\n[{page_num}/20] Acessando...")
    try:
        page_obj = await browser.new_page()
        await page_obj.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page_obj.wait_for_timeout(3000)

        # Coletar URLs — média resolução
        urls = await page_obj.evaluate("""() => {
            const seen = new Set();
            const results = [];
            document.querySelectorAll("img").forEach(img => {
                const src = img.src || img.getAttribute("data-src") || "";
                if (src.includes("photo.yupoo") && !seen.has(src)) {
                    seen.add(src);
                    const hiRes = src.replace("/thumbs/", "/").replace("/small.", "/medium.");
                    results.push(hiRes);
                }
            });
            return results;
        }""")

        print(f"  -> {len(urls)} imagens")
        await page_obj.close()
        return urls
    except Exception as e:
        print(f"  Erro: {e}")
        try:
            await page_obj.close()
        except:
            pass
        return []


async def main():
    from playwright.async_api import async_playwright

    print("=== Scraper Yupoo - Baixando todas as imagens ===\n")

    downloaded = 0
    skipped = 0

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )

        for page_num in range(1, 21):
            img_urls = await scrape_page(page_num, browser)

            for idx, img_url in enumerate(img_urls):
                filename = make_filename(img_url, page_num, idx)
                dest = os.path.join(UPLOAD_DIR, filename)

                # Pular se já existe e tem tamanho ok
                if os.path.exists(dest):
                    size = os.path.getsize(dest)
                    if size >= MIN_SIZE:
                        skipped += 1
                        continue

                print(f"  [{idx+1}/{len(img_urls)}] {filename}")
                ok = download(img_url, dest)
                if ok:
                    downloaded += 1
                    size = os.path.getsize(dest) / 1024
                    print(f"    OK {size:.0f}KB")
                else:
                    print(f"    FALHOU")

                # Respeitoso com o servidor
                await asyncio.sleep(0.3)

            print(f"  Página {page_num}: {downloaded} baixadas, {skipped} já existentes")
            await asyncio.sleep(2)

        await browser.close()

    total = len(os.listdir(UPLOAD_DIR))
    print(f"\n=== CONCLUIDO ===")
    print(f"  Total baixadas: {downloaded}")
    print(f"  Já existiam: {skipped}")
    print(f"  Arquivos em {UPLOAD_DIR}: {total}")


if __name__ == "__main__":
    asyncio.run(main())