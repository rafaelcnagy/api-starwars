from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from main import app, get_db
from database.database import Base


# CREATE DATABASE FOR TESTS
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# --- TESTS ---

# CREATE TESTS
def test_film_create():
    data = {
        'title': 'Teste',
        'release_date': '2022-02-09',
        'planets': [],
    }
    
    response = client.post('/film/create/', json=data)
    assert response.status_code == 201
    assert response.json() == {
        'id': 1,
        'title': 'Teste',
        'release_date': '2022-02-09',
        'planets': []
    }

def test_planet_create():
    data = {
        'name': 'Planeteste',
        'climates': 'arrid',
        'diameter': '1000',
        'population': '1000',
        'films': [1]
    }
    
    response = client.post('/planet/create/', json=data)
    assert response.status_code == 201
    assert response.json() == {
        'id': 1,
        'name': 'Planeteste',
        'climates': 'arrid',
        'diameter': '1000',
        'population': '1000',
        'films': [1]
    }

# READ TESTS
def test_film_read():
    
    response = client.get('/film/1')
    assert response.status_code == 200
    assert response.json() == {
        'id': 1,
        'title': 'Teste',
        'release_date': '2022-02-09',
        'planets': [1]
    }

def test_film_read_not_found():
    
    response = client.get('/film/0')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Film with id 0 not found'}

def test_planet_read():
    
    response = client.get('/planet/1')
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {
        'id': 1,
        'name': 'Planeteste',
        'climates': 'arrid',
        'diameter': '1000.0',
        'population': '1000',
        'films': [1]
    }

def test_planet_read_not_found():
    response = client.get('/planet/0')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Planet with id 0 not found'}

# UPDATE TESTS
def test_film_update():
    data = {
        'title': 'Teste - Epsódio 4',
        'release_date': '2022-02-08',
        'planets': [1]
    }
    
    response = client.put('/film/1/update', json=data)
    assert response.status_code == 200
    assert response.json() == {
        'id': 1,
        'title': 'Teste - Epsódio 4',
        'release_date': '2022-02-08',
        'planets': [1]
    }

def test_planet_update():
    data = {
        'name': 'Planeteste',
        'climates': 'arrid, urban',
        'diameter': '1000.0',
        'population': '10000000',
        'films': [1]
    }
    
    response = client.put('/planet/1/update', json=data)
    assert response.status_code == 200
    assert response.json() == {
        'id': 1,
        'name': 'Planeteste',
        'climates': 'arrid, urban',
        'diameter': '1000.0',
        'population': '10000000',
        'films': [1]
    }

# DELETE TESTS
def test_film_delete():
    response = client.delete(f'/film/1/delete')
    assert response.status_code == 204

def test_planet_delete():
    response = client.delete(f'/planet/1/delete')
    assert response.status_code == 204

