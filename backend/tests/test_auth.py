import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.sqlite3")

from main import app
from database import Base, SessionLocal
from models import User
from auth import hash_password


@pytest.fixture(autouse=True)
def reset_db():
    engine = create_engine("sqlite:///./test_auth.sqlite3", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    SessionLocal.configure(bind=engine)

    db = TestingSessionLocal()
    db.add(User(username="demo", email="demo@example.com", password=hash_password("secret123")))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def test_login_returns_401_for_unknown_email():
    with TestClient(app) as client:
        response = client.post("/login", json={"email": "missing@example.com", "password": "secret123"})
        assert response.status_code == 401
        assert response.json()["detail"] == "No user exists for this email."


def test_login_returns_401_for_wrong_password():
    with TestClient(app) as client:
        response = client.post("/login", json={"email": "demo@example.com", "password": "wrongpass"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Email and password do not match."


def test_login_returns_200_for_valid_credentials():
    with TestClient(app) as client:
        response = client.post("/login", json={"email": "demo@example.com", "password": "secret123"})
        assert response.status_code == 200
        assert response.json()["message"] == "Login successful"
