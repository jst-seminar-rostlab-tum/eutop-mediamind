from enum import Enum

from app.core.config import get_configs

configs = get_configs()


class TaskModelMapping(Enum):

    ARTICLE_SUMMARY = configs.LLM_MODEL_LARGE
    CHATBOT = configs.LLM_MODEL_SMALL
    TRANSLATION = configs.LLM_MODEL_LARGE
    LOGIN_AUTOMATION = configs.LLM_MODEL_LARGE
    ARTICLE_CLEANER = configs.LLM_MODEL_LARGE
    KEYWORD_SUGGESTION = configs.LLM_MODEL_LARGE
