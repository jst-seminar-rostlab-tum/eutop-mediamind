from sqlmodel import Session, SQLModel, create_engine, select


from app.core.config import configs
from app.models import User, UserCreate

engine = create_engine(str(configs.SQLALCHEMY_DATABASE_URI))

# Drop and recreate all tables to apply new schema changes
# SQLModel.metadata.drop_all(engine)

# SQLModel.metadata.create_all(engine)

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    
