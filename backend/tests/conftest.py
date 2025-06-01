import pytest
import os
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from sqlmodel import SQLModel, Session


from app.core.db import engine, init_db
from app.main import AppCreator


@pytest.fixture
def client():
    app_creator = AppCreator()
    app = app_creator.app
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_name(request):
    return request.node.name


#--- Test Database Setup ------------------------------------------------------

postgres = PostgresContainer("postgres:16-alpine")


@pytest.fixture(autouse=True, scope="package")
def setup(request):
    # Spin up a Postgres container
    postgres.start()

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)
    os.environ["POSTGRES_SERVER"] = postgres.get_container_host_ip()
    os.environ["POSTGRES_PORT"] = str(postgres.get_exposed_port(5432))
    os.environ["POSTGRES_USER"] = postgres.username
    os.environ["POSTGRES_PASSWORD"] = postgres.password
    os.environ["POSTGRES_DB"] = postgres.dbname
    with Session(engine) as session:
        init_db(session)
    return session


@pytest.fixture(scope="function", autouse=True)
def setup_data():
    # Clear SQLModel metadata to reset the database state after each test
    SQLModel.metadata.clear()
