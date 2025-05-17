import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate
from app.models.organization import Organization, OrganizationCreate, OrganizationUpdate
from app.models.user import User
from app.models.search_profile import (
    SearchProfile, SearchProfileCreate, SearchProfileRead,
    SearchProfileUpdate
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    # Assign user to default organization if not provided
    if hasattr(user_create, 'organization_id') and user_create.organization_id:
        db_obj.organization_id = user_create.organization_id
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


# Organization CRUD operations

def get_organization_by_id(*, session: Session, organization_id: uuid.UUID) -> Organization | None:
    return session.get(Organization, organization_id)


def get_organizations(*, session: Session, skip: int = 0, limit: int = 100) -> list[Organization]:
    statement = select(Organization).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_organization(*, session: Session, organization_create: OrganizationCreate) -> Organization:
    db_obj = Organization.model_validate(organization_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_organization(*, session: Session, db_organization: Organization, organization_update: OrganizationUpdate) -> Organization:
    update_data = organization_update.model_dump(exclude_unset=True)
    db_organization.sqlmodel_update(update_data)
    session.add(db_organization)
    session.commit()
    session.refresh(db_organization)
    return db_organization


def delete_organization(*, session: Session, db_organization: Organization) -> None:
    session.delete(db_organization)
    session.commit()


def add_user_to_organization(*, session: Session, organization_id: uuid.UUID, user_id: uuid.UUID) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None
    user.organization_id = organization_id
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# SearchProfile CRUD operations

def get_search_profile_by_id(*, session: Session, search_profile_id: uuid.UUID) -> SearchProfile | None:
    return session.get(SearchProfile, search_profile_id)


def get_search_profiles(*, session: Session, skip: int = 0, limit: int = 100) -> list[SearchProfile]:
    statement = select(SearchProfile).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_search_profile(*, session: Session, search_profile_create: SearchProfileCreate) -> SearchProfile:
    db_obj = SearchProfile.model_validate(search_profile_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_search_profile(*, session: Session, db_search_profile: SearchProfile, search_profile_update: SearchProfileUpdate) -> SearchProfile:
    update_data = search_profile_update.model_dump(exclude_unset=True)
    db_search_profile.sqlmodel_update(update_data)
    session.add(db_search_profile)
    session.commit()
    session.refresh(db_search_profile)
    return db_search_profile


def delete_search_profile(*, session: Session, db_search_profile: SearchProfile) -> None:
    session.delete(db_search_profile)
    session.commit()
