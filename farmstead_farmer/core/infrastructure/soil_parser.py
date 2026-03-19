import re
import unicodedata


class SoilTypeParserUA:
    """Rule-based soil type extractor for Ukrainian free text fields."""

    CANONICAL_SOILS = {
        'суглинок': ('суглин',),
        'чорнозем': ('чорнозем',),
        'супісок': ('супіщан', 'супіс', 'супіск'),
        'піщаний ґрунт': ('піщан',),
        'глинистий ґрунт': ('глинист',),
    }

    NOISE_PATTERNS = [
        r'добре\s+росте',
        r'підходить\s+для\s+вирощування',
        r'вимагає',
        r'не\s*вимоглив\w*',
        r'невимоглив\w*',
        r'нейтральн\w*',
        r'родюч\w*',
        r'слабокисл\w*',
        r'дренован\w*',
        r'цей\s+сорт',
        r'а\s+також',
    ]

    def _normalize_text(self, text: str) -> str:
        text = (text or '').lower()
        text = ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.combining(ch))
        text = text.replace('ё', 'е')
        text = text.replace('ї', 'і')
        text = text.replace('ї̈', 'ї')
        text = re.sub(r'["“”„\'`]', '', text)
        text = re.sub(r'[.!?;:()]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _remove_noise(self, text: str) -> str:
        cleaned = text
        for pattern in self.NOISE_PATTERNS:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def parse(self, raw_text: str) -> list[str]:
        text = self._normalize_text(raw_text)
        if not text:
            return []

        # Unrestricted/neutral phrasing means we should not block by soil type.
        if re.search(r'(не\s*вимоглив\w*|невимоглив\w*|нейтральн\w*)', text, flags=re.IGNORECASE):
            return []

        text = self._remove_noise(text)
        found = []

        for canonical, stems in self.CANONICAL_SOILS.items():
            if any(stem in text for stem in stems):
                found.append(canonical)

        # stable output order based on dict order
        return found
