#!/usr/bin/env python3
"""
Popula o banco de dados com produtos a partir das imagens baixadas.
Funciona a partir dos nomes dos arquivos (pXXX_YYY_hash.ext).
"""
import os, sys, json, re
sys.path.insert(0, '/opt/craque-do-jogo/backend')

from database import get_db_ctx, init_db

UPLOAD_DIR = "/opt/craque-do-jogo/uploads"

# ── Times principais ──
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

# ── Times infantis ──
INFANTIL_TEAMS = [
    ("Brasil", "Seleções", "Brasil"),
    ("Flamengo", "Brasileirão", "Flamengo"),
    ("Real Madrid", "La Liga", "Real Madrid"),
    ("Barcelona", "La Liga", "Barcelona"),
    ("Bayern", "Bundesliga", "Bayern"),
    ("PSG", "Ligue 1", "PSG"),
    ("Al-Nassr", "Pro League", "Al-Nassr"),
    ("Cruzeiro", "Brasileirão", "Cruzeiro"),
    ("Alemanha", "Seleções", "Alemanha"),
    ("Internacional", "Brasileirão", "Internacional"),
]

# ── Tipos ──
TYPES = ["home", "away", "third", "retro"]
INFANTIL_TYPES = ["home", "away", "third"]
SIZES = ["P", "M", "G", "GG", "XG"]
INFANTIL_SIZES = ["2", "4", "6", "8", "10", "12", "14"]


def slug(name: str) -> str:
    name = re.sub(r'[^\w\s]', '', name.lower())
    name = re.sub(r'[\s]+', '-', name.strip())
    return name[:60]


def calcular_preco(name: str, league: str) -> float:
    """Calcula o preço com base no nome e league do produto."""
    name_lower = name.lower()
    league_lower = league.lower()

    # NBA: R$259,90
    if league_lower == "nba" or any(t in name_lower for t in [
        "lakers", "celtics", "warriors", "bulls", "heat",
        "knicks", "nets", "suns", "mavericks", "bucks", "nuggets", "clippers"
    ]):
        return 259.90

    # MLB: R$259,90
    if league_lower == "mlb" or any(t in name_lower for t in [
        "yankees", "dodgers", "red sox", "cubs", "astros", "giants"
    ]):
        return 259.90

    # Infantil: R$199,90 (todos)
    if "infantil" in name_lower:
        return 199.90

    # Retrô: detecta ano no nome
    if any(k in name_lower for k in ["retro", "copa", "vintage"]):
        anos = re.findall(r'\b(19[789]\d|200[0-5])\b', name)
        if anos:
            ano = int(anos[0])
            if ano <= 1998:
                return 199.90   # Standard (anos 90)
            else:
                return 209.90   # Premium (anos 2000+)
        if "manga longa" in name_lower:
            return 229.90
        return 209.90   # padrão retrô

    # Comum (padrão)
    return 175.90


def populate():
    init_db()
    files = [f for f in os.listdir(UPLOAD_DIR)
             if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.getsize(os.path.join(UPLOAD_DIR, f)) > 50000]

    print(f"Encontrados {len(files)} imagens (50KB+)")
    if not files:
        print("Nenhuma imagem grande o suficiente. Execute o scraper primeiro.")
        return

    infantil_files = [f for f in files if "infantil" in f.lower()]
    regular_files   = [f for f in files if f not in infantil_files]

    products_per_team  = max(1, len(regular_files)  // len(TEAMS))
    infantil_per_team  = max(1, len(infantil_files) // len(INFANTIL_TEAMS))

    with get_db_ctx() as conn:
        created = 0

        # ── Produtos infantis ──
        for i, filename in enumerate(infantil_files):
            team_idx = i // infantil_per_team
            if team_idx >= len(INFANTIL_TEAMS):
                team_idx = i % len(INFANTIL_TEAMS)

            team_name, league, team = INFANTIL_TEAMS[team_idx]
            img_type = INFANTIL_TYPES[i % len(INFANTIL_TYPES)]
            year_str = f"{2024 + (i % 2)}-{2025 + (i % 2)}"
            name = f"{team_name} Infantil {img_type.title()} {year_str}"
            product_slug = slug(name)

            existing = conn.execute("SELECT id FROM products WHERE slug=?", (product_slug,)).fetchone()
            if existing:
                continue

            image_url   = f"/uploads/{filename}"
            base_price  = calcular_preco(name, league)
            compare_price = base_price + 40

            conn.execute("""
                INSERT INTO products
                (name, slug, price, compare_price, image_url, sizes, league, team, type, stock, featured, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, product_slug,
                base_price, compare_price,
                image_url, json.dumps(INFANTIL_SIZES),
                league, team, "infantil",
                10, 1 if i < 15 else 0, 1
            ))
            created += 1

        # ── Produtos regulares ──
        for i, filename in enumerate(regular_files):
            team_idx = i // products_per_team
            if team_idx >= len(TEAMS):
                team_idx = i % len(TEAMS)

            team_name, league, team = TEAMS[team_idx]
            img_type = TYPES[i % len(TYPES)]
            year_str = f"{2024 + (i % 2)}-{2025 + (i % 2)}"
            name = f"{team_name} {img_type.title()} {year_str}"
            product_slug = slug(name)

            existing = conn.execute("SELECT id FROM products WHERE slug=?", (product_slug,)).fetchone()
            if existing:
                continue

            image_url     = f"/uploads/{filename}"
            base_price    = calcular_preco(name, league)
            compare_price = base_price + 40

            conn.execute("""
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

        print(f"\n=== CONCLUÍDO ===")
        print(f"  {created} novos produtos criados")
        total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"  Total no banco: {total}")


if __name__ == "__main__":
    populate()
