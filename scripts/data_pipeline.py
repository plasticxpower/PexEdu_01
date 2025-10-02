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
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import parse_qsl, quote_plus, urlencode, urljoin, urlparse, urlunparse

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

logger = logging.getLogger(__name__)

RESIZE_QUERY_KEYS = {
    "width",
    "w",
    "height",
    "h",
    "crop",
    "c",
    "fit",
    "auto",
    "quality",
    "q",
    "format",
    "fm",
    "dpr",
}

NEGATIVE_ALT_KEYWORDS = (
    "illustration",
    "drawing",
    "diagram",
    "map",
    "vector",
    "clipart",
    "clip art",
    "logo",
    "icon",
    "silhouette",
    "coat of arms",
    "emblem",
    "badge",
    "flag",
    "statue",
    "sculpture",
    "toy",
    "stuffed",
    "animation",
    "cartoon",
    "poster",
    "typography",
    "text",
    "word",
    "words",
)

NEGATIVE_URL_KEYWORDS = (
    "illustration",
    "vector",
    "logo",
    "icon",
    "diagram",
    "map",
    "clipart",
    "clip-art",
    "silhouette",
    "coat-of-arms",
    "emblem",
    "badge",
    "flag",
    "cartoon",
    "drawing",
    "typography",
    "poster",
    "infographic",
)

ANIMAL_LABEL_KEYWORDS = (
    "animal",
    "mammal",
    "bird",
    "reptile",
    "amphibian",
    "fish",
    "insect",
    "arachnid",
    "crustacean",
    "mollusk",
    "fox",
    "wolf",
    "dog",
    "canine",
    "cat",
    "feline",
    "lion",
    "tiger",
    "leopard",
    "cheetah",
    "panther",
    "jaguar",
    "lynx",
    "bobcat",
    "bear",
    "panda",
    "koala",
    "kangaroo",
    "wallaby",
    "elephant",
    "giraffe",
    "hippopotamus",
    "rhinoceros",
    "antelope",
    "gazelle",
    "deer",
    "moose",
    "elk",
    "boar",
    "pig",
    "hog",
    "cow",
    "bull",
    "bison",
    "buffalo",
    "camel",
    "alpaca",
    "llama",
    "goat",
    "sheep",
    "horse",
    "zebra",
    "donkey",
    "monkey",
    "ape",
    "orangutan",
    "gorilla",
    "chimp",
    "lemur",
    "ibex",
    "sloth",
    "otter",
    "beaver",
    "weasel",
    "badger",
    "ferret",
    "wolverine",
    "skunk",
    "raccoon",
    "possum",
    "marsupial",
    "rodent",
    "squirrel",
    "mouse",
    "rat",
    "hamster",
    "porcupine",
    "hedgehog",
    "bat",
    "rabbit",
    "hare",
    "seal",
    "walrus",
    "sea lion",
    "manatee",
    "dolphin",
    "whale",
    "orca",
    "narwhal",
    "shark",
    "hammerhead",
    "ray",
    "manta",
    "stingray",
    "eel",
    "salmon",
    "trout",
    "cod",
    "tuna",
    "pike",
    "lionfish",
    "seahorse",
    "frog",
    "bullfrog",
    "toad",
    "salamander",
    "newt",
    "snake",
    "viper",
    "python",
    "cobra",
    "boa",
    "lizard",
    "gecko",
    "iguana",
    "chameleon",
    "dragon",
    "turtle",
    "tortoise",
    "alligator",
    "crocodile",
    "bird",
    "eagle",
    "hawk",
    "falcon",
    "owl",
    "penguin",
    "albatross",
    "pelican",
    "heron",
    "stork",
    "spoonbill",
    "ibis",
    "swan",
    "goose",
    "duck",
    "flamingo",
    "crane",
    "parrot",
    "macaw",
    "toucan",
    "cockatoo",
    "lyrebird",
    "kiwi",
    "emu",
    "cassowary",
    "ostrich",
    "vulture",
    "puffin",
    "kingfisher",
    "hummingbird",
    "bee",
    "ant",
    "butterfly",
    "moth",
    "dragonfly",
    "spider",
    "scorpion",
    "lobster",
    "crab",
    "shrimp",
    "octopus",
    "squid",
    "starfish",
    "urchin",
    "pangolin",
)

