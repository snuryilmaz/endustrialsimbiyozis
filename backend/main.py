from fastapi import FastAPI
from backend.routers import firma, atik

app = FastAPI(title="Endustriyel Simbiyoz Backend")

app.include_router(firma.router)
app.include_router(atik.router)
