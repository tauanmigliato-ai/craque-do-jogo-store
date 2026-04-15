# tests/test_scraper.py
import sys
sys.path.insert(0, 'backend')

import scraper
from scraper import detect_type, find_category_ids, parse_subcategories, parse_albums, parse_image_urls


def test_detect_type_home():
    assert detect_type("Flamengo 2025-26 Home Jersey") == "home"

def test_detect_type_home_uppercase():
    assert detect_type("BRAZIL 2026 HOME") == "home"

def test_detect_type_away():
    assert detect_type("Flamengo 2025-26 Away Kit") == "away"

def test_detect_type_third():
    assert detect_type("Flamengo 2025-26 Third") == "third"

def test_detect_type_third_variant():
    assert detect_type("PSG 2025 3rd Kit") == "third"

def test_detect_type_unknown_returns_none():
    assert detect_type("Flamengo Goalkeeper 2025") is None

def test_detect_type_kids_returns_none():
    assert detect_type("Flamengo Kids Home 2025") is None

def test_detect_type_priority_home_over_away():
    assert detect_type("Home Away Kit") == "home"


def test_find_category_ids_brasileirao():
    html = '''
    <a href="/categories/680738">Brasileirão Série A</a>
    <a href="/categories/111111">Premier League</a>
    '''
    result = find_category_ids(html, ["brasileiro", "série a", "brasileirao"])
    assert "680738" in result

def test_find_category_ids_copa():
    html = '''
    <a href="/categories/999999">Copa do Mundo 2026</a>
    <a href="/categories/111111">Bundesliga</a>
    '''
    result = find_category_ids(html, ["copa do mundo", "world cup", "2026"])
    assert "999999" in result

def test_find_category_ids_no_match():
    html = '<a href="/categories/111111">NBA</a>'
    result = find_category_ids(html, ["copa do mundo"])
    assert result == []


def test_parse_subcategories():
    html = '''
    <a href="/categories/720293?isSubCate=true">Flamengo</a>
    <a href="/categories/720294?isSubCate=true">Palmeiras</a>
    <a href="/categories/720295">Not a subcategory</a>
    '''
    result = parse_subcategories(html)
    assert ("Flamengo", "720293") in result
    assert ("Palmeiras", "720294") in result
    assert len(result) == 2


def test_parse_albums():
    html = '''
    <a href="/albums/232738603">Brazil 2026 Home</a>
    <a href="/albums/232738604">Brazil 2026 Away</a>
    <a href="/categories/123">Not an album</a>
    '''
    result = parse_albums(html)
    assert ("Brazil 2026 Home", "232738603") in result
    assert ("Brazil 2026 Away", "232738604") in result
    assert len(result) == 2


def test_parse_image_urls():
    html = '''
    src="https://photo.yupoo.com/abc/def/small.jpg"
    src="https://photo.yupoo.com/ghi/jkl/medium.jpg"
    src="https://other.com/image.jpg"
    '''
    result = parse_image_urls(html)
    assert len(result) == 2
    assert all("medium.jpg" in url or "small" not in url for url in result)


# Testes de download (Task 3)
from unittest.mock import patch, MagicMock
import os, json, tempfile


def test_make_filename_is_deterministic():
    url = "https://photo.yupoo.com/abc/def/medium.jpg"
    name1 = scraper.make_filename(url)
    name2 = scraper.make_filename(url)
    assert name1 == name2
    assert name1.endswith(".jpg")


def test_make_filename_different_urls_differ():
    url1 = "https://photo.yupoo.com/abc/def/medium.jpg"
    url2 = "https://photo.yupoo.com/xyz/uvw/medium.jpg"
    assert scraper.make_filename(url1) != scraper.make_filename(url2)


def test_download_image_skips_if_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(scraper, "UPLOAD_DIR", str(tmp_path))
    url = "https://photo.yupoo.com/abc/def/medium.jpg"
    filename = scraper.make_filename(url)
    dest = tmp_path / filename
    dest.write_bytes(b"x" * 10000)

    result = scraper.download_image(url)
    assert result == filename


def test_download_image_fetches_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(scraper, "UPLOAD_DIR", str(tmp_path))
    url = "https://photo.yupoo.com/new/img/medium.jpg"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"x" * 15000

    with patch.object(scraper.SESSION, "get", return_value=mock_resp):
        result = scraper.download_image(url)

    assert result == scraper.make_filename(url)
    assert (tmp_path / result).exists()


def test_save_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(scraper, "METADATA_PATH", str(tmp_path / "metadata.json"))
    entries = [
        {
            "league": "Brasileirão",
            "league_slug": "brasileirao",
            "team": "Flamengo",
            "type": "home",
            "album_name": "Flamengo 2025 Home",
            "album_url": "https://minkang.x.yupoo.com/albums/1",
            "images": ["abc.jpg", "def.jpg"],
        }
    ]
    scraper.save_metadata(entries)
    data = json.loads((tmp_path / "metadata.json").read_text())
    assert data[0]["team"] == "Flamengo"
    assert data[0]["images"] == ["abc.jpg", "def.jpg"]
