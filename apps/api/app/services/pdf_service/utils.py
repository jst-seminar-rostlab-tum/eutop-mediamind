# This file contains utility functions for the PDF service.
def calculate_reading_time(text, words_per_minute=180):
    word_count = len(text.split())
    return max(1, int(round(word_count / words_per_minute)))
