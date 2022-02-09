from fastapi import APIRouter
from endpoints import films, planets 

router = APIRouter()
router.include_router(films.router)
router.include_router(planets.router)
