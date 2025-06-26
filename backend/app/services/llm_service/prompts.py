# backend/app/prompts/search_profile_prompts.py

KEYWORD_SUGGESTION_PROMPT_EN = """
System:
You are an assistant that suggests precise and relevant search keywords for a user.

User:
Search profile name: {search_profile_name}
Topic: {selected_topic_name}
Already used keywords: {selected_topic_keywords}

Related topics:
{related_topics}

Task:
Suggest exactly five new keywords that
1. Do not appear in “Already used keywords.”
2. Are optimal for the search profile name, topic, and “Already used keywords.”
3. Are not synonyms of the existing keywords.
4. Consist of 1–3 words each.

Response format (JSON list):
["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
"""

KEYWORD_SUGGESTION_PROMPT_DE = """
System:
Du bist ein Assistent, der für einen Nutzer präzise und relevante Such-Keywords vorschlägt.

User:
Suchprofilname: {search_profile_name}
Thema: {selected_topic_name}
Bereits verwendete Keywords: {selected_topic_keywords}

Verwandte Themen:
{related_topics}

Aufgabe:
Schlage genau fünf neue Keywords vor, die
1. Nicht in „Bereits verwendete Keywords“ vorkommen.
2. Optimal zu Suchprofilname, Thema und "Bereits verwendete Keywords" passen.
3. Keine Synonyme der vorhandenen Keywords sind.
4. Jeweils 1–3 Wörter umfassen.

Antwortformat (JSON-Liste):
["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
            """
