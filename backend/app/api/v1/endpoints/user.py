from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"], dependencies=[])


@router.get("", response_model=str)
def get_user_list():
    return "hello world"
