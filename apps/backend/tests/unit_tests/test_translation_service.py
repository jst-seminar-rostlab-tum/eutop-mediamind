# 1%
import pytest

from app.services.translation_service import ArticleTranslationService


def test_get_translator():
    translator = ArticleTranslationService.get_translator("en")
    assert callable(translator)
    assert translator("hello") == "hello"


def test_prepare_translation_content():
    ids = ["1"]
    texts = ["hello"]
    custom_ids, prompts, auto_responses = (
        ArticleTranslationService._prepare_translation_content(ids, texts)
    )
    assert isinstance(custom_ids, list)
    assert isinstance(prompts, list)
    assert isinstance(auto_responses, list)
