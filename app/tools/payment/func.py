import re

from flask import request

from config import FlaskConfig


def get_paginated_data(query):
    """Возвращает query paginate data."""

    page = request.args.get("page", 1, type=int)
    paginated_data = query.paginate(
        page=page, per_page=FlaskConfig.ITEMS_PER_PAGE, error_out=True
    )
    return paginated_data


def transliterate(text):
    """Транслитерация текста."""

    cyrillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    latin = (
        "a|b|v|g|d|e|e|zh|z|i|i|k|l|m|n|o|p|r|s|t|u|f|kh|tc|ch|sh|shch||"
        "y||e|iu|ia|A|B|V|G|D|E|E|Zh|Z|I|I|K|L|M|N|O|P|R|S|T|U|F|Kh|Tc|"
        "Ch|Sh|Shch||Y||E|Iu|Ia".split("|")
    )
    return text.translate({ord(k): v for k, v in zip(cyrillic, latin)})


def make_slug(text, prefix=None):
    """Делает Slug из текста."""

    def process(data):
        return re.sub(
            "[^a-z_A-Z0-9]+",
            "",
            transliterate(data).replace(" ", "_").rstrip().lower(),
        )[:32]

    return process(f"{prefix}{text}") if prefix else process(text)
