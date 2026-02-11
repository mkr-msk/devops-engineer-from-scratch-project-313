import pytest
from sqlmodel import Session, SQLModel, create_engine, delete
from sqlmodel.pool import StaticPool

import app.database as database
import app.routes as routes
from app.models import Link
from main import app as flask_app


# TEST DB
@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    yield engine

    SQLModel.metadata.drop_all(engine)


# TEST FLASK APP
@pytest.fixture(scope="function")
def client(test_engine, monkeypatch):
    with Session(bind=test_engine) as session:
        statement = delete(Link)
        session.exec(statement)
        session.commit()

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(routes, "BASE_URL", "http://testserver")

    flask_app.config["TESTING"] = True

    with flask_app.test_client() as test_client:
        yield test_client
