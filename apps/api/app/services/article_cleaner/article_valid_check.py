import string
from logging import getLogger

logger = getLogger(__name__)


def is_article_valid(text: str) -> bool:
    """
    Check if the article text contains only allowed characters.
    This function returns True if the text is valid, meaning it does not
    contain any disallowed characters.
    """
    return not contains_disallowed_chars(text)


ALLOWED_CHARS = set(
    string.ascii_letters
    + string.digits
    + "äöüÄÖÜßéèêëàâîïôùûçÉÈÊËÀÂÎÏÔÙÛÇ"  # german, french characters
    + ".,;:!?()[]\"'-–—…"  # punctuation
    + "+-×÷=%<>±≈≠∞π√∑∆∫∂°$€£¥"  # numbers and symbols
    + "@#^&*_~|\\"
    + " "  # space
)


def contains_disallowed_chars(text: str, max_violations=5) -> bool:
    violations = 0
    for ch in text:
        if ch not in ALLOWED_CHARS and not ch.isspace():
            logger.warning
            (f"[Gibberish] illegal char: '{ch}' (U+{ord(ch):04X})")
            violations += 1
            if violations >= max_violations:
                print("... (too many violations, truncated)")
                return True
    return violations > 0
