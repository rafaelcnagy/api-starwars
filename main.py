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
    films = db.query(models.Film).all()

    return films

@app.get("/film/{id}", response_model=schemas.FilmRequest)
def show_film(id: int, db: Session = Depends(get_db)):
    film_db = db.query(models.Film).get(id)

    if not film_db:
        raise HTTPException(status_code=404, detail=f'Film with id {id} not found')
    
    film = schemas.FilmRequest(
        id=film_db.id, 
        title=film_db.title, 
        release_date=film_db.release_date
    )

    return film

@app.post("/film/create/", response_model=schemas.FilmRequest, status_code=status.HTTP_201_CREATED)
def create_film(film: schemas.FilmRequest, db: Session = Depends(get_db)):
    
    film_db = models.Film(title=film.title, release_date=film.release_date)

    try:
        db.add(film_db)
        db.commit()
        db.refresh(film_db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f'A film with title "{film.title}" already exists in the database') 
    except Exception as e:
        raise e

    film.id = film_db.id
    
    return film

@app.put("/film/{id}/update", response_model=schemas.FilmRequest)
def update_film(id: int, film: schemas.FilmRequest, db: Session = Depends(get_db)):
    
    film_db = db.query(models.Film).get(id)

    if film_db:
        film_db.title = film.title
        film_db.release_date = film.release_date
        db.commit()
        db.refresh(film_db)
    else:
        raise HTTPException(status_code=404, detail=f'Film with id {id} not found')

    film.id = film_db.id
    
    return film

@app.delete("/film/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_film(id: int, db: Session = Depends(get_db)):
    
    film_db = db.query(models.Film).get(id)

    if film_db:
        db.delete(film_db)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail=f'Film with id {id} not found')
    
    return
