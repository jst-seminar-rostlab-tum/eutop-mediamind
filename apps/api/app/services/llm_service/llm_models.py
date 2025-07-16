from enum import Enum


class LLMModels(Enum):
    # High-performance models
    OPENAI_4O = "gpt-4o-2024-08-06"
    OPENAI_4O_MINI = "gpt-4o-mini-2024-07-18"
    


class ModelServiceMapping:
    """Maps services to their optimal models"""
    
    DEFAULT = LLMModels.OPENAI_4O.value
    ARTICLE_SUMMARY = LLMModels.OPENAI_4O.value
    CHATBOT = LLMModels.OPENAI_4O_MINI.value
    TRANSLATION = LLMModels.OPENAI_4O.value
    LOGIN_AUTOMATION = LLMModels.OPENAI_4O.value
    ARTICLE_CLEANER = LLMModels.OPENAI_4O.value
    KEYWORD_SUGGESTION = LLMModels.OPENAI_4O.value
