import datetime
import requests

from database.database import SessionLocal
import database.models as models


def download_official_data():
    db = SessionLocal()
    qtd_films = db.query(models.Film).filter(models.Film.official == True).count()
    qtd_planets = db.query(models.Planet).filter(models.Planet.official == True).count()

    if qtd_films < 6 or qtd_planets < 60:
        print(f'{datetime.datetime.now()} - Downloading data from swapi.dev')
        films = request_films(db)
        print(f'{datetime.datetime.now()} - Films done')
        request_planets(db, films)
        print(f'{datetime.datetime.now()} - Planets done')
        print(f'{datetime.datetime.now()} - Data download completed')
    else:
        print(f'{datetime.datetime.now()} - All official data checked')


def request_films(db):
    films = dict()

    with requests.get('https://swapi.dev/api/films') as response:
        response.raise_for_status()
        json = response.json()

    for film_json in json['results']:
        title = film_json['title']
        release_date = datetime.datetime.strptime(film_json['release_date'], '%Y-%m-%d').date()
        film_db = models.Film(
            title=title,
            release_date=release_date,
            official=True,
        )

        film_db_exists = db.query(models.Film).filter_by(title=title).first()
        if film_db_exists is None:
            db.add(film_db)
            db.commit()
            db.refresh(film_db)
        else:
            film_db = film_db_exists
        
        films[film_json['url']] = film_db

    return films

def request_planets(db, films):
    url = 'https://swapi.dev/api/planets'
    while url:
        with requests.get(url) as response:
            response.raise_for_status()
            json = response.json()

        for planet_json in json['results']:
            name = planet_json['name']
            diameter = planet_json['diameter'] if planet_json['diameter'] != 'unknown' else None
            climate = planet_json['climate'] if planet_json['climate'] != 'unknown' else None
            population = planet_json['population'] if planet_json['population'] != 'unknown' else None

            planet_db = models.Planet(
                name=name,
                diameter=diameter,
                climates=climate,
                population=population,
                official=True,
            )

            planet_db_exists = db.query(models.Planet).filter_by(name=name).first()
            if planet_db_exists is None:
                for film_url in planet_json['films']:
                    film_db = films[film_url]
                    association = models.Association(official=True)
                    association.film = film_db
                    planet_db.films.append(association)
                    db.add(association)

                db.add(planet_db)
                db.commit()
                db.refresh(planet_db)
            else:
                planet_db = planet_db_exists

        url = json['next']
