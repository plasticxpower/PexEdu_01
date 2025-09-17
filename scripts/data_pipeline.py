"""PexEdu data collection pipeline.

This script reads the curated seed list in data/animals_source.json and queries
Britannica for each animal using its scientific name. It extracts descriptive
sentences for the memory cards and downloads the leading image that the article
exposes through Open Graph metadata. The resulting structured dataset is written
back to data/animals.json and images are stored under public/assets/animals.

The pipeline is intentionally resilient so it can be resumed; if an image or
article is already cached locally it is not fetched again unless --refresh
is provided.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import quote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BRITANNICA_BASE = "https://www.britannica.com"
USER_AGENT = "PexEduDataCollector/1.0 (+https://example.com)"
TEXT_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

SIZE_KEYWORDS = ("size", "length", "height", "weight", "wingspan", "mass")
LIFE_KEYWORDS = ("life span", "lifespan", "life expectancy", "longevity", "years old")
HABITAT_KEYWORDS = ("habitat", "native", "found", "range", "distributed", "lives in")

TIMEOUT = 20
EXCLUDED_PHRASES = (
    'our editors will review',
    'this article was most recently revised',
    'britannica premium',
    'subscribe to britannica',
    'click here to',
    'join britannica',
    'citation style rules',
    'britannica quiz'
)

RETRY_DELAY = 3
MAX_RETRIES = 3

def is_placeholder_image(url: str) -> bool:
    lowered = url.lower()
    return any(token in lowered for token in ('thistle', 'social-image', 'placeholder', 'default', 'thumbnail'))

def sentence_is_informative(sentence: str) -> bool:
    cleaned = sentence.strip()
    if len(cleaned) < 40:
        return False
    lower = cleaned.lower()
    if any(phrase in lower for phrase in EXCLUDED_PHRASES):
        return False
    if cleaned.endswith(':'):
        return False
    return True


@dataclass
class AnimalSeed:
    group: str
    common_name: str
    scientific_name: str


@dataclass
class AnimalRecord:
    id: str
    group: str
    commonName: str
    scientificName: str
    size: str
    lifeExpectancy: str
    habitat: str
    funFact: str
    image: str


class BritannicaClient:
    def __init__(self, *, refresh: bool = False) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.refresh = refresh

    def fetch_article_url(self, scientific_name: str) -> str:
        search_url = f"{BRITANNICA_BASE}/search?query={quote_plus(scientific_name)}"
        response = self._request("GET", search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        candidates = []
        # Primary search result list.
        for anchor in soup.select("li.m-search-results__item a[href]"):
            href = anchor.get("href")
            if not href:
                continue
            text = anchor.get_text(" ", strip=True).lower()
            href_lower = href.lower()
            score = 0
            if scientific_name.lower() in text:
                score += 3
            if scientific_name.lower().replace(" ", "-") in href_lower:
                score += 2
            if "/animal/" in href_lower:
                score += 1
            candidates.append((score, href))

        # Fallback to any anchor that mentions "/science/" topics.
        if not candidates:
            for anchor in soup.select("a[href]"):
                href = anchor.get("href") or ""
                if not href.startswith("/"):
                    continue
                href_lower = href.lower()
                if any(part in href_lower for part in ("/animal/", "/science/", "/plant/")):
                    candidates.append((0, href))

        if not candidates:
            raise RuntimeError(f"No search results found for {scientific_name}")

        candidates.sort(key=lambda item: item[0], reverse=True)
        chosen = candidates[0][1]
        return urljoin(BRITANNICA_BASE, chosen)

    def fetch_article(self, url: str) -> BeautifulSoup:
        response = self._request("GET", url)
        return BeautifulSoup(response.text, "html.parser")

    def download_image(self, url: str) -> bytes:
        response = self._request("GET", url, stream=True)
        return response.content

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        for attempt in range(MAX_RETRIES):
            response = self.session.request(method, url, timeout=TIMEOUT, **kwargs)
            if response.status_code >= 400:
                if attempt == MAX_RETRIES - 1:
                    response.raise_for_status()
                time.sleep(RETRY_DELAY)
                continue
            return response
        raise RuntimeError(f"Failed to fetch {url}")


def slugify_scientific_name(scientific_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", scientific_name.lower()).strip("_")


def extract_sentences(soup: BeautifulSoup) -> list[str]:
    article_sections = soup.select("section.m-article__body-content p")
    if not article_sections:
        article_sections = soup.select("article p")

    sentences: list[str] = []
    for paragraph in article_sections:
        text = paragraph.get_text(" ", strip=True)
        if not text:
            continue
        for sentence in TEXT_SENTENCE_SPLIT.split(text):
            cleaned = sentence.strip()
            if cleaned:
                sentences.append(cleaned)
    return sentences


def pick_sentence(sentences: Iterable[str], keywords: Iterable[str], used: set[str]) -> Optional[str]:
    for sentence in sentences:
        lower = sentence.lower()
        if sentence in used:
            continue
        if any(keyword in lower for keyword in keywords):
            used.add(sentence)
            return sentence
    return None


def fallback_sentence(sentences: Iterable[str], used: set[str]) -> str:
    sentinel = None
    for sentence in sentences:
        if sentinel is None:
            sentinel = sentence
        if sentence not in used:
            used.add(sentence)
            return sentence
    if sentinel is not None:
        return sentinel
    raise RuntimeError("Could not locate any descriptive sentence")


def select_image_url(soup: BeautifulSoup) -> str | None:
    def candidate_from(img: BeautifulSoup) -> str | None:
        classes = img.get('class', [])
        if isinstance(classes, str):
            classes = [classes]
        if any('logo' in cls for cls in classes):
            return None
        alt = (img.get('alt') or '').lower()
        if 'logo' in alt:
            return None
        for attr in ('data-width', 'width'):
            value = img.get(attr)
            if value:
                try:
                    if int(str(value).split('x')[0]) < 200:
                        return None
                except ValueError:
                    pass
        for attr in ('data-height', 'height'):
            value = img.get(attr)
            if value:
                try:
                    if int(str(value)) < 150:
                        return None
                except ValueError:
                    pass
        for attr in ('data-src', 'data-original', 'data-srcset', 'src'):
            candidate = img.get(attr)
            if candidate:
                candidate = candidate.split(' ')[0]
                if not is_placeholder_image(candidate):
                    return candidate
        return None

    for selector in ('figure img', '.md-assembly img', '.assemblies img'):
        img = soup.select_one(selector)
        if img:
            url = candidate_from(img)
            if url:
                return url
    for img in soup.select('img'):
        url = candidate_from(img)
        if url:
            return url
    return None



def derive_image_filename(url: str, animal_id: str) -> str:
    parsed = urlparse(url)
    basename = os.path.basename(parsed.path)
    _, _, ext = basename.rpartition('.')
    ext = ext.lower() if ext else 'jpg'
    return f"{animal_id}.{ext}"


def build_record(seed: AnimalSeed, client: BritannicaClient, image_dir: Path, *, skip_images: bool) -> AnimalRecord:
    try:
        article_url = client.fetch_article_url(seed.scientific_name)
    except RuntimeError:
        article_url = client.fetch_article_url(seed.common_name)
    article_soup = client.fetch_article(article_url)

    sentences = extract_sentences(article_soup)
    if not sentences:
        raise RuntimeError(f"No descriptive content found for {seed.scientific_name}")

    informative = [sentence for sentence in sentences if sentence_is_informative(sentence)]
    pool = informative if informative else sentences

    used_sentences: set[str] = set()
    size_sentence = pick_sentence(pool, SIZE_KEYWORDS, used_sentences) or fallback_sentence(pool, used_sentences)
    life_sentence = pick_sentence(pool, LIFE_KEYWORDS, used_sentences) or fallback_sentence(pool, used_sentences)
    habitat_sentence = pick_sentence(pool, HABITAT_KEYWORDS, used_sentences) or fallback_sentence(pool, used_sentences)
    fun_sentence = fallback_sentence(pool, used_sentences)

    image_path = "/assets/placeholder.svg"
    if not skip_images:
        image_url = select_image_url(article_soup)
        if not image_url and seed.common_name.lower() != seed.scientific_name.lower():
            try:
                common_url = client.fetch_article_url(seed.common_name)
            except RuntimeError:
                common_url = None
            if common_url and common_url != article_url:
                common_soup = client.fetch_article(common_url)
                fallback_image = select_image_url(common_soup)
                if fallback_image:
                    image_url = fallback_image
        if image_url:
            filename = derive_image_filename(image_url, slugify_scientific_name(seed.scientific_name))
            target_path = image_dir / filename
            if client.refresh or not target_path.exists():
                image_bytes = client.download_image(image_url)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(image_bytes)
            image_path = f"/assets/animals/{filename}"

    return AnimalRecord(
        id=slugify_scientific_name(seed.scientific_name),
        group=seed.group,
        commonName=seed.common_name,
        scientificName=seed.scientific_name,
        size=size_sentence,
        lifeExpectancy=life_sentence,
        habitat=habitat_sentence,
        funFact=fun_sentence,
        image=image_path,
    )


def load_seeds(path: Path) -> list[AnimalSeed]:
    raw_entries = json.loads(path.read_text(encoding="utf-8"))
    seeds: list[AnimalSeed] = []
    for raw in raw_entries:
        seeds.append(
            AnimalSeed(
                group=raw["group"],
                common_name=raw["commonName"],
                scientific_name=raw["scientificName"],
            )
        )
    return seeds


def serialize_records(records: Iterable[AnimalRecord], path: Path) -> None:
    payload = [record.__dict__ for record in records]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def run(limit: Optional[int], skip_images: bool, refresh: bool, output_path: Path, image_dir: Path) -> None:
    seeds = load_seeds(Path("data/animals_source.json"))
    if limit is not None:
        seeds = seeds[:limit]

    client = BritannicaClient(refresh=refresh)
    records: list[AnimalRecord] = []
    failures: list[tuple[AnimalSeed, Exception]] = []
    for seed in seeds:
        try:
            record = build_record(seed, client, image_dir, skip_images=skip_images)
        except Exception as exc:  # noqa: BLE001 - re-raise after processing
            failures.append((seed, exc))
            continue
        records.append(record)
        time.sleep(0.5)  # be polite to Britannica

    if failures:
        messages = [f"{seed.scientific_name} ({seed.common_name}): {exc}" for seed, exc in failures]
        raise RuntimeError("Some animals failed to process:\n" + "\n".join(messages))

    serialize_records(records, output_path)


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Fetch animal data and images from Britannica")
    parser.add_argument("--limit", type=int, help="Only process the first N animals from the seed list")
    parser.add_argument("--skip-images", action="store_true", help="Do not download images, keep placeholder paths")
    parser.add_argument("--refresh", action="store_true", help="Force re-download of images even if cached")
    parser.add_argument("--output", type=Path, default=Path("data/animals.json"), help="Path to write the compiled dataset")
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path("public/assets/animals"),
        help="Directory for storing downloaded images",
    )

    args = parser.parse_args(argv)
    run(args.limit, args.skip_images, args.refresh, args.output, args.image_dir)


if __name__ == "__main__":
    main()
