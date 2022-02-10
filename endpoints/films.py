from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List

import database.models as models, schemas.schemas as schemas
from main import get_db

router = APIRouter(
    prefix="/film",
    tags=["Film"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.FilmRequest])
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

@router.get("/{id}", response_model=schemas.FilmRequest)
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

@router.post("/create/", response_model=schemas.FilmRequest, status_code=status.HTTP_201_CREATED)
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

@router.put("/{id}/update", response_model=schemas.FilmUpdateRequest)
def update_film(id: int, film: schemas.FilmUpdateRequest, db: Session = Depends(get_db)):
    
    film_db = db.query(models.Film).get(id)

    if not film_db:
        raise HTTPException(status_code=404, detail=f'Film with id {id} not found')
    
    film_db.title = film.title if film.title else film_db.title
    film_db.release_date = film.release_date if film.release_date else film_db.release_date

    if film.planets is not None:
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

@router.delete("/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_film(id: int, db: Session = Depends(get_db)):
    
    film_db = db.query(models.Film).get(id)

    if not film_db:
        raise HTTPException(status_code=404, detail=f'Film with id {id} not found')

    for association in film_db.planets:
        db.delete(association)

    db.delete(film_db)
    db.commit()
    
    return

