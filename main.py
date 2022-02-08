from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


@app.get("/films/", response_model=List[schemas.FilmRequest])
def show_all_films(db: Session = Depends(get_db)):
    films_db = db.query(models.Film).all()
    films = list()

    for film_db in films_db:
        films.append(
            schemas.FilmRequest(
                id=film_db.id, 
                title=film_db.title, 
                release_date=film_db.release_date,
                planets=[association.planet_id for association in film_db.planets],
            )
        )
    
    return films

@app.get("/film/{id}", response_model=schemas.FilmRequest)
def show_film(id: int, db: Session = Depends(get_db)):
    film_db = db.query(models.Film).get(id)

    if not film_db:
        raise HTTPException(status_code=404, detail=f'Film with id {id} not found')

    film = schemas.FilmRequest(
        id=film_db.id, 
        title=film_db.title, 
        release_date=film_db.release_date,
        planets=[association.planet_id for association in film_db.planets],
    )

    return film

@app.post("/film/create/", response_model=schemas.FilmRequest, status_code=status.HTTP_201_CREATED)
def create_film(film: schemas.FilmRequest, db: Session = Depends(get_db)):
    
    film_db = models.Film(title=film.title, release_date=film.release_date)
    planets_db = list()
    for planet_id in film.planets:
        planet_db = db.query(models.Planet).get(planet_id)
        if not planet_db:
            raise HTTPException(status_code=404, detail=f'Planet with id {planet_id} not found') 
        planets_db.append(planet_db)

    for planet_db in planets_db:
        association = models.Association()
        association.planet = planet_db
        film_db.planets.append(association)
        db.add(association)

    db.add(film_db)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f'A film with title "{film.title}" already exists in the database') 
    except Exception as e:
        raise e

    db.refresh(film_db)

    film.id = film_db.id
    
    return film

@app.put("/film/{id}/update", response_model=schemas.FilmRequest)
def update_film(id: int, film: schemas.FilmRequest, db: Session = Depends(get_db)):
    
    film_db = db.query(models.Film).get(id)

    if not film_db:
        raise HTTPException(status_code=404, detail=f'Film with id {id} not found')
    
    film_db.title = film.title
    film_db.release_date = film.release_date

    # Verifica se planetas existem no banco
    planets_db = list()
    for planet_id in film.planets:
        planet_db = db.query(models.Planet).get(planet_id)
        if not planet_db:
            raise HTTPException(status_code=404, detail=f'Planet with id {planet_id} not found')
        planets_db.append(planet_db)

    # Encontra associações planeta-filme que devem ser adicionados e removidos
    planets_db_to_add = [planet_db for planet_db in planets_db if planet_db not in film_db.planets]
    associations_to_remove = [planet_db for planet_db in film_db.planets if planet_db not in planets_db]

    # Adiciona associações
    for planet_db in planets_db_to_add:
        association = models.Association()
        association.planet = planet_db
        film_db.planets.append(association)
        db.add(association)

    # Remove associações
    for association in associations_to_remove:
        association = db.query(models.Association).get({'planet_id': association.planet_id, 'film_id': film_db.id})
        db.delete(association)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f'A film with title "{film.title}" already exists in the database') 
    except Exception as e:
        raise e
    
    db.refresh(film_db)

    film.id = film_db.id
    
    return film

@app.delete("/film/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_film(id: int, db: Session = Depends(get_db)):
    
    film_db = db.query(models.Film).get(id)

    if not film_db:
        raise HTTPException(status_code=404, detail=f'Film with id {id} not found')

    for association in film_db.planets:
        db.delete(association)

    db.delete(film_db)
    db.commit()
    
    return

