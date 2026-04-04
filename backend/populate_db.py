#!/usr/bin/env python3
"""
Popula o banco de dados com produtos a partir das imagens baixadas.
Funciona a partir dos nomes dos arquivos (pXXX_YYY_hash.ext).
"""
import os, sys, json
sys.path.insert(0, '/opt/craque-do-jogo/backend')

from database import get_db_ctx, init_db
import hashlib

UPLOAD_DIR = "/opt/craque-do-jogo/uploads"

# Mapeamento de times brasileiros
TEAMS = [
    ("Flamengo", "Brasileirão", "Flamengo"),
    ("Corinthians", "Brasileirão", "Corinthians"),
    ("Palmeiras", "Brasileirão", "Palmeiras"),
    ("São Paulo FC", "Brasileirão", "São Paulo"),
    ("Cruzeiro", "Brasileirão", "Cruzeiro"),
    ("Atlético-MG", "Brasileirão", "Atlético"),
    ("Santos", "Brasileirão", "Santos"),
    ("Vasco da Gama", "Brasileirão", "Vasco"),
    ("Grêmio", "Brasileirão", "Grêmio"),
    ("Internacional", "Brasileirão", "Internacional"),
    ("Botafogo", "Brasileirão", "Botafogo"),
    ("Fluminense", "Brasileirão", "Fluminense"),
    ("Bahia", "Brasileirão", "Bahia"),
    ("Sport Club", "Brasileirão", "Sport"),
    ("Ceará", "Brasileirão", "Ceará"),
    ("Athletico-PR", "Brasileirão", "Athletico"),
    ("Real Madrid", "La Liga", "Real Madrid"),
    ("FC Barcelona", "La Liga", "Barcelona"),
    ("Liverpool FC", "Premier League", "Liverpool"),
    ("Manchester United", "Premier League", "Manchester United"),
    ("Manchester City", "Premier League", "Manchester City"),
    ("PSG", "Ligue 1", "PSG"),
    ("Bayern München", "Bundesliga", "Bayern"),
    ("Juventus", "Serie A", "Juventus"),
    ("Chelsea FC", "Premier League", "Chelsea"),
    ("Arsenal FC", "Premier League", "Arsenal"),
    ("AC Milan", "Serie A", "Milan"),
    ("Inter Milan", "Serie A", "Inter"),
    ("SL Benfica", "Liga Portugal", "Benfica"),
    ("FC Porto", "Liga Portugal", "Porto"),
    ("Seleção Brasileira", "Seleções", "Brasil"),
    ("Seleção Argentina", "Seleções", "Argentina"),
    ("Seleção da França", "Seleções", "França"),
    ("Seleção da Alemanha", "Seleções", "Alemanha"),
    ("Seleção Italiana", "Seleções", "Italia"),
    ("Seleção de Portugal", "Seleções", "Portugal"),
    ("Seleção da Espanha", "Seleções", "Espanha"),
    ("Seleção Inglesa", "Seleções", "Inglaterra"),
    ("Seleção Holandesa", "Seleções", "Holanda"),
    ("Los Angeles Lakers", "NBA", "Lakers"),
    ("Boston Celtics", "NBA", "Celtics"),
    ("Golden State Warriors", "NBA", "Warriors"),
    ("Chicago Bulls", "NBA", "Bulls"),
    ("Miami Heat", "NBA", "Heat"),
    ("New York Knicks", "NBA", "Knicks"),
    ("Brooklyn Nets", "NBA", "Nets"),
    ("Phoenix Suns", "NBA", "Suns"),
    ("Dallas Mavericks", "NBA", "Mavericks"),
    ("Milwaukee Bucks", "NBA", "Bucks"),
    ("Denver Nuggets", "NBA", "Nuggets"),
    ("LA Clippers", "NBA", "Clippers"),
    ("New York Yankees", "MLB", "Yankees"),
    ("Los Angeles Dodgers", "MLB", "Dodgers"),
    ("Boston Red Sox", "MLB", "Red Sox"),
    ("Chicago Cubs", "MLB", "Cubs"),
    ("Houston Astros", "MLB", "Astros"),
    ("San Francisco Giants", "MLB", "Giants"),
]

TYPES = ["home", "away", "third", "retro"]
SIZES = ["P", "M", "G", "GG", "XG"]


def slug(name: str) -> str:
    import re
    name = re.sub(r'[^\w\s]', '', name.lower())
    name = re.sub(r'[\s]+', '-', name.strip())
    return name[:60]


def populate():
    init_db()
    files = [f for f in os.listdir(UPLOAD_DIR)
             if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.getsize(os.path.join(UPLOAD_DIR, f)) > 50000]

    print(f"Encontrados {len(files)} imagens (50KB+)")
    if not files:
        print("Nenhuma imagem grande o suficiente..Execute o scraper primeiro.")
        return

    # Dividir em lotes de times
    products_per_team = max(1, len(files) // len(TEAMS))

    with get_db_ctx() as conn:
        created = 0
        base_idx = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

        for i, filename in enumerate(sorted(files)):
            team_idx = i // products_per_team
            if team_idx >= len(TEAMS):
                team_idx = i % len(TEAMS)

            team_name, league, team = TEAMS[team_idx]
            img_type = TYPES[i % len(TYPES)]

            # Nome do produto
            name = f"{team_name} {img_type.title()} {2024 + (i % 2)}-{2025 + (i % 2)}"
            product_slug = slug(name)

            # Verificar se já existe
            existing = conn.execute("SELECT id FROM products WHERE slug=?", (product_slug,)).fetchone()
            if existing:
                continue

            # URL da imagem (via FastAPI serve uploads)
            image_url = f"/uploads/{filename}"

            # Preço baseado no tipo (retro é mais caro)
            base_price = 189.90 if img_type == "retro" else 219.90
            compare_price = base_price + 40

            cur = conn.execute("""
                INSERT INTO products
                (name, slug, price, compare_price, image_url, sizes, league, team, type, stock, featured, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, product_slug,
                base_price, compare_price,
                image_url, json.dumps(SIZES),
                league, team, img_type,
                10, 1 if i < 30 else 0, 1
            ))
            created += 1
            if created % 20 == 0:
                print(f"  {created} produtos criados...")

        print(f"\n=== CONCLUIDO ===")
        print(f"  {created} novos produtos criados")
        total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"  Total no banco: {total}")


if __name__ == "__main__":
    populate()