import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models.search_profile import (
    SearchProfile,
    SearchProfileCreate,
    SearchProfileRead,
    SearchProfilesRead,
    SearchProfileUpdate,
)

router = APIRouter(prefix="/search-profiles", tags=["search-profiles"])


@router.get(
    "/",
    response_model=SearchProfilesRead,
    dependencies=[Depends(get_current_active_superuser)],
)
def read_search_profiles(
    *, session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve search profiles.
    """
    count_stmt = select(func.count()).select_from(SearchProfile)
    count = session.exec(count_stmt).one()
    stmt = select(SearchProfile).offset(skip).limit(limit)
    search_profiles = session.exec(stmt).all()
    return SearchProfilesRead(data=search_profiles, count=count)


@router.post(
    "/",
    response_model=SearchProfileRead,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_search_profile(
    *, session: SessionDep, search_profile_in: SearchProfileCreate
) -> Any:
    """
    Create a new search profile.
    """
    search_profile = crud.create_search_profile(
        session=session, search_profile_create=search_profile_in
    )
    return search_profile


@router.get("/{search_profile_id}", response_model=SearchProfileRead)
def read_search_profile(
    *, session: SessionDep, search_profile_id: uuid.UUID
) -> Any:
    """
    Get a specific search profile by ID.
    """
    search_profile = crud.get_search_profile_by_id(
        session=session, search_profile_id=search_profile_id
    )
    if not search_profile:
        raise HTTPException(status_code=404, detail="SearchProfile not found")
    return search_profile


@router.put(
    "/{search_profile_id}",
    response_model=SearchProfileRead,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_search_profile(
    *,
    session: SessionDep,
    search_profile_id: uuid.UUID,
    search_profile_in: SearchProfileUpdate,
) -> Any:
    """
    Update an existing search profile.
    """
    db_search_profile = crud.get_search_profile_by_id(
        session=session, search_profile_id=search_profile_id
    )
    if not db_search_profile:
        raise HTTPException(status_code=404, detail="SearchProfile not found")
    updated = crud.update_search_profile(
        session=session,
        db_search_profile=db_search_profile,
        search_profile_update=search_profile_in,
    )
    return updated


@router.delete(
    "/{search_profile_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_search_profile(
    *, session: SessionDep, search_profile_id: uuid.UUID
) -> Any:
    """
    Delete a search profile.
    """
    db_search_profile = crud.get_search_profile_by_id(
        session=session, search_profile_id=search_profile_id
    )
    if not db_search_profile:
        raise HTTPException(status_code=404, detail="SearchProfile not found")
    crud.delete_search_profile(
        session=session, db_search_profile=db_search_profile
    )
    return {"message": "SearchProfile deleted successfully"}
