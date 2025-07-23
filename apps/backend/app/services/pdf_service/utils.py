# This file contains utility functions for the PDF service.


def calculate_reading_time(text, words_per_minute=180):
    word_count = len(text.split())
    return max(1, int(round(word_count / words_per_minute)))


# Hyphenation utilities
try:
    from hyphen import Hyphenator
except ImportError:
    Hyphenator = None


def get_hyphenator(lang_code):
    # Map ISO language code to PyHyphen dictionary
    lang_map = {
        "en": "en_US",
        "de": "de_DE",
        "fr": "fr_FR",
        "es": "es_ES",
        # Add more as needed
    }
    dict_code = lang_map.get(lang_code, "en_US")
    return Hyphenator(dict_code) if Hyphenator else None


def hyphenate_text(text, lang_code):
    h = get_hyphenator(lang_code)
    if not h or not text:
        return text

    def hyph_word(word):
        clean_word = word.replace("\u00ad", "")  # Remove existing soft hyphens
        if len(clean_word) > 8:
            # Split on real hyphens, hyphenate each part, then rejoin
            parts = clean_word.split("-")

            def hyph_part(part):
                if len(part) > 8:
                    if hasattr(h, "inserted"):
                        return h.inserted(part, hyphen="\u00ad")
                    elif hasattr(h, "syllables"):
                        sylls = h.syllables(part)
                        if sylls:
                            return "\u00ad".join(sylls)
                return part

            return "-".join(hyph_part(part) for part in parts)
        return clean_word

    return " ".join(hyph_word(w) for w in text.split())
