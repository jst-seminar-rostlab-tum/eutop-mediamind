from sqlmodel import Session, SQLModel, create_engine

from app.core.config import configs

engine = create_engine(str(configs.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
