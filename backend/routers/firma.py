from fastapi import APIRouter, HTTPException, Request
from backend.db import SessionLocal
from backend.models import Firma

router = APIRouter()

@router.get("/firmalar")
def get_firmalar():
    db = SessionLocal()
    firmalar = db.query(Firma).all()
    return [ { "id": f.id, "ad": f.ad, "sektor": f.sektor, "atik": f.atik, "fiyat": f.fiyat, "miktar": f.miktar, "lead_time_days": f.lead_time_days } for f in firmalar ]

@router.post("/firma-ekle")
def add_firma(ad: str, sektor: str, atik: str = "", fiyat: float = 0, miktar: float = 0, lead_time_days: int = 0):
    db = SessionLocal()
    yeni_firma = Firma(ad=ad, sektor=sektor, atik=atik, fiyat=fiyat, miktar=miktar, lead_time_days=lead_time_days)
    db.add(yeni_firma)
    db.commit()
    db.refresh(yeni_firma)
    return {"success": True, "firma": yeni_firma.id}

@router.delete("/firma-sil/{firma_id}")
def delete_firma(firma_id: int):
    db = SessionLocal()
    firma = db.query(Firma).filter(Firma.id == firma_id).first()
    if not firma:
        raise HTTPException(status_code=404, detail="Firma bulunamadı")
    db.delete(firma)
    db.commit()
    return {"success": True}