POSITIVE_ALT_KEYWORDS = (
    "wild",
    "habitat",
    "nature",
    "forest",
    "ocean",
    "desert",
    "jungle",
    "savanna",
    "land",
    "sea",
    "reef",
    "river",
    "mountain",
    "tundra",
) + ANIMAL_LABEL_KEYWORDS


@dataclass
class ImageCandidate:
    urls: list[str]
    alt_text: str
    width: Optional[int]
    height: Optional[int]
    score: int

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


def _parse_dimension(value: object) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    stringified = str(value).strip().lower()
    if not stringified:
        return None
    stringified = stringified.replace("px", "")
    if "x" in stringified:
        stringified = stringified.split("x")[0]
    try:
        return int(float(stringified))
    except ValueError:
        return None


def sanitize_image_variants(url: str) -> list[str]:
    parsed = urlparse(url)
    if not parsed.scheme:
        return [url]

    filtered_query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in RESIZE_QUERY_KEYS
    ]
    sanitized_query = urlencode(filtered_query, doseq=True) if filtered_query else ""
    sanitized = urlunparse(parsed._replace(query=sanitized_query))

    variants: list[str] = []
    if sanitized:
        variants.append(sanitized)
    if url not in variants:
        variants.append(url)
    return variants


_SRCSET_DESCRIPTOR = re.compile(r"(?P<value>\d+)(?P<unit>[wx])")


def _parse_srcset(attr: str) -> list[tuple[str, Optional[int]]]:
    entries: list[tuple[str, Optional[int]]] = []
    for chunk in attr.split(','):
        candidate = chunk.strip()
        if not candidate:
            continue
        url_part, _, descriptor = candidate.partition(' ')
        width: Optional[int] = None
        match = _SRCSET_DESCRIPTOR.search(descriptor)
        if match:
            width = int(match.group('value'))
            if match.group('unit') == 'x':
                width *= 1000
        entries.append((url_part, width))
    entries.sort(key=lambda item: item[1] or 0, reverse=True)
    return entries


def collect_image_candidates(soup: BeautifulSoup, base_url: str) -> list[ImageCandidate]:
    candidates: list[ImageCandidate] = []
    seen_nodes: set[int] = set()
    seen_urls: set[str] = set()

    def consider(img: BeautifulSoup) -> None:
        node_id = id(img)
        if node_id in seen_nodes:
            return
        seen_nodes.add(node_id)

        classes = img.get('class', [])
        if isinstance(classes, str):
            classes = [classes]
        if any('logo' in cls.lower() for cls in classes if isinstance(cls, str)):
            return

        alt_text = (img.get('alt') or '').strip()
        alt_lower = alt_text.lower()
        if 'logo' in alt_lower or 'placeholder' in alt_lower:
            return

        variant_entries: list[tuple[str, Optional[int]]] = []
        for attr in ('data-srcset', 'srcset'):
            value = img.get(attr)
            if value:
                variant_entries.extend(_parse_srcset(value))
                break

        direct_width = _parse_dimension(img.get('data-width')) or _parse_dimension(img.get('width'))
        direct_height = _parse_dimension(img.get('data-height')) or _parse_dimension(img.get('height'))
        for attr in ('data-src', 'data-original', 'data-url', 'src'):
            value = img.get(attr)
            if value:
                variant_entries.append((value, direct_width))
                break

        if not variant_entries:
            return

        normalized_urls: list[str] = []
        max_width: Optional[int] = None
        for raw_url, width in variant_entries:
            if not raw_url:
                continue
            absolute = urljoin(base_url, raw_url)
            if not absolute:
                continue
            if is_placeholder_image(absolute):
                continue
            lowered = absolute.lower()
            if any(keyword in lowered for keyword in NEGATIVE_URL_KEYWORDS):
                continue
            for variant in sanitize_image_variants(absolute):
                if variant in seen_urls:
                    continue
                normalized_urls.append(variant)
                seen_urls.add(variant)
                if len(normalized_urls) >= 6:
                    break
            if len(normalized_urls) >= 6:
                break
            if width and (max_width is None or width > max_width):
                max_width = width

        if not normalized_urls:
            return

        score = (max_width or 0) * 4 + (direct_height or 0)
        if alt_lower:
            if any(keyword in alt_lower for keyword in POSITIVE_ALT_KEYWORDS):
                score += 2500
            if any(keyword in alt_lower for keyword in NEGATIVE_ALT_KEYWORDS):
                score -= 3000

        candidates.append(
            ImageCandidate(
                urls=normalized_urls,
                alt_text=alt_text,
                width=max_width,
                height=direct_height,
                score=score,
            )
        )

    for selector in ('figure img', '.md-assembly img', '.assemblies img', 'img'):
        for img in soup.select(selector):
            consider(img)

    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates


