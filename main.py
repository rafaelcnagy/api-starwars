from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import models, schemas, api
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
api.download_official_data()

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
    
    film_db = models.Film(
        title=film.title,
        release_date=film.release_date
    )

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



@app.get("/planets/", response_model=List[schemas.PlanetRequest])
def show_all_planets(db: Session = Depends(get_db)):
    planets_db = db.query(models.Planet).all()
    planets = list()

    for planet_db in planets_db:
        planets.append(
            schemas.PlanetRequest(
                id=planet_db.id, 
                name=planet_db.name, 
                climates=planet_db.climates,
                diameter=planet_db.diameter,
                population=planet_db.population,
                films=[association.film_id for association in planet_db.films],
            )
        )
    
    return planets

@app.get("/planet/{id}", response_model=schemas.PlanetRequest)
def show_planet(id: int, db: Session = Depends(get_db)):
    planet_db = db.query(models.Planet).get(id)

    if not planet_db:
        raise HTTPException(status_code=404, detail=f'Planet with id {id} not found')

    planet = schemas.PlanetRequest(
        id=planet_db.id, 
        name=planet_db.name, 
        climates=planet_db.climates,
        diameter=planet_db.diameter,
        population=planet_db.population,
        films=[association.film_id for association in planet_db.films],
    )

    return planet

@app.post("/planet/create/", response_model=schemas.PlanetRequest, status_code=status.HTTP_201_CREATED)
def create_planet(planet: schemas.PlanetRequest, db: Session = Depends(get_db)):
    
    planet_db = models.Planet(
        name=planet.name, 
        climates=planet.climates,
        diameter=planet.diameter,
        population=planet.population,
    )

    films_db = list()
    for film_id in planet.films:
        film_db = db.query(models.Film).get(film_id)
        if not film_db:
            raise HTTPException(status_code=404, detail=f'Film with id {film_id} not found') 
        films_db.append(film_db)

    for film_db in films_db:
        association = models.Association()
        association.film = film_db
        planet_db.films.append(association)
        db.add(association)

    db.add(planet_db)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f'A planet with name "{planet.name}" already exists in the database') 
    except Exception as e:
        raise e

    db.refresh(planet_db)

    planet.id = planet_db.id
    
    return planet

@app.put("/planet/{id}/update", response_model=schemas.PlanetRequest)
def update_planet(id: int, planet: schemas.PlanetRequest, db: Session = Depends(get_db)):
    
    planet_db = db.query(models.Planet).get(id)

    if not planet_db:
        raise HTTPException(status_code=404, detail=f'Planet with id {id} not found')
    
    planet_db.name = planet.name
    planet_db.climates = planet.climates
    planet_db.diameter = planet.diameter
    planet_db.population = planet.population

    # Verifica se filmas existem no banco
    films_db = list()
    for film_id in planet.films:
        film_db = db.query(models.Film).get(film_id)
        if not film_db:
            raise HTTPException(status_code=404, detail=f'Film with id {film_id} not found')
        films_db.append(film_db)

    # Encontra associações filma-planete que devem ser adicionados e removidos
    films_db_to_add = [film_db for film_db in films_db if film_db not in planet_db.films]
    associations_to_remove = [film_db for film_db in planet_db.films if film_db not in films_db]

    # Adiciona associações
    for film_db in films_db_to_add:
        association = models.Association()
        association.film = film_db
        planet_db.films.append(association)
        db.add(association)

    # Remove associações
    for association in associations_to_remove:
        association = db.query(models.Association).get({'film_id': association.film_id, 'planet_id': planet_db.id})
        db.delete(association)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f'A planet with name "{planet.name}" already exists in the database') 
    except Exception as e:
        raise e
    
    db.refresh(planet_db)

    planet.id = planet_db.id
    
    return planet

@app.delete("/planet/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_planet(id: int, db: Session = Depends(get_db)):
    
    planet_db = db.query(models.Planet).get(id)

    if not planet_db:
        raise HTTPException(status_code=404, detail=f'Planet with id {id} not found')

    for association in planet_db.films:
        db.delete(association)

    db.delete(planet_db)
    db.commit()
    
    return

