# This file parses Markdown into Reportlab Paragraph functions
import re

from reportlab.platypus import ListFlowable, ListItem, Paragraph


def markdown_to_html(text: str) -> str:
    """
    Converts inline markdown (bold, italic, bold-italic) to simple
    HTML tags that ReportLab can use with the fonts.py "addMappings".
    Does NOT handle headings or block structure.
    """
    # Convert markdown to HTML suitable for ReportLab Paragraphs
    # Only allow <b>, <i>, <br/>, <para> tags
    # This implementation avoids overlapping tags (e.g., <b><i>text</b></i>)
    # 'text' is already the argument; no need to reassign
    # Replace < and > to avoid HTML injection
    text = text.replace("<", "&lt;").replace(">", "&gt;")

    # To avoid nested/overlapping tags, parse markdown in order:
    # bold-italic, bold, italic, and do not allow overlapping
    # Replace bold-italic (***text*** or ___text___)
    text = re.sub(r"(\*\*\*\*|___)(.+?)(\1)", r"<b><i>\2</i></b>", text)
    # Replace bold (**text** or __text__)
    text = re.sub(r"(\*\*|__)(.+?)(\1)", r"<b>\2</b>", text)
    # Replace italic (*text* or _text_)
    text = re.sub(r"(\*|_)(.+?)(\1)", r"<i>\2</i>", text)

    # Remove any remaining asterisks/underscores (malformed markdown)
    text = text.replace("*", "").replace("_", "")

    # Replace newlines with <br/>
    text = text.replace("\n", "<br/>")

    # Remove duplicate tags
    text = re.sub(r"(<i>)+", "<i>", text)
    text = re.sub(r"(</i>)+", "</i>", text)
    text = re.sub(r"(<b>)+", "<b>", text)
    text = re.sub(r"(</b>)+", "</b>", text)

    # Remove overlapping and mis-nested tags
    # Remove <b><i>...</i></i></b> => <b><i>...</i></b>
    text = re.sub(r"<b><i>(.*?)</i></i></b>", r"<b><i>\1</i></b>", text)
    # Remove <b><i>...</b></i></b> => <b><i>...</i></b>
    text = re.sub(r"<b><i>(.*?)</b></i></b>", r"<b><i>\1</i></b>", text)
    # Remove <b><i>...</i></b></i> => <b><i>...</i></b>
    text = re.sub(r"<b><i>(.*?)</i></b></i>", r"<b><i>\1</i></b>", text)
    # Remove <b><i>...</b></b></i> => <b><i>...</i></b>
    text = re.sub(r"<b><i>(.*?)</b></b></i>", r"<b><i>\1</i></b>", text)

    # Wrap in <para> for ReportLab
    return f"<para>{text}</para>"


def _flush_paragraph(paragraph, blocks):
    """Helper to flush a paragraph block into blocks list if not empty."""
    if paragraph:
        para_text = "\n".join(paragraph).strip()
        if para_text:
            blocks.append((para_text, "content_style"))
        paragraph.clear()


def parse_markdown_blocks(text: str):
    """
    Parses markdown text into a list of (content, style_key) tuples.
    Recognizes headings (# ...), paragraphs, and lists.
    Lists are returned as (items, "ul") or (items, "ol") where items
    is a list of strings.
    """
    blocks = []
    lines = text.splitlines()
    paragraph = []
    list_items = []
    list_type = None
    ul_pattern = re.compile(r"^\s*([-*+])\s+(.*)")
    ol_pattern = re.compile(r"^\s*(\d+)\.\s+(.*)")
    heading_pattern = re.compile(r"^(#+)\s+(.*)")

    for line in lines + [None]:  # Add None to flush last block
        if line is None or re.match(r"^\s*$", line):
            _flush_paragraph(paragraph, blocks)
            if list_items:
                blocks.append((list_items, list_type))
                list_items = []
                list_type = None
            continue

        heading_match = heading_pattern.match(line)
        ul_match = ul_pattern.match(line)
        ol_match = ol_pattern.match(line)

        if heading_match:
            _flush_paragraph(paragraph, blocks)
            if list_items:
                blocks.append((list_items, list_type))
                list_items = []
                list_type = None
            hashes, heading_text = heading_match.groups()
            level = len(hashes)
            style_key = f"h{level}"
            blocks.append((heading_text.strip(), style_key))
        elif ul_match:
            _flush_paragraph(paragraph, blocks)
            if list_type not in (None, "ul"):
                blocks.append((list_items, list_type))
                list_items = []
            list_type = "ul"
            list_items.append(ul_match.group(2).strip())
        elif ol_match:
            _flush_paragraph(paragraph, blocks)
            if list_type not in (None, "ol"):
                blocks.append((list_items, list_type))
                list_items = []
            list_type = "ol"
            list_items.append(ol_match.group(2).strip())
        else:
            if list_items:
                blocks.append((list_items, list_type))
                list_items = []
                list_type = None
            paragraph.append(line)
    return blocks


def markdown_blocks_to_paragraphs(text: str, styles):
    """
    Converts markdown text to a list of
    ReportLab Paragraph/ListFlowable objects with correct styles.
    """
    blocks = parse_markdown_blocks(text)
    paragraphs = []
    for content, style_key in blocks:
        if style_key in ("ul", "ol"):
            # Render list items as ListFlowable
            bulletType = "bullet" if style_key == "ul" else "1"
            items = [
                ListItem(
                    Paragraph(markdown_to_html(item), styles["content_style"])
                )
                for item in content
            ]
            paragraphs.append(
                ListFlowable(
                    items,
                    bulletType=bulletType,
                    start="1" if style_key == "ol" else None,
                )
            )
        else:
            html = markdown_to_html(content)
            style = styles.get(style_key, styles["content_style"])
            paragraphs.append(Paragraph(html, style))
    return paragraphs
