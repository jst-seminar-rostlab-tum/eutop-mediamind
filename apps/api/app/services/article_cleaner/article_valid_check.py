import string
import unicodedata
from logging import getLogger

logger = getLogger(__name__)


def is_article_valid(text: str) -> bool:
    """
    Check if the article text contains only allowed characters.
    This function returns True if the text is valid, meaning it does not
    contain any disallowed characters.
    """
    return not contains_disallowed_chars(text)


def build_allowed_chars():
    allowed = set(
        string.ascii_letters
        + string.digits
        + ".,;:!?()[]\"'-–—…„“”’‹›«»/‐‑"
        + "+-×÷=%<>±≈≠∞π√∑∆∫∂°$€£¥"
        + "@#^&*_~|\\"
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
        + "©®™"
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
            logger.warning(
                f"[Gibberish] illegal char: '{ch}' (U+{ord(ch):04X})"
            )
            violations += 1
            if violations >= max_violations:
                logger.warning("... (too many violations, truncated)")
                return True
    return violations > 1
