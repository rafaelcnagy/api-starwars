from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List

import database.models as models
from schemas.planets import PlanetRequest, PlanetUpdateRequest, PlanetResponse
from main import get_db

router = APIRouter(
    prefix="/planet",
    tags=["Planet"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[PlanetResponse])
def show_all_planets(db: Session = Depends(get_db)):
    planets_db = db.query(models.Planet).all()
    response = list()

    for planet_db in planets_db:
        response.append(
            PlanetResponse(
                id=planet_db.id, 
                name=planet_db.name, 
                climates=planet_db.climates,
                diameter=planet_db.diameter,
                population=planet_db.population,
                films=[association.film_id for association in planet_db.films],
            )
        )
    
    return response

@router.get("/{id}", response_model=PlanetResponse)
def show_planet(id: int, db: Session = Depends(get_db)):
    planet_db = db.query(models.Planet).get(id)

    if not planet_db:
        raise HTTPException(status_code=404, detail=f'Planet with id {id} not found')

    planet = PlanetResponse(
        id=planet_db.id, 
        name=planet_db.name, 
        climates=planet_db.climates,
        diameter=planet_db.diameter,
        population=planet_db.population,
        films=[association.film_id for association in planet_db.films],
    )

    return planet

@router.post("/create/", response_model=PlanetResponse, status_code=status.HTTP_201_CREATED)
def create_planet(planet: PlanetRequest, db: Session = Depends(get_db)):
    
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

    response = PlanetResponse(
        id=planet_db.id, 
        name=planet_db.name, 
        climates=planet_db.climates,
        diameter=planet_db.diameter,
        population=planet_db.population,
        films=[association.film_id for association in planet_db.films],
    )
    
    return response

@router.put("/{id}/update", response_model=PlanetResponse)
def update_planet(id: int, planet: PlanetUpdateRequest, db: Session = Depends(get_db)):
    
    planet_db = db.query(models.Planet).get(id)

    if not planet_db:
        raise HTTPException(status_code=404, detail=f'Planet with id {id} not found')
    
    planet_db.name = planet.name if planet.name is not None else planet_db.name
    
    planet_db.climates = planet.climates if planet.climates is not None else planet_db.climates
    planet_db.diameter = planet.diameter if planet.diameter is not None else planet_db.diameter
    planet_db.population = planet.population if planet.population is not None else planet_db.population

    if planet.films is not None:
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
    
    response = PlanetResponse(
        id=planet_db.id, 
        name=planet_db.name, 
        climates=planet_db.climates,
        diameter=planet_db.diameter,
        population=planet_db.population,
        films=[association.film_id for association in planet_db.films],
    )
    return response

@router.delete("/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_planet(id: int, db: Session = Depends(get_db)):
    
    planet_db = db.query(models.Planet).get(id)

    if not planet_db:
        raise HTTPException(status_code=404, detail=f'Planet with id {id} not found')

    for association in planet_db.films:
        db.delete(association)

    db.delete(planet_db)
    db.commit()
    
    return
