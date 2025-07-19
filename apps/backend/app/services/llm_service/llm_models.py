from enum import Enum

from app.core.config import get_configs

configs = get_configs()


class TaskModelMapping(Enum):

    TEST = configs.MODEL_TEST
    ARTICLE_SUMMARY = configs.MODEL_ARTICLE_SUMMARY
    CHATBOT = configs.MODEL_CHATBOT
    TRANSLATION = configs.MODEL_TRANSLATION
    LOGIN_AUTOMATION = configs.MODEL_LOGIN_AUTOMATION
    ARTICLE_CLEANER = configs.MODEL_ARTICLE_CLEANER
    KEYWORD_SUGGESTION = configs.MODEL_KEYWORD_SUGGESTION