@dataclass
class AnimalSeed:
    group: str
    common_name: str
    scientific_name: str
    size: str
    life_expectancy: str
    habitat: str
    fun_fact: str
    image_url: str
    image_search_terms: list[str]


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


class ImageValidator:
    def __init__(self, *, debug: bool = False, log: Optional[logging.Logger] = None) -> None:
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            self._image_module = None
        else:
            self._image_module = Image

        try:
            import numpy as np  # type: ignore
        except ImportError:
            self._np = None
        else:
            self._np = np

        self._clip_model = None
        self._clip_processor = None
        self._clip_device = None
        self._clip_initialised = False
        self._torch = None
        self._vision_model = None
        self._vision_device = None
        self._vision_transforms = None
        self._vision_categories: Optional[list[str]] = None
        self._last_clip_positive: Optional[float] = None
        self._last_clip_negative: Optional[float] = None
        self._debug = debug
        self._log = log or logger
        self._clip_prompts = [
            "a photo of a living animal in the wild",
            "a photo of a living animal in its natural habitat",
            "a drawing or illustration of an animal",
            "an image of an animal statue or toy",
            "an image with text over a picture of an animal",
        ]
        self._clip_positive_indices = {0, 1}

    def _debug_log(self, message: str) -> None:
        if self._debug and self._log:
            self._log.info(message)

    def accepts(
        self,
        image_bytes: bytes,
        *,
        alt_text: str = "",
        scientific_name: str = "",
        common_name: str = "",
        source_url: str = "",
    ) -> bool:
        descriptor = source_url or alt_text or scientific_name or "<unknown>"
        self._debug_log(f"Validating image candidate {descriptor}")
        if not image_bytes:
            self._debug_log(f"Rejecting {descriptor}: empty payload")
            return False

        alt_lower = (alt_text or "").lower()
        alt_support = self._alt_text_supports(alt_lower, scientific_name, common_name)
        strong_alt_match = self._alt_text_matches_names(alt_lower, scientific_name, common_name)
        if source_url and any(keyword in source_url.lower() for keyword in NEGATIVE_URL_KEYWORDS):
            self._debug_log(f"Rejecting {descriptor}: URL keyword filter")
            return False
        if alt_lower and any(keyword in alt_lower for keyword in NEGATIVE_ALT_KEYWORDS):
            self._debug_log(f"Rejecting {descriptor}: negative alt keyword match")
            return False

        image = self._load_image(image_bytes)
        if image is None:
            if strong_alt_match:
                self._debug_log(f"Accepting {descriptor}: image decode unavailable but alt text supports animal")
                return True
            else:
                self._debug_log(f"Rejecting {descriptor}: cannot decode image and alt text unsupported")
                return False
        try:
            if image.width < 320 or image.height < 240:
                self._debug_log(f"Rejecting {descriptor}: resolution {image.width}x{image.height} below threshold")
                return False

            if self._detect_text_overlay(image):
                self._debug_log(f"Rejecting {descriptor}: detected text overlay")
                return False

            vision_result: Optional[bool] = None
            passed_clip = self._clip_confirms(image)
            clip_positive = self._last_clip_positive if self._last_clip_positive is not None else None
            if (
                passed_clip is False
                and clip_positive is not None
                and clip_positive < 0.05
                and not strong_alt_match
            ):
                self._debug_log(
                    f"Rejecting {descriptor}: CLIP confidence {clip_positive:.3f} too low for override"
                )
                return False
            if passed_clip is False:
                vision_result = self._vision_confirms(image)
                if vision_result:
                    self._debug_log(
                        f"Overriding CLIP rejection for {descriptor}: vision model detected animal subject"
                    )
                    passed_clip = None
                elif strong_alt_match:
                    self._debug_log(
                        f"Overriding CLIP rejection for {descriptor}: alt text strongly matches animal context"
                    )
                    passed_clip = None
                else:
                    self._debug_log(f"Rejecting {descriptor}: CLIP classifier flagged as non-natural photo")
                    return False

            if passed_clip is None and not self._basic_variance_check(image):
                self._debug_log(f"Rejecting {descriptor}: grayscale variance too low without CLIP confirmation")
                return False

            if alt_lower and not alt_support:
                self._debug_log(f"Rejecting {descriptor}: alt text lacks animal context")
                return False

            if vision_result is None:
                vision_result = self._vision_confirms(image)
            if vision_result is False:
                self._debug_log(f"Rejecting {descriptor}: vision model did not find an animal subject")
                return False

            self._debug_log(
                f"Accepted {descriptor}: {image.width}x{image.height}, clip={'yes' if passed_clip else 'no'}"
            )
            return True
        finally:
            try:
                image.close()
            except Exception:
                pass

    def _load_image(self, image_bytes: bytes):
        image_module = self._image_module
        if image_module is None:
            return None
        try:
            with image_module.open(BytesIO(image_bytes)) as image:
                return image.convert("RGB")
        except Exception:
            return None

    def _basic_variance_check(self, image) -> bool:
        if self._np is None:
            return True
        gray = image.convert("L")
        try:
            arr = self._np.asarray(gray)
        finally:
            try:
                gray.close()
            except Exception:
                pass
        return float(arr.std()) > 12.0

    def _detect_text_overlay(self, image) -> bool:
        if self._np is None:
            return False
        downscaled = image.copy()
        try:
            downscaled.thumbnail((512, 512))
            arr = self._np.asarray(downscaled.convert("L"))
            if arr.size == 0:
                return False
            high = (arr > 240).mean()
            low = (arr < 15).mean()
            return high > 0.55 and low > 0.15
        finally:
            try:
                downscaled.close()
            except Exception:
                pass

    def _alt_text_supports(self, alt_lower: str, scientific_name: str, common_name: str) -> bool:
        if not alt_lower:
            return True
        tokens: set[str] = set()
        for name in (scientific_name, common_name):
            for token in re.split(r"[^a-z0-9]+", name.lower()):
                if len(token) >= 4:
                    tokens.add(token)
        if not tokens:
            return False
        return any(token in alt_lower for token in tokens)

    def _alt_text_matches_names(self, alt_lower: str, scientific_name: str, common_name: str) -> bool:
        if not alt_lower:
            return False
        names = [scientific_name.lower(), common_name.lower()]
        return any(name and name in alt_lower for name in names)

    def _label_is_animal(self, label: str) -> bool:
        lower = label.lower()
        return any(keyword in lower for keyword in ANIMAL_LABEL_KEYWORDS)

    def _ensure_vision_model(self) -> bool:
        if self._vision_model is not None:
            return True
        try:
            import torch
            from torchvision import models
        except ImportError:
            self._debug_log("torch/torchvision unavailable; cannot run vision check")
            return False

        try:
            weights_enum = getattr(models, "ResNet50_Weights", None)
            if weights_enum is None:
                raise RuntimeError("ResNet50 weights unavailable")
            weights = getattr(weights_enum, "IMAGENET1K_V2", getattr(weights_enum, "DEFAULT"))
            model = models.resnet50(weights=weights)
        except Exception:
            self._debug_log("Failed to initialise ResNet50 vision model")
            return False

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()

        self._vision_model = model
        self._vision_device = device
        self._vision_transforms = weights.transforms()
        self._vision_categories = list(weights.meta.get("categories", []))
        self._torch = torch
        self._debug_log(f"Vision model ready on device {device}")
        return True

    def _vision_confirms(self, image) -> Optional[bool]:
        if not self._ensure_vision_model():
            return None
        assert self._vision_model is not None and self._vision_transforms is not None
        if not self._vision_categories:
            return None
        torch = self._torch
        assert torch is not None
        transforms = self._vision_transforms
        tensor = transforms(image).unsqueeze(0).to(self._vision_device)
        with torch.no_grad():
            logits = self._vision_model(tensor)
            probs = torch.nn.functional.softmax(logits[0], dim=0)
        top_probs, top_indices = probs.topk(5)
        labels = [self._vision_categories[index] for index in top_indices.tolist()]
        label_debug = ", ".join(f"{label}:{prob:.3f}" for label, prob in zip(labels, top_probs.tolist()))
        self._debug_log(f"Vision labels: {label_debug}")
        if any(self._label_is_animal(label) for label in labels):
            return True
        return False

    def _clip_confirms(self, image) -> Optional[bool]:
        self._last_clip_positive = None
        self._last_clip_negative = None
        if not self._ensure_clip():
            self._debug_log("Skipping CLIP evaluation: model unavailable")
            return None
        assert self._clip_processor is not None and self._clip_model is not None and self._torch is not None
        processor = self._clip_processor
        torch = self._torch
        inputs = processor(text=self._clip_prompts, images=image, return_tensors="pt", padding=True)
        inputs = {key: tensor.to(self._clip_device) for key, tensor in inputs.items()}
        with torch.no_grad():
            outputs = self._clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        positive = max(probs[index].item() for index in self._clip_positive_indices)
        negative = max(
            probs[index].item()
            for index in range(len(self._clip_prompts))
            if index not in self._clip_positive_indices
        )
        self._last_clip_positive = positive
        self._last_clip_negative = negative
        self._debug_log(
            f"CLIP evaluation: positive={positive:.3f}, negative={negative:.3f}"
        )
        return positive >= 0.35 and positive >= negative + 0.1

    def _ensure_clip(self) -> bool:
        if self._clip_initialised:
            return self._clip_model is not None
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor  # type: ignore
        except ImportError:
            self._clip_initialised = True
            self._debug_log("CLIP dependencies missing; install torch and transformers for full validation")
            return False

        try:
            model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        except Exception:
            self._clip_initialised = True
            self._debug_log("Failed to load CLIP model from Hugging Face; continuing without it")
            return False

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()

        self._clip_model = model
        self._clip_processor = processor
        self._clip_device = device
        self._torch = torch
        self._clip_initialised = True
        self._debug_log(f"CLIP model ready on device {device}")
        return True
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
def derive_image_filename(url: str, animal_id: str) -> str:
    parsed = urlparse(url)
    basename = os.path.basename(parsed.path)
    _, _, ext = basename.rpartition('.')
    ext = ext.lower() if ext else 'jpg'
    return f"{animal_id}.{ext}"


