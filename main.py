import time
from ipaddress import ip_address
from typing import Callable
import pathlib

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import settings


app = FastAPI()


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing caches.

    :return: A list of coroutines
    :doc-author: Trelent
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_IPS = [
    ip_address('192.168.1.0'),
    ip_address('172.16.0.0'),
    ip_address("127.0.0.1")
]


# @app.middleware("http")
# async def limit_access_by_ip(request: Request, call_next: Callable):
#     """
#     The limit_access_by_ip function is a middleware function that limits access to the API by IP address.
#     It checks if the client's IP address is in ALLOWED_IPS, and if not, returns a 403 Forbidden response.
#
#     :param request: Request: Access the request object
#     :param call_next: Callable: Pass the next function in the chain
#     :return: An error if the ip address is not allowed
#     :doc-author: Trelent
#     """
#     ip = ip_address(request.client.host)
#     if ip not in ALLOWED_IPS:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
#     response = await call_next(request)
#     return response


@app.middleware('http')
async def custom_middleware(request: Request, call_next):
    """
    The custom_middleware function is a middleware function that adds the time it took to process
    the request in seconds as a header called 'performance'

    :param request: Request: Get the request object
    :param call_next: Call the next middleware in the chain
    :return: A response object
    :doc-author: Trelent
    """
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers['performance'] = str(duration)
    return response

templates = Jinja2Templates(directory='templates')
BASE_DIR = pathlib.Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    """
    The root function is the entry point of the application.
    It returns a TemplateResponse object, which renders an HTML template using Jinja2.
    The template is located in templates/index.html and uses data from the request object to render itself.

    :param request: Request: Get the request object for the current request
    :return: A templateresponse object, which contains the template index
    :doc-author: Trelent
    """
    return templates.TemplateResponse('index.html', {"request": request, "title": "Contacts App"})


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If there are no results, then we know something is wrong with our connection.

    :param db: Session: Pass the database session to the function
    :return: A dict with a message
    :doc-author: Trelent
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')
