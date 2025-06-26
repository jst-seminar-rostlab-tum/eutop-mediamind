# backend/app/prompts/search_profile_prompts.py

KEYWORD_SUGGESTION_PROMPT_EN = (
    "I will give you a list of related keywords. Please add 5 new relevant keywords. "
    "Don't include synonyms, but suggest words to pin down the topic more exactly with your added relevant keywords.\n"
    "Keywords: {keywords}\n\n"
)

KEYWORD_SUGGESTION_PROMPT_DE = """
            Du bist ein Assitent, der für einen Nutzer relevante Such-Keywords vorschlägt.
            
            Suchprofilname: {search_profile_name}
            
            Ausgewähltes Thema: {selected_topic_name}
            Ausgewählte Keywords: {selected_topic_keywords}
            
            Verwandte Themen:
            {related_topics}
            
            Aufgabe:
            Schlage **genau fünf** neue Keywords vor, die:
            1. Nicht in der obigen Liste der ausgewählten Keywords enthalten sind.
            2. Sehr gut zum Suchprofilename und dem ausgewählten Thema passen.
            3. Keine Synonyme der bereits vorhandenen Keywords sind.
            4. Prägnant sind (jeweils nur 1-3 Wörter).
            
            Antwortformat:
            Gib die fünf neuen Keywords als liste zurück. z.B.: ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
            """