def build_record(
    seed: AnimalSeed,
    client: BritannicaClient,
    image_dir: Path,
    *,
    skip_images: bool,
    image_validator: Optional[ImageValidator] = None,
    debug: bool = False,
    used_hashes: Optional[set[str]] = None,
) -> AnimalRecord:
    try:
        article_url = client.fetch_article_url(seed.scientific_name)
    except RuntimeError:
        article_url = client.fetch_article_url(seed.common_name)
    article_soup = client.fetch_article(article_url)

    size_sentence = seed.size or ""
    life_sentence = seed.life_expectancy or ""
    habitat_sentence = seed.habitat or ""
    fun_sentence = seed.fun_fact or ""

    image_path = "/assets/placeholder.svg"
    if not skip_images:
        direct_urls: list[str] = []
        if seed.image_url:
            direct_urls = sanitize_image_variants(seed.image_url)
        if direct_urls:
            if debug:
                logger.info("Trying direct image URL(s) for %s", seed.scientific_name)
            for candidate_url in direct_urls:
                try:
                    image_bytes = client.download_image(candidate_url)
                except Exception:
                    if debug:
                        logger.info("Direct download failed for %s", candidate_url)
                    continue
                candidate_hash = hashlib.sha256(image_bytes).hexdigest()
                if used_hashes is not None and candidate_hash in used_hashes:
                    if debug:
                        logger.info("Direct image duplicate for %s", candidate_url)
                    continue
                if image_validator and not image_validator.accepts(
                    image_bytes,
                    alt_text=seed.common_name,
                    scientific_name=seed.scientific_name,
                    common_name=seed.common_name,
                    source_url=candidate_url,
                ):
                    continue
                filename = derive_image_filename(candidate_url, slugify_scientific_name(seed.scientific_name))
                target_path = image_dir / filename
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(image_bytes)
                if used_hashes is not None:
                    used_hashes.add(candidate_hash)
                image_path = f"/assets/animals/{filename}"
                if debug:
                    logger.info("Selected direct image %s for %s", candidate_url, seed.scientific_name)
                break
            if not image_path.endswith('placeholder.svg'):
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

        search_terms: list[str] = []
        seen_terms: set[str] = set()
        for term in [seed.scientific_name, seed.common_name, *seed.image_search_terms]:
            if not term:
                continue
            normalized = term.strip().lower()
            if not normalized or normalized in seen_terms:
                continue
            seen_terms.add(normalized)
            try:
                article_url = client.fetch_article_url(term)
            except RuntimeError:
                continue
            article_soup = client.fetch_article(article_url)
            candidates = collect_image_candidates(article_soup, article_url)
            if debug:
                logger.info(
                    "Found %d image candidates for %s using term %s",
                    len(candidates),
                    seed.scientific_name,
                    term,
                )
            if not candidates:
                continue

            attempted_urls: set[str] = set()
            for candidate in candidates:
                chosen_url: Optional[str] = None
                chosen_hash: Optional[str] = None
                image_bytes: Optional[bytes] = None
                for candidate_url in candidate.urls:
                    if candidate_url in attempted_urls:
                        continue
                    attempted_urls.add(candidate_url)
                    if debug:
                        logger.info(
                            "Downloading candidate image %s (alt=%r) for %s",
                            candidate_url,
                            candidate.alt_text,
                            seed.scientific_name,
                        )
                    try:
                        image_bytes = client.download_image(candidate_url)
                    except Exception:
                        if debug:
                            logger.info("Download failed for %s", candidate_url)
                        image_bytes = None
                        continue

                    candidate_hash = hashlib.sha256(image_bytes).hexdigest()
                    if used_hashes is not None and candidate_hash in used_hashes:
                        if debug:
                            logger.info("Skipping duplicate image for %s", candidate_url)
                        image_bytes = None
                        continue

                    if image_validator and not image_validator.accepts(
                        image_bytes,
                        alt_text=candidate.alt_text,
                        scientific_name=seed.scientific_name,
                        common_name=seed.common_name,
                        source_url=candidate_url,
                    ):
                        image_bytes = None
                        continue

                    chosen_url = candidate_url
                    chosen_hash = candidate_hash
                    break

                if chosen_url and image_bytes:
                    filename = derive_image_filename(chosen_url, slugify_scientific_name(seed.scientific_name))
                    target_path = image_dir / filename
                    if client.refresh or not target_path.exists():
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        target_path.write_bytes(image_bytes)
                    if used_hashes is not None and chosen_hash is not None:
                        used_hashes.add(chosen_hash)
                    image_path = f"/assets/animals/{filename}"
                    if debug:
                        logger.info("Selected image %s for %s", chosen_url, seed.scientific_name)
                    break
            if not image_path.endswith('placeholder.svg'):
                break

        if image_path.endswith('placeholder.svg') and debug:
            logger.info("No acceptable image found for %s", seed.scientific_name)

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
                size=raw.get("size", ""),
                life_expectancy=raw.get("lifeExpectancy", ""),
                habitat=raw.get("habitat", ""),
                fun_fact=raw.get("funFact", ""),
                image_url=raw.get("imageUrl", ""),
                image_search_terms=list(raw.get("imageSearch", [])) if isinstance(raw.get("imageSearch", []), (list, tuple)) else ([raw.get("imageSearch")] if raw.get("imageSearch") else []),
            )
        )
    return seeds


