#This file parses Markdown into Reportlab Paragraph functions
import re

from reportlab.platypus import Paragraph, ListFlowable, ListItem


def markdown_to_html(text: str) -> str:
    """
    Converts inline markdown (bold, italic, bold-italic) to simple 
    HTML tags that ReportLab can use with the fonts.py "addMappings".
    Does NOT handle headings or block structure.
    """
    # Bold-italic: ***text*** or ___text___
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.+?)___', r'<b><i>\1</i></b>', text)
    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    # Italic: *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    # Replace markdown line breaks with <br/>
    text = text.replace('\n', '<br/>')
    return text

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
    Lists are returned as (items, "ul") or (items, "ol") where items is a list of strings.
    """
    blocks = []
    lines = text.splitlines()
    paragraph = []
    list_items = []
    list_type = None
    ul_pattern = re.compile(r"^\s*([-*+])\s+(.*)")
    ol_pattern = re.compile(r"^\s*(\d+)\.\s+(.*)")
    for line in lines + [None]:  # Add None to flush last block
        if line is None or re.match(r"^\s*$", line):
            _flush_paragraph(paragraph, blocks)
            if list_items:
                blocks.append((list_items, list_type))
                list_items = []
                list_type = None
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
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
    Converts markdown text to a list of ReportLab Paragraph/ListFlowable objects with correct styles.
    """
    blocks = parse_markdown_blocks(text)
    paragraphs = []
    for content, style_key in blocks:
        if style_key in ("ul", "ol"):
            # Render list items as ListFlowable
            bulletType = "bullet" if style_key == "ul" else "1"
            items = [ListItem(Paragraph(markdown_to_html(item), styles["content_style"])) for item in content]
            paragraphs.append(ListFlowable(items, bulletType=bulletType, start="1" if style_key=="ol" else None))
        else:
            html = markdown_to_html(content)
            style = styles.get(style_key, styles["content_style"])
            paragraphs.append(Paragraph(html, style))
    return paragraphs
