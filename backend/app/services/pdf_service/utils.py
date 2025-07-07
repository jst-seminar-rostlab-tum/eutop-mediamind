# This file contains utility functions for the PDF service.
import re

def markdown_to_html(text: str) -> str:
    """
    Converts basic markdown in text to simple HTML tags that ReportLab
    can read with the addMapping from fonts.py file.
    Handles bold (**text**), italic (*text*), bold-italic (***text***), and line breaks.
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


def calculate_reading_time(text, words_per_minute=180):
    word_count = len(text.split())
    return max(1, int(round(word_count / words_per_minute)))
