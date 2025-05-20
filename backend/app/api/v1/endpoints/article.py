from fastapi import APIRouter

router = APIRouter(prefix="/articles", tags=["articles"], dependencies=[])


@router.get("", response_model=str)
def get_article_list():
    return "articles"
