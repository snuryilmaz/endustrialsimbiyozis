from fastapi import FastAPI
from backend.routers import firma, atik

app = FastAPI(
    title="Endüstriyel Simbiyoz API",
    description="Firmaların ürün alım/satım işlemlerini yöneten API",
    version="1.0.0"
)

app.include_router(firma.router)
app.include_router(atik.router)
