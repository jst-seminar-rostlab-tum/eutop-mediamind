from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from sqlmodel import Session

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models.organization import (
    OrganizationCreate, OrganizationRead, OrganizationsRead
)
from app.models.organization import Organization
from app.models.user import UserPublic

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.get("/", response_model=OrganizationsRead, dependencies=[Depends(get_current_active_superuser)])
def read_organizations(
    *, session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve organizations.
    """
    count_statement = select(func.count()).select_from(Organization)
    count = session.exec(count_statement).one()
    statement = select(Organization).offset(skip).limit(limit)
    organizations = session.exec(statement).all()
    return OrganizationsRead(data=organizations, count=count)

@router.post("/", response_model=OrganizationRead, dependencies=[Depends(get_current_active_superuser)])
def create_organization(
    *, session: SessionDep, organization_in: OrganizationCreate
) -> Any:
    """
    Create new organization.
    """
    # Check for existing organization name
    existing = session.exec(select(Organization).where(Organization.name == organization_in.name)).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="The organization with this name already exists in the system.",
        )
    organization = crud.create_organization(
        session=session, organization_create=organization_in
    )
    return organization

@router.get("/{organization_id}", response_model=OrganizationRead)
def read_organization(
    *, session: SessionDep, organization_id: uuid.UUID
) -> Any:
    """
    Get a specific organization by id.
    """
    organization = crud.get_organization_by_id(
        session=session, organization_id=organization_id
    )
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@router.delete("/{organization_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_organization(
    *, session: SessionDep, organization_id: uuid.UUID
) -> Any:
    """
    Delete an organization.
    """
    organization = crud.get_organization_by_id(
        session=session, organization_id=organization_id
    )
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    crud.delete_organization(session=session, db_organization=organization)
    return {"message": "Organization deleted successfully"}

@router.post("/{organization_id}/users/{user_id}", response_model=UserPublic, dependencies=[Depends(get_current_active_superuser)])
def add_user(
    *, session: SessionDep, organization_id: uuid.UUID, user_id: uuid.UUID
) -> Any:
    """
    Add a user to an organization.
    """
    organization = crud.get_organization_by_id(
        session=session, organization_id=organization_id
    )
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    user = crud.add_user_to_organization(
        session=session, organization_id=organization_id, user_id=user_id
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