def serialize_records(records: Iterable[AnimalRecord], path: Path) -> None:
    payload = [record.__dict__ for record in records]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def run(
    limit: Optional[int],
    skip_images: bool,
    refresh: bool,
    output_path: Path,
    image_dir: Path,
    *,
    debug_image_selection: bool = False,
) -> None:
    seeds = load_seeds(Path("data/animals_source.json"))
    if limit is not None:
        seeds = seeds[:limit]

    client = BritannicaClient(refresh=refresh)
    image_validator = None if skip_images else ImageValidator(debug=debug_image_selection, log=logger)
    used_hashes: Optional[set[str]] = None
    if not skip_images:
        used_hashes = set()
        if image_dir.exists() and not refresh:
            for existing in image_dir.glob("*"):
                try:
                    used_hashes.add(hashlib.sha256(existing.read_bytes()).hexdigest())
                except Exception:
                    continue
    records: list[AnimalRecord] = []
    failures: list[tuple[AnimalSeed, Exception]] = []
    for seed in seeds:
        try:
            record = build_record(
                seed,
                client,
                image_dir,
                skip_images=skip_images,
                image_validator=image_validator,
                debug=debug_image_selection,
                used_hashes=used_hashes,
            )
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
    parser.add_argument(
        "--debug-image-selection",
        action="store_true",
        help="Emit detailed logs about image candidate filtering",
    )

    args = parser.parse_args(argv)
    if args.debug_image_selection:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    run(
        args.limit,
        args.skip_images,
        args.refresh,
        args.output,
        args.image_dir,
        debug_image_selection=args.debug_image_selection,
    )


if __name__ == "__main__":
    main()
