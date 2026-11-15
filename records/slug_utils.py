"""Латинские URL для русских и англоязычных названий пластинок."""

import unicodedata

from django.utils.text import slugify


_CYRILLIC = (
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ("a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k",
     "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts",
     "ch", "sh", "shch", "", "y", "", "e", "yu", "ya"),
)
_TRANSLITERATION = dict(zip(*_CYRILLIC))


def record_slug_base(title, artist):
    """Возвращает короткий slug из названия и исполнителя (без ID)."""
    value = f"{title} {artist}".lower()
    value = "".join(_TRANSLITERATION.get(char, char) for char in value)
    value = unicodedata.normalize("NFKD", value)
    value = slugify(value, allow_unicode=False)
    return value[:175].strip("-") or "record"
