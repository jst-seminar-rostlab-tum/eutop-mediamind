import re
import string
import unicodedata
from logging import getLogger

from app.services.article_cleaner.cleaner_llm import ArticleCleaner

logger = getLogger(__name__)


async def clean_article_llm(text: str) -> str:
    cleaner = ArticleCleaner()
    return await cleaner.clean_plain_text(text)


def is_article_valid(text: str) -> bool:
    """
    Check if the article text contains only allowed characters.
    This function returns True if the text is valid, meaning it does not
    contain any disallowed characters.
    """
    return (
        not contains_disallowed_chars(text)
        and not contains_url(text)
        and has_minimum_content(text)
    )


def build_allowed_chars():
    allowed = set(
        string.ascii_letters
        + string.digits
        + ".,;:!?()[]\"'-–—…„“”’‹›«»‐‑"
        + "+-×÷=%<>±≈≠∞π√∑∆∫∂°$€£¥"
        + "@#^&*_~|\\"
        + "§"
        + " \u00a0\u202f\n\r\t"
        + "₀₁₂₃₄₅₆₇₈₉"
        + "¹²³⁴⁵⁶⁷⁸⁹⁰"
        + "‘’‚“”„‹›«»"
        + "㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩"
        + "µμΩωαβγΓΔδθλσΣφπΠχψΦΨ"
        + "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
        + "。、《》「」『』【】〜"
        + "ÆæŒœøØÅå"
        + "‰‱℃℉ℓ℮"
        + "·•※‧⁃"
        + "®™"
        + "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ"
        + "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿˢᵀᵁⱽᵂ"
        + "ʰʲʳʷʸˠˤˡˢˣ"
    )

    for codepoint in range(0x00A0, 0x2FFF):  # Latin Extended A/B/C/D/E
        char = chr(codepoint)
        try:
            if char.isalpha() and "LATIN" in unicodedata.name(char):
                allowed.add(char)
        except ValueError:
            continue

    return allowed


ALLOWED_CHARS = build_allowed_chars()


def contains_disallowed_chars(text: str, max_violations=5) -> bool:
    violations = 0
    for ch in text:
        if ch not in ALLOWED_CHARS and not ch.isspace():
            violations += 1
            if violations >= max_violations:
                logger.warning("... (too many violations, truncated)")
                return True
    return violations > 0


def contains_url(text: str) -> bool:
    """
    Detect if a string contains a URL (e.g., http(s) or www.).
    """
    url_pattern = re.compile(r"(http[s]?://|www\.)\S+", re.IGNORECASE)
    path_pattern = re.compile(r"(?<!\w)/[a-zA-Z0-9_\-]+(/[a-zA-Z0-9_\-]+)+")
    result = url_pattern.search(text) or path_pattern.search(text)
    if result:
        logger.warning(f"URL detected: {result.group(0)}")
        return True
    return False


def has_minimum_content(text: str, min_chars: int = 150) -> bool:
    condensed = re.sub(r"\s+", "", text)
    length = len(condensed)
    if length < min_chars:
        logger.warning(
            f"Article of length {length}, expected at least {min_chars}."
        )
        return False
    return True
