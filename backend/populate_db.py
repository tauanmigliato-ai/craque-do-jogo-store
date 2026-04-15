#!/usr/bin/env python3
"""
Popula o banco a partir do metadata.json gerado pelo scraper.
Executa: python populate_db.py
"""
import os
import sys
import json
import sqlite3
import re

METADATA_PATH = "/opt/craque-do-jogo/uploads/metadata.json"

CATEGORIES = [
    {"name": "Copa do Mundo 2026", "slug": "copa-do-mundo"},
    {"name": "Brasileirão",        "slug": "brasileirao"},
]

SIZES = ["P", "M", "G", "GG", "XG"]


def calcular_preco(league: str, kit_type: str) -> float:
    """Retorna preço base pelo tipo e liga."""
    if kit_type == "third":
        return 189.90
    return 175.90


def _slug(text: str) -> str:
    text = re.sub(r"[^\w\s]", "", text.lower())
    text = re.sub(r"\s+", "-", text.strip())
    return text[:60]


def populate_with_conn(conn: sqlite3.Connection, entries: list) -> None:
    """Popula banco a partir de lista de entradas. Recebe conexão aberta (testável)."""
    conn.execute("DELETE FROM products")
    conn.execute("DELETE FROM categories")
    conn.commit()

    # Cria categorias
    cat_map: dict = {}
    for cat in CATEGORIES:
        cur = conn.execute(
            "INSERT INTO categories (name, slug) VALUES (?, ?)",
            (cat["name"], cat["slug"]),
        )
        cat_map[cat["slug"]] = cur.lastrowid
    conn.commit()

    # Insere produtos
    inserted = 0
    for entry in entries:
        league = entry["league"]
        league_slug = entry["league_slug"]
        team = entry["team"]
        kit_type = entry["type"]
        images = entry["images"]

        if not images:
            print(f"  [SKIP] Sem imagens: {team} {kit_type}")
            continue

        category_id = cat_map.get(league_slug)
        price = calcular_preco(league, kit_type)
        compare_price = round(price + 40, 2)
        image_url = f"/uploads/{images[0]}"
        images_json = json.dumps([f"/uploads/{img}" for img in images])
        product_name = f"{team} {kit_type.title()} 2025-26"
        product_slug = _slug(product_name)
        featured = 1 if inserted < 20 else 0

        existing = conn.execute(
            "SELECT id FROM products WHERE slug=?", (product_slug,)
        ).fetchone()
        if existing:
            print(f"  [SKIP] Já existe: {product_slug}")
            continue

        conn.execute(
            """
            INSERT INTO products
              (name, slug, price, compare_price, image_url, images, sizes,
               category_id, team, league, type, stock, featured, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                product_name, product_slug, price, compare_price,
                image_url, images_json, json.dumps(SIZES),
                category_id, team, league, kit_type,
                10, featured,
            ),
        )
        inserted += 1
        if inserted % 10 == 0:
            print(f"  {inserted} produtos inseridos...")

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"\n=== Concluído: {inserted} produtos inseridos (total no banco: {total}) ===")


def populate() -> None:
    """Entry point para execução na VPS."""
    if not os.path.exists(METADATA_PATH):
        print(f"ERRO: {METADATA_PATH} não encontrado. Execute o scraper primeiro.")
        sys.exit(1)

    with open(METADATA_PATH, encoding="utf-8") as f:
        entries = json.load(f)

    print(f"metadata.json carregado: {len(entries)} entradas")

    # Importa funções do backend da VPS
    sys.path.insert(0, "/opt/craque-do-jogo/backend")
    from database import get_db_ctx, init_db

    init_db()
    with get_db_ctx() as conn:
        populate_with_conn(conn, entries)


if __name__ == "__main__":
    populate()
