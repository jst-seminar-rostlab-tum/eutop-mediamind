BREAKING_NEWS_TRANSLATION_PROMPT = """
System:
You are a professional translator. Your task is to translate
breaking news content (title and summary) as accurately and
neutrally as possible.

User:
Translate the following breaking news to {target_lang}:

Title:
{title}

Summary:
{summary}

Instructions:
- Do not add or remove meaning.
- Do not assume facts not present in the original text.
- Keep the translation faithful and neutral.
- If the input is already in {target_lang}, return it as is.

Response format (JSON):
{
  "title": "...translated title...",
  "summary": "...translated summary..."
}
"""
