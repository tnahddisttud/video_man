from fastapi import FastAPI
import api.video as video
from api import auth
from database import models
from database.db import engine

app = FastAPI(title="VideoMan: The Ultimate Video Management API")

models.Base.metadata.create_all(engine)

app.include_router(video.router)
app.include_router(auth.router)


@app.get("/")
async def home():
    return "Hello Admin"
