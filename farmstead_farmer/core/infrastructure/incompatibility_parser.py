import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedIncompatibility:
    incompatible_species_names: list[str]
    incompatible_categories: list[str]


class IncompatibilityParserUA:
    """Lightweight UA incompatibility parser for non-structured text fields.

    It is intentionally rule-based and dependency-free to run in production
    without heavy NLP models.
    """

    _STOP_WORDS = {
        'усі', 'всі', 'види', 'види', 'культур', 'культурами', 'культури', 'культура',
        'зокрема', 'з', 'із', 'зі', 'та', 'і', 'й', 'або', 'для', 'зокрема з'
    }

    _CATEGORY_PATTERNS = {
        'кісточкові': re.compile(r'кісточк\w*', re.IGNORECASE),
        'гарбузові': re.compile(r'гарбузов\w*', re.IGNORECASE),
    }

    _MORPH_ENDINGS = (
        'ами', 'ями', 'ові', 'еві', 'ому', 'ему', 'ою', 'ею', 'єю', 'ий', 'ій', 'а', 'я', 'у', 'ю', 'і', 'и', 'о',
    )

    def __init__(self, known_species_names: list[str] | None = None):
        self._known_species = list({self._normalize_phrase(x) for x in (known_species_names or []) if x})

    @staticmethod
    def _strip_accents(value: str) -> str:
        return ''.join(ch for ch in unicodedata.normalize('NFKD', value) if not unicodedata.combining(ch))

    def _normalize_phrase(self, text: str) -> str:
        text = self._strip_accents(text.lower())
        text = re.sub(r'["“”„\'`]', '', text)
        text = re.sub(r'[.!?;:()]', ',', text)
        text = text.replace('—', '-')
        text = re.sub(r'\s+', ' ', text).strip(' ,')
        return text

    def _split_chunks(self, text: str) -> list[str]:
        normalized = re.sub(r'\s+(і|й|та)\s+', ',', text)
        return [part.strip(' ,') for part in normalized.split(',') if part.strip(' ,')]

    def _extract_categories(self, text: str) -> set[str]:
        categories: set[str] = set()
        for canonical, pattern in self._CATEGORY_PATTERNS.items():
            if pattern.search(text):
                categories.add(canonical)
        return categories

    def _simple_lemma_word(self, word: str) -> str:
        w = re.sub(r'[^a-zа-щьюяґєії\-]', '', word, flags=re.IGNORECASE)
        if not w:
            return ''
        for suffix in self._MORPH_ENDINGS:
            if len(w) > len(suffix) + 2 and w.endswith(suffix):
                return w[:-len(suffix)]
        return w

    def _candidate_to_canonical_species(self, candidate: str) -> str | None:
        if not candidate:
            return None

        cleaned = self._normalize_phrase(candidate)
        if not cleaned:
            return None

        tokens = [t for t in cleaned.split() if t not in self._STOP_WORDS]
        if not tokens:
            return None

        cleaned = ' '.join(tokens)

        # Remove obvious helper words often present in chunks
        cleaned = re.sub(r'\b(усі|всі|види|зокрема|культур\w*)\b', '', cleaned).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(' ,')
        if not cleaned:
            return None

        # Best-effort typo fixes for known frequent values
        cleaned = cleaned.replace('садовий жасми', 'садовий жасмин')
        cleaned = cleaned.replace('порічки золотисті', 'порічка золотиста')
        cleaned = cleaned.replace('порічки золотиста', 'порічка золотиста')

        # If direct match exists
        if cleaned in self._known_species:
            return cleaned

        # Try normalized/lemmatized stem matching against known species
        candidate_stems = [self._simple_lemma_word(t) for t in cleaned.split()]
        candidate_stems = [s for s in candidate_stems if s]
        if not candidate_stems:
            return None

        best_match = None
        best_score = 0

        for species in self._known_species:
            species_tokens = species.split()
            species_stems = [self._simple_lemma_word(t) for t in species_tokens]
            species_stems = [s for s in species_stems if s]
            if not species_stems:
                continue

            overlap = len(set(candidate_stems) & set(species_stems))
            if overlap > best_score:
                best_score = overlap
                best_match = species

            # strong partial match for single-word forms
            if len(candidate_stems) == 1 and len(species_stems) == 1:
                c = candidate_stems[0]
                s = species_stems[0]
                if c == s or c in s or s in c:
                    best_match = species
                    best_score = max(best_score, 1)

        if best_match and best_score > 0:
            return best_match

        # fallback: return normalized candidate
        return cleaned

    def parse(self, raw_text: str) -> ParsedIncompatibility:
        text = self._normalize_phrase(raw_text or '')
        if not text:
            return ParsedIncompatibility([], [])

        categories = self._extract_categories(text)
        species: set[str] = set()

        chunks = self._split_chunks(text)
        for chunk in chunks:
            if re.search(r'культур\w*', chunk):
                continue
            canonical = self._candidate_to_canonical_species(chunk)
            if canonical:
                species.add(canonical)

        # remove entries that are clearly category-like
        species = {s for s in species if s not in categories}

        return ParsedIncompatibility(
            incompatible_species_names=sorted(species),
            incompatible_categories=sorted(categories),
        )
