from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Assistant de jeu de société"}

