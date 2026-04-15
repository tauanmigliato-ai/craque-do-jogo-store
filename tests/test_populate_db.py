# tests/test_populate_db.py
import sys, json, os
sys.path.insert(0, 'backend')

import populate_db


SAMPLE_METADATA = [
    {
        "league": "Brasileirão",
        "league_slug": "brasileirao",
        "team": "Flamengo",
        "type": "home",
        "album_name": "Flamengo 2025-26 Home",
        "album_url": "https://minkang.x.yupoo.com/albums/1",
        "images": ["abc123.jpg", "def456.jpg"],
    },
    {
        "league": "Brasileirão",
        "league_slug": "brasileirao",
        "team": "Flamengo",
        "type": "away",
        "album_name": "Flamengo 2025-26 Away",
        "album_url": "https://minkang.x.yupoo.com/albums/2",
        "images": ["ghi789.jpg"],
    },
    {
        "league": "Copa do Mundo 2026",
        "league_slug": "copa-do-mundo",
        "team": "Brasil",
        "type": "home",
        "album_name": "Brazil 2026 Home",
        "album_url": "https://minkang.x.yupoo.com/albums/3",
        "images": ["jkl012.jpg"],
    },
]


def test_calcular_preco_brasileirao_home():
    assert populate_db.calcular_preco("Brasileirão", "home") == 175.90

def test_calcular_preco_brasileirao_away():
    assert populate_db.calcular_preco("Brasileirão", "away") == 175.90

def test_calcular_preco_brasileirao_third():
    assert populate_db.calcular_preco("Brasileirão", "third") == 189.90

def test_calcular_preco_copa_home():
    assert populate_db.calcular_preco("Copa do Mundo 2026", "home") == 175.90

def test_calcular_preco_copa_away():
    assert populate_db.calcular_preco("Copa do Mundo 2026", "away") == 175.90

def test_calcular_preco_copa_third():
    assert populate_db.calcular_preco("Copa do Mundo 2026", "third") == 189.90


def test_populate_inserts_products(tmp_path, monkeypatch):
    import sqlite3

    db_path = str(tmp_path / "test.db")
    meta_path = str(tmp_path / "metadata.json")

    with open(meta_path, "w") as f:
        json.dump(SAMPLE_METADATA, f)

    monkeypatch.setattr(populate_db, "METADATA_PATH", meta_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(open("backend/schema.sql").read())

    populate_db.populate_with_conn(conn, SAMPLE_METADATA)

    products = conn.execute("SELECT * FROM products").fetchall()
    assert len(products) == 3

    flamengo_home = conn.execute(
        "SELECT * FROM products WHERE team=? AND type=?", ("Flamengo", "home")
    ).fetchone()
    assert flamengo_home is not None
    assert flamengo_home["league"] == "Brasileirão"
    assert flamengo_home["price"] == 175.90
    assert flamengo_home["compare_price"] == 215.90
    assert flamengo_home["image_url"] == "/uploads/abc123.jpg"
    assert "def456.jpg" in flamengo_home["images"]

    categories = conn.execute("SELECT * FROM categories").fetchall()
    assert len(categories) == 2
    slugs = [c["slug"] for c in categories]
    assert "brasileirao" in slugs
    assert "copa-do-mundo" in slugs

    conn.close()


def test_populate_sets_featured_for_first_20(tmp_path, monkeypatch):
    import sqlite3

    db_path = str(tmp_path / "test.db")
    meta_path = str(tmp_path / "metadata.json")

    many = []
    for i in range(25):
        many.append({
            "league": "Brasileirão",
            "league_slug": "brasileirao",
            "team": f"Time{i}",
            "type": "home",
            "album_name": f"Time{i} Home",
            "album_url": f"https://minkang.x.yupoo.com/albums/{i}",
            "images": [f"img{i}.jpg"],
        })

    with open(meta_path, "w") as f:
        json.dump(many, f)

    monkeypatch.setattr(populate_db, "METADATA_PATH", meta_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(open("backend/schema.sql").read())
    populate_db.populate_with_conn(conn, many)

    featured = conn.execute("SELECT COUNT(*) FROM products WHERE featured=1").fetchone()[0]
    assert featured == 20

    conn.close()
