from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models import Article, Keyword
from app.repositories.keyword_repository import KeywordRepository

router = APIRouter(prefix="/keywords", tags=["keywords"])

logger = get_logger(__name__)

